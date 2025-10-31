import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Unmute(commands.Cog):
    """Unmute/remove timeout commands with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="unmute",
        description="Remove timeout from a member"
    )
    @app_commands.describe(
        member="The member to unmute",
        reason="Reason for unmuting"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Remove timeout from a member with creative embed styling"""
        
        if not member.is_timed_out():
            embed = discord.Embed(
                title="❌ Not Muted",
                description=f"{member.mention} is not currently muted.",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        # Try to DM the user
        try:
            dm_embed = discord.Embed(
                title="✅ You Have Been Unmuted",
                description=f"You have been unmuted in **{ctx.guild.name}**",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            dm_embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            await member.send(embed=dm_embed)
        except:
            pass
        
        # Remove timeout
        await member.timeout(None, reason=f"{ctx.author} ({ctx.author.id}): {reason}")
        
        # Send success embed with creative styling
        embed = discord.Embed(
            title="✅ Member Unmuted",
            color=discord.Color.from_rgb(40, 167, 69),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Unmuted User", value=f"{member.mention}\n`{member} ({member.id})`", inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=True)
        embed.add_field(name="📋 Reason", value=f"```{reason}```", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Unmuted in {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Unmute(bot))
