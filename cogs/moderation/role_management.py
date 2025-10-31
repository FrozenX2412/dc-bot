import discord
from discord.ext import commands
from discord import app_commands
import datetime

class RoleManagement(commands.Cog):
    """Role management commands (roleadd, roleremove, roleinfo) with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="roleadd",
        description="Add a role to a user"
    )
    @app_commands.describe(
        member="The member to add the role to",
        role="The role to add"
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def roleadd(self, ctx, member: discord.Member, role: discord.Role):
        """Add a role to a member with creative embed styling"""
        
        # Check role hierarchy
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Role Addition Failed",
                description=f"You cannot add {role.mention} as it's higher than or equal to your highest role.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        if role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Role Addition Failed",
                description=f"I cannot add {role.mention} as it's higher than or equal to my highest role.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        if role in member.roles:
            embed = discord.Embed(
                title="⚠️ Role Already Assigned",
                description=f"{member.mention} already has the {role.mention} role.",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        await member.add_roles(role)
        
        embed = discord.Embed(
            title="✅ Role Added",
            color=discord.Color.from_rgb(40, 167, 69),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Member", value=f"{member.mention}\n`{member}`", inline=True)
        embed.add_field(name="🏷️ Role", value=f"{role.mention}\n`{role.name}`", inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Role management in {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="roleremove",
        description="Remove a role from a user"
    )
    @app_commands.describe(
        member="The member to remove the role from",
        role="The role to remove"
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def roleremove(self, ctx, member: discord.Member, role: discord.Role):
        """Remove a role from a member with creative embed styling"""
        
        # Check role hierarchy
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Role Removal Failed",
                description=f"You cannot remove {role.mention} as it's higher than or equal to your highest role.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        if role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Role Removal Failed",
                description=f"I cannot remove {role.mention} as it's higher than or equal to my highest role.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        if role not in member.roles:
            embed = discord.Embed(
                title="⚠️ Role Not Found",
                description=f"{member.mention} doesn't have the {role.mention} role.",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True)
        
        await member.remove_roles(role)
        
        embed = discord.Embed(
            title="➖ Role Removed",
            color=discord.Color.from_rgb(220, 53, 69),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Member", value=f"{member.mention}\n`{member}`", inline=True)
        embed.add_field(name="🏷️ Role", value=f"{role.mention}\n`{role.name}`", inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Role management in {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="roleinfo",
        description="Display information about a role"
    )
    @app_commands.describe(
        role="The role to get information about"
    )
    async def roleinfo(self, ctx, role: discord.Role):
        """Display role information with creative embed styling"""
        
        embed = discord.Embed(
            title=f"🏷️ Role Information",
            color=role.color if role.color != discord.Color.default() else discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Name", value=f"{role.mention}\n`{role.name}`", inline=True)
        embed.add_field(name="ID", value=f"`{role.id}`", inline=True)
        embed.add_field(name="Color", value=f"`{str(role.color)}`", inline=True)
        
        embed.add_field(name="Position", value=f"`{role.position}`", inline=True)
        embed.add_field(name="Members", value=f"`{len(role.members)}`", inline=True)
        embed.add_field(name="Mentionable", value="✅ Yes" if role.mentionable else "❌ No", inline=True)
        
        embed.add_field(name="Hoisted", value="✅ Yes" if role.hoist else "❌ No", inline=True)
        embed.add_field(name="Managed", value="✅ Yes" if role.managed else "❌ No", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(role.created_at.timestamp())}:R>", inline=True)
        
        # Key permissions
        key_perms = []
        if role.permissions.administrator:
            key_perms.append("Administrator")
        if role.permissions.manage_guild:
            key_perms.append("Manage Server")
        if role.permissions.manage_channels:
            key_perms.append("Manage Channels")
        if role.permissions.manage_roles:
            key_perms.append("Manage Roles")
        if role.permissions.kick_members:
            key_perms.append("Kick Members")
        if role.permissions.ban_members:
            key_perms.append("Ban Members")
        
        if key_perms:
            embed.add_field(name="Key Permissions", value=", ".join(key_perms), inline=False)
        
        embed.set_footer(text=f"Role info from {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
