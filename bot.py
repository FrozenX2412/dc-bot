import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX', '!')  # Default prefix is '!'

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class DiscordBot(commands.Bot):
    """Custom Discord Bot class"""
    
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None  # We'll create a custom help command
        )
    
    async def setup_hook(self):
        """
        This is called when the bot is starting up.
        Load all cogs here.
        """
        print("Loading cogs...")
        
        # List of cog files to load
        cogs = [
            'cogs.ban',
            'cogs.unban',
            'cogs.kick',
            'cogs.mute',
            'cogs.unmute',
            'cogs.serverinfo',
            'cogs.avatar',
            'cogs.utility'
        ]
        
        # Load each cog
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✓ Loaded {cog}")
            except Exception as e:
                print(f"✗ Failed to load {cog}: {e}")
        
        # Sync slash commands with Discord
        print("Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            print(f"✓ Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"✗ Failed to sync commands: {e}")
    
    async def on_ready(self):
        """
        Called when the bot is ready and connected to Discord
        """
        print(f"\n{'='*50}")
        print(f"Bot is ready!")
        print(f"Logged in as: {self.user.name} (ID: {self.user.id})")
        print(f"Connected to {len(self.guilds)} guild(s)")
        print(f"Prefix: {PREFIX}")
        print(f"Discord.py version: {discord.__version__}")
        print(f"{'='*50}\n")
        
        # Set bot presence/status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {PREFIX}help"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
    
    async def on_guild_join(self, guild):
        """
        Called when the bot joins a new guild
        """
        print(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Update presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {PREFIX}help"
        )
        await self.change_presence(activity=activity)
    
    async def on_guild_remove(self, guild):
        """
        Called when the bot is removed from a guild
        """
        print(f"Left guild: {guild.name} (ID: {guild.id})")
        
        # Update presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {PREFIX}help"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """
        Global error handler for commands
        """
        # Ignore these errors
        ignored_errors = (commands.CommandNotFound,)
        
        if isinstance(error, ignored_errors):
            return
        
        # Handle specific errors
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Argument",
                description=f"Missing required argument: `{error.param.name}`\n\nUsage: `{PREFIX}{ctx.command.usage}`" if ctx.command.usage else f"Missing required argument: `{error.param.name}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
        
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Invalid Argument",
                description=f"{str(error)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
        
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, ephemeral=True)
        
        else:
            # Log unexpected errors
            print(f"Unhandled error in {ctx.command}: {error}")
            embed = discord.Embed(
                title="❌ An Error Occurred",
                description="An unexpected error occurred while executing this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)

async def main():
    """
    Main function to run the bot
    """
    # Check if token is set
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in .env file!")
        print("Please create a .env file with your bot token.")
        return
    
    # Create and run the bot
    bot = DiscordBot()
    
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        print("\nBot shutting down...")
        await bot.close()
    except Exception as e:
        print(f"Error: {e}")
        await bot.close()

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
