import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Optional

class Whois(commands.Cog):
    """Show detailed user information in an embed. Supports hybrid commands for multi-guild use."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="whois", aliases=["userinfo", "ui"])
    @app_commands.describe(user="The user to look up. Defaults to yourself.")
    async def whois(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """Shows info about a user in this server."""
        user = user or ctx.author
        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        embed = discord.Embed(
            title=f"Whois: {user}",
            description=f"Info for {user.mention}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="Nickname", value=f"{user.nick or 'N/A'}", inline=True)
        embed.add_field(name="Server join", value=user.joined_at.strftime("%Y-%m-%d %H:%M"), inline=False)
        embed.add_field(name="Discord join", value=user.created_at.strftime("%Y-%m-%d %H:%M"), inline=False)
        embed.add_field(name=f"Roles ({len(roles)})", value=", ".join(roles) or "None", inline=False)
        embed.add_field(name="Bot?", value=str(user.bot), inline=True)
        embed.add_field(name="Top Role", value=user.top_role.mention, inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Load the Whois cog."""
    await bot.add_cog(Whois(bot))
