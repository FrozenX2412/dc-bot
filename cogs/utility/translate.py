import discord
from discord.ext import commands
from discord import app_commands
from googletrans import Translator, LANGUAGES

class Translate(commands.Cog):
    """Translate text between languages"""
    
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
    
    @commands.command(name='translate', aliases=['tr'])
    async def translate_prefix(self, ctx, dest_lang: str, *, text: str):
        """Translate text to another language (prefix command)"""
        await self._translate_text(ctx, dest_lang, text)
    
    @app_commands.command(name='translate', description='Translate text to another language')
    async def translate_slash(self, interaction: discord.Interaction, dest_lang: str, text: str):
        """Translate text to another language (slash command)"""
        await self._translate_text(interaction, dest_lang, text)
    
    async def _translate_text(self, ctx_or_interaction, dest_lang: str, text: str):
        """Internal method to translate text"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        
        try:
            # Normalize language code
            dest_lang = dest_lang.lower()
            
            # Check if language is valid
            if dest_lang not in LANGUAGES:
                raise ValueError(f"'{dest_lang}' is not a valid language code")
            
            # Translate text
            translation = self.translator.translate(text, dest=dest_lang)
            
            # Get language names
            source_lang_name = LANGUAGES.get(translation.src, translation.src.upper())
            dest_lang_name = LANGUAGES.get(dest_lang, dest_lang.upper())
            
            # Create embed
            embed = discord.Embed(
                title="🌍 Translation",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name=f"Original ({source_lang_name.title()})",
                value=text[:1024],  # Discord field limit
                inline=False
            )
            
            embed.add_field(
                name=f"Translation ({dest_lang_name.title()})",
                value=translation.text[:1024],
                inline=False
            )
            
            embed.set_footer(text=f"Requested by {ctx_or_interaction.user.display_name if is_interaction else ctx_or_interaction.author.display_name}")
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
                
        except ValueError as e:
            error_embed = discord.Embed(
                title="Invalid Language",
                description=str(e),
                color=discord.Color.red()
            )
            error_embed.add_field(
                name="Common Language Codes",
                value="`en` (English), `es` (Spanish), `fr` (French), `de` (German), `ja` (Japanese), `ko` (Korean), `zh-cn` (Chinese)",
                inline=False
            )
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)
        
        except Exception as e:
            error_embed = discord.Embed(
                title="Translation Error",
                description=f"Failed to translate: {str(e)}",
                color=discord.Color.red()
            )
            if is_interaction:
                if not ctx_or_interaction.response.is_done():
                    await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)

async def setup(bot):
    await bot.add_cog(Translate(bot))
