import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Unban(commands.Cog):
    """Unban command cog with both slash and prefix support"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="unban",
        description="Unban a user from the server",
        usage="unban <user_id> [reason]"
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: str, *, reason: str = "No reason provided"):
        """
        Unban a user from the server using their user ID
        
        Parameters:
        -----------
        user_id: str
            The ID of the user to unban
        reason: str
            The reason for unbanning (optional)
        """
        # Check if the user_id is valid
        try:
            user_id = int(user_id)
        except ValueError:
            embed = discord.Embed(
                title="❌ Error",
                description="Invalid user ID. Please provide a valid numeric user ID.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Get the list of banned users
        try:
            banned_users = [entry async for entry in ctx.guild.bans()]
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to view the ban list.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Find the user in the ban list
        user_to_unban = None
        for ban_entry in banned_users:
            if ban_entry.user.id == user_id:
                user_to_unban = ban_entry.user
                break
        
        if user_to_unban is None:
            embed = discord.Embed(
                title="❌ Error",
                description=f"User with ID `{user_id}` is not banned from this server.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Unban the user
        try:
            await ctx.guild.unban(user_to_unban, reason=f"{reason} | Unbanned by {ctx.author}")
            
            # Send success message
            embed = discord.Embed(
                title="✅ Member Unbanned",
                description=f"Successfully unbanned **{user_to_unban}**",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="User", value=f"{user_to_unban} (ID: {user_to_unban.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            embed.set_thumbnail(url=user_to_unban.display_avatar.url)
            embed.set_footer(text=f"Unbanned by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to unban this user.",
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
    
    @unban.error
    async def unban_error(self, ctx, error):
        """Error handler for unban command"""
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need **Ban Members** permission to use this command.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description="I need **Ban Members** permission to execute this command.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Unban(bot))
