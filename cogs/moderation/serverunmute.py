"""Server unmute moderation module.

Provides functionality to remove server mute from members.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class ServerUnmute(commands.Cog):
    """Server unmute utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverunmute", description="Remove server mute from a member")
    @commands.has_permissions(mute_members=True)
    @commands.bot_has_permissions(mute_members=True)
    async def serverunmute(self, ctx, member: discord.Member, *, reason: Optional[str] = None):
        """Remove server mute from a member in voice channel.
        
        Args:
            ctx: Command context
            member: Member to unmute
            reason: Reason for unmuting
        """
        if not member.voice:
            await ctx.send("❌ Member is not in a voice channel")
            return
        
        if not member.voice.mute:
            await ctx.send("❌ Member is not muted")
            return
        
        try:
            await member.edit(mute=False, reason=reason)
            reason_text = f" for: {reason}" if reason else ""
            await ctx.send(f"✅ Server unmuted {member.mention}{reason_text}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unmute that member")


async def setup(bot):
    """Load the ServerUnmute cog."""
    await bot.add_cog(ServerUnmute(bot))
