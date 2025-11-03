import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

class Pun(commands.Cog):
    """Pun commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="pun", description="Get a random pun")
    async def pun(self, ctx):
        """Get a random pun"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://v2.jokeapi.dev/joke/Pun?type=single') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('type') == 'single':
                        joke = data['joke']
                    else:
                        joke = f"{data['setup']}\n\n{data['delivery']}"
                    
                    embed = discord.Embed(
                        title="🎉 Pun Time!",
                        description=joke,
                        color=discord.Color.gold()
                    )
                    embed.set_footer(text="JokeAPI")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Failed to fetch pun. Try again!")

async def setup(bot):
    await bot.add_cog(Pun(bot))
