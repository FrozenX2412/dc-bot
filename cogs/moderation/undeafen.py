"""Undeafen moderation module.

Provides functionality to remove server deafen from members in voice channels.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class Undeafen(commands.Cog):
    """Voice undeafen utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="undeafen", description="Remove server deafen from a member")
    @commands.has_permissions(deafen_members=True)
    @commands.bot_has_permissions(deafen_members=True)
    async def undeafen(self, ctx, member: discord.Member, *, reason: Optional[str] = None):
        """Remove server deafen from a member in voice channel.
        
        Args:
            ctx: Command context
            member: Member to undeafen
            reason: Reason for undeafening
        """
        if not member.voice:
            await ctx.send("❌ Member is not in a voice channel")
            return
        
        if not member.voice.deaf:
            await ctx.send("❌ Member is not deafened")
            return
        
        try:
            await member.edit(deafen=False, reason=reason)
            reason_text = f" for: {reason}" if reason else ""
            await ctx.send(f"✅ Undeafened {member.mention}{reason_text}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to undeafen that member")


async def setup(bot):
    """Load the Undeafen cog."""
    await bot.add_cog(Undeafen(bot))
