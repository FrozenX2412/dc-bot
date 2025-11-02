import discord
from discord.ext import commands
from discord import app_commands
import datetime

class UserInfo(commands.Cog):
    """User information commands (userinfo, id, joined) with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="userinfo",
        description="Display information about a user",
        aliases=["ui", "whois"]  # 👈 this already covers 'whois'
    )
    @app_commands.describe(
        member="The member to get information about (default: you)"
    )
    async def userinfo(self, ctx, member: discord.Member = None):
        """Display user information with creative embed styling"""
        
        member = member or ctx.author
        
        account_age = datetime.datetime.now() - member.created_at
        account_days = account_age.days
        
        if member.joined_at:
            join_age = datetime.datetime.now() - member.joined_at
            join_days = join_age.days
        else:
            join_days = "Unknown"
        
        embed = discord.Embed(
            title=f"👤 User Information",
            color=member.color if member.color != discord.Color.default() else discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="Name", value=f"{member.mention}\n`{member.name}`", inline=True)
        embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="Nickname", value=f"`{member.nick}`" if member.nick else "`None`", inline=True)
        
        embed.add_field(
            name="Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:F>\n({account_days} days ago)",
            inline=False
        )
        
        if member.joined_at:
            embed.add_field(
                name="Joined Server",
                value=f"<t:{int(member.joined_at.timestamp())}:F>\n({join_days} days ago)",
                inline=False
            )
        
        if len(member.roles) > 1:
            roles = [role.mention for role in reversed(member.roles) if role.name != "@everyone"][:10]
            roles_text = ", ".join(roles)
            if len(member.roles) > 11:
                roles_text += f" and {len(member.roles) - 11} more..."
            embed.add_field(
                name=f"Roles [{len(member.roles) - 1}]",
                value=roles_text,
                inline=False
            )
        
        status_emoji = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        embed.add_field(name="Status", value=status_emoji.get(member.status, "⚫ Unknown"), inline=True)
        embed.add_field(name="Bot Account", value="✅ Yes" if member.bot else "❌ No", inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="id",
        description="Get the ID of a user or the current server"
    )
    @app_commands.describe(member="The member to get the ID of (optional)")
    async def id_command(self, ctx, member: discord.Member = None):
        """Get user or server ID with creative embed styling"""
        
        embed = discord.Embed(
            title="🆔 ID Information",
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        if member:
            embed.add_field(name="User", value=f"{member.mention}\n`{member.name}`", inline=True)
            embed.add_field(name="User ID", value=f"`{member.id}`", inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
        else:
            embed.add_field(name="Server", value=f"`{ctx.guild.name}`", inline=True)
            embed.add_field(name="Server ID", value=f"`{ctx.guild.id}`", inline=True)
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="joined",
        description="Shows when a user joined the server"
    )
    @app_commands.describe(member="The member to check (default: you)")
    async def joined(self, ctx, member: discord.Member = None):
        """Show when a user joined with creative embed styling"""
        
        member = member or ctx.author
        
        if not member.joined_at:
            embed = discord.Embed(
                title="❌ Unknown",
                description="Unable to determine join date.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        join_age = datetime.datetime.now() - member.joined_at
        join_days = join_age.days
        
        embed = discord.Embed(
            title="🗓️ Member Join Date",
            color=member.color if member.color != discord.Color.default() else discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Member", value=f"{member.mention}\n`{member.name}`", inline=True)
        embed.add_field(name="Joined", value=f"<t:{int(member.joined_at.timestamp())}:F>", inline=False)
        embed.add_field(name="Time Since Join", value=f"`{join_days}` days ago", inline=True)
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))
