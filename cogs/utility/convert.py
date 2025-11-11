# cogs/util/convert.py
import re
import math
from typing import Union, Tuple, Optional

import discord
from discord.ext import commands
from discord import app_commands

# Canonical unit maps -> base unit factors
# Length: base = meters
_LENGTH_UNITS = {
    "m": 1.0, "meter": 1.0, "metre": 1.0,
    "cm": 0.01, "centimeter": 0.01, "centimetre": 0.01,
    "mm": 0.001, "millimeter": 0.001, "millimetre": 0.001,
    "km": 1000.0, "kilometer": 1000.0, "kilometre": 1000.0,
    "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
    "in": 0.0254, "inch": 0.0254,
    "yd": 0.9144, "yard": 0.9144,
    "mi": 1609.344, "mile": 1609.344,
    "nm": 1852.0,  # nautical mile
}

# Mass: base = kilograms
_MASS_UNITS = {
    "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0,
    "g": 0.001, "gram": 0.001, "grams": 0.001,
    "mg": 1e-6, "milligram": 1e-6,
    "lb": 0.45359237, "pound": 0.45359237, "pounds": 0.45359237,
    "oz": 0.028349523125, "ounce": 0.028349523125, "ounces": 0.028349523125,
    "ton": 907.18474, "tonne": 1000.0, "metric ton": 1000.0,
}

# Temperature: handled separately (Celsius, Fahrenheit, Kelvin)
_TEMP_UNITS = {"c": "c", "celsius": "c", "°c": "c", "f": "f", "fahrenheit": "f", "°f": "f", "k": "k", "kelvin": "k"}

# Aggregate lookups
UNIT_ALIASES = {}
UNIT_ALIASES.update({k: ("length", v) for k, v in _LENGTH_UNITS.items()})
UNIT_ALIASES.update({k: ("mass", v) for k, v in _MASS_UNITS.items()})
UNIT_ALIASES.update({k: ("temp", None) for k in _TEMP_UNITS.keys()})  # temp units map to type only

# Normalize keys with plurals/variants
_extra_aliases = {
    "meters": "m", "metres": "m", "kilometers": "km", "kilometres": "km",
    "grams": "g", "kilograms": "kg", "pounds": "lb", "lbs": "lb", "ounces": "oz",
    "yards": "yd", "inches": "in", "feet": "ft", "miles": "mi",
}
for a, b in _extra_aliases.items():
    if b in UNIT_ALIASES:
        UNIT_ALIASES[a] = UNIT_ALIASES[b]

# parsing regex for free-form like "1 km to m" or "100F to C"
_FREEFORM_RE = re.compile(
    r"""^\s*
    (?P<amount>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)   # number (supports scientific)
    \s*
    (?P<from_unit>[a-zA-Z°]+)                            # unit token (letters or degree sign)
    (?:\s*(?:to|in)\s*|[\s]+)                            # separator 'to' / 'in' or whitespace
    (?P<to_unit>[a-zA-Z°]+)                              # target unit
    \s*$""",
    re.VERBOSE | re.IGNORECASE,
)


def _normalize_unit(u: str) -> str:
    return u.strip().lower()


def _format_number(n: float) -> str:
    """Friendly formatting with up to 6 significant digits, scientific for extremes."""
    if n == 0:
        return "0"
    mag = abs(n)
    if mag < 1e-3 or mag >= 1e6:
        return f"{n:.6e}"
    # up to 6 significant digits
    digits = 6
    int_part = int(math.floor(math.log10(mag))) + 1
    decimals = max(0, digits - int_part)
    out = f"{n:.{decimals}f}".rstrip("0").rstrip(".")
    return out


def _parse_freeform(query: str) -> Optional[Tuple[float, str, str]]:
    """Try to parse expressions like '1km to m' -> (1.0, 'km', 'm')."""
    m = _FREEFORM_RE.match(query)
    if not m:
        return None
    try:
        amount = float(m.group("amount"))
        from_u = m.group("from_unit")
        to_u = m.group("to_unit")
        return amount, from_u, to_u
    except Exception:
        return None


def _identify_unit(u: str) -> Optional[Tuple[str, Optional[float]]]:
    """Return (type, factor) where type in {length,mass,temp}; factor is factor to base unit or None for temp."""
    nu = _normalize_unit(u)
    # allow degree symbols like '°c' or 'c'
    nu = nu.replace("°", "")
    if nu in UNIT_ALIASES:
        return UNIT_ALIASES[nu]
    return None


def _convert_temperature(value: float, from_u: str, to_u: str) -> float:
    """Convert between Celsius, Fahrenheit, Kelvin. from_u/to_u are normalized short forms 'c','f','k'."""
    fu = from_u.lower().replace("°", "")
    tu = to_u.lower().replace("°", "")
    if fu == tu:
        return value
    # to celsius
    if fu == "f":
        c = (value - 32) * 5.0 / 9.0
    elif fu == "k":
        c = value - 273.15
    else:  # c
        c = value
    # from celsius to target
    if tu == "f":
        return c * 9.0 / 5.0 + 32
    if tu == "k":
        return c + 273.15
    return c


