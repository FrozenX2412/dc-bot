import discord
from discord.ext import commands
from discord import app_commands
import requests
from datetime import datetime
from typing import Optional

class Expand(commands.Cog):
    """Expand shortened URLs. Supports hybrid commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="expand")
    @app_commands.describe(url="The shortened URL to expand.")
    async def expand(self, ctx: commands.Context, url: str):
        """Expand a shortened URL by following redirects."""
        try:
            resp = requests.get(url, timeout=10, allow_redirects=True)
            expanded = resp.url
        except Exception as e:
            expanded = f"Error: {e}"
        embed = discord.Embed(
            title="🔎 Expanded URL",
            description=f"Input: {url}\nExpanded: {expanded}",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Load the Expand cog."""
    await bot.add_cog(Expand(bot))
