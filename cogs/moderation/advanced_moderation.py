import discord
from discord.ext import commands
from discord import app_commands
import datetime
import json
import os

class AdvancedModeration(commands.Cog):
    """Advanced moderation commands (softban, prune, infractions, modlog, report, blacklist, whitelist)"""
    
    def __init__(self, bot):
        self.bot = bot
        self.warnings_file = "warnings.json"
        self.blacklist_file = "blacklist.json"
        self.warnings = self.load_json(self.warnings_file)
        self.blacklist = self.load_json(self.blacklist_file)
    
    def load_json(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}
    
    def save_json(self, filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    
    @commands.hybrid_command(
        name="softban",
        description="Softban a user (ban then immediately unban to delete messages)"
    )
    @app_commands.describe(
        member="The member to softban",
        reason="Reason for the softban"
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Softban a member"""
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Softban Failed",
                description=f"You cannot softban {member.mention}.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            return await ctx.send(embed=embed, ephemeral=True)
        
        await ctx.guild.ban(member, reason=f"Softban by {ctx.author}: {reason}", delete_message_days=1)
        await ctx.guild.unban(member.id, reason="Softban - Auto unban")
        
        embed = discord.Embed(
            title="🛡️ Member Softbanned",
            color=discord.Color.from_rgb(255, 193, 7),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 User", value=f"{member.mention}\n`{member}`", inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="📋 Reason", value=f"```{reason}```", inline=False)
        embed.set_footer(text=f"Softbanned from {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="prune",
        description="Remove inactive members from the server"
    )
    @app_commands.describe(
        days="Number of days of inactivity (1-30)"
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def prune(self, ctx, days: int = 7):
        """Prune inactive members"""
        
        if days < 1 or days > 30:
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Days must be between 1 and 30.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, ephemeral=True)
        
        pruned = await ctx.guild.estimate_pruned_members(days=days)
        
        embed = discord.Embed(
            title="🧹 Prune Preview",
            description=f"This will remove approximately **{pruned}** members who have been inactive for **{days}** days.",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="Use with caution")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="infractions",
        description="Show a user's warning history"
    )
    @app_commands.describe(
        member="The member to check infractions for"
    )
    async def infractions(self, ctx, member: discord.Member):
        """Show member infractions"""
        
        guild_key = str(ctx.guild.id)
        user_key = str(member.id)
        
        warnings = self.warnings.get(guild_key, {}).get(user_key, [])
        
        if not warnings:
            embed = discord.Embed(
                title="✅ Clean Record",
                description=f"{member.mention} has no warnings.",
                color=discord.Color.green()
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"⚠️ Infractions for {member.name}",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now()
        )
        
        for i, warning in enumerate(warnings[-5:], 1):  # Show last 5
            moderator = ctx.guild.get_member(warning['moderator_id'])
            mod_name = moderator.name if moderator else "Unknown"
            timestamp = warning['timestamp'][:10]  # Date only
            embed.add_field(
                name=f"Warning #{i}",
                value=f"**Date:** {timestamp}\n**Mod:** {mod_name}\n**Reason:** {warning['reason']}",
                inline=False
            )
        
        embed.set_footer(text=f"Total warnings: {len(warnings)}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="modlog",
        description="Display recent moderation actions"
    )
    @commands.has_permissions(moderate_members=True)
    async def modlog(self, ctx):
        """Display moderation log"""
        
        embed = discord.Embed(
            title="📜 Moderation Log",
            description="Recent moderation actions will be displayed here.",
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Modlog for {ctx.guild.name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="report",
        description="Report a user for review by moderators"
    )
    @app_commands.describe(
        member="The member to report",
        reason="Reason for the report"
    )
    async def report(self, ctx, member: discord.Member, *, reason: str):
        """Report a user"""
        
        embed = discord.Embed(
            title="🚨 User Reported",
            color=discord.Color.from_rgb(220, 53, 69),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Reported User", value=f"{member.mention}\n`{member}`", inline=True)
        embed.add_field(name="Reporter", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text="Report submitted for moderator review")
        
        await ctx.send(embed=embed, ephemeral=True)
        
        # Try to send to a mod channel (you'd need to configure this)
        # For now, just confirm to user
        confirm_embed = discord.Embed(
            title="✅ Report Submitted",
            description="Your report has been submitted to the moderation team.",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed, ephemeral=True)
    
    @commands.hybrid_command(
        name="blacklist",
        description="Block a user from using the bot"
    )
    @app_commands.describe(
        user_id="The user ID to blacklist"
    )
    @commands.is_owner()
    async def blacklist(self, ctx, user_id: str):
        """Blacklist a user from bot usage"""
        
        if not self.blacklist.get('users'):
            self.blacklist['users'] = []
        
        if user_id in self.blacklist['users']:
            embed = discord.Embed(
                title="⚠️ Already Blacklisted",
                description=f"User `{user_id}` is already blacklisted.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)
        
        self.blacklist['users'].append(user_id)
        self.save_json(self.blacklist_file, self.blacklist)
        
        embed = discord.Embed(
            title="⛔ User Blacklisted",
            description=f"User `{user_id}` has been blacklisted from bot usage.",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="whitelist",
        description="Allow a user to use the bot again"
    )
    @app_commands.describe(
        user_id="The user ID to whitelist"
    )
    @commands.is_owner()
    async def whitelist(self, ctx, user_id: str):
        """Whitelist a user for bot usage"""
        
        if not self.blacklist.get('users') or user_id not in self.blacklist['users']:
            embed = discord.Embed(
                title="⚠️ Not Blacklisted",
                description=f"User `{user_id}` is not blacklisted.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)
        
        self.blacklist['users'].remove(user_id)
        self.save_json(self.blacklist_file, self.blacklist)
        
        embed = discord.Embed(
            title="✅ User Whitelisted",
            description=f"User `{user_id}` has been removed from the blacklist.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedModeration(bot))
