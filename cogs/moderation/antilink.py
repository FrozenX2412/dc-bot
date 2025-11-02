"""Anti-link moderation module.

Provides anti-link functionality to prevent unauthorized link posting.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import re


class AntiLink(commands.Cog):
    """Anti-link detection and prevention system."""

    def __init__(self, bot):
        self.bot = bot
        # Multi-guild configuration storage
        self.guild_configs = {}
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    @commands.hybrid_command(name="antilink", description="Configure anti-link settings")
    @commands.has_permissions(manage_guild=True)
    async def antilink(self, ctx, action: str, *whitelist: str):
        """Configure anti-link settings for the server.
        
        Args:
            ctx: Command context
            action: Action to perform (enable/disable/whitelist)
            whitelist: Domains to whitelist (optional)
        """
        guild_id = ctx.guild.id
        
        if action.lower() == "enable":
            self.guild_configs[guild_id] = {"enabled": True, "whitelist": list(whitelist)}
            await ctx.send(f"✅ Anti-link enabled with whitelist: {', '.join(whitelist) if whitelist else 'None'}")
        elif action.lower() == "disable":
            self.guild_configs[guild_id] = {"enabled": False}
            await ctx.send("❌ Anti-link disabled")
        else:
            await ctx.send("Invalid action. Use: enable/disable")


async def setup(bot):
    """Load the AntiLink cog."""
    await bot.add_cog(AntiLink(bot))
