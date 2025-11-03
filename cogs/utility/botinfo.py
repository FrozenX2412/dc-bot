import discord
from discord.ext import commands
from discord import app_commands
import platform
import psutil
import time

class BotInfo(commands.Cog):
    """Display bot information and statistics"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @commands.command(name='botinfo', aliases=['bi', 'info', 'stats'])
    async def botinfo_prefix(self, ctx):
        """Display bot information (prefix command)"""
        await self._show_bot_info(ctx)
    
    @app_commands.command(name='botinfo', description='Display bot information and statistics')
    async def botinfo_slash(self, interaction: discord.Interaction):
        """Display bot information (slash command)"""
        await self._show_bot_info(interaction)
    
    async def _show_bot_info(self, ctx_or_interaction):
        """Internal method to display bot information"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        
        try:
            # Calculate uptime
            uptime_seconds = int(time.time() - self.start_time)
            uptime_str = self._format_uptime(uptime_seconds)
            
            # Get system info
            memory_usage = psutil.Process().memory_info().rss / 1024 ** 2  # MB
            cpu_percent = psutil.cpu_percent()
            
            # Create embed
            embed = discord.Embed(
                title=f"{self.bot.user.name} - Bot Information",
                description="Here's detailed information about me!",
                color=discord.Color.blue()
            )
            
            # Add bot avatar
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            # Bot stats
            embed.add_field(
                name="📊 Statistics",
                value=f"**Guilds:** {len(self.bot.guilds)}\n"
                      f"**Users:** {len(self.bot.users)}\n"
                      f"**Commands:** {len(self.bot.commands)}",
                inline=True
            )
            
            # System info
            embed.add_field(
                name="💻 System",
                value=f"**CPU Usage:** {cpu_percent}%\n"
                      f"**Memory:** {memory_usage:.2f} MB\n"
                      f"**Python:** {platform.python_version()}",
                inline=True
            )
            
            # Bot info
            embed.add_field(
                name="🤖 Bot Info",
                value=f"**Uptime:** {uptime_str}\n"
                      f"**Discord.py:** {discord.__version__}\n"
                      f"**Ping:** {round(self.bot.latency * 1000)}ms",
                inline=True
            )
            
            embed.set_footer(text=f"Requested by {ctx_or_interaction.user.display_name if is_interaction else ctx_or_interaction.author.display_name}")
            embed.timestamp = discord.utils.utcnow()
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
                
        except Exception as e:
            error_embed = discord.Embed(
                title="Error",
                description=f"Failed to fetch bot info: {str(e)}",
                color=discord.Color.red()
            )
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)
    
    def _format_uptime(self, seconds):
        """Format uptime in human-readable format"""
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return ' '.join(parts)

async def setup(bot):
    await bot.add_cog(BotInfo(bot))
