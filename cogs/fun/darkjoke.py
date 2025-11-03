import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

class DarkJoke(commands.Cog):
    """Dark joke commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="darkjoke", description="Get a random dark joke")
    async def darkjoke(self, ctx):
        """Get a random dark joke"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://v2.jokeapi.dev/joke/Dark?type=single') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('type') == 'single':
                        joke = data['joke']
                    else:
                        joke = f"{data['setup']}\n\n{data['delivery']}"
                    
                    embed = discord.Embed(
                        title="🔪 Dark Humor",
                        description=joke,
                        color=discord.Color.dark_gray()
                    )
                    embed.set_footer(text="⚠️ Dark humor - not for everyone | JokeAPI")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Failed to fetch dark joke. Try again!")

async def setup(bot):
    await bot.add_cog(DarkJoke(bot))
