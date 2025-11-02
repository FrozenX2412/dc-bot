"""Anti-spam moderation module.

Provides anti-spam functionality with configurable thresholds and actions.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class AntiSpam(commands.Cog):
    """Anti-spam detection and prevention system."""

    def __init__(self, bot):
        self.bot = bot
        # Multi-guild configuration storage
        self.guild_configs = {}

    @commands.hybrid_command(name="antispam", description="Configure anti-spam settings")
    @commands.has_permissions(manage_guild=True)
    async def antispam(self, ctx, action: str, threshold: Optional[int] = 5):
        """Configure anti-spam settings for the server.
        
        Args:
            ctx: Command context
            action: Action to perform (enable/disable/configure)
            threshold: Message threshold for spam detection
        """
        guild_id = ctx.guild.id
        
        if action.lower() == "enable":
            self.guild_configs[guild_id] = {"enabled": True, "threshold": threshold}
            await ctx.send(f"✅ Anti-spam enabled with threshold: {threshold}")
        elif action.lower() == "disable":
            self.guild_configs[guild_id] = {"enabled": False}
            await ctx.send("❌ Anti-spam disabled")
        else:
            await ctx.send("Invalid action. Use: enable/disable")


async def setup(bot):
    """Load the AntiSpam cog."""
    await bot.add_cog(AntiSpam(bot))
