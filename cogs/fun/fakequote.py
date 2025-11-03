import discord
from discord.ext import commands
from discord import app_commands
import random

class FakeQuote(commands.Cog):
    """Fake quote commands for fun"""
    
    def __init__(self, bot):
        self.bot = bot
        self.famous_people = [
            "Albert Einstein", "Abraham Lincoln", "Mark Twain",
            "Winston Churchill", "Gandhi", "Socrates",
            "Confucius", "Benjamin Franklin", "Oscar Wilde",
            "Maya Angelou", "Shakespeare", "Steve Jobs"
        ]
        self.quote_templates = [
            "The only way to {} is to {}.",
            "Life is what happens when you're busy {}.",
            "In the end, we only regret the {} we didn't {}.",
            "The greatest glory in living lies not in never {}, but in {} every time we {}.",
            "Don't watch the clock; do what it does. Keep {}.",
            "The future belongs to those who {} in the beauty of their {}.",
            "It is during our darkest moments that we must {} to see the light.",
            "The way to get started is to quit {} and start {}."
        ]
        self.words = [
            "trying", "learning", "growing", "believing", "succeeding",
            "dreaming", "achieving", "thinking", "creating", "living",
            "loving", "hoping", "working", "failing", "rising"
        ]
    
    @commands.hybrid_command(name="fakequote", description="Generate a fake inspirational quote")
    async def fakequote(self, ctx):
        """Generate a fake inspirational quote"""
        person = random.choice(self.famous_people)
        template = random.choice(self.quote_templates)
        
        # Count how many {} placeholders we need
        num_words = template.count('{}')
        words_needed = random.sample(self.words, num_words)
        
        try:
            quote = template.format(*words_needed)
        except:
            quote = "The greatest adventure is what lies ahead."
        
        embed = discord.Embed(
            title="💬 Fake Quote",
            description=f'\"*{quote}*\"\n\n— {person}',
            color=discord.Color.purple()
        )
        embed.set_footer(text="Disclaimer: This quote is completely made up!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FakeQuote(bot))
