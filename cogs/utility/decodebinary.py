import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Binary(commands.Cog):
    """Convert text to binary representation. Supports hybrid commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="binary", aliases=["tobinary"])
    @app_commands.describe(text="Text to convert to binary.")
    async def binary(self, ctx: commands.Context, text: str):
        """Converts ASCII text to binary byte codes."""
        b = ' '.join(format(ord(char), '08b') for char in text)
        embed = discord.Embed(
            title="💾 Binary Output",
            description=f"Input: {text}\nBinary: {b}",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Load the Binary cog."""
    await bot.add_cog(Binary(bot))
