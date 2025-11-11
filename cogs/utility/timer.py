import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import re
import time
from datetime import datetime


class Timer(commands.Cog):
    """Simple countdown timer with optional progress updates."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="timer", aliases=["countdown"], description="Start a countdown timer.")
    @app_commands.describe(duration="Timer duration (e.g. 10s, 5m, 2h, 1h30m).")
    async def timer(self, ctx: commands.Context, duration: str):
        """Starts a countdown timer."""
        is_interaction = isinstance(ctx, discord.Interaction)
        user = ctx.user if is_interaction else ctx.author

        try:
            seconds = self._parse_duration(duration)
            if seconds <= 0:
                raise ValueError("Timer duration must be positive.")
            if seconds > 86400:
                raise ValueError("Timer duration cannot exceed 24 hours.")

            end_timestamp = int(time.time() + seconds)

            embed = discord.Embed(
                title="⏱️ Timer Started",
                description=f"Duration: **{self._format_duration(seconds)}**\nEnds <t:{end_timestamp}:R>",
                color=discord.Color.blurple(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Started by", value=user.mention, inline=True)
            embed.set_footer(text="I'll notify you when it finishes!")

            if is_interaction:
                await ctx.response.send_message(embed=embed)
                message = await ctx.original_response()
            else:
                message = await ctx.send(embed=embed)

            # Progress updates every 10s for long timers
            update_interval = 10
            while seconds > 0:
                await asyncio.sleep(min(update_interval, seconds))
                seconds -= update_interval
                if seconds > 0 and seconds % 60 == 0:  # every minute, update embed
                    embed.description = f"Duration: **{self._format_duration(seconds)} remaining**\nEnds <t:{end_timestamp}:R>"
                    try:
                        await message.edit(embed=embed)
                    except discord.Forbidden:
                        break

            # When timer completes
            done_embed = discord.Embed(
                title="⏰ Timer Complete!",
                description=f"Your timer ({self._format_duration(int(time.time() - (end_timestamp - seconds)))}) has finished!",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
            done_embed.set_footer(text=f"Timer for {user.display_name}")

            try:
                if is_interaction:
                    await ctx.followup.send(f"{user.mention}", embed=done_embed)
                else:
                    await ctx.send(f"{user.mention}", embed=done_embed)
            except discord.Forbidden:
                # fallback to DM
                try:
                    await user.send(embed=done_embed)
                except discord.Forbidden:
                    pass

        except ValueError as e:
            err = discord.Embed(title="Invalid Duration", description=str(e), color=discord.Color.red())
            err.add_field(name="Examples", value="10s, 5m, 1h, 2h30m", inline=False)
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
        except Exception as e:
            err = discord.Embed(title="Error", description=f"Failed to start timer: {e}", color=discord.Color.red())
            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)

    # --- Helper methods ---
    def _parse_duration(self, duration: str) -> int:
        """Parse flexible duration formats (e.g. 1h30m, 45s)."""
        duration = duration.lower().strip()
        pattern = re.findall(r"(\d+)([smhd])", duration)
        if not pattern:
            raise ValueError("Invalid format. Examples: 10s, 5m, 2h, 1h30m")
        multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        return sum(int(value) * multipliers[unit] for value, unit in pattern)

    def _format_duration(self, seconds: int) -> str:
        """Human-friendly duration string."""
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        days, hours = divmod(hours, 24)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if mins:
            parts.append(f"{mins}m")
        if secs or not parts:
            parts.append(f"{secs}s")
        return " ".join(parts)


async def setup(bot: commands.Bot):
    await bot.add_cog(Timer(bot))
