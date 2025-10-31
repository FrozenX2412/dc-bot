import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Mute(commands.Cog):
    """Mute command cog with both slash and prefix support"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="mute",
        description="Mute a member in the server",
        usage="mute <member> [duration] [reason]"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):
        """
        Timeout/mute a member in the server
        
        Parameters:
        -----------
        member: discord.Member
            The member to mute
        duration: str
            Duration in format: 1m, 1h, 1d (optional, defaults to 5 minutes)
        reason: str
            The reason for muting (optional)
        """
        # Check if the bot's highest role is higher than the target's highest role
        if member.top_role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Error",
                description="I cannot mute this member as their role is higher than or equal to mine.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Check if the author's highest role is higher than the target's highest role
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot mute this member as their role is higher than or equal to yours.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Check if trying to mute the owner
        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Error",
                description="I cannot mute the server owner!",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Check if member is already muted
        if member.is_timed_out():
            embed = discord.Embed(
                title="❌ Error",
                description=f"{member.mention} is already muted.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Parse duration (default 5 minutes)
        mute_duration = datetime.timedelta(minutes=5)
        duration_text = "5 minutes"
        
        if duration:
            try:
                # Parse duration string (e.g., "10m", "1h", "1d")
                if duration.endswith('m'):
                    minutes = int(duration[:-1])
                    mute_duration = datetime.timedelta(minutes=minutes)
                    duration_text = f"{minutes} minute{'s' if minutes != 1 else ''}"
                elif duration.endswith('h'):
                    hours = int(duration[:-1])
                    mute_duration = datetime.timedelta(hours=hours)
                    duration_text = f"{hours} hour{'s' if hours != 1 else ''}"
                elif duration.endswith('d'):
                    days = int(duration[:-1])
                    mute_duration = datetime.timedelta(days=days)
                    duration_text = f"{days} day{'s' if days != 1 else ''}"
                else:
                    # If no unit specified, treat as minutes
                    minutes = int(duration)
                    mute_duration = datetime.timedelta(minutes=minutes)
                    duration_text = f"{minutes} minute{'s' if minutes != 1 else ''}"
            except ValueError:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Invalid duration format. Use: `10m`, `1h`, or `1d`",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.utcnow()
                )
                await ctx.send(embed=embed, ephemeral=True)
                return
        
        # Discord timeout limit is 28 days
        if mute_duration > datetime.timedelta(days=28):
            embed = discord.Embed(
                title="❌ Error",
                description="Timeout duration cannot exceed 28 days.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Try to DM the member before muting
        try:
            dm_embed = discord.Embed(
                title="🔇 You have been muted",
                description=f"You have been muted in **{ctx.guild.name}**",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )
            dm_embed.add_field(name="Duration", value=duration_text, inline=False)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Muted by", value=ctx.author.mention, inline=False)
            await member.send(embed=dm_embed)
        except:
            pass  # Member has DMs disabled
        
        # Mute the member
        try:
            until_time = discord.utils.utcnow() + mute_duration
            await member.timeout(until_time, reason=f"{reason} | Muted by {ctx.author}")
            
            # Send success message
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"Successfully muted {member.mention}",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="User", value=f"{member} (ID: {member.id})", inline=False)
            embed.add_field(name="Duration", value=duration_text, inline=True)
            embed.add_field(name="Expires", value=f"<t:{int(until_time.timestamp())}:R>", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Muted by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to mute this member.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
    
    @mute.error
    async def mute_error(self, ctx, error):
        """Error handler for mute command"""
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need **Moderate Members** permission to use this command.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description="I need **Moderate Members** permission to execute this command.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title="❌ Member Not Found",
                description="I couldn't find that member. Please mention a valid member.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Mute(bot))
