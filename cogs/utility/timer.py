import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import time

class Timer(commands.Cog):
    """Simple countdown timer"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='timer', aliases=['countdown'])
    async def timer_prefix(self, ctx, seconds: int):
        """Start a countdown timer (prefix command)"""
        await self._start_timer(ctx, seconds)
    
    @app_commands.command(name='timer', description='Start a countdown timer')
    async def timer_slash(self, interaction: discord.Interaction, seconds: int):
        """Start a countdown timer (slash command)"""
        await self._start_timer(interaction, seconds)
    
    async def _start_timer(self, ctx_or_interaction, seconds: int):
        """Internal method to start a timer"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        user = ctx_or_interaction.user if is_interaction else ctx_or_interaction.author
        
        try:
            # Validate timer duration
            if seconds <= 0:
                raise ValueError("Timer duration must be positive")
            
            if seconds > 86400:  # Max 24 hours
                raise ValueError("Timer duration cannot exceed 24 hours")
            
            # Create initial embed
            embed = discord.Embed(
                title="⏱️ Timer Started",
                description=f"Timer set for **{seconds}** seconds",
                color=discord.Color.blue()
            )
            embed.add_field(name="Started by", value=user.mention, inline=True)
            embed.add_field(name="Ends", value=f"<t:{int(time.time() + seconds)}:R>", inline=True)
            embed.set_footer(text="I'll notify you when the timer ends")
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            
            # Wait for timer to complete
            await asyncio.sleep(seconds)
            
            # Create completion embed
            complete_embed = discord.Embed(
                title="⏰ Timer Complete!",
                description=f"Your **{seconds}** second timer has finished!",
                color=discord.Color.green()
            )
            complete_embed.set_footer(text=f"Timer for {user.display_name}")
            complete_embed.timestamp = discord.utils.utcnow()
            
            try:
                if is_interaction:
                    await ctx_or_interaction.followup.send(f"{user.mention}", embed=complete_embed)
                else:
                    await ctx_or_interaction.send(f"{user.mention}", embed=complete_embed)
            except:
                # If can't send in channel, try DM
                try:
                    await user.send(embed=complete_embed)
                except:
                    pass
                    
        except ValueError as e:
            error_embed = discord.Embed(
                title="Invalid Duration",
                description=str(e),
                color=discord.Color.red()
            )
            error_embed.add_field(
                name="Valid Range",
                value="Timer must be between 1 second and 86400 seconds (24 hours)",
                inline=False
            )
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)
        
        except Exception as e:
            error_embed = discord.Embed(
                title="Error",
                description=f"Failed to start timer: {str(e)}",
                color=discord.Color.red()
            )
            if is_interaction:
                if not ctx_or_interaction.response.is_done():
                    await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)

async def setup(bot):
    await bot.add_cog(Timer(bot))
