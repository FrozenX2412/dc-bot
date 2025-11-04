# time.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import pytz

class TimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="time")
    async def time_prefix(self, ctx, *, tz: str = "UTC"):
        now = self.get_time(tz)
        await ctx.send(now)

    @app_commands.command(name="time", description="Get the current time in a time zone.")
    async def time_slash(self, interaction: discord.Interaction, tz: str = "UTC"):
        now = self.get_time(tz)
        await interaction.response.send_message(now)

    def get_time(self, tz):
        try:
            timezone = pytz.timezone(tz)
            now = datetime.now(timezone)
            return f"Current time in {tz}: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        except Exception:
            return "Invalid timezone."

async def setup(bot):
    await bot.add_cog(TimeCog(bot))
