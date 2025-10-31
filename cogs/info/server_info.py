import discord
from discord.ext import commands
from discord import app_commands
import datetime

class ServerInfo(commands.Cog):
    """Server information commands with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="membercount",
        description="Shows member count of the server"
    )
    async def membercount(self, ctx):
        """Display server member count with creative styling"""
        
        total_members = ctx.guild.member_count
        bots = len([m for m in ctx.guild.members if m.bot])
        humans = total_members - bots
        
        embed = discord.Embed(
            title="👥 Member Count",
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Total Members", value=f"`{total_members}`", inline=True)
        embed.add_field(name="👤 Humans", value=f"`{humans}`", inline=True)
        embed.add_field(name="🤖 Bots", value=f"`{bots}`", inline=True)
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="roles",
        description="Lists all server roles"
    )
    async def roles(self, ctx):
        """Display all server roles with creative styling"""
        
        roles = [role.mention for role in reversed(ctx.guild.roles) if role.name != "@everyone"]
        
        if not roles:
            roles_text = "No roles available"
        else:
            roles_text = ", ".join(roles[:25])  # Show first 25
            if len(ctx.guild.roles) > 26:
                roles_text += f"\n\n*and {len(ctx.guild.roles) - 26} more...*"
        
        embed = discord.Embed(
            title=f"🏷️ Server Roles",
            description=roles_text,
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_footer(text=f"Total Roles: {len(ctx.guild.roles) - 1} | {ctx.guild.name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="channelinfo",
        description="Information about a specific channel"
    )
    @app_commands.describe(
        channel="The channel to get information about"
    )
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        """Display channel information with creative styling"""
        
        channel = channel or ctx.channel
        
        embed = discord.Embed(
            title="💬 Channel Information",
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Name", value=f"{channel.mention}\n`{channel.name}`", inline=True)
        embed.add_field(name="ID", value=f"`{channel.id}`", inline=True)
        embed.add_field(name="Category", value=f"`{channel.category.name if channel.category else 'None'}`", inline=True)
        
        embed.add_field(name="Topic", value=channel.topic or "*No topic set*", inline=False)
        
        embed.add_field(name="Created", value=f"<t:{int(channel.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name="NSFW", value="✅ Yes" if channel.is_nsfw() else "❌ No", inline=True)
        
        embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="emoji",
        description="Shows server emojis",
        aliases=["emojis"]
    )
    async def emoji(self, ctx):
        """Display server emojis with creative styling"""
        
        if not ctx.guild.emojis:
            embed = discord.Embed(
                title="😭 No Emojis",
                description="This server has no custom emojis.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)
        
        emoji_list = [str(emoji) for emoji in ctx.guild.emojis[:25]]  # Show first 25
        emoji_text = " ".join(emoji_list)
        
        embed = discord.Embed(
            title=f"😀 Server Emojis",
            description=emoji_text,
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        if len(ctx.guild.emojis) > 25:
            embed.set_footer(text=f"Showing 25/{len(ctx.guild.emojis)} emojis | {ctx.guild.name}")
        else:
            embed.set_footer(text=f"{len(ctx.guild.emojis)} emojis | {ctx.guild.name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="emotes",
        description="Lists custom server emotes (alias for emoji)"
    )
    async def emotes(self, ctx):
        """Alias for emoji command"""
        await self.emoji(ctx)
    
    @commands.hybrid_command(
        name="servericon",
        description="Displays server icon"
    )
    async def servericon(self, ctx):
        """Display server icon with creative styling"""
        
        if not ctx.guild.icon:
            embed = discord.Embed(
                title="❌ No Icon",
                description="This server doesn't have an icon.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"🖼️ {ctx.guild.name} Icon",
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        embed.set_image(url=ctx.guild.icon.url)
        embed.add_field(name="Download", value=f"[PNG]({ctx.guild.icon.url}) | [WEBP]({ctx.guild.icon.with_format('webp').url})")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="boostcount",
        description="Shows number of server boosters"
    )
    async def boostcount(self, ctx):
        """Display server boost information with creative styling"""
        
        embed = discord.Embed(
            title="🚀 Server Boosts",
            color=discord.Color.from_rgb(245, 127, 186),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Boost Level", value=f"`{ctx.guild.premium_tier}`", inline=True)
        embed.add_field(name="Boost Count", value=f"`{ctx.guild.premium_subscription_count or 0}`", inline=True)
        
        booster_count = len(ctx.guild.premium_subscribers)
        embed.add_field(name="Boosters", value=f"`{booster_count}`", inline=True)
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="servercreated",
        description="Shows when the server was created"
    )
    async def servercreated(self, ctx):
        """Display server creation date with creative styling"""
        
        created_timestamp = int(ctx.guild.created_at.timestamp())
        age = datetime.datetime.now() - ctx.guild.created_at
        age_days = age.days
        
        embed = discord.Embed(
            title="🎂 Server Birthday",
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Server", value=f"`{ctx.guild.name}`", inline=False)
        embed.add_field(name="Created", value=f"<t:{created_timestamp}:F>", inline=False)
        embed.add_field(name="Age", value=f"`{age_days}` days old", inline=True)
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"Server ID: {ctx.guild.id}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="invite",
        description="Generates bot invite link"
    )
    async def invite(self, ctx):
        """Generate bot invite link with creative styling"""
        
        permissions = discord.Permissions(
            ban_members=True,
            kick_members=True,
            moderate_members=True,
            manage_roles=True,
            manage_channels=True,
            manage_messages=True,
            read_messages=True,
            send_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True
        )
        
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=permissions,
            scopes=["bot", "applications.commands"]
        )
        
        embed = discord.Embed(
            title="🔗 Invite Me!",
            description=f"Click the link below to invite me to your server!",
            color=discord.Color.from_rgb(99, 102, 241),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Invite Link", value=f"[Click Here]({invite_url})", inline=False)
        embed.add_field(name="Features", value="✅ Moderation\n✅ Information\n✅ Slash Commands\n✅ Prefix Commands", inline=False)
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
