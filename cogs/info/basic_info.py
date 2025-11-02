import discord
from discord.ext import commands
import datetime
import time

class BasicInfo(commands.Cog):
    """Basic information commands (help, ping, uptime, stats) with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @commands.hybrid_command(
        name="help",
        description="Shows all available commands"
    )
    async def help(self, ctx):
        """Display help information with creative embed styling"""
        
        embed = discord.Embed(
            title="🤖 Bot Commands",
            description="Here's a list of all available commands organized by category.",
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        # Moderation Commands
        mod_commands = (
            "`ban` `unban` `kick` `mute` `unmute` `warn` `clear` "
            "`slowmode` `lock` `unlock` `roleadd` `roleremove` `roleinfo` "
            "`softban` `prune` `infractions` `modlog` `report` `blacklist` `whitelist`"
        )
        embed.add_field(
            name="🛡️ Moderation",
            value=mod_commands,
            inline=False
        )
        
        # Info Commands
        info_commands = (
            "`help` `ping` `uptime` `stats` `userinfo` `membercount` `roles` "
            "`channelinfo` `emoji` `emotes` `id` `servericon` "
            "`boostcount` `joined` `servercreated` `invite`"
        )
        embed.add_field(
            name="ℹ️ Information",
            value=info_commands,
            inline=False
        )
        
        embed.add_field(
            name="💡 Tip",
            value="You can use both slash (`/command`) and prefix (`!command`) forms.",
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="ping",
        description="Check the bot's latency"
    )
    async def ping(self, ctx):
        """Check bot latency with creative embed styling"""
        
        latency = round(self.bot.latency * 1000)
        
        # Color and status based on latency
        if latency < 100:
            color = discord.Color.green()
            status = "✅ Excellent"
        elif latency < 200:
            color = discord.Color.from_rgb(255, 193, 7)
            status = "⚠️ Good"
        else:
            color = discord.Color.red()
            status = "❌ Poor"
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="📊 Latency", value=f"`{latency}ms`", inline=True)
        embed.add_field(name="📡 Status", value=status, inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="uptime",
        description="Shows how long the bot has been online"
    )
    async def uptime(self, ctx):
        """Display bot uptime with creative embed styling"""
        
        uptime_seconds = int(time.time() - self.start_time)
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = ""
        if days > 0:
            uptime_str += f"{days}d "
        if hours > 0:
            uptime_str += f"{hours}h "
        if minutes > 0:
            uptime_str += f"{minutes}m "
        uptime_str += f"{seconds}s"
        
        embed = discord.Embed(
            title="⏰ Bot Uptime",
            color=discord.Color.from_rgb(40, 167, 69),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🔄 Online For", value=f"`{uptime_str}`", inline=True)
        embed.add_field(name="🕓 Started", value=f"<t:{int(self.start_time)}:R>", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="stats",
        description="Displays bot statistics"
    )
    async def stats(self, ctx):
        """Display bot statistics with creative embed styling"""
        
        guild_count = len(self.bot.guilds)
        user_count = len(set(self.bot.get_all_members()))
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🏛️ Servers", value=f"`{guild_count}`", inline=True)
        embed.add_field(name="👥 Users", value=f"`{user_count}`", inline=True)
        embed.add_field(name="📡 Latency", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
        
        uptime_seconds = int(time.time() - self.start_time)
        days = uptime_seconds // 86400
        embed.add_field(name="⏰ Uptime", value=f"`{days}d+`", inline=True)
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BasicInfo(bot))
