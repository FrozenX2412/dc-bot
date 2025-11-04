import discord
from discord.ext import commands
from discord import app_commands
import requests
from datetime import datetime
from typing import Optional

class Shorten(commands.Cog):
    """Shorten URLs using a public API. Supports hybrid commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="shorten", aliases=["short"])
    @app_commands.describe(url="The URL to be shortened.")
    async def shorten(self, ctx: commands.Context, url: str):
        """Shorten a given URL using cleanuri.com."""
        api = "https://cleanuri.com/api/v1/shorten"
        data = {"url": url}
        try:
            resp = requests.post(api, data=data, timeout=10)
            resp.raise_for_status()
            short_url = resp.json().get("result_url", "Error")
        except Exception as e:
            short_url = f"Error: {e}"
        embed = discord.Embed(
            title="🔗 Shortened URL",
            description=f"Input: {url}\nShortened: {short_url}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Load the Shorten cog."""
    await bot.add_cog(Shorten(bot))
