import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

class DadJoke(commands.Cog):
    """Dad joke commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="dadjoke", description="Get a random dad joke")
    async def dadjoke(self, ctx):
        """Get a random dad joke"""
        async with aiohttp.ClientSession() as session:
            headers = {'Accept': 'application/json'}
            async with session.get('https://icanhazdadjoke.com/', headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    embed = discord.Embed(
                        title="👨 Dad Joke",
                        description=data['joke'],
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text="icanhazdadjoke.com")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Failed to fetch dad joke. Try again!")

async def setup(bot):
    await bot.add_cog(DadJoke(bot))
