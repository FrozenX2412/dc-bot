import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import re
from datetime import datetime, timedelta

class Remind(commands.Cog):
    """Set reminders for yourself"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='remind', aliases=['reminder', 'remindme'])
    async def remind_prefix(self, ctx, time: str, *, reminder: str):
        """Set a reminder (prefix command)"""
        await self._set_reminder(ctx, time, reminder)
    
    @app_commands.command(name='remind', description='Set a reminder for yourself')
    async def remind_slash(self, interaction: discord.Interaction, time: str, reminder: str):
        """Set a reminder (slash command)"""
        await self._set_reminder(interaction, time, reminder)
    
    async def _set_reminder(self, ctx_or_interaction, time_str: str, reminder: str):
        """Internal method to set a reminder"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        user = ctx_or_interaction.user if is_interaction else ctx_or_interaction.author
        
        try:
            # Parse time string (e.g., "10m", "1h", "2d")
            seconds = self._parse_time(time_str)
            
            if seconds <= 0:
                raise ValueError("Time must be positive")
            
            if seconds > 31536000:  # More than 1 year
                raise ValueError("Time cannot exceed 1 year")
            
            # Calculate reminder time
            remind_at = datetime.utcnow() + timedelta(seconds=seconds)
            
            # Create confirmation embed
            embed = discord.Embed(
                title="⏰ Reminder Set",
                description=f"I'll remind you in **{self._format_duration(seconds)}**",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Reminder", value=reminder, inline=False)
            embed.add_field(name="Time", value=f"<t:{int(remind_at.timestamp())}:R>", inline=False)
            embed.set_footer(text=f"Reminder for {user.display_name}")
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            
            # Wait and send reminder
            await asyncio.sleep(seconds)
            
            # Create reminder embed
            remind_embed = discord.Embed(
                title="🔔 Reminder!",
                description=reminder,
                color=discord.Color.gold()
            )
            remind_embed.set_footer(text=f"Reminder set {self._format_duration(seconds)} ago")
            remind_embed.timestamp = discord.utils.utcnow()
            
            try:
                if is_interaction:
                    await ctx_or_interaction.followup.send(f"{user.mention}", embed=remind_embed)
                else:
                    await ctx_or_interaction.send(f"{user.mention}", embed=remind_embed)
            except:
                # If can't send in channel, try DM
                try:
                    await user.send(embed=remind_embed)
                except:
                    pass
                    
        except ValueError as e:
            error_embed = discord.Embed(
                title="Invalid Time Format",
                description=str(e),
                color=discord.Color.red()
            )
            error_embed.add_field(
                name="Valid Formats",
                value="`10s` (seconds)\n`5m` (minutes)\n`2h` (hours)\n`1d` (days)",
                inline=False
            )
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)
        
        except Exception as e:
            error_embed = discord.Embed(
                title="Error",
                description=f"Failed to set reminder: {str(e)}",
                color=discord.Color.red()
            )
            if is_interaction:
                if not ctx_or_interaction.response.is_done():
                    await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)
    
    def _parse_time(self, time_str: str) -> int:
        """Parse time string to seconds"""
        time_str = time_str.lower().strip()
        
        # Match pattern like: 10m, 1h, 2d, etc.
        match = re.match(r'^(\d+)([smhd])$', time_str)
        
        if not match:
            raise ValueError("Invalid time format. Use: 10s, 5m, 2h, 1d")
        
        amount = int(match.group(1))
        unit = match.group(2)
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        return amount * multipliers[unit]
    
    def _format_duration(self, seconds: int) -> str:
        """Format seconds into readable duration"""
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = seconds // 86400
            return f"{days} day{'s' if days != 1 else ''}"

async def setup(bot):
    await bot.add_cog(Remind(bot))
