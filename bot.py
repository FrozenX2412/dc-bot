import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True


class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        print("🔍 Auto-loading all cogs...")

        # Load all cogs automatically
        for root, dirs, files in os.walk("./cogs"):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    ext = os.path.join(root, file).replace("/", ".").replace("\\", ".").replace(".py", "")

                    try:
                        await self.load_extension(ext)
                        print(f"✅ Loaded: {ext}")
                    except Exception as e:
                        print(f"❌ Failed to load {ext}: {e}")

        # Sync slash commands
        try:
            await self.tree.sync()
            print("✅ Slash commands synced!")
        except Exception as e:
            print(f"❌ Slash command sync error: {e}")

    async def on_ready(self):
        print(f"✅ Bot is online as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_command_error(self, ctx, error):
        """Better error messages"""

        if isinstance(error, commands.MissingPermissions):
            missing = ", ".join(error.missing_permissions)
            await ctx.send(f"❌ Missing permissions: `{missing}`")
            return

        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ Only the bot owner can do that.")
            return

        if isinstance(error, commands.CommandNotFound):
            return  # ignore

        await ctx.send(f"⚠️ Error: `{error}`")


bot = DiscordBot()

if __name__ == "__main__":
    if TOKEN is None:
        print("❌ ERROR: DISCORD_TOKEN missing in .env")
    else:
        bot.run(TOKEN)
