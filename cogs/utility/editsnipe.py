import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from typing import Optional

class EditSnipe(commands.Cog):
    """Track and display recently edited messages across guilds.
    
    This cog captures message edit events and allows users to view
    the before/after content of recently edited messages in a channel.
    Supports hybrid commands (prefix + slash) with multi-guild functionality.
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Store edited messages: {guild_id: {channel_id: [(before, after, author, timestamp)]}}
        self.edit_snipes = {}
        self.max_snipes_per_channel = 10
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Listener to capture message edits.
        
        Args:
            before: The message before editing
            after: The message after editing
        """
        # Ignore bot messages and messages without content changes
        if before.author.bot or before.content == after.content:
            return
        
        guild_id = before.guild.id if before.guild else 0
        channel_id = before.channel.id
        
        # Initialize storage for this guild if needed
        if guild_id not in self.edit_snipes:
            self.edit_snipes[guild_id] = {}
        
        # Initialize storage for this channel if needed
        if channel_id not in self.edit_snipes[guild_id]:
            self.edit_snipes[guild_id][channel_id] = []
        
        # Store the edit (before, after, author, timestamp)
        edit_data = (before.content, after.content, before.author, datetime.now(timezone.utc))
        self.edit_snipes[guild_id][channel_id].insert(0, edit_data)
        
        # Keep only the most recent edits
        if len(self.edit_snipes[guild_id][channel_id]) > self.max_snipes_per_channel:
            self.edit_snipes[guild_id][channel_id].pop()
    
    @commands.hybrid_command(name="editsnipe", aliases=["es", "esnipe"])
    @app_commands.describe(index="The position of the edit to retrieve (1 = most recent)")
    async def editsnipe(self, ctx: commands.Context, index: Optional[int] = 1):
        """Display recently edited messages in the current channel.
        
        Args:
            ctx: The command context
            index: Which edit to show (1-10, default 1 for most recent)
        """
        # Validate index range
        if index < 1 or index > self.max_snipes_per_channel:
            embed = discord.Embed(
                title="❌ Invalid Index",
                description=f"Please provide a number between 1 and {self.max_snipes_per_channel}.",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        guild_id = ctx.guild.id if ctx.guild else 0
        channel_id = ctx.channel.id
        
        # Check if we have any edits for this channel
        if (guild_id not in self.edit_snipes or 
            channel_id not in self.edit_snipes[guild_id] or 
            not self.edit_snipes[guild_id][channel_id]):
            embed = discord.Embed(
                title="🔍 No Edits Found",
                description="No recently edited messages in this channel.",
                color=discord.Color.orange(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Check if the requested index exists
        edits = self.edit_snipes[guild_id][channel_id]
        if index > len(edits):
            embed = discord.Embed(
                title="❌ Index Out of Range",
                description=f"Only {len(edits)} edit(s) available in this channel.",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Get the requested edit (convert to 0-based index)
        before_content, after_content, author, timestamp = edits[index - 1]
        
        # Create master embed design
        embed = discord.Embed(
            title="📝 Edit Sniped",
            description=f"Message edited by {author.mention} in {ctx.channel.mention}",
            color=discord.Color.blue(),
            timestamp=timestamp
        )
        
        # Add before content
        before_text = before_content[:1024] if before_content else "*Empty message*"
        embed.add_field(
            name="📤 Before",
            value=before_text,
            inline=False
        )
        
        # Add after content
        after_text = after_content[:1024] if after_content else "*Empty message*"
        embed.add_field(
            name="📥 After",
            value=after_text,
            inline=False
        )
        
        # Add metadata
        embed.add_field(
            name="👤 Author",
            value=f"{author.mention} (`{author.id}`)",
            inline=True
        )
        embed.add_field(
            name="📊 Edit Number",
            value=f"{index}/{len(edits)}",
            inline=True
        )
        
        # Set author and footer
        embed.set_author(name=str(author), icon_url=author.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Load the EditSnipe cog."""
    await bot.add_cog(EditSnipe(bot))
