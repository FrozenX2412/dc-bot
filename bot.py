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
            'cogs.moderation.ban',
            'cogs.moderation.unban',
            'cogs.moderation.kick',
            'cogs.moderation.mute',
            'cogs.moderation.unmute',
            'cogs.moderation.clear',
            'cogs.moderation.warn',
            'cogs.moderation.serverinfo',
            'cogs.moderation.avatar',
            'cogs.moderation.utility',
            'cogs.moderation.role_management',
            'cogs.moderation.channel_management',
            'cogs.moderation.advanced_moderation'
        ]
        
        # Load each cog
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✓ Loaded {cog}")
            except Exception as e:
                print(f"✗ Failed to load {cog}: {e}")

    async def on_ready(self):
        """Called when the bot is ready"""
        print(f'Bot is ready! Logged in as {self.user.name}')
        print(f'Bot ID: {self.user.id}')
        print('------')

# Create bot instance
bot = DiscordBot()

# Run the bot
if __name__ == "__main__":
    if TOKEN is None:
        print("Error: DISCORD_TOKEN not found in .env file")
    else:
        bot.run(TOKEN)
