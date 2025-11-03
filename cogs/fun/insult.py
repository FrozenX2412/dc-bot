import discord
from discord.ext import commands
from discord import app_commands
import random

class Insult(commands.Cog):
    """Insult commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
        self.insults = [
            "You're not stupid; you just have bad luck thinking.",
            "Somewhere out there is a tree working very hard to produce oxygen so you can breathe. Go apologize to it.",
            "I'd like to see things from your point of view, but I can't seem to get my head that far up my...",
            "You're the reason the gene pool needs a lifeguard.",
            "I'm not saying you're dumb, but you have more loose ends than a ripped carpet.",
            "If I had a dollar for every brain you don't have, I'd have one dollar.",
            "You're like a software update. Whenever I see you, I think 'not now'.",
            "You're not completely useless. You can always serve as a bad example.",
            "I would ask you how old you are, but I know you can't count that high.",
            "You're so fake, even China denied they made you."
        ]
    
    @commands.hybrid_command(name="insult", description="Insult someone or yourself")
    async def insult(self, ctx, member: discord.Member = None):
        """Insult someone or yourself"""
        target = member or ctx.author
        insult_text = random.choice(self.insults)
        
        embed = discord.Embed(
            title="🗡️ Insulted!",
            description=f"{target.mention}\n\n{insult_text}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Just kidding! It's all in fun!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Insult(bot))
