# cogs/util/encodings.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import re
import base64
import binascii
from typing import Union

# Simple regexes
BINARY_RE = re.compile(r"^[01\s]+$")
HEX_RE = re.compile(r"^[0-9a-fA-F\s]+$")
BASE64_RE = re.compile(r"^[A-Za-z0-9+/=\s]+$")

# Output length guard
MAX_OUTPUT_CHARS = 3800

def _truncate(s: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    if len(s) > limit:
        return s[:limit] + "\n… *(truncated)*"
    return s

class Encodings(commands.Cog):
    """Convert between text, binary, hex, and base64. Hybrid command."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="encode",
        aliases=["converttext", "enc"],
        description="Encode/decode between text, binary, hex, and base64. Auto-detects when mode not provided."
    )
    @app_commands.describe(
        text="Input text or encoded string",
        mode="Force mode: encode/decode (optional). If encoding, specify target via 'to' argument.",
        to="Target encoding when encoding: binary|hex|base64 (optional, defaults to hex)"
    )
    async def encode(
        self,
        ctx: Union[commands.Context, discord.Interaction],
        text: str,
        mode: str = None,
        to: str = None
    ):
        """
        Examples:
          - /encode text:"hello" to:base64        -> encodes text to base64
          - /encode text:"aGVsbG8=" mode:decode    -> decodes base64 to text (auto-detected)
          - !encode 01001000 01100101               -> auto-detects binary -> decodes to text
        """
        is_interaction = isinstance(ctx, discord.Interaction)
        requester = getattr(ctx.user if is_interaction else ctx.author, "display_name", "Unknown")
        mode = (mode or "").lower().strip()
        to = (to or "").lower().strip()

        # Normalize input
        s = text.strip()

        # Helper send
        async def send(embed: discord.Embed, ephemeral_error=False):
            if is_interaction:
                if ephemeral_error:
                    await ctx.response.send_message(embed=embed, ephemeral=True)
                else:
                    if not ctx.response.is_done():
                        await ctx.response.send_message(embed=embed)
                    else:
                        await ctx.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

        # Auto-detect mode if not provided
        if not mode:
            # If input looks like encoded (binary/hex/base64) prefer decode
            if BINARY_RE.fullmatch(s) and len(s.replace(" ", "")) % 8 == 0:
                mode = "decode"
            elif HEX_RE.fullmatch(s) and len(s.replace(" ", "")) % 2 == 0:
                # even-length hex -> likely decode
                mode = "decode"
            elif BASE64_RE.fullmatch(s) and len(s) % 4 == 0:
                # plausible base64
                mode = "decode"
            else:
                mode = "encode"

        try:
            if mode.startswith("dec"):
                # Attempt decode: try binary -> hex -> base64 order by detection
                if BINARY_RE.fullmatch(s) and len(s.replace(" ", "")) % 8 == 0:
                    # binary -> text
                    bits = s.split()
                    try:
                        chars = [chr(int(b, 2)) for b in bits if b]
                        decoded = "".join(chars)
                    except Exception:
                        raise ValueError("Invalid binary input.")
                    embed = discord.Embed(title="💽 Binary → Text", description=_truncate(f"**Input (binary):** `{s}`\n**Decoded:** {decoded}"), color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
                    embed.set_footer(text=f"Requested by {requester}")
                    return await send(embed)

                # Hex decode?
                if HEX_RE.fullmatch(s) and len(s.replace(" ", "")) % 2 == 0:
                    raw = s.replace(" ", "")
                    try:
                        b = binascii.unhexlify(raw)
                        decoded = b.decode("utf-8", errors="replace")
                    except Exception:
                        raise ValueError("Invalid hex input.")
                    # Also provide hex -> bytes -> base64 representation
                    b64 = base64.b64encode(b).decode()
                    embed = discord.Embed(title="🔢 Hex → Text", description=_truncate(f"**Input (hex):** `{s}`\n**Decoded:** {decoded}\n**Base64:** `{b64}`"), color=discord.Color.teal(), timestamp=discord.utils.utcnow())
                    embed.set_footer(text=f"Requested by {requester}")
                    return await send(embed)

                # Base64 decode?
                if BASE64_RE.fullmatch(s):
                    try:
                        raw_b = base64.b64decode(s, validate=True)
                        decoded = raw_b.decode("utf-8", errors="replace")
                        hexed = binascii.hexlify(raw_b).decode()
                    except Exception:
                        raise ValueError("Invalid base64 input.")
                    embed = discord.Embed(title="🗜️ Base64 → Text", description=_truncate(f"**Input (base64):** `{s}`\n**Decoded:** {decoded}\n**Hex:** `{hexed}`"), color=discord.Color.green(), timestamp=discord.utils.utcnow())
                    embed.set_footer(text=f"Requested by {requester}")
                    return await send(embed)

                # If none matched reliably, inform user
                raise ValueError("Could not detect encoding to decode. Provide a valid binary/hex/base64 string or specify mode=decode and type in 'to'.")

            elif mode.startswith("enc"):
                # Encoding path: we need to know target (to)
                if not to:
                    to = "hex"  # default target

                # Text -> target
                if to in ("hex", "h"):
                    b = s.encode("utf-8")
                    hexed = binascii.hexlify(b).decode()
                    embed = discord.Embed(title="📝 Text → Hex", description=_truncate(f"**Input:** {s}\n**Hex:** `{hexed}`"), color=discord.Color.teal(), timestamp=discord.utils.utcnow())
                    embed.set_footer(text=f"Requested by {requester}")
                    return await send(embed)

                if to in ("base64", "b64"):
                    b = s.encode("utf-8")
                    b64 = base64.b64encode(b).decode()
                    embed = discord.Embed(title="📝 Text → Base64", description=_truncate(f"**Input:** {s}\n**Base64:** `{b64}`"), color=discord.Color.green(), timestamp=discord.utils.utcnow())
                    embed.set_footer(text=f"Requested by {requester}")
                    return await send(embed)

                if to in ("binary", "bin"):
                    b = s.encode("utf-8")
                    bits = " ".join(format(byte, "08b") for byte in b)
                    embed = discord.Embed(title="📝 Text → Binary", description=_truncate(f"**Input:** {s}\n**Binary:** `{bits}`"), color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
                    embed.set_footer(text=f"Requested by {requester}")
                    return await send(embed)

                raise ValueError("Unknown target encoding for encode. Use `to` = binary | hex | base64.")

            else:
                raise ValueError("Unknown mode. Use `mode=encode` or `mode=decode` (or omit to auto-detect).")

        except ValueError as ve:
            err = discord.Embed(title="❌ Conversion error", description=str(ve), color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.set_footer(text=f"Requested by {requester}")
            return await send(err, ephemeral_error=True)
        except Exception as exc:
            # Unexpected
            err = discord.Embed(title="⚠️ Internal error", description="An unexpected error occurred while converting.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.set_footer(text=f"Requested by {requester}")
            # Log internally if you have logging (not added here)
            return await send(err, ephemeral_error=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Encodings(bot))
