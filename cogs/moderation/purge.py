"""Purge moderation module.

Provides message purging/bulk deletion functionality.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class Purge(commands.Cog):
    """Message purging utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="purge", description="Bulk delete messages")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int, member: Optional[discord.Member] = None):
        """Purge messages from the current channel.
        
        Args:
            ctx: Command context
            amount: Number of messages to delete
            member: Optional member to filter messages from
        """
        if amount < 1 or amount > 1000:
            await ctx.send("❌ Amount must be between 1 and 1000")
            return
        
        def check(message):
            if member:
                return message.author == member
            return True
        
        await ctx.defer(ephemeral=True)
        deleted = await ctx.channel.purge(limit=amount, check=check)
        
        await ctx.send(f"✅ Successfully deleted {len(deleted)} messages", ephemeral=True, delete_after=5)


async def setup(bot):
    """Load the Purge cog."""
    await bot.add_cog(Purge(bot))
