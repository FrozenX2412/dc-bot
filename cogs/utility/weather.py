# weather.py
import discord
from discord.ext import commands
from discord import app_commands
import requests

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="weather")
    async def weather_prefix(self, ctx, *, location: str):
        data = self.get_weather(location)
        if data:
            await ctx.send(data)
        else:
            await ctx.send("Could not fetch weather info.")

    @app_commands.command(name="weather", description="Get weather info for a location.")
    async def weather_slash(self, interaction: discord.Interaction, location: str):
        data = self.get_weather(location)
        if data:
            await interaction.response.send_message(data)
        else:
            await interaction.response.send_message("Could not fetch weather info.")

    def get_weather(self, location):
        # This should use a valid API key
        response = requests.get(f"https://wttr.in/{location}?format=3")
        if response.status_code == 200:
            return response.text
        return None

async def setup(bot):
    await bot.add_cog(Weather(bot))
