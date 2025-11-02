"""Set nickname moderation module.

Provides functionality to set the bot's own nickname.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class SetNick(commands.Cog):
    """Bot nickname management utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="setnick", description="Set the bot's nickname")
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(change_nickname=True)
    async def setnick(self, ctx, *, nickname: Optional[str] = None):
        """Set the bot's nickname in the server.
        
        Args:
            ctx: Command context
            nickname: New nickname for the bot (None to reset)
        """
        try:
            old_nick = ctx.guild.me.display_name
            await ctx.guild.me.edit(nick=nickname)
            
            if nickname:
                await ctx.send(f"✅ Changed my nickname to {nickname}")
            else:
                await ctx.send("✅ Reset my nickname")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to change my nickname")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to change nickname: {e}")


async def setup(bot):
    """Load the SetNick cog."""
    await bot.add_cog(SetNick(bot))
