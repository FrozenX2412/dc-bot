# cogs/util/translate.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Union, List
import asyncio

# googletrans (community) -- blocking API, we'll run it in executor
from googletrans import Translator, LANGUAGES

# Build lookup: both code -> name and name -> code (lowercased)
CODE_TO_NAME = {k.lower(): v.title() for k, v in LANGUAGES.items()}
NAME_TO_CODE = {v.lower(): k for k, v in LANGUAGES.items()}

# Prepare list for autocomplete (limit 25 handled by autocomplete function)
LANG_CHOICES = sorted([(code, name) for code, name in CODE_TO_NAME.items()], key=lambda t: t[1].lower())


async def _lang_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    cur = (current or "").lower()
    choices = []
    for code, name in LANG_CHOICES:
        if not cur or cur in name.lower() or cur in code:
            choices.append(app_commands.Choice(name=f"{name} ({code})", value=code))
            if len(choices) >= 25:
                break
    return choices


class TranslateCog(commands.Cog):
    """Translate text between languages using googletrans (runs translation in executor)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Keep one translator instance (thread-safe enough for small bots)
        self._translator = Translator()

    @commands.hybrid_command(
        name="translate",
        aliases=["tr"],
        description="Translate text to another language. Example: /translate dest:en text:\"Hello\""
    )
    @app_commands.describe(
        dest="Destination language (code like 'en' or name like 'English')",
        text="Text to translate"
    )
    @app_commands.autocomplete(dest=_lang_autocomplete)
    async def translate(self, ctx: Union[commands.Context, discord.Interaction], dest: str, *, text: str):
        """
        Translate `text` to `dest`. `dest` may be a language code (en) or name (english).
        If dest is invalid, user is notified.
        """
        is_interaction = isinstance(ctx, discord.Interaction)
        requester = getattr(ctx.user if is_interaction else ctx.author, "display_name", "Unknown")

        # Normalize destination: accept code or name
        dest_raw = (dest or "").strip().lower()
        if not dest_raw:
            err = discord.Embed(title="❌ Missing language", description="Provide a destination language code (e.g. `en`) or name (e.g. `English`).", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
            return

        # If user provided a language name, map to code if possible
        dest_code = None
        if dest_raw in CODE_TO_NAME:
            dest_code = dest_raw
        elif dest_raw in NAME_TO_CODE:
            dest_code = NAME_TO_CODE[dest_raw]
        else:
            # Try fuzzy: look for substring in language names
            match = next((code for code, name in CODE_TO_NAME.items() if dest_raw in name.lower()), None)
            if match:
                dest_code = match

        if not dest_code:
            err = discord.Embed(title="❌ Unknown language", description=f"Couldn't recognize `{dest}` as a language. Try `en` for English, `es` for Spanish, etc.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.add_field(name="Tip", value="You can type a language name (English) or code (en). Try the slash autocomplete for suggestions.", inline=False)
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
            return

        # Run translation in executor to avoid blocking
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(None, lambda: self._translator.translate(text, dest=dest_code))
        except Exception as exc:
            err = discord.Embed(title="⚠️ Translation failed", description="An error occurred while translating. Try again later.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.add_field(name="Details", value=str(exc)[:800], inline=False)
            err.set_footer(text=f"Requested by {requester}")
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)
            return

        # Build response embed (truncate fields safely)
        src_code = getattr(result, "src", "").lower() or "auto"
        src_name = CODE_TO_NAME.get(src_code, src_code.upper())
        dest_name = CODE_TO_NAME.get(dest_code, dest_code.upper())

        orig = (text[:1000] + "…") if len(text) > 1000 else text
        trans_text = (result.text[:1000] + "…") if len(result.text) > 1000 else result.text

        embed = discord.Embed(title="🌍 Translation", color=discord.Color.blue(), timestamp=discord.utils.utcnow())
        embed.add_field(name=f"From — {src_name} ({src_code})", value=f"```{orig}```", inline=False)
        embed.add_field(name=f"To — {dest_name} ({dest_code})", value=f"```{trans_text}```", inline=False)
        # optional: show pronunciation if present
        if getattr(result, "pronunciation", None):
            pron = result.pronunciation
            if len(pron) > 800:
                pron = pron[:800] + "…"
            embed.add_field(name="Pronunciation", value=pron, inline=False)

        embed.set_footer(text=f"Requested by {requester}")
        if is_interaction:
            # reply via interaction
            if not ctx.response.is_done():
                await ctx.response.send_message(embed=embed)
            else:
                await ctx.followup.send(embed=embed)
        else:
            await ctx.send(embed=embed)
