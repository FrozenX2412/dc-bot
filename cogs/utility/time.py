# cogs/util/time.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone as dt_timezone
from typing import Optional, List

# Prefer zoneinfo if available, fall back to pytz
try:
    from zoneinfo import ZoneInfo, available_timezones  # Python 3.9+
    ZONEINFO_AVAILABLE = True
except Exception:
    ZONEINFO_AVAILABLE = False
    try:
        import pytz
    except Exception:
        pytz = None

# small alias map for common short names
ALIASES = {
    "utc": "UTC",
    "est": "America/New_York",
    "edt": "America/New_York",
    "cst": "America/Chicago",
    "cdt": "America/Chicago",
    "mst": "America/Denver",
    "mdt": "America/Denver",
    "pst": "America/Los_Angeles",
    "pdt": "America/Los_Angeles",
    "gmt": "Etc/GMT",
    "cet": "Europe/Paris",
    "bst": "Europe/London",
}

def _all_timezones_list() -> List[str]:
    if ZONEINFO_AVAILABLE:
        try:
            return sorted(t for t in available_timezones())
        except Exception:
            pass
    if pytz is not None:
        return list(pytz.all_timezones)
    # fallback small list
    return ["UTC", "America/New_York", "Europe/London", "Europe/Paris", "Asia/Kolkata", "Asia/Tokyo"]

async def _tz_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    """Autocomplete provider for slash command - filters timezones by substring."""
    cur = (current or "").lower()
    choices = []
    for tz in _all_timezones_list():
        if not cur or cur in tz.lower():
            choices.append(app_commands.Choice(name=tz, value=tz))
            if len(choices) >= 25:
                break
    return choices

class TimeCog(commands.Cog):
    """Time utilities: show current time in a timezone (hybrid command)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="time", description="Get current time in a timezone. Example: /time tz:Asia/Kolkata")
    @app_commands.describe(tz="IANA timezone name (autocomplete available), or a common short name like PST/EST. Default: UTC")
    @app_commands.autocomplete(tz=_tz_autocomplete)
    async def time(self, ctx: commands.Context, tz: Optional[str] = "UTC"):
        """
        Works as both prefix and slash command.
        Examples:
          - /time tz:Asia/Kolkata
          - !time UTC
          - !time PST
        """
        is_interaction = isinstance(ctx, discord.Interaction)
        requester = getattr(ctx.user if is_interaction else ctx.author, "display_name", "Unknown")

        tz_input = (tz or "UTC").strip()
        # resolve aliases
        key = tz_input.lower()
        if key in ALIASES:
            tz_input = ALIASES[key]

        try:
            # Try zoneinfo first
            if ZONEINFO_AVAILABLE:
                tz_obj = ZoneInfo(tz_input)
                now = datetime.now(tz_obj)
                offset = now.utcoffset() or dt_timezone.utc.utcoffset(now)
                is_dst = bool(now.dst())
                offset_hours = (offset.total_seconds() / 3600) if offset else 0
                offset_str = f"UTC{offset_hours:+g}"
            elif pytz is not None:
                tz_obj = pytz.timezone(tz_input)
                now = datetime.now(tz_obj)
                offset = now.utcoffset()
                is_dst = bool(now.dst())
                offset_hours = (offset.total_seconds() / 3600) if offset else 0
                offset_str = f"UTC{offset_hours:+g}"
            else:
                raise RuntimeError("No timezone backend available (install pytz or run on Python 3.9+).")

            friendly = now.strftime("%Y-%m-%d %H:%M:%S")
            desc = (
                f"**Timezone:** `{tz_input}`\n"
                f"**Local time:** `{friendly}`\n"
                f"**Offset:** `{offset_str}`\n"
                f"**DST:** `{'Yes' if is_dst else 'No'}`\n"
                f"**Timestamp (UTC):** `<t:{int(now.astimezone(dt_timezone.utc).timestamp())}:F>`"
            )
            embed = discord.Embed(title="🕒 Current time", description=desc, color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
            embed.set_footer(text=f"Requested by {requester}", icon_url=getattr(ctx.user if is_interaction else ctx.author, "display_avatar", None).url if (getattr(ctx.user if is_interaction else ctx.author, "display_avatar", None)) else None)

            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=embed)
                else:
                    await ctx.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

        except Exception:
            # friendly error
            err = discord.Embed(
                title="❌ Invalid timezone",
                description="Could not find the timezone. Use the autocomplete for common IANA names (e.g. `Asia/Kolkata`) or try aliases like `PST`, `EST`, or `UTC`.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)


async def setup(bot: commands.Bot):
    await bot.add_cog(TimeCog(bot))
