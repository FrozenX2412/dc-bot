import discord
from discord.ext import commands
from discord import app_commands
import datetime

class ServerInfo(commands.Cog):
    """ServerInfo command cog with both slash and prefix support"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="serverinfo",
        description="Display detailed information about the server",
        aliases=["si", "guildinfo"]
    )
    async def serverinfo(self, ctx):
        """
        Display detailed information about the server
        """
        guild = ctx.guild
        
        # Create embed
        embed = discord.Embed(
            title=f"📊 Server Information - {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        
        # Set server icon as thumbnail
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Set server banner as image (if available)
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        
        # Basic Information
        embed.add_field(
            name="🆔 Server ID",
            value=f"`{guild.id}`",
            inline=True
        )
        
        embed.add_field(
            name="👑 Owner",
            value=guild.owner.mention if guild.owner else "Unknown",
            inline=True
        )
        
        embed.add_field(
            name="📅 Created",
            value=f"<t:{int(guild.created_at.timestamp())}:R>",
            inline=True
        )
        
        # Member Statistics
        total_members = guild.member_count
        bots = sum(1 for member in guild.members if member.bot)
        humans = total_members - bots
        
        embed.add_field(
            name="👥 Members",
            value=f"Total: **{total_members}**\nHumans: **{humans}**\nBots: **{bots}**",
            inline=True
        )
        
        # Channel Statistics
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📝 Channels",
            value=f"Text: **{text_channels}**\nVoice: **{voice_channels}**\nCategories: **{categories}**",
            inline=True
        )
        
        # Roles
        embed.add_field(
            name="🎭 Roles",
            value=f"**{len(guild.roles)}** roles",
            inline=True
        )
        
        # Emojis
        regular_emojis = sum(1 for emoji in guild.emojis if not emoji.animated)
        animated_emojis = sum(1 for emoji in guild.emojis if emoji.animated)
        
        embed.add_field(
            name="😊 Emojis",
            value=f"Regular: **{regular_emojis}**\nAnimated: **{animated_emojis}**",
            inline=True
        )
        
        # Boost Information
        embed.add_field(
            name="🚀 Boost Status",
            value=f"Level: **{guild.premium_tier}**\nBoosts: **{guild.premium_subscription_count or 0}**\nBoosters: **{len(guild.premium_subscribers)}**",
            inline=True
        )
        
        # Verification Level
        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest"
        }
        
        embed.add_field(
            name="🔒 Verification Level",
            value=verification_levels.get(guild.verification_level, "Unknown"),
            inline=True
        )
        
        # Features
        features = guild.features
        if features:
            # Format features nicely
            formatted_features = [feature.replace('_', ' ').title() for feature in features[:5]]
            features_text = "\n".join(f"• {feature}" for feature in formatted_features)
            if len(features) > 5:
                features_text += f"\n*... and {len(features) - 5} more*"
            
            embed.add_field(
                name="✨ Features",
                value=features_text or "No special features",
                inline=False
            )
        
        # Set footer
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)
    
    @serverinfo.error
    async def serverinfo_error(self, ctx, error):
        """Error handler for serverinfo command"""
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred while fetching server information: {str(error)}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
