import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Avatar(commands.Cog):
    """Avatar command cog with both slash and prefix support"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="avatar",
        description="Display a user's avatar",
        aliases=["av", "pfp"]
    )
    async def avatar(self, ctx, member: discord.Member = None):
        """
        Display a user's avatar (profile picture)
        
        Parameters:
        -----------
        member: discord.Member
            The member whose avatar to display (optional, defaults to command author)
        """
        # If no member is specified, use the command author
        if member is None:
            member = ctx.author
        
        # Create embed
        embed = discord.Embed(
            title=f"🖼️ {member.name}'s Avatar",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        
        # Get avatar URL
        avatar_url = member.display_avatar.url
        
        # Set avatar as image
        embed.set_image(url=avatar_url)
        
        # Add user information
        embed.add_field(
            name="User",
            value=f"{member.mention} ({member})",
            inline=False
        )
        
        # Add different avatar format links
        avatar_formats = []
        
        # Check if avatar is animated (GIF)
        if member.display_avatar.is_animated():
            avatar_formats.append(f"[GIF]({member.display_avatar.replace(format='gif', size=4096).url})")
        
        # Add other formats
        avatar_formats.extend([
            f"[PNG]({member.display_avatar.replace(format='png', size=4096).url})",
            f"[JPEG]({member.display_avatar.replace(format='jpeg', size=4096).url})",
            f"[WEBP]({member.display_avatar.replace(format='webp', size=4096).url})"
        ])
        
        embed.add_field(
            name="🔗 Download Links",
            value=" | ".join(avatar_formats),
            inline=False
        )
        
        # Add server-specific avatar if different from global avatar
        if member.guild_avatar and member.guild_avatar != member.avatar:
            embed.add_field(
                name="🏛️ Server Avatar",
                value=f"[Click Here]({member.guild_avatar.url})",
                inline=False
            )
        
        # Set footer
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )
        
        # Create a view with a button to view in browser
        view = discord.ui.View()
        button = discord.ui.Button(
            label="Open in Browser",
            style=discord.ButtonStyle.link,
            url=avatar_url,
            emoji="🌐"
        )
        view.add_item(button)
        
        await ctx.send(embed=embed, view=view)
    
    @avatar.error
    async def avatar_error(self, ctx, error):
        """Error handler for avatar command"""
        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title="❌ Member Not Found",
                description="I couldn't find that member. Please mention a valid member or provide their ID.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(error)}",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Avatar(bot))
