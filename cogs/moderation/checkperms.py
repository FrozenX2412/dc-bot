"""Check permissions moderation module.

Provides functionality to check user and bot permissions.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class CheckPerms(commands.Cog):
    """Permission checking utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="checkperms", description="Check permissions for a user or role")
    @commands.has_permissions(administrator=True)
    async def checkperms(self, ctx, target: Optional[discord.Member] = None):
        """Check permissions for a member in the current channel.
        
        Args:
            ctx: Command context
            target: Member to check permissions for (defaults to command user)
        """
        member = target or ctx.author
        permissions = ctx.channel.permissions_for(member)
        
        embed = discord.Embed(
            title=f"Permissions for {member.display_name}",
            description="Channel permissions overview",
            color=discord.Color.blue()
        )
        
        perms_list = [f"**{perm[0]}**: {perm[1]}" for perm in permissions]
        embed.add_field(name="Permissions", value="\n".join(perms_list[:25]), inline=False)
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Load the CheckPerms cog."""
    await bot.add_cog(CheckPerms(bot))
