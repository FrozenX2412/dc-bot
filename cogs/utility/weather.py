# cogs/util/weather.py
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from datetime import datetime
from typing import Union


class Weather(commands.Cog):
    """Fetch weather info for any location using wttr.in."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._session: aiohttp.ClientSession | None = None

    async def cog_load(self):
        """Create aiohttp session on load."""
        self._session = aiohttp.ClientSession()

    async def cog_unload(self):
        """Close aiohttp session on unload."""
        if self._session and not self._session.closed:
            await self._session.close()

    @commands.hybrid_command(name="weather", description="Get current weather for a location.")
    @app_commands.describe(location="City or place to check (e.g. London, Tokyo, New York)")
    async def weather(self, ctx: Union[commands.Context, discord.Interaction], *, location: str):
        """Fetch and display weather info."""
        is_interaction = isinstance(ctx, discord.Interaction)
        requester = getattr(ctx.user if is_interaction else ctx.author, "display_name", "User")

        # Make sure session exists
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

        # Basic wttr.in text API (no key needed)
        url = f"https://wttr.in/{location}?format=j1"

        try:
            async with self._session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    raise ValueError(f"API returned {resp.status}")
                data = await resp.json()

            # Parse data
            current = data["current_condition"][0]
            weather_desc = current["weatherDesc"][0]["value"]
            temp_c = current["temp_C"]
            feels_like = current["FeelsLikeC"]
            humidity = current["humidity"]
            wind = current["windspeedKmph"]
            icon_url = current["weatherIconUrl"][0]["value"]

            # Format embed
            embed = discord.Embed(
                title=f"🌤️ Weather in {location.title()}",
                description=weather_desc,
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="🌡️ Temperature", value=f"{temp_c}°C (Feels like {feels_like}°C)", inline=True)
            embed.add_field(name="💨 Wind", value=f"{wind} km/h", inline=True)
            embed.add_field(name="💧 Humidity", value=f"{humidity}%", inline=True)
            embed.set_thumbnail(url=icon_url)
            embed.set_footer(text=f"Requested by {requester}")

            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=embed)
                else:
                    await ctx.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

        except asyncio.TimeoutError:
            err = discord.Embed(
                title="⏱️ Timeout",
                description="The weather service took too long to respond. Please try again later.",
                color=discord.Color.red(),
            )
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)

        except Exception as e:
            err = discord.Embed(
                title="❌ Error fetching weather",
                description=f"Could not fetch weather info for `{location}`.\n\n**Details:** {str(e)}",
                color=discord.Color.red(),
            )
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)


async def setup(bot: commands.Bot):
    await bot.add_cog(Weather(bot))
