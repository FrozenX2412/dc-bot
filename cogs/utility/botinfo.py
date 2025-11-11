# cogs/info/bot_info.py
import discord
from discord.ext import commands
from discord import app_commands
import platform
import psutil
import time
from typing import Union

class BotInfo(commands.Cog):
    """Display bot information and statistics."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # record start time in seconds (monotonic-like)
        self.start_time = time.time()
        # reuse process object for memory/cpu stats
        self._proc = psutil.Process()

    @commands.hybrid_command(name="botinfo", description="Display bot information and statistics")
    async def botinfo(self, ctx: commands.Context):
        """
        Works as both a prefix command and a slash command (hybrid).
        Use /botinfo or <prefix>botinfo
        """
        # `ctx` can be a Context (prefix) or an Interaction when invoked as a slash command
        # discord.py will convert an Interaction to a Context for hybrid commands when calling here,
        # but we still support the case of a direct Interaction object manually if needed.
        await self._show_bot_info(ctx)

    async def _show_bot_info(self, ctx_or_interaction: Union[commands.Context, discord.Interaction]):
        # normalize interaction vs context
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)

        try:
            uptime_seconds = int(time.time() - self.start_time)
            uptime_str = self._format_uptime(uptime_seconds)

            # memory (MB)
            memory_usage = self._proc.memory_info().rss / (1024 ** 2)

            # cpu percent: non-blocking short interval for a more accurate snapshot
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Build embed
            embed = discord.Embed(
                title=f"{self.bot.user.name} — Bot Information",
                description="Information and runtime stats",
                color=discord.Color.blurple(),
                timestamp=discord.utils.utcnow()
            )

            # avatar (safe access)
            if getattr(self.bot.user, "display_avatar", None):
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            embed.add_field(
                name="📊 Statistics",
                value=(
                    f"**Guilds:** {len(self.bot.guilds)}\n"
                    f"**Users (cached):** {len(self.bot.users)}\n"
                    f"**Commands (registered):** {len(self.bot.commands)}"
                ),
                inline=False
            )

            embed.add_field(
                name="💻 System",
                value=(
                    f"**CPU Usage:** {cpu_percent}%\n"
                    f"**Memory:** {memory_usage:.2f} MB\n"
                    f"**Python:** {platform.python_version()}"
                ),
                inline=False
            )

            embed.add_field(
                name="🤖 Bot Info",
                value=(
                    f"**Uptime:** {uptime_str}\n"
                    f"**discord.py:** {getattr(discord, '__version__', 'unknown')}\n"
                    f"**Ping:** {round(self.bot.latency * 1000)} ms"
                ),
                inline=False
            )

            requester_name = None
            if is_interaction:
                requester_name = ctx_or_interaction.user.display_name
            else:
                requester_name = ctx_or_interaction.author.display_name

            embed.set_footer(text=f"Requested by {requester_name}")

            # Send response depending on invocation type.
            # For hybrid commands, `ctx_or_interaction` is usually a Context object.
            if is_interaction:
                # If interaction hasn't responded yet:
                if not ctx_or_interaction.response.is_done():
                    await ctx_or_interaction.response.send_message(embed=embed)
                else:
                    # fallback: followup
                    await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)

        except Exception as exc:
            # don't leak raw exception to users; ephemeral for interactions
            err_embed = discord.Embed(
                title="Error",
                description="Failed to fetch bot info.",
                color=discord.Color.red()
            )
            if is_interaction:
                try:
                    if not ctx_or_interaction.response.is_done():
                        await ctx_or_interaction.response.send_message(embed=err_embed, ephemeral=True)
                    else:
                        await ctx_or_interaction.followup.send(embed=err_embed, ephemeral=True)
                except Exception:
                    # last resort, try channel send (may fail in DMs)
                    if ctx_or_interaction.channel:
                        await ctx_or_interaction.channel.send(embed=err_embed)
            else:
                await ctx_or_interaction.send(embed=err_embed)

    def _format_uptime(self, seconds: int) -> str:
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, secs = divmod(rem, 60)

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if secs or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)

async def setup(bot: commands.Bot):
    await bot.add_cog(BotInfo(bot))
