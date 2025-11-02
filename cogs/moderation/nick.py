"""Nickname moderation module.

Provides functionality to change user nicknames.
Supports both slash commands and prefix commands with multi-guild logic.
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class Nick(commands.Cog):
    """Nickname management utilities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="nick", description="Change a member's nickname")
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nickname: Optional[str] = None):
        """Change a member's nickname in the server.
        
        Args:
            ctx: Command context
            member: Member whose nickname to change
            nickname: New nickname (None to reset)
        """
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot change the nickname of someone with a higher or equal role")
            return
        
        try:
            old_nick = member.display_name
            await member.edit(nick=nickname)
            
            if nickname:
                await ctx.send(f"✅ Changed {old_nick}'s nickname to {nickname}")
            else:
                await ctx.send(f"✅ Reset {old_nick}'s nickname")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to change that member's nickname")


async def setup(bot):
    """Load the Nick cog."""
    await bot.add_cog(Nick(bot))
