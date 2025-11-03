import discord
from discord.ext import commands
from discord import app_commands
import random

class EightBall(commands.Cog):
    """8ball commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
        self.responses = [
            # Positive
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            # Neutral
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            # Negative
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
    
    @commands.hybrid_command(name="8ball", description="Ask the magic 8ball a question")
    async def eightball(self, ctx, *, question: str):
        """Ask the magic 8ball a question"""
        response = random.choice(self.responses)
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.purple()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        embed.set_footer(text="The 8-ball has spoken!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EightBall(bot))
