import discord
from discord.ext import commands
from discord import app_commands
import random

class Pickup(commands.Cog):
    """Pickup line commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
        self.pickup_lines = [
            "Are you a magician? Because whenever I look at you, everyone else disappears.",
            "Do you have a map? I keep getting lost in your eyes.",
            "Is your name Google? Because you have everything I've been searching for.",
            "Are you a time traveler? Because I see you in my future.",
            "Do you have a Band-Aid? I just scraped my knee falling for you.",
            "Are you made of copper and tellurium? Because you're Cu-Te!",
            "If you were a vegetable, you'd be a cute-cumber.",
            "Are you a parking ticket? Because you've got FINE written all over you.",
            "Is your name Wi-Fi? Because I'm feeling a connection.",
            "Do you believe in love at first sight, or should I walk by again?"
        ]
    
    @commands.hybrid_command(name="pickup", description="Get a random pickup line")
    async def pickup(self, ctx, member: discord.Member = None):
        """Get a random pickup line"""
        target = member or ctx.author
        pickup_line = random.choice(self.pickup_lines)
        
        embed = discord.Embed(
            title="💘 Pickup Line",
            description=f"{target.mention}\n\n{pickup_line}",
            color=discord.Color.magenta()
        )
        embed.set_footer(text="Smooth operator!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Pickup(bot))
