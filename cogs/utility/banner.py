import discord
from discord.ext import commands
from discord import app_commands

class Banner(commands.Cog):
    """Get user banner command - displays user's profile banner"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='banner', aliases=['userbanner'])
    async def banner_prefix(self, ctx, user: discord.User = None):
        """Get a user's banner (prefix command)"""
        await self._get_banner(ctx, user or ctx.author)
    
    @app_commands.command(name='banner', description='Get a user\'s banner')
    async def banner_slash(self, interaction: discord.Interaction, user: discord.User = None):
        """Get a user's banner (slash command)"""
        await self._get_banner(interaction, user or interaction.user)
    
    async def _get_banner(self, ctx_or_interaction, user: discord.User):
        """Internal method to fetch and display user banner"""
        # Determine if it's a context or interaction
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        
        try:
            # Fetch full user to get banner
            fetched_user = await self.bot.fetch_user(user.id)
            
            # Create embed
            embed = discord.Embed(
                title=f"{user.display_name}'s Banner",
                color=discord.Color.blue()
            )
            
            # Check if user has a banner
            if fetched_user.banner:
                banner_url = fetched_user.banner.url
                embed.set_image(url=banner_url)
                embed.set_footer(text=f"Requested by {ctx_or_interaction.user.display_name if is_interaction else ctx_or_interaction.author.display_name}")
            else:
                embed.description = f"**{user.display_name}** doesn't have a banner set."
                embed.color = discord.Color.red()
            
            # Set thumbnail to user avatar
            embed.set_thumbnail(url=user.display_avatar.url)
            
            # Send response
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
                
        except Exception as e:
            error_embed = discord.Embed(
                title="Error",
                description=f"Failed to fetch banner: {str(e)}",
                color=discord.Color.red()
            )
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)

async def setup(bot):
    await bot.add_cog(Banner(bot))
