import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Kick(commands.Cog):
    """Kick command cog with both slash and prefix support"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="kick",
        description="Kick a member from the server",
        usage="kick <member> [reason]"
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """
        Kick a member from the server
        
        Parameters:
        -----------
        member: discord.Member
            The member to kick
        reason: str
            The reason for kicking (optional)
        """
        # Check if the bot's highest role is higher than the target's highest role
        if member.top_role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Error",
                description="I cannot kick this member as their role is higher than or equal to mine.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Check if the author's highest role is higher than the target's highest role
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot kick this member as their role is higher than or equal to yours.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Check if trying to kick the owner
        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Error",
                description="I cannot kick the server owner!",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Check if trying to kick self
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot kick yourself!",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Try to DM the member before kicking
        try:
            dm_embed = discord.Embed(
                title="👢 You have been kicked",
                description=f"You have been kicked from **{ctx.guild.name}**",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Kicked by", value=ctx.author.mention, inline=False)
            await member.send(embed=dm_embed)
        except:
            pass  # Member has DMs disabled
        
        # Kick the member
        try:
            await member.kick(reason=f"{reason} | Kicked by {ctx.author}")
            
            # Send success message
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"Successfully kicked {member.mention}",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="User", value=f"{member} (ID: {member.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to kick this member.",
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
    
    @kick.error
    async def kick_error(self, ctx, error):
        """Error handler for kick command"""
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need **Kick Members** permission to use this command.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description="I need **Kick Members** permission to execute this command.",
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
    await bot.add_cog(Kick(bot))
