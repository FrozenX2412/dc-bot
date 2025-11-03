import discord
from discord.ext import commands
from discord import app_commands
import random

class Roast(commands.Cog):
    """Roast commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
        self.roasts = [
            "If I wanted to hear from you, I'd ask for it.",
            "You're like a cloud. When you disappear, it's a beautiful day.",
            "I'd agree with you, but then we'd both be wrong.",
            "You bring everyone so much joy when you leave the room.",
            "I'm not insulting you, I'm describing you.",
            "Light travels faster than sound, which is why you seemed bright until you spoke.",
            "You're proof that evolution can go in reverse.",
            "If ignorance is bliss, you must be the happiest person alive.",
            "I'd explain it to you, but I don't have any crayons with me.",
            "You're like the first slice of bread - everyone touches you, but no one wants you."
        ]
    
    @commands.hybrid_command(name="roast", description="Roast someone or yourself")
    async def roast(self, ctx, member: discord.Member = None):
        """Roast someone or yourself"""
        target = member or ctx.author
        roast_text = random.choice(self.roasts)
        
        embed = discord.Embed(
            title="🔥 Roasted!",
            description=f"{target.mention}\n\n{roast_text}",
            color=discord.Color.orange()
        )
        embed.set_footer(text="It's all in good fun!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Roast(bot))
