# cogs/util/emoji_info.py
import re
import unicodedata
from typing import Union

import discord
from discord.ext import commands
from discord import app_commands

# regex for Discord custom emoji: <a:name:id> or <:name:id>
_CUSTOM_EMOJI_RE = re.compile(r"<(a?):(?P<name>[^:]+):(?P<id>\d+)>")

def _unicode_info(text: str) -> tuple[str, str]:
    """
    Return (codepoints_str, names_str) for the given emoji/text.
    Handles multi-codepoint emoji (e.g. flags, family).
    """
    cps = [f"U+{ord(ch):04X}" for ch in text]
    names = []
    for ch in text:
        try:
            names.append(unicodedata.name(ch))
        except Exception:
            names.append("<unknown>")
    return " ".join(cps), " | ".join(names)


class EmojiInfo(commands.Cog):
    """Get detailed information about an emoji (custom or unicode)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="emojiinfo",
        description="Get detailed information about an emoji (custom or unicode)."
    )
    @app_commands.describe(emoji="Emoji to inspect (paste the emoji or custom emoji like <:name:id>)")
    async def emojiinfo(self, ctx: Union[commands.Context, discord.Interaction], emoji: str):
        """
        Works as both prefix and slash:
        - /emojiinfo emoji:"😀"
        - !emojiinfo <:thonk:123456789012345678>
        """
        is_interaction = isinstance(ctx, discord.Interaction)
        requester = getattr(ctx.user if is_interaction else ctx.author, "display_name", "Unknown")

        try:
            # Try custom emoji pattern first
            m = _CUSTOM_EMOJI_RE.match(emoji.strip())
            if m:
                animated = bool(m.group(1))
                name = m.group("name")
                eid = int(m.group("id"))

                # Try to get the Emoji object via bot cache
                emoji_obj = self.bot.get_emoji(eid)

                embed = discord.Embed(
                    title="Custom Emoji Information",
                    color=discord.Color.purple(),
                    timestamp=discord.utils.utcnow()
                )

                embed.add_field(name="Name", value=name, inline=True)
                embed.add_field(name="ID", value=str(eid), inline=True)
                embed.add_field(name="Animated", value="Yes" if animated else "No", inline=True)

                # emoji URL
                fmt = "gif" if animated else "png"
                url = f"https://cdn.discordapp.com/emojis/{eid}.{fmt}"
                embed.add_field(name="URL", value=f"[Open emoji]({url})", inline=False)
                embed.set_thumbnail(url=url)

                # If we have the Emoji object (cached), show more info
                if isinstance(emoji_obj, discord.Emoji):
                    guild = emoji_obj.guild
                    embed.add_field(name="Guild", value=f"{guild.name} (`{guild.id}`)", inline=False)
                    # created_at is available on PartialEmoji? For Emoji it should be present
                    created = getattr(emoji_obj, "created_at", None)
                    if created:
                        embed.add_field(name="Created At (UTC)", value=created.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=True)
                    else:
                        embed.add_field(name="Created At (UTC)", value="Unknown", inline=True)
                    embed.add_field(name="Require Colons", value=str(getattr(emoji_obj, "require_colons", True)), inline=True)
                else:
                    # Not in cache (maybe from another guild); still show URL and name/id
                    embed.add_field(name="Guild", value="Not cached (bot may not share that guild)", inline=False)

            else:
                # Treat as Unicode emoji or a sequence of characters
                text = emoji.strip()
                if not text:
                    raise ValueError("No emoji provided.")

                # In case user pasted a string with spaces, pick first visual cluster-like token
                # but we will analyze the whole provided string
                codepoints, names = _unicode_info(text)

                embed = discord.Embed(
                    title="Unicode Emoji Information",
                    color=discord.Color.gold(),
                    timestamp=discord.utils.utcnow()
                )

                embed.add_field(name="Emoji", value=text, inline=True)
                embed.add_field(name="Codepoints", value=codepoints, inline=True)
                embed.add_field(name="Names", value=names, inline=False)

                # Raw representation
                # Show escaped code units for clarity
                raw_repr = " ".join(f"\\u{ord(ch):04x}" for ch in text)
                embed.add_field(name="Raw Escape", value=f"`{raw_repr}`", inline=False)

            embed.set_footer(text=f"Requested by {requester}", icon_url=getattr(ctx.user if is_interaction else ctx.author, "display_avatar", None).url if (getattr(ctx.user if is_interaction else ctx.author, "display_avatar", None)) else None)

            # Send response appropriately
            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=embed)
                else:
                    await ctx.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

        except Exception as exc:
            err = discord.Embed(title="Error", description="Failed to get emoji info.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.add_field(name="Details", value=str(exc), inline=False)
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiInfo(bot))
