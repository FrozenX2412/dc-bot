import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Convert(commands.Cog):
    """Convert between different units easily. Supports hybrid commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Supported basic conversions (unit: factor to base unit)
        self.length_units = {
            'm': 1, 'cm': 0.01, 'mm': 0.001,
            'km': 1000, 'ft': 0.3048, 'in': 0.0254, 'yd': 0.9144, 'mi': 1609.34
        }

    @commands.hybrid_command(name="convert")
    @app_commands.describe(amount="The value to convert.", from_unit="Original unit.", to_unit="Unit to convert to.")
    async def convert(self, ctx: commands.Context, amount: float, from_unit: str, to_unit: str):
        """Convert between length units. Eg. 1 km to m."""
        from_u = from_unit.lower()
        to_u = to_unit.lower()
        if from_u in self.length_units and to_u in self.length_units:
            meters = amount * self.length_units[from_u]
            result = meters / self.length_units[to_u]
            embed = discord.Embed(
                title=f"🔄 Conversion Result",
                description=f"{amount} {from_u} = {result:g} {to_u}",
                color=discord.Color.teal(),
                timestamp=datetime.now()
            )
        else:
            embed = discord.Embed(
                title="❌ Unsupported Unit",
                description="Try units like m, cm, mm, km, ft, in, yd, mi.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Load the Convert cog."""
    await bot.add_cog(Convert(bot))
