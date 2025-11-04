import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import re

class Color(commands.Cog):
    """Display color information and preview embeds. Supports hybrid commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="color")
    @app_commands.describe(hex="The hex code or color name")
    async def color(self, ctx: commands.Context, hex: str):
        """Shows a color preview with its hex, RGB, and decimal values."""
        hex_code = hex.replace("#", "").strip().lower()
        if re.match(r"^[0-9a-f]{6}$", hex_code):
            rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
            decimal = int(hex_code, 16)
        else:
            embed = discord.Embed(
                title="❌ Invalid Color",
                description="Provide a hex code like #ff0000.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            title=f"🎨 Color Information",
            description=f"Hex: #{hex_code}\nRGB: {rgb}\nDecimal: {decimal}",
            color=decimal,
            timestamp=datetime.now()
        )
        embed.set_image(url=f"https://singlecolorimage.com/get/{hex_code}/600x100")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Load the Color cog."""
    await bot.add_cog(Color(bot))
