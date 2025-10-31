import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Clear(commands.Cog):
    """Message clearing/deletion commands with creative embed styling"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="clear",
        description="Delete a specified number of messages from the channel",
        aliases=["purge", "delete"]
    )
    @app_commands.describe(
        amount="Number of messages to delete (1-100)"
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Clear messages with creative embed styling"""
        
        if amount < 1:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please specify a number greater than 0.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            return await ctx.send(embed=embed, ephemeral=True, delete_after=5)
        
        if amount > 100:
            amount = 100
            embed = discord.Embed(
                title="⚠️ Amount Capped",
                description="Amount capped at 100 messages due to Discord limitations.",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, ephemeral=True, delete_after=3)
        
        # Delete the command message if it's a prefix command
        if ctx.interaction is None:
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit=amount)
        else:
            deleted = await ctx.channel.purge(limit=amount)
        
        # Send success embed with creative styling
        embed = discord.Embed(
            title="🧹 Messages Cleared",
            color=discord.Color.from_rgb(23, 162, 184),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🗑️ Deleted", value=f"`{len(deleted)}` message(s)", inline=True)
        embed.add_field(name="📍 Channel", value=ctx.channel.mention, inline=True)
        embed.add_field(name="⚖️ Moderator", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=False)
        embed.set_footer(text=f"Cleared in {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        msg = await ctx.send(embed=embed, ephemeral=True if ctx.interaction else False)
        if not ctx.interaction:
            await msg.delete(delay=5)

async def setup(bot):
    await bot.add_cog(Clear(bot))
