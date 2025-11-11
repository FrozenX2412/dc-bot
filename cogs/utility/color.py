# cogs/util/color.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Union
import re

# small map of common color names to hex (6-digit)
COLOR_NAMES = {
    "red": "ff0000", "green": "00ff00", "blue": "0000ff",
    "white": "ffffff", "black": "000000", "yellow": "ffff00",
    "orange": "ffa500", "purple": "800080", "pink": "ffc0cb",
    "teal": "008080", "navy": "000080", "lime": "00ff00",
}

HEX_RE = re.compile(r"^[0-9a-fA-F]+$")

def expand_shorthand(hex_raw: str) -> str:
    """
    Expand 3-digit -> 6-digit, 4-digit -> 8-digit (repeat each nibble).
    If already 6 or 8 digits, returns as-is.
    Only accepts lengths: 3,4,6,8.
    """
    l = len(hex_raw)
    if l == 3:
        return "".join(ch * 2 for ch in hex_raw)
    if l == 4:
        return "".join(ch * 2 for ch in hex_raw)  # becomes 8 (RGBA)
    if l in (6, 8):
        return hex_raw
    raise ValueError("Unsupported hex length")

class Color(commands.Cog):
    """Display color information and preview embeds. Supports hybrid commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="color", description="Show color info and a preview")
    @app_commands.describe(code="Hex like #ff0000, shorthand #f80, 4/8-digit with alpha, or a common name")
    async def color(self, ctx: Union[commands.Context, discord.Interaction], code: str):
        is_interaction = isinstance(ctx, discord.Interaction)
        requester = getattr(ctx.user if is_interaction else ctx.author, "display_name", "Unknown")
        # normalize input
        raw = code.strip().lower()
        # accept named colors first
        if raw in COLOR_NAMES:
            hex6 = COLOR_NAMES[raw]
            hex8 = None
        else:
            # strip prefixes if present
            if raw.startswith("#"):
                raw = raw[1:]
            if raw.startswith("0x"):
                raw = raw[2:]

            if not HEX_RE.fullmatch(raw):
                err = discord.Embed(
                    title="❌ Invalid color",
                    description="Hex must contain only 0-9 and a-f characters, or use a color name.",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                err.set_footer(text=f"Requested by {requester}")
                if is_interaction:
                    await ctx.response.send_message(embed=err, ephemeral=True)
                else:
                    await ctx.send(embed=err)
                return

            # only allow 3,4,6,8 lengths (reject 5 etc.)
            if len(raw) not in (3, 4, 6, 8):
                err = discord.Embed(
                    title="❌ Invalid hex length",
                    description="Supported lengths: 3 (RGB), 4 (RGBA), 6 (RRGGBB), 8 (RRGGBBAA). Example: `#ff0000`, `#f80`, `#f80c`.",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                err.set_footer(text=f"Requested by {requester}")
                if is_interaction:
                    await ctx.response.send_message(embed=err, ephemeral=True)
                else:
                    await ctx.send(embed=err)
                return

            try:
                expanded = expand_shorthand(raw)  # now 6 or 8 digits
            except ValueError:
                err = discord.Embed(
                    title="❌ Unsupported hex",
                    description="Only 3, 4, 6 or 8 digit hex formats are supported.",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                err.set_footer(text=f"Requested by {requester}")
                if is_interaction:
                    await ctx.response.send_message(embed=err, ephemeral=True)
                else:
                    await ctx.send(embed=err)
                return

            # If we have 8-digit (RGBA), store both forms
            if len(expanded) == 8:
                hex8 = expanded
                hex6 = expanded[:6]  # use RGB portion for display/preview
            else:
                hex8 = None
                hex6 = expanded

        # now hex6 is the 6-digit RGB hex string, hex8 optionally contains alpha
        try:
            decimal = int(hex6, 16)
            rgb = tuple(int(hex6[i:i+2], 16) for i in (0, 2, 4))
        except Exception:
            err = discord.Embed(
                title="❌ Parsing error",
                description="Couldn't parse the color hex. Ensure it's valid hex digits.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
            return

        # Build embed
        embed = discord.Embed(
            title="🎨 Color Information",
            description=(
                f"**Hex:** `#{hex6}`\n"
                f"**RGB:** `{rgb}`\n"
                f"**Decimal:** `{decimal}`"
                + (f"\n**Alpha (hex):** `#{hex8[6:8]}`" if hex8 else "")
            ),
            color=discord.Color(decimal),
            timestamp=discord.utils.utcnow()
        )

        # preview image uses RGB hex (no alpha)
        embed.set_image(url=f"https://singlecolorimage.com/get/{hex6}/600x100")
        icon = getattr(ctx.user if is_interaction else ctx.author, "display_avatar", None)
        icon_url = icon.url if icon else None
        embed.set_footer(text=f"Requested by {requester}", icon_url=icon_url)

        if is_interaction:
            if not ctx.response.is_done():
                await ctx.response.send_message(embed=embed)
            else:
                await ctx.followup.send(embed=embed)
        else:
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Color(bot))
