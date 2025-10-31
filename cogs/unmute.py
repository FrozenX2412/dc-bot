import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Unmute(commands.Cog):
    """Unmute command cog with both slash and prefix support"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="unmute",
        description="Unmute a member in the server",
        usage="unmute <member> [reason]"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """
        Remove timeout/unmute a member in the server
        
        Parameters:
        -----------
        member: discord.Member
            The member to unmute
        reason: str
            The reason for unmuting (optional)
        """
        # Check if member is actually muted
        if not member.is_timed_out():
            embed = discord.Embed(
                title="❌ Error",
                description=f"{member.mention} is not currently muted.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Try to DM the member before unmuting
        try:
            dm_embed = discord.Embed(
                title="✅ You have been unmuted",
                description=f"You have been unmuted in **{ctx.guild.name}**",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Unmuted by", value=ctx.author.mention, inline=False)
            await member.send(embed=dm_embed)
        except:
            pass  # Member has DMs disabled
        
        # Unmute the member
        try:
            await member.timeout(None, reason=f"{reason} | Unmuted by {ctx.author}")
            
            # Send success message
            embed = discord.Embed(
                title="✅ Member Unmuted",
                description=f"Successfully unmuted {member.mention}",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="User", value=f"{member} (ID: {member.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Unmuted by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to unmute this member.",
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
    
    @unmute.error
    async def unmute_error(self, ctx, error):
        """Error handler for unmute command"""
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
    await bot.add_cog(Unmute(bot))
