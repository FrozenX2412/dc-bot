# bot.py
import logging
import traceback
from pathlib import Path
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
DEV_GUILD_ID = int(os.getenv("DEV_GUILD_ID", 0)) or None  # optional fast sync while developing

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=PREFIX, intents=intents, help_command=None)
        self.owner_id = OWNER_ID

    async def setup_hook(self):
        logger.info("Auto-loading cogs...")
        base = Path("cogs")
        if not base.exists():
            logger.warning("No cogs directory found at %s", base.resolve())

        # Load all python files under cogs (skip __init__.py)
        for py in base.rglob("*.py"):
            if py.name == "__init__.py":
                continue
            module = ".".join(py.with_suffix("").parts)  # e.g. cogs.fun.insult
            try:
                await self.load_extension(module)
                logger.info("✅ Loaded: %s", module)
            except Exception:
                logger.exception("❌ Failed to load %s", module)

        # Sync application commands (fast per-guild if DEV_GUILD_ID set)
        try:
            if DEV_GUILD_ID:
                guild = discord.Object(id=DEV_GUILD_ID)
                await self.tree.sync(guild=guild)
                logger.info("✅ Synced app commands to dev guild %s", DEV_GUILD_ID)
            else:
                await self.tree.sync()
                logger.info("✅ Synced global app commands")
        except Exception:
            logger.exception("❌ Slash command sync error")

    async def on_ready(self):
        logger.info("Bot is online as %s (ID: %s)", self.user, self.user.id)
        # Set presence to show prefix help
        try:
            await self.change_presence(activity=discord.Game(name=f"{PREFIX}help"))
        except Exception:
            logger.exception("Failed to set presence")

    async def on_command_error(self, ctx, error):
        # Common user-facing errors
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"❌ Missing permissions: {', '.join(error.missing_permissions)}")
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I lack required permissions to run that command.")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument. Check command usage.")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Bad argument. Check the types/IDs you provided.")
            return
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⌛ Command on cooldown. Try again in {round(error.retry_after, 1)}s.")
            return
        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ Only the bot owner can run that command.")
            return
        if isinstance(error, commands.CommandNotFound):
            return  # ignore unknown commands silently

        # Unexpected errors: log full traceback, send friendly message
        logger.exception("Unhandled command error in %s", getattr(ctx, "command", None))
        try:
            await ctx.send("⚠️ An internal error occurred. The owner has been notified.")
        except Exception:
            logger.exception("Failed to send error message to channel")

bot = DiscordBot()

if __name__ == "__main__":
    if not TOKEN:
        logger.critical("DISCORD_TOKEN missing in environment")
        raise SystemExit(1)
    bot.run(TOKEN)
