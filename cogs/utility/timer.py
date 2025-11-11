# cogs/util/timer.py
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
from typing import Any, Dict, List, Optional

DATA_DIR = Path("data")
TIMERS_FILE = DATA_DIR / "timers.json"


class Timer(commands.Cog):
    """Persistent countdown timers saved to data/timers.json."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._lock = asyncio.Lock()
        self.timers: List[Dict[str, Any]] = []  # entries: {id, user_id, channel_id, label, end_ts}
        self._boot_task = asyncio.create_task(self._boot_and_start())

    def cog_unload(self):
        self.check_timers.cancel()
        try:
            asyncio.create_task(self._save_timers())
        except Exception:
            pass

    # ---------- Boot / persistence ----------
    async def _boot_and_start(self):
        await self.bot.wait_until_ready()
        await self._ensure_datafile()
        await self._load_timers()
        if not self.check_timers.is_running():
            self.check_timers.start()

    async def _ensure_datafile(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not TIMERS_FILE.exists():
            TIMERS_FILE.write_text("[]", encoding="utf-8")

    async def _load_timers(self):
        loop = asyncio.get_running_loop()

        def read_file():
            try:
                with TIMERS_FILE.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    return []
                return data
            except Exception:
                return []

        data = await loop.run_in_executor(None, read_file)

        valid: List[Dict[str, Any]] = []
        now_ts = int(datetime.now(timezone.utc).timestamp())
        for item in data:
            try:
                tid = str(item.get("id", ""))
                uid = int(item.get("user_id"))
                cid = item.get("channel_id")
                cid = int(cid) if cid is not None else None
                label = str(item.get("label", ""))[:200]
                end_ts = int(item.get("end_ts", 0))
                # ignore timers that ended long ago (> 1 day) to avoid spam on restart
                if end_ts <= now_ts - 86400:
                    continue
                if end_ts <= 0:
                    continue
                valid.append({"id": tid, "user_id": uid, "channel_id": cid, "label": label, "end_ts": end_ts})
            except Exception:
                continue

        async with self._lock:
            self.timers = valid

    async def _save_timers(self):
        loop = asyncio.get_running_loop()
        async with self._lock:
            payload = list(self.timers)

        def write_file(payload):
            tmp = TIMERS_FILE.with_suffix(".tmp")
            try:
                with tmp.open("w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                tmp.replace(TIMERS_FILE)
                return True
            except Exception:
                try:
                    if tmp.exists():
                        tmp.unlink()
                except Exception:
                    pass
                return False

        await loop.run_in_executor(None, write_file, payload)

    # ---------- Commands ----------
    @commands.hybrid_command(
        name="timer",
        description="Start a countdown timer. Examples: /timer 10s, /timer 1h30m Lunch"
    )
    @app_commands.describe(duration="Duration like 10s, 5m, 1h, 1h30m", label="Optional label shown when the timer finishes")
    async def timer(self, ctx: commands.Context, duration: str, *, label: Optional[str] = ""):
        """
        Start a persistent timer. Stores timer in data/timers.json so it survives restarts.
        """
        is_interaction = isinstance(ctx, discord.Interaction)
        user = ctx.user if is_interaction else ctx.author
        try:
            seconds = self._parse_duration(duration)
            if seconds <= 0:
                raise ValueError("Duration must be positive.")
            if seconds > 86400:  # 24 hours limit
                raise ValueError("Duration cannot exceed 24 hours.")

            end_ts = int((datetime.now(timezone.utc) + timedelta(seconds=seconds)).timestamp())
            # generate id (timestamp + random suffix)
            tid = f"{end_ts}-{user.id}-{int(time.time() * 1000) % 1000}"

            entry = {"id": tid, "user_id": user.id, "channel_id": ctx.channel.id if not is_interaction else (ctx.channel.id if ctx.channel else None), "label": label or "", "end_ts": end_ts}

            async with self._lock:
                self.timers.append(entry)
            # persist in background
            asyncio.create_task(self._save_timers())

            embed = discord.Embed(
                title="⏱️ Timer Started",
                description=f"Timer ID: `{tid}`\nDuration: **{self._format_duration(seconds)}**\nEnds <t:{end_ts}:R>",
                color=discord.Color.blurple(),
                timestamp=discord.utils.utcnow()
            )
            if label:
                embed.add_field(name="Label", value=label, inline=False)
            embed.set_footer(text=f"Timer for {user.display_name}")

            if is_interaction:
                await ctx.response.send_message(embed=embed)
            else:
                await ctx.send(embed=embed)

        except ValueError as e:
            err = discord.Embed(title="Invalid Duration", description=str(e), color=discord.Color.red())
            err.add_field(name="Examples", value="10s, 5m, 1h, 1h30m", inline=False)
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
        except Exception as exc:
            err = discord.Embed(title="Error", description=f"Failed to start timer: {exc}", color=discord.Color.red())
            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)

    @commands.hybrid_command(name="timers", description="List your active timers")
    async def list_timers(self, ctx: commands.Context):
        is_interaction = isinstance(ctx, discord.Interaction)
        user = ctx.user if is_interaction else ctx.author
        now_ts = int(datetime.now(timezone.utc).timestamp())
        async with self._lock:
            user_timers = [t for t in self.timers if t["user_id"] == user.id]
        if not user_timers:
            m = discord.Embed(title="No active timers", description="You have no timers set.", color=discord.Color.green(), timestamp=discord.utils.utcnow())
            if is_interaction:
                await ctx.response.send_message(embed=m, ephemeral=True)
            else:
                await ctx.send(embed=m)
            return

        lines = []
        for t in sorted(user_timers, key=lambda x: x["end_ts"]):
            seconds = max(0, t["end_ts"] - now_ts)
            label = t.get("label", "") or "(no label)"
            lines.append(f"`{t['id'][:12]}` — {label} — ends <t:{t['end_ts']}:R>")

        embed = discord.Embed(title="Your timers", description="\n".join(lines), color=discord.Color.teal(), timestamp=discord.utils.utcnow())
        embed.set_footer(text=f"{len(lines)} active timer(s)")
        if is_interaction:
            await ctx.response.send_message(embed=embed, ephemeral=True)
        else:
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="cancel_timer", aliases=["ct", "cancel"], description="Cancel a timer by ID (prefix use starts with the printed short id).")
    async def cancel_timer(self, ctx: commands.Context, id_prefix: str):
        is_interaction = isinstance(ctx, discord.Interaction)
        user = ctx.user if is_interaction else ctx.author
        removed = False
        async with self._lock:
            for t in list(self.timers):
                if t["user_id"] == user.id and t["id"].startswith(id_prefix):
                    self.timers.remove(t)
                    removed = True
            if removed:
                asyncio.create_task(self._save_timers())

        if removed:
            msg = discord.Embed(title="✅ Timer cancelled", description=f"Cancelled timers starting with `{id_prefix}`", color=discord.Color.green(), timestamp=discord.utils.utcnow())
            if is_interaction:
                await ctx.response.send_message(embed=msg, ephemeral=True)
            else:
                await ctx.send(embed=msg)
        else:
            msg = discord.Embed(title="❌ Not found", description="No matching timer found for that ID prefix.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            if is_interaction:
                await ctx.response.send_message(embed=msg, ephemeral=True)
            else:
                await ctx.send(embed=msg)

    # ---------- Background checker ----------
    @tasks.loop(seconds=10)
    async def check_timers(self):
        now_ts = int(datetime.now(timezone.utc).timestamp())
        to_fire: List[Dict[str, Any]] = []
        async with self._lock:
            for t in list(self.timers):
                if t.get("end_ts", 0) <= now_ts:
                    to_fire.append(t)
            if to_fire:
                # remove fired
                self.timers = [t for t in self.timers if t not in to_fire]
                asyncio.create_task(self._save_timers())

        for t in to_fire:
            try:
                user = self.bot.get_user(t["user_id"]) or await self.bot.fetch_user(t["user_id"])
                if not user:
                    continue

                channel = None
                if t.get("channel_id") is not None:
                    channel = self.bot.get_channel(t["channel_id"])

                label = t.get("label", "") or "Timer finished"
                embed = discord.Embed(title="⏰ Timer Complete!", description=label, color=discord.Color.green(), timestamp=discord.utils.utcnow())
                embed.add_field(name="Timer ID", value=t["id"], inline=False)

                sent = False
                if channel and isinstance(channel, discord.TextChannel):
                    try:
                        await channel.send(f"{user.mention}", embed=embed)
                        sent = True
                    except Exception:
                        sent = False
                if not sent:
                    try:
                        await user.send(embed=embed)
                    except Exception:
                        pass
            except Exception:
                continue

    @check_timers.before_loop
    async def before_check_timers(self):
        await self.bot.wait_until_ready()

    # ---------- Helpers ----------
    def _parse_duration(self, duration: str) -> int:
        """Parse formats like 10s, 5m, 1h30m. Returns seconds."""
        duration = duration.lower().strip()
        parts = re.findall(r"(\d+)([smhd])", duration)
        if not parts:
            raise ValueError("Invalid format. Examples: 10s, 5m, 1h, 1h30m")
        multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        total = sum(int(v) * multipliers[u] for v, u in parts)
        return total

    def _format_duration(self, seconds: int) -> str:
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
    await bot.add_cog(Timer(bot))
