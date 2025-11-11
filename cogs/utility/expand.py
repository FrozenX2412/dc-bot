# cogs/util/expand.py
import aiohttp
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Union, Optional
from urllib.parse import urlparse
import socket
import ipaddress

# Basic private-network check helper (resolves hostname -> addresses)
# NOTE: this uses getaddrinfo which may block; run in executor to avoid blocking the event loop.
def _is_private_host(host: str) -> bool:
    try:
        # resolve all addresses for host
        infos = socket.getaddrinfo(host, None)
        for family, _, _, _, sockaddr in infos:
            addr = sockaddr[0]
            ip = ipaddress.ip_address(addr)
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                return True
    except Exception:
        # On resolution failure, be conservative and return True? Here we return False so we don't block legitimate hosts.
        return False
    return False

def _normalize_url(u: str) -> Optional[str]:
    u = u.strip()
    if not u:
        return None
    # if scheme missing, assume https
    parsed = urlparse(u, scheme="https")
    if not parsed.netloc:
        # maybe user passed without scheme like example.com/path
        parsed = urlparse("https://" + u, scheme="https")
    # accept only http/https
    if parsed.scheme not in ("http", "https"):
        return None
    return parsed.geturl()

class Expand(commands.Cog):
    """Expand shortened URLs and show redirect chain (async)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._session: Optional[aiohttp.ClientSession] = None
        # configuration
        self._timeout = aiohttp.ClientTimeout(total=12)  # seconds
        self._max_redirects = 10

    async def cog_load(self) -> None:
        # create session when cog loads
        self._session = aiohttp.ClientSession(timeout=self._timeout)

    async def cog_unload(self) -> None:
        # close session cleanly
        if self._session and not self._session.closed:
            await self._session.close()

    @commands.hybrid_command(name="expand", description="Expand a shortened URL and show redirect chain. Example: /expand url:https://bit.ly/...")
    @app_commands.describe(url="The shortened URL to expand (with or without scheme).", follow="If true, fetch full content when HEAD isn't supported.")
    async def expand(self, ctx: Union[commands.Context, discord.Interaction], url: str, follow: bool = True):
        is_interaction = isinstance(ctx, discord.Interaction)
        requester = getattr(ctx.user if is_interaction else ctx.author, "display_name", "Unknown")

        # normalize & validate
        normalized = _normalize_url(url)
        if not normalized:
            err = discord.Embed(
                title="❌ Invalid URL",
                description="Provide a valid http/https URL. Example: `https://bit.ly/xyz` or `bit.ly/xyz`.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
            return

        # optional basic host private-check (run in executor to avoid blocking)
        parsed = urlparse(normalized)
        host = parsed.hostname or ""
        try:
            loop = asyncio.get_running_loop()
            is_private = await loop.run_in_executor(None, _is_private_host, host)
            if is_private:
                err = discord.Embed(
                    title="❌ Refusing to expand private or local host",
                    description="For security, expansion of URLs that resolve to private/local addresses is blocked.",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                err.set_footer(text=f"Requested by {requester}")
                if is_interaction:
                    await ctx.response.send_message(embed=err, ephemeral=True)
                else:
                    await ctx.send(embed=err)
                return
        except Exception:
            # resolution failed; continue but do not block user unnecessarily
            pass

        # ensure we have a session
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout)

        try:
            redirect_chain = []
            current_url = normalized
            remaining = self._max_redirects
            status = None
            headers = None

            # First try HEAD (less data). If server returns 405/501 or doesn't support HEAD well, optionally fall back to GET.
            while remaining > 0:
                remaining -= 1
                async with self._session.request("HEAD", current_url, allow_redirects=False) as resp:
                    status = resp.status
                    headers = resp.headers
                    location = headers.get("Location")
                    redirect_chain.append((current_url, status))
                    if 300 <= status < 400 and location:
                        # build absolute URL if location is relative
                        next_url = urlparse(location, scheme=parsed.scheme).geturl() if urlparse(location).scheme else urlparse(current_url)._replace(path=location).geturl()
                        current_url = next_url
                        continue
                    # Not a redirect -> stop here
                    break

            # If HEAD gave us no content info and follow==True, try GET on final url to obtain content-type/length and final url (some services only redirect on GET)
            content_type = headers.get("Content-Type") if headers else None
            content_length = headers.get("Content-Length") if headers else None
            final_url = redirect_chain[-1][0] if redirect_chain else current_url

            # Some services only perform redirects on GET; check for common redirect-statuss or if content info missing and follow allowed
            if follow and (status in (405, 501) or (not content_type and status < 400)):
                try:
                    async with self._session.get(final_url, allow_redirects=True, max_redirects=self._max_redirects) as gres:
                        # get final url and history
                        content_type = gres.headers.get("Content-Type")
                        content_length = gres.headers.get("Content-Length")
                        final_url = str(gres.url)
                        # append get-history if any
                        # note: aiohttp .history exists when allow_redirects True
                        # but here we used allow_redirects so history is in gres.history
                        if getattr(gres, "history", None):
                            for h in gres.history:
                                redirect_chain.append((str(h.url), h.status))
                            redirect_chain.append((final_url, gres.status))
                except aiohttp.TooManyRedirects:
                    raise ValueError("Too many redirects while following GET.")
                except Exception:
                    # fallback: ignore GET errors and use HEAD results
                    pass

            # Build embed of results
            embed = discord.Embed(
                title="🔎 Expanded URL",
                description=f"**Input:** {url}\n**Final URL:** {final_url}",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            # add basic info
            if status:
                embed.add_field(name="Final status", value=str(status), inline=True)
            if content_type:
                embed.add_field(name="Content-Type", value=content_type, inline=True)
            if content_length:
                embed.add_field(name="Content-Length", value=content_length, inline=True)

            # Redirect chain (show last N)
            chain_lines = []
            for u, s in redirect_chain:
                chain_lines.append(f"`[{s}]` {u}")
            if chain_lines:
                embed.add_field(name=f"Redirect chain ({len(chain_lines)})", value="\n".join(chain_lines[:10]), inline=False)

            embed.set_footer(text=f"Requested by {requester}")

            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=embed)
                else:
                    await ctx.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

        except ValueError as ve:
            err = discord.Embed(title="❌ Error", description=str(ve), color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
        except Exception as exc:
            # unexpected
            err = discord.Embed(title="⚠️ Failed to expand URL", description="An error occurred while expanding the URL.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.add_field(name="Details", value=str(exc), inline=False)
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)

