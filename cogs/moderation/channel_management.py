import discord
from discord.ext import commands
from discord import app_commands
import datetime

class ChannelManagement(commands.Cog):
    """Channel management commands (slowmode, lock, unlock) with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="slowmode",
        description="Set slowmode delay for a channel"
    )
    @app_commands.describe(
        seconds="Slowmode delay in seconds (0 to disable)"
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """Set channel slowmode with creative embed styling"""
        
        if seconds < 0 or seconds > 21600:  # Discord max is 6 hours
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Slowmode must be between 0 and 21600 seconds (6 hours).",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        await ctx.channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            embed = discord.Embed(
                title="✅ Slowmode Disabled",
                description=f"Slowmode has been disabled in {ctx.channel.mention}",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
        else:
            embed = discord.Embed(
                title="⏱️ Slowmode Enabled",
                color=discord.Color.from_rgb(23, 162, 184),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="📍 Channel", value=ctx.channel.mention, inline=True)
            embed.add_field(name="⏰ Delay", value=f"`{seconds}` seconds", inline=True)
            embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=False)
        
        embed.set_footer(text=f"Channel management in {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="lock",
        description="Lock a channel to prevent members from sending messages"
    )
    @app_commands.describe(
        channel="The channel to lock (current channel if not specified)"
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """Lock a channel with creative embed styling"""
        
        channel = channel or ctx.channel
        
        # Lock the channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"{channel.mention} has been locked.",
            color=discord.Color.from_rgb(220, 53, 69),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="📍 Channel", value=channel.mention, inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=True)
        embed.set_footer(text=f"Channel locked in {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="unlock",
        description="Unlock a channel to allow members to send messages"
    )
    @app_commands.describe(
        channel="The channel to unlock (current channel if not specified)"
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """Unlock a channel with creative embed styling"""
        
        channel = channel or ctx.channel
        
        # Unlock the channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=None)
        
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"{channel.mention} has been unlocked.",
            color=discord.Color.from_rgb(40, 167, 69),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="📍 Channel", value=channel.mention, inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=True)
        embed.set_footer(text=f"Channel unlocked in {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ChannelManagement(bot))
