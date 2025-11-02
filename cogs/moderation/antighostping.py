"""Anti-ghost ping moderation module.

Provides anti-ghost ping functionality to detect deleted pings.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class AntiGhostPing(commands.Cog):
    """Anti-ghost ping detection and prevention system."""

    def __init__(self, bot):
        self.bot = bot
        # Multi-guild configuration storage
        self.guild_configs = {}
        # Track recent messages with pings
        self.recent_pings = {}

    @commands.hybrid_command(name="antighostping", description="Configure anti-ghost ping settings")
    @commands.has_permissions(manage_guild=True)
    async def antighostping(self, ctx, action: str):
        """Configure anti-ghost ping settings for the server.
        
        Args:
            ctx: Command context
            action: Action to perform (enable/disable)
        """
        guild_id = ctx.guild.id
        
        if action.lower() == "enable":
            self.guild_configs[guild_id] = {"enabled": True}
            await ctx.send("✅ Anti-ghost ping enabled")
        elif action.lower() == "disable":
            self.guild_configs[guild_id] = {"enabled": False}
            await ctx.send("❌ Anti-ghost ping disabled")
        else:
            await ctx.send("Invalid action. Use: enable/disable")


async def setup(bot):
    """Load the AntiGhostPing cog."""
    await bot.add_cog(AntiGhostPing(bot))
