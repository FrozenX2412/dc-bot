import discord
from discord.ext import commands
from discord import app_commands
import unicodedata

class EmojiInfo(commands.Cog):
    """Get detailed information about an emoji"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='emojiinfo', aliases=['ei', 'emoji'])
    async def emojiinfo_prefix(self, ctx, emoji: str):
        """Get information about an emoji (prefix command)"""
        await self._get_emoji_info(ctx, emoji)
    
    @app_commands.command(name='emojiinfo', description='Get detailed information about an emoji')
    async def emojiinfo_slash(self, interaction: discord.Interaction, emoji: str):
        """Get information about an emoji (slash command)"""
        await self._get_emoji_info(interaction, emoji)
    
    async def _get_emoji_info(self, ctx_or_interaction, emoji: str):
        """Internal method to get emoji information"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        
        try:
            # Try to parse as custom emoji
            if emoji.startswith('<') and emoji.endswith('>'):
                # Custom Discord emoji
                animated = emoji.startswith('<a:')
                emoji_id = emoji.split(':')[-1][:-1]
                emoji_name = emoji.split(':')[1]
                
                embed = discord.Embed(
                    title="Custom Emoji Information",
                    color=discord.Color.purple()
                )
                
                embed.add_field(name="Name", value=emoji_name, inline=True)
                embed.add_field(name="ID", value=emoji_id, inline=True)
                embed.add_field(name="Animated", value="Yes" if animated else "No", inline=True)
                
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if animated else 'png'}"
                embed.add_field(name="URL", value=f"[Click Here]({emoji_url})", inline=False)
                embed.set_thumbnail(url=emoji_url)
                
            else:
                # Unicode emoji
                embed = discord.Embed(
                    title="Unicode Emoji Information",
                    color=discord.Color.gold()
                )
                
                # Get unicode information
                try:
                    emoji_char = emoji[0] if emoji else ''
                    emoji_name = unicodedata.name(emoji_char, "Unknown")
                    emoji_code = f"U+{ord(emoji_char):04X}"
                    
                    embed.add_field(name="Emoji", value=emoji, inline=True)
                    embed.add_field(name="Name", value=emoji_name, inline=True)
                    embed.add_field(name="Unicode", value=emoji_code, inline=True)
                    embed.add_field(name="Raw", value=f"`{emoji}`", inline=False)
                    
                except Exception:
                    embed.description = "Could not parse emoji information."
            
            embed.set_footer(text=f"Requested by {ctx_or_interaction.user.display_name if is_interaction else ctx_or_interaction.author.display_name}")
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
                
        except Exception as e:
            error_embed = discord.Embed(
                title="Error",
                description=f"Failed to get emoji info: {str(e)}",
                color=discord.Color.red()
            )
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)

async def setup(bot):
    await bot.add_cog(EmojiInfo(bot))
