"""Mass kick moderation module.

Provides functionality to kick multiple members at once.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import List


class MassKick(commands.Cog):
    """Mass kick utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="masskick", description="Kick multiple members at once")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def masskick(self, ctx, members: commands.Greedy[discord.Member], *, reason: str = None):
        """Kick multiple members from the server.
        
        Args:
            ctx: Command context
            members: List of members to kick
            reason: Reason for kicking
        """
        if not members:
            await ctx.send("❌ Please specify at least one member to kick")
            return
        
        await ctx.defer()
        
        success_count = 0
        fail_count = 0
        
        for member in members:
            try:
                await ctx.guild.kick(member, reason=reason)
                success_count += 1
            except (discord.Forbidden, discord.HTTPException):
                fail_count += 1
        
        result_msg = f"✅ Kicked {success_count} member(s)"
        if fail_count > 0:
            result_msg += f" | Failed to kick {fail_count} member(s)"
        
        await ctx.send(result_msg)


async def setup(bot):
    """Load the MassKick cog."""
    await bot.add_cog(MassKick(bot))
