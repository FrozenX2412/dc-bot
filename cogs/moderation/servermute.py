"""Server mute moderation module.

Provides functionality to server mute members.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class ServerMute(commands.Cog):
    """Server mute utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="servermute", description="Server mute a member")
    @commands.has_permissions(mute_members=True)
    @commands.bot_has_permissions(mute_members=True)
    async def servermute(self, ctx, member: discord.Member, *, reason: Optional[str] = None):
        """Server mute a member in voice channel.
        
        Args:
            ctx: Command context
            member: Member to mute
            reason: Reason for muting
        """
        if not member.voice:
            await ctx.send("❌ Member is not in a voice channel")
            return
        
        if member.voice.mute:
            await ctx.send("❌ Member is already muted")
            return
        
        try:
            await member.edit(mute=True, reason=reason)
            reason_text = f" for: {reason}" if reason else ""
            await ctx.send(f"✅ Server muted {member.mention}{reason_text}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to mute that member")


async def setup(bot):
    """Load the ServerMute cog."""
    await bot.add_cog(ServerMute(bot))
