import discord
from discord.ext import commands
import datetime
from typing import Optional, Union

class Utility(commands.Cog):
    """Utility functions and helper commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @staticmethod
    def format_datetime(dt: datetime.datetime) -> str:
        """
        Format a datetime object into a readable string
        
        Parameters:
        -----------
        dt: datetime.datetime
            The datetime to format
        
        Returns:
        --------
        str: Formatted datetime string
        """
        return dt.strftime("%B %d, %Y at %I:%M %p UTC")
    
    @staticmethod
    def create_error_embed(title: str, description: str) -> discord.Embed:
        """
        Create a standardized error embed
        
        Parameters:
        -----------
        title: str
            The title of the error
        description: str
            The description of the error
        
        Returns:
        --------
        discord.Embed: The error embed
        """
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def create_success_embed(title: str, description: str) -> discord.Embed:
        """
        Create a standardized success embed
        
        Parameters:
        -----------
        title: str
            The title of the success message
        description: str
            The description of the success
        
        Returns:
        --------
        discord.Embed: The success embed
        """
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def create_info_embed(title: str, description: str) -> discord.Embed:
        """
        Create a standardized info embed
        
        Parameters:
        -----------
        title: str
            The title of the info message
        description: str
            The description of the info
        
        Returns:
        --------
        discord.Embed: The info embed
        """
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def check_hierarchy(executor: discord.Member, target: discord.Member, guild: discord.Guild) -> tuple[bool, Optional[str]]:
        """
        Check if an executor can perform an action on a target member
        
        Parameters:
        -----------
        executor: discord.Member
            The member trying to perform the action
        target: discord.Member
            The member being targeted
        guild: discord.Guild
            The guild where the action is taking place
        
        Returns:
        --------
        tuple[bool, Optional[str]]: (Can perform action, Error message if any)
        """
        # Check if target is the guild owner
        if target == guild.owner:
            return False, "You cannot perform actions on the server owner."
        
        # Check if executor is the owner (owners can do anything)
        if executor == guild.owner:
            return True, None
        
        # Check role hierarchy
        if target.top_role >= executor.top_role:
            return False, "You cannot perform actions on this member as their role is higher than or equal to yours."
        
        return True, None
    
    @staticmethod
    def check_bot_hierarchy(bot_member: discord.Member, target: discord.Member) -> tuple[bool, Optional[str]]:
        """
        Check if the bot can perform an action on a target member
        
        Parameters:
        -----------
        bot_member: discord.Member
            The bot's member object
        target: discord.Member
            The member being targeted
        
        Returns:
        --------
        tuple[bool, Optional[str]]: (Can perform action, Error message if any)
        """
        if target.top_role >= bot_member.top_role:
            return False, "I cannot perform actions on this member as their role is higher than or equal to mine."
        
        return True, None
    
    @commands.hybrid_command(
        name="ping",
        description="Check the bot's latency"
    )
    async def ping(self, ctx):
        """
        Check the bot's latency and response time
        """
        # Calculate latency
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.add_field(
            name="Status",
            value="🟢 Excellent" if latency < 100 else "🟡 Good" if latency < 200 else "🔴 Poor",
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="userinfo",
        description="Display information about a user",
        aliases=["ui", "whois"]
    )
    async def userinfo(self, ctx, member: discord.Member = None):
        """
        Display detailed information about a user
        
        Parameters:
        -----------
        member: discord.Member
            The member to get info about (optional, defaults to command author)
        """
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"👤 User Information - {member}",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Basic info
        embed.add_field(
            name="🆔 User ID",
            value=f"`{member.id}`",
            inline=True
        )
        
        embed.add_field(
            name="📛 Nickname",
            value=member.nick if member.nick else "None",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Bot",
            value="Yes" if member.bot else "No",
            inline=True
        )
        
        # Dates
        embed.add_field(
            name="📅 Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="📆 Joined Server",
            value=f"<t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "Unknown",
            inline=True
        )
        
        # Roles
        roles = [role.mention for role in member.roles[1:]]  # Skip @everyone
        embed.add_field(
            name=f"🎭 Roles [{len(roles)}]",
            value=" ".join(roles[:10]) if roles else "No roles",
            inline=False
        )
        
        # Highest role
        embed.add_field(
            name="🎖️ Highest Role",
            value=member.top_role.mention,
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
