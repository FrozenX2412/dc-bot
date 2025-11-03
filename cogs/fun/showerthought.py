import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

class ShowerThought(commands.Cog):
    """Shower thought commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="showerthought", description="Get a random shower thought")
    async def showerthought(self, ctx):
        """Get a random shower thought from Reddit"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.reddit.com/r/Showerthoughts/random/.json',
                                 headers={'User-agent': 'bot'}) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    try:
                        post = data[0]['data']['children'][0]['data']
                        thought = post['title']
                        
                        embed = discord.Embed(
                            title="🚿 Shower Thought",
                            description=thought,
                            color=discord.Color.blue()
                        )
                        embed.set_footer(text="r/Showerthoughts")
                        
                        await ctx.send(embed=embed)
                    except (KeyError, IndexError):
                        await ctx.send("Failed to fetch shower thought. Try again!")
                else:
                    await ctx.send("Failed to fetch shower thought. Try again!")

async def setup(bot):
    await bot.add_cog(ShowerThought(bot))
