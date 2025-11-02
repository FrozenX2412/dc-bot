import discord
from discord.ext import commands
import datetime
from typing import Optional

class Utility(commands.Cog):
    """Utility functions and helper commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @staticmethod
    def format_datetime(dt: datetime.datetime) -> str:
        """Format a datetime object into a readable string"""
        return dt.strftime("%B %d, %Y at %I:%M %p UTC")
    
    @staticmethod
    def create_error_embed(title: str, description: str) -> discord.Embed:
        """Create a standardized error embed"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def create_success_embed(title: str, description: str) -> discord.Embed:
        """Create a standardized success embed"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def create_info_embed(title: str, description: str) -> discord.Embed:
        """Create a standardized info embed"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def check_hierarchy(executor: discord.Member, target: discord.Member, guild: discord.Guild) -> tuple[bool, Optional[str]]:
        """Check if an executor can perform an action on a target member"""
        if target == guild.owner:
            return False, "You cannot perform actions on the server owner."
        if executor == guild.owner:
            return True, None
        if target.top_role >= executor.top_role:
            return False, "You cannot perform actions on this member as their role is higher than or equal to yours."
        return True, None
    
    @staticmethod
    def check_bot_hierarchy(bot_member: discord.Member, target: discord.Member) -> tuple[bool, Optional[str]]:
        """Check if the bot can perform an action on a target member"""
        if target.top_role >= bot_member.top_role:
            return False, "I cannot perform actions on this member as their role is higher than or equal to mine."
        return True, None
    
    @commands.hybrid_command(
        name="ping",
        description="Check the bot's latency"
    )
    async def ping(self, ctx: commands.Context):
        """Check the bot's latency"""
        latency = round(self.bot.latency * 1000)
        embed = self.create_info_embed("Pong!", f"🏓 Latency: **{latency}ms**")
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
