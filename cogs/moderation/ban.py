import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Ban(commands.Cog):
    """Ban management commands with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="ban",
        description="Ban a member from the server"
    )
    @app_commands.describe(
        member="The member to ban",
        reason="Reason for the ban"
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Ban a member with creative embed styling"""
        
        # Check role hierarchy
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Ban Failed",
                description=f"You cannot ban {member.mention} as their role is higher than or equal to yours.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        if member.top_role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Ban Failed",
                description=f"I cannot ban {member.mention} as their role is higher than or equal to mine.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        # Try to DM the user
        try:
            dm_embed = discord.Embed(
                title="🔨 You Have Been Banned",
                description=f"You have been banned from **{ctx.guild.name}**",
                color=discord.Color.dark_red(),
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            dm_embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            await member.send(embed=dm_embed)
        except:
            pass
        
        # Ban the member
        await ctx.guild.ban(member, reason=f"{ctx.author} ({ctx.author.id}): {reason}")
        
        # Send success embed with creative styling
        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.from_rgb(220, 53, 69),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Banned User", value=f"{member.mention}\n`{member} ({member.id})`", inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=True)
        embed.add_field(name="📋 Reason", value=f"```{reason}```", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Banned from {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ban(bot))