class Convert(commands.Cog):
    """Convert between length, mass, and temperature units. Supports hybrid command and free-form strings."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="convert",
        description="Convert units. Examples: `/convert 1 km m` or `/convert query:\"100 F to C\"`"
    )
    @app_commands.describe(
        amount="Value to convert (optional if using query)",
        from_unit="Original unit (optional if using query)",
        to_unit="Target unit (optional if using query)",
        query="Free-form string like '1km to m' (optional)"
    )
    async def convert(
        self,
        ctx: Union[commands.Context, discord.Interaction],
        amount: Optional[float] = None,
        from_unit: Optional[str] = None,
        to_unit: Optional[str] = None,
        *,
        query: Optional[str] = None
    ):
        """
        Usage examples:
          - /convert amount:1 from_unit:km to_unit:m
          - /convert query:"1km to m"
          - <prefix>convert 100 F to C
        """
        is_interaction = isinstance(ctx, discord.Interaction)
        requester = getattr(ctx.user if is_interaction else ctx.author, "display_name", "Unknown")

        # If query provided, try to parse it first (free-form)
        if query:
            parsed = _parse_freeform(query)
            if not parsed:
                err = discord.Embed(title="❌ Could not parse query",
                                    description="Examples: `1 km to m`, `100 F to C`, `2mi in km`.",
                                    color=discord.Color.red(),
                                    timestamp=discord.utils.utcnow())
                err.set_footer(text=f"Requested by {requester}")
                if is_interaction:
                    await ctx.response.send_message(embed=err, ephemeral=True)
                else:
                    await ctx.send(embed=err)
                return
            amount, from_unit, to_unit = parsed

        # If user used prefix-style single argument (freeform), attempt to parse context.message.content
        if amount is None and from_unit is None and to_unit is None:
            # try to extract a freeform after the command name (prefix usage)
            if not is_interaction:
                content = ctx.message.content
                # remove leading prefix+command -> find first space then take rest
                parts = content.split(None, 1)
                if len(parts) > 1:
                    rest = parts[1].strip()
                    parsed = _parse_freeform(rest)
                    if parsed:
                        amount, from_unit, to_unit = parsed

        # Still missing args?
        if amount is None or from_unit is None or to_unit is None:
            err = discord.Embed(
                title="❌ Missing arguments",
                description="Provide `amount from_unit to_unit`, or use `query` argument. Examples:\n`/convert 1 km m` or `/convert query:\"100 F to C\"`",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
            return

        # Identify unit types
        from_info = _identify_unit(from_unit)
        to_info = _identify_unit(to_unit)
        if not from_info or not to_info:
            err = discord.Embed(
                title="❌ Unknown unit",
                description=f"Could not recognize units `{from_unit}` or `{to_unit}`. Try examples: m, km, mi, kg, lb, g, C, F, K.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
            return

        from_type, from_factor = from_info
        to_type, to_factor = to_info

        # Ensure same type (or temperature special-case allowed between temperature units only)
        if from_type != to_type:
            err = discord.Embed(
                title="❌ Incompatible unit types",
                description=f"Cannot convert from `{from_unit}` ({from_type}) to `{to_unit}` ({to_type}). Convert length↔length, mass↔mass, temp↔temp only.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
            return

        try:
            # Temperature conversions
            if from_type == "temp":
                # normalize temperature keys to short forms
                fu = _normalize_unit(from_unit).replace("°", "")
                tu = _normalize_unit(to_unit).replace("°", "")
                fu = _TEMP_UNITS.get(fu, fu)
                tu = _TEMP_UNITS.get(tu, tu)
                res = _convert_temperature(amount, fu, tu)
                fmt_in = f"{_format_number(amount)} {from_unit}"
                fmt_out = f"{_format_number(res)} {to_unit}"
            elif from_type == "length":
                # convert to meters then to target
                meters = amount * from_factor
                res_val = meters / to_factor
                fmt_in = f"{_format_number(amount)} {from_unit}"
                fmt_out = f"{_format_number(res_val)} {to_unit}"
            elif from_type == "mass":
                # convert to kilograms then to target
                kgs = amount * from_factor
                res_val = kgs / to_factor
                fmt_in = f"{_format_number(amount)} {from_unit}"
                fmt_out = f"{_format_number(res_val)} {to_unit}"
            else:
                raise RuntimeError("Unhandled unit type")

            embed = discord.Embed(
                title="🔄 Conversion Result",
                description=f"**Input:** {fmt_in}\n**Output:** {fmt_out}",
                color=discord.Color.teal(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=embed)
                else:
                    await ctx.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

        except Exception as exc:
            err = discord.Embed(
                title="⚠️ Conversion error",
                description="An internal error occurred while converting. Ensure your inputs are valid.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)


async def setup(bot: commands.Bot):
    await bot.add_cog(Convert(bot))
