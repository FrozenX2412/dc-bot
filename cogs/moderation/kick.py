import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Kick(commands.Cog):
    """Kick management commands with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="kick",
        description="Kick a member from the server"
    )
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for the kick"
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Kick a member with creative embed styling"""
        
        # Check role hierarchy
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Kick Failed",
                description=f"You cannot kick {member.mention} as their role is higher than or equal to yours.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        if member.top_role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Kick Failed",
                description=f"I cannot kick {member.mention} as their role is higher than or equal to mine.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        # Try to DM the user
        try:
            dm_embed = discord.Embed(
                title="👢 You Have Been Kicked",
                description=f"You have been kicked from **{ctx.guild.name}**",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            dm_embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            await member.send(embed=dm_embed)
        except:
            pass
        
        # Kick the member
        await ctx.guild.kick(member, reason=f"{ctx.author} ({ctx.author.id}): {reason}")
        
        # Send success embed with creative styling
        embed = discord.Embed(
            title="👢 Member Kicked",
            color=discord.Color.from_rgb(255, 193, 7),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Kicked User", value=f"{member.mention}\n`{member} ({member.id})`", inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=True)
        embed.add_field(name="📋 Reason", value=f"```{reason}```", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Kicked from {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Kick(bot))
