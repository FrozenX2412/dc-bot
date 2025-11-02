"""Move moderation module.

Provides functionality to move members between voice channels.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class Move(commands.Cog):
    """Voice channel movement utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="move", description="Move a member to a different voice channel")
    @commands.has_permissions(move_members=True)
    @commands.bot_has_permissions(move_members=True)
    async def move(self, ctx, member: discord.Member, channel: discord.VoiceChannel):
        """Move a member to a different voice channel.
        
        Args:
            ctx: Command context
            member: Member to move
            channel: Target voice channel
        """
        if not member.voice:
            await ctx.send("❌ Member is not in a voice channel")
            return
        
        try:
            await member.move_to(channel)
            await ctx.send(f"✅ Moved {member.mention} to {channel.mention}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to move that member")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to move member: {e}")


async def setup(bot):
    """Load the Move cog."""
    await bot.add_cog(Move(bot))
