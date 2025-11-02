import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Unban(commands.Cog):
    """Unban management commands with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="unban",
        description="Unban a user from the server"
    )
    @app_commands.describe(
        user_id="The ID of the user to unban",
        reason="Reason for unbanning"
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: str, *, reason: str = "No reason provided"):
        """Unban a user by their ID"""
        
        try:
            user_id = int(user_id)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid User ID",
                description="Please provide a valid numeric user ID.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        try:
            # Get ban list
            bans = [entry async for entry in ctx.guild.bans()]
            ban_entry = next((ban for ban in bans if ban.user.id == user_id), None)
            
            if not ban_entry:
                embed = discord.Embed(
                    title="❌ User Not Banned",
                    description=f"User with ID `{user_id}` is not banned from this server.",
                    color=discord.Color.orange(),
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
                return await ctx.send(embed=embed, ephemeral=True)
            
            user = ban_entry.user
            
            # Unban the user
            await ctx.guild.unban(user, reason=f"{ctx.author} ({ctx.author.id}): {reason}")
            
            # Send success embed with creative styling
            embed = discord.Embed(
                title="✅ User Unbanned",
                color=discord.Color.from_rgb(40, 167, 69),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="👤 Unbanned User", value=f"`{user} ({user.id})`", inline=True)
            embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=True)
            embed.add_field(name="📋 Reason", value=f"```{reason}```", inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Unbanned from {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="I don't have permission to unban users.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Unban(bot))
