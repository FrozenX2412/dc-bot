# cogs/util/remind.py
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import re
from datetime import datetime, timedelta, timezone
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_DIR = Path("data")
REMINDERS_FILE = DATA_DIR / "reminders.json"


class Remind(commands.Cog):
    """Set reminders that persist to data/reminders.json."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reminders: List[Dict[str, Any]] = []  # each: {user_id, channel_id, message, remind_at}
        self._lock = asyncio.Lock()
        # ensure data dir exists and load reminders asynchronously
        self._boot_task = asyncio.create_task(self._boot_and_start())

    def cog_unload(self):
        """Stop background loop and save reminders on unload."""
        self.check_reminders.cancel()
        # attempt to save synchronously via event loop task
        try:
            asyncio.create_task(self._save_reminders())
        except Exception:
            pass

    # --- boot sequence ---
    async def _boot_and_start(self):
        await self.bot.wait_until_ready()
        await self._ensure_datafile()
        await self._load_reminders()
        # start background loop
        if not self.check_reminders.is_running():
            self.check_reminders.start()

    async def _ensure_datafile(self):
        """Ensure data directory and file exists."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            if not REMINDERS_FILE.exists():
                # create empty list file
                REMINDERS_FILE.write_text("[]", encoding="utf-8")
        except Exception:
            # If file creation fails, just continue; load will handle errors
            pass

    async def _load_reminders(self):
        """Load reminders from JSON file (run in executor)."""
        loop = asyncio.get_running_loop()
        try:
            def read_file():
                try:
                    with REMINDERS_FILE.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                        # validate structure: list of dicts
                        if not isinstance(data, list):
                            return []
                        return data
                except Exception:
                    return []

            data = await loop.run_in_executor(None, read_file)
            # normalize to expected keys and types
            valid: List[Dict[str, Any]] = []
            now_ts = int(datetime.now(timezone.utc).timestamp())
            for item in data:
                try:
                    uid = int(item.get("user_id"))
                    cid = item.get("channel_id")
                    cid = int(cid) if cid is not None else None
                    msg = str(item.get("message", ""))
                    remind_at = int(item.get("remind_at", 0))
                    # ignore reminders in the past by a huge margin (>1 year) or malformed
                    if remind_at <= 0:
                        continue
                    # keep reminders that are reasonable
                    if remind_at < now_ts - 31536000:  # older than a year ago -> skip
                        continue
                    valid.append({"user_id": uid, "channel_id": cid, "message": msg, "remind_at": remind_at})
                except Exception:
                    continue
            async with self._lock:
                self.reminders = valid
        except Exception:
            # fallback: empty list
            async with self._lock:
                self.reminders = []

    async def _save_reminders(self):
        """Save reminders to JSON file (run in executor). Uses atomic write."""
        loop = asyncio.get_running_loop()

        async with self._lock:
            data = list(self.reminders)  # shallow copy

        def write_file(payload):
            tmp = REMINDERS_FILE.with_suffix(".tmp")
            try:
                with tmp.open("w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                # atomic replace
                tmp.replace(REMINDERS_FILE)
                return True
            except Exception:
                # cleanup tmp if exists
                try:
                    if tmp.exists():
                        tmp.unlink()
                except Exception:
                    pass
                return False

        await loop.run_in_executor(None, write_file, data)

    # --- COMMAND ---
    @commands.hybrid_command(
        name="remind",
        description="Set a reminder for yourself. Example: /remind 10m Take a break!"
    )
    @app_commands.describe(time="Time like 10s, 5m, 2h, 1d, or combinations like 1h30m", reminder="What to be reminded about")
    async def remind(self, ctx: commands.Context, time: str, *, reminder: str):
        """Sets a reminder (works as prefix or slash)."""
        is_interaction = isinstance(ctx, discord.Interaction)
        user = ctx.user if is_interaction else ctx.author

        try:
            seconds = self._parse_time(time)
            if seconds <= 0:
                raise ValueError("Time must be positive.")
            if seconds > 31_536_000:  # 1 year
                raise ValueError("Time cannot exceed 1 year.")

            remind_at_dt = datetime.now(timezone.utc) + timedelta(seconds=seconds)
            remind_at_ts = int(remind_at_dt.timestamp())

            entry = {
                "user_id": user.id,
                "channel_id": ctx.channel.id if not is_interaction else (ctx.channel.id if ctx.channel else None),
                "message": reminder,
                "remind_at": remind_at_ts,
            }

            # add and persist
            async with self._lock:
                self.reminders.append(entry)
            # save in background
            asyncio.create_task(self._save_reminders())

            embed = discord.Embed(
                title="⏰ Reminder Set",
                description=f"I'll remind you in **{self._format_duration(seconds)}**",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Reminder", value=reminder, inline=False)
            embed.add_field(name="Time", value=f"<t:{remind_at_ts}:R>", inline=False)
            embed.set_footer(text=f"Reminder for {user.display_name}")

            if is_interaction:
                await ctx.response.send_message(embed=embed)
            else:
                await ctx.send(embed=embed)

        except ValueError as e:
            err = discord.Embed(
                title="Invalid Time Format",
                description=str(e),
                color=discord.Color.red()
            )
            err.add_field(name="Valid formats", value="`10s` (seconds)\n`5m` (minutes)\n`2h` (hours)\n`1d` (days)\nOr combinations like `1h30m`", inline=False)
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
        except Exception as e:
            err = discord.Embed(title="Error", description=f"Failed to set reminder: {e}", color=discord.Color.red())
            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)

    # --- BACKGROUND TASK ---
    @tasks.loop(seconds=30)
    async def check_reminders(self):
        """Check pending reminders every 30 seconds and deliver them."""
        now_ts = int(datetime.now(timezone.utc).timestamp())
        to_send: List[Dict[str, Any]] = []

        async with self._lock:
            # collect due reminders
            for r in list(self.reminders):
                if r.get("remind_at", 0) <= now_ts:
                    to_send.append(r)

            # remove them from the main list
            if to_send:
                self.reminders = [r for r in self.reminders if r not in to_send]
                # persist removal
                asyncio.create_task(self._save_reminders())

        for r in to_send:
            try:
                user = self.bot.get_user(r["user_id"]) or await self.bot.fetch_user(r["user_id"])
                if not user:
                    continue

                channel_obj = None
                if r.get("channel_id") is not None:
                    channel_obj = self.bot.get_channel(r["channel_id"])

                embed = discord.Embed(
                    title="🔔 Reminder!",
                    description=r.get("message", ""),
                    color=discord.Color.gold(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_footer(text="Reminder")

                sent = False
                if channel_obj and isinstance(channel_obj, discord.TextChannel):
                    try:
                        await channel_obj.send(f"{user.mention}", embed=embed)
                        sent = True
                    except discord.Forbidden:
                        sent = False
                    except Exception:
                        sent = False

                if not sent:
                    try:
                        await user.send(embed=embed)
                        sent = True
                    except Exception:
                        sent = False

            except Exception:
                # per-reminder error shouldn't stop others
                continue

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

    # --- HELPERS ---
    def _parse_time(self, time_str: str) -> int:
        """Parse times like 10s, 2h30m, 1d2h, etc. Returns seconds."""
        time_str = time_str.lower().strip()
        pattern = re.findall(r"(\d+)([smhd])", time_str)
        if not pattern:
            raise ValueError("Invalid format. Example: 10m, 1h30m, 2d.")
        multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        total = sum(int(value) * multipliers[unit] for value, unit in pattern)
        return total

    def _format_duration(self, seconds: int) -> str:
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)
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
    await bot.add_cog(Remind(bot))
