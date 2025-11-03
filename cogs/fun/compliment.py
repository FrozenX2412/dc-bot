import discord
from discord.ext import commands
from discord import app_commands
import random

class Compliment(commands.Cog):
    """Compliment commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
        self.compliments = [
            "You're an awesome friend!",
            "You light up the room!",
            "You have the best laugh!",
            "You're a great listener.",
            "Your smile is contagious!",
            "You bring out the best in other people.",
            "You're a smart cookie!",
            "Your perspective is refreshing.",
            "You're an inspiration!",
            "You're more helpful than you realize!",
            "You have impeccable manners.",
            "Your kindness is a balm to all who encounter it.",
            "You're all that and a super-size bag of chips!",
            "You're even better than a unicorn, because you're real!"
        ]
    
    @commands.hybrid_command(name="compliment", description="Compliment someone or yourself")
    async def compliment(self, ctx, member: discord.Member = None):
        """Compliment someone or yourself"""
        target = member or ctx.author
        compliment_text = random.choice(self.compliments)
        
        embed = discord.Embed(
            title="💖 Compliment",
            description=f"{target.mention}\n\n{compliment_text}",
            color=discord.Color.pink()
        )
        embed.set_footer(text="You're awesome!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Compliment(bot))
