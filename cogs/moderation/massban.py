"""Mass ban moderation module.

Provides functionality to ban multiple members at once.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import List


class MassBan(commands.Cog):
    """Mass ban utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="massban", description="Ban multiple members at once")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def massban(self, ctx, members: commands.Greedy[discord.Member], *, reason: str = None):
        """Ban multiple members from the server.
        
        Args:
            ctx: Command context
            members: List of members to ban
            reason: Reason for banning
        """
        if not members:
            await ctx.send("❌ Please specify at least one member to ban")
            return
        
        await ctx.defer()
        
        success_count = 0
        fail_count = 0
        
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
                success_count += 1
            except (discord.Forbidden, discord.HTTPException):
                fail_count += 1
        
        result_msg = f"✅ Banned {success_count} member(s)"
        if fail_count > 0:
            result_msg += f" | Failed to ban {fail_count} member(s)"
        
        await ctx.send(result_msg)


async def setup(bot):
    """Load the MassBan cog."""
    await bot.add_cog(MassBan(bot))
