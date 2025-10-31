import discord
from discord.ext import commands
from discord import app_commands
import datetime
import json
import os

class Warn(commands.Cog):
    """Warning management commands with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
        self.warnings_file = "warnings.json"
        self.warnings = self.load_warnings()
    
    def load_warnings(self):
        """Load warnings from JSON file"""
        if os.path.exists(self.warnings_file):
            with open(self.warnings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_warnings(self):
        """Save warnings to JSON file"""
        with open(self.warnings_file, 'w') as f:
            json.dump(self.warnings, f, indent=4)
    
    def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str):
        """Add a warning to the database"""
        guild_key = str(guild_id)
        user_key = str(user_id)
        
        if guild_key not in self.warnings:
            self.warnings[guild_key] = {}
        if user_key not in self.warnings[guild_key]:
            self.warnings[guild_key][user_key] = []
        
        warning = {
            "timestamp": datetime.datetime.now().isoformat(),
            "moderator_id": moderator_id,
            "reason": reason
        }
        self.warnings[guild_key][user_key].append(warning)
        self.save_warnings()
        return len(self.warnings[guild_key][user_key])
    
    @commands.hybrid_command(
        name="warn",
        description="Issue a warning to a user"
    )
    @app_commands.describe(
        member="The member to warn",
        reason="Reason for the warning"
    )
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Warn a member with creative embed styling"""
        
        if member.bot:
            embed = discord.Embed(
                title="❌ Cannot Warn Bot",
                description="You cannot warn a bot.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        # Add warning
        warning_count = self.add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
        
        # Try to DM the user
        try:
            dm_embed = discord.Embed(
                title="⚠️ You Have Been Warned",
                description=f"You have been warned in **{ctx.guild.name}**",
                color=discord.Color.from_rgb(255, 193, 7),
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Warning Count", value=f"`{warning_count}` warning(s)", inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            dm_embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            await member.send(embed=dm_embed)
        except:
            pass
        
        # Send success embed with creative styling
        embed = discord.Embed(
            title="⚠️ Warning Issued",
            color=discord.Color.from_rgb(255, 193, 7),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Warned User", value=f"{member.mention}\n`{member} ({member.id})`", inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=True)
        embed.add_field(name="🔢 Total Warnings", value=f"`{warning_count}`", inline=True)
        embed.add_field(name="📋 Reason", value=f"```{reason}```", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Warned in {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Warn(bot))
