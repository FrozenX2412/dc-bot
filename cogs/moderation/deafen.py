"""Deafen moderation module.

Provides functionality to server deafen members in voice channels.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class Deafen(commands.Cog):
    """Voice deafen utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="deafen", description="Server deafen a member")
    @commands.has_permissions(deafen_members=True)
    @commands.bot_has_permissions(deafen_members=True)
    async def deafen(self, ctx, member: discord.Member, *, reason: Optional[str] = None):
        """Server deafen a member in voice channel.
        
        Args:
            ctx: Command context
            member: Member to deafen
            reason: Reason for deafening
        """
        if not member.voice:
            await ctx.send("❌ Member is not in a voice channel")
            return
        
        if member.voice.deaf:
            await ctx.send("❌ Member is already deafened")
            return
        
        try:
            await member.edit(deafen=True, reason=reason)
            reason_text = f" for: {reason}" if reason else ""
            await ctx.send(f"✅ Deafened {member.mention}{reason_text}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to deafen that member")


async def setup(bot):
    """Load the Deafen cog."""
    await bot.add_cog(Deafen(bot))
