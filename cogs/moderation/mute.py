import discord
from discord.ext import commands
from discord import app_commands
import datetime
import re

class Mute(commands.Cog):
    """Mute/timeout management commands with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def parse_duration(self, duration_str: str) -> int:
        """Parse duration string (e.g., '10m', '2h', '1d') to seconds"""
        match = re.match(r'(\d+)([mhd]?)', duration_str.lower())
        if not match:
            return 600  # Default 10 minutes
        
        value, unit = match.groups()
        value = int(value)
        
        if unit == 'm' or unit == '':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        return 600
    
    @commands.hybrid_command(
        name="mute",
        description="Timeout a member"
    )
    @app_commands.describe(
        member="The member to timeout",
        duration="Duration (e.g., 10m, 2h, 1d)",
        reason="Reason for the timeout"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: str = "10m", *, reason: str = "No reason provided"):
        """Mute/timeout a member with creative embed styling"""
        
        # Check role hierarchy
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Mute Failed",
                description=f"You cannot mute {member.mention} as their role is higher than or equal to yours.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        if member.top_role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Mute Failed",
                description=f"I cannot mute {member.mention} as their role is higher than or equal to mine.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        # Parse duration
        duration_seconds = self.parse_duration(duration)
        if duration_seconds > 2419200:  # 28 days max
            duration_seconds = 2419200
        
        timeout_until = datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)
        
        # Try to DM the user
        try:
            dm_embed = discord.Embed(
                title="🔇 You Have Been Muted",
                description=f"You have been muted in **{ctx.guild.name}**",
                color=discord.Color.from_rgb(108, 117, 125),
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Duration", value=duration, inline=True)
            dm_embed.add_field(name="Until", value=f"<t:{int(timeout_until.timestamp())}:F>", inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            dm_embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            await member.send(embed=dm_embed)
        except:
            pass
        
        # Timeout the member
        await member.timeout(timeout_until, reason=f"{ctx.author} ({ctx.author.id}): {reason}")
        
        # Send success embed with creative styling
        embed = discord.Embed(
            title="🔇 Member Muted",
            color=discord.Color.from_rgb(108, 117, 125),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Muted User", value=f"{member.mention}\n`{member} ({member.id})`", inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=True)
        embed.add_field(name="⏰ Duration", value=f"`{duration}`", inline=True)
        embed.add_field(name="🗓️ Until", value=f"<t:{int(timeout_until.timestamp())}:F>", inline=True)
        embed.add_field(name="📋 Reason", value=f"```{reason}```", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Muted in {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mute(bot))
