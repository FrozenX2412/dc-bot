import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

class Meme(commands.Cog):
    """Meme commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="meme", description="Get a random meme")
    async def meme(self, ctx):
        """Get a random meme from Reddit"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    embed = discord.Embed(
                        title=data['title'],
                        color=discord.Color.random()
                    )
                    embed.set_image(url=data['url'])
                    embed.set_footer(text=f"👍 {data['ups']} | r/{data['subreddit']}")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Failed to fetch meme. Try again!")

async def setup(bot):
    await bot.add_cog(Meme(bot))
