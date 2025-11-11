# cogs/util/shorten.py
import aiohttp
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Union, Optional
from urllib.parse import urlparse

CLEANURI_API = "https://cleanuri.com/api/v1/shorten"
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=12)


def _normalize_url(u: str) -> Optional[str]:
    u = u.strip()
    if not u:
        return None
    # add https if scheme missing
    parsed = urlparse(u, scheme="https")
    if not parsed.netloc:
        parsed = urlparse("https://" + u, scheme="https")
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return parsed.geturl()


class Shorten(commands.Cog):
    """Shorten URLs using a public API (async)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._session: Optional[aiohttp.ClientSession] = None
        self._timeout = DEFAULT_TIMEOUT

    async def cog_load(self) -> None:
        self._session = aiohttp.ClientSession(timeout=self._timeout)

    async def cog_unload(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    @commands.hybrid_command(name="shorten", aliases=["short"], description="Shorten a URL (uses cleanuri.com by default)")
    @app_commands.describe(url="The URL to shorten (you can omit https://)")
    async def shorten(self, ctx: Union[commands.Context, discord.Interaction], url: str):
        is_interaction = isinstance(ctx, discord.Interaction)
        requester = getattr(ctx.user if is_interaction else ctx.author, "display_name", "Unknown")

        normalized = _normalize_url(url)
        if not normalized:
            err = discord.Embed(
                title="❌ Invalid URL",
                description="Please provide a valid http/https URL. Example: `https://example.com` or `example.com`.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
            return

        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout)

        try:
            async with self._session.post(CLEANURI_API, data={"url": normalized}) as resp:
                # safe parsing and error handling
                text = await resp.text()
                if resp.status != 200:
                    raise ValueError(f"API returned status {resp.status}: {text}")

                try:
                    data = await resp.json()
                except Exception:
                    # fallback: try to parse as plain text result
                    raise ValueError("Invalid JSON from shortening service.")

                short = data.get("result_url") or data.get("short_url") or data.get("url")
                if not short:
                    raise ValueError("Shortening service did not return a shortened URL.")

                embed = discord.Embed(
                    title="🔗 Shortened URL",
                    description=f"**Input:** {normalized}\n**Shortened:** {short}",
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_footer(text=f"Requested by {requester}")
                if is_interaction:
                    if not ctx.response.is_done():
                        await ctx.response.send_message(embed=embed)
                    else:
                        await ctx.followup.send(embed=embed)
                else:
                    await ctx.send(embed=embed)

        except asyncio.TimeoutError:
            err = discord.Embed(title="❌ Timeout", description="Shortening service timed out. Try again later.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)

        except ValueError as ve:
            err = discord.Embed(title="❌ Shorten error", description=str(ve), color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)

        except Exception as exc:
            # unexpected
            err = discord.Embed(title="⚠️ Error", description="An unexpected error occurred while shortening the URL.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.add_field(name="Details", value=str(exc), inline=False)
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)


async def setup(bot: commands.Bot):
    await bot.add_cog(Shorten(bot))
