import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ Reload EVERYTHING: cogs + env + tree
    @app_commands.command(name="reload", description="Reload all cogs + .env (Owner only)")
    async def reload_all(self, interaction: discord.Interaction):
        owner_id = int(os.getenv("OWNER_ID", 0))
        if interaction.user.id != owner_id:
            return await interaction.response.send_message("❌ Only bot owner can use this.", ephemeral=True)

        await interaction.response.send_message("🔄 Reloading bot...", ephemeral=True)

        # Reload .env
        load_dotenv()
        print("✅ Reloaded .env variables")

        # Reload all cogs
        for root, dirs, files in os.walk("./cogs"):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    ext = os.path.join(root, file).replace("/", ".").replace("\\", ".").replace(".py", "")
                    try:
                        await self.bot.unload_extension(ext)
                        await self.bot.load_extension(ext)
                        print(f"♻️ Reloaded: {ext}")
                    except Exception as e:
                        print(f"❌ Failed to reload {ext}: {e}")

        # Re-sync slash commands
        await self.bot.tree.sync()
        print("✅ Slash commands synced after reload!")

        await interaction.followup.send("✅ Bot fully reloaded!", ephemeral=True)

    # ✅ Reload ONE specific cog
    @app_commands.command(name="reloadcog", description="Reload one cog by name (Owner only)")
    @app_commands.describe(name="Example: cogs.moderation.ban")
    async def reload_cog(self, interaction: discord.Interaction, name: str):
        owner_id = int(os.getenv("OWNER_ID", 0))
        if interaction.user.id != owner_id:
            return await interaction.response.send_message("❌ Only bot owner can use this.", ephemeral=True)

        await interaction.response.send_message(f"🔄 Reloading `{name}`...", ephemeral=True)

        try:
            await self.bot.unload_extension(name)
            await self.bot.load_extension(name)
            await self.bot.tree.sync()
            await interaction.followup.send(f"✅ Reloaded `{name}`!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed: `{e}`", ephemeral=True)

    # ✅ Shutdown command
    @app_commands.command(name="shutdown", description="Turn off the bot (Owner only)")
    async def shutdown(self, interaction: discord.Interaction):
        owner_id = int(os.getenv("OWNER_ID", 0))
        if interaction.user.id != owner_id:
            return await interaction.response.send_message("❌ Only bot owner can use this.", ephemeral=True)

        await interaction.response.send_message("🛑 Shutting down...", ephemeral=True)
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Reload(bot))
