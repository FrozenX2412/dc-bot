from __future__ import annotations
import asyncio
from typing import Optional, List
import discord
from discord import app_commands
from discord.ext import commands
import wavelink

# === Lavalink Connection ===
LAVALINK_URI = "lava-v4.ajieblogs.eu.org:443"
LAVALINK_PASSWORD = "https://dsc.gg/ajidevserver"
LAVALINK_SSL = True

# === Embed Color ===
GUILD_LOGO = 0x2b7fff


def make_embed(
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    color: int = GUILD_LOGO,
    user: Optional[discord.Member | discord.User] = None,
) -> discord.Embed:
    e = discord.Embed(title=title, description=description, color=color)
    e.timestamp = discord.utils.utcnow()
    if user is not None:
        e.set_footer(text=f"Requested by {user.display_name}", icon_url=user.display_avatar.url)
    return e


class Player(wavelink.Player):
    queue: asyncio.Queue[wavelink.Playable]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.queue = asyncio.Queue()
        self._volume = 50

    async def do_next(self) -> None:
        try:
            track = await asyncio.wait_for(self.queue.get(), timeout=0.1)
        except asyncio.TimeoutError:
            return
        await self.play(track)


class MusicView(discord.ui.View):
    def __init__(self, cog: "Music", *, timeout: float = 120):
        super().__init__(timeout=timeout)
        self.cog = cog

    async def _ensure(self, interaction: discord.Interaction) -> Optional[Player]:
        if not interaction.guild:
            await interaction.response.send_message(embed=make_embed(description="This must be used in a guild."), ephemeral=True)
            return None
        player = self.cog.get_player(interaction.guild)
        if player is None:
            await interaction.response.send_message(embed=make_embed(description="Nothing is playing."), ephemeral=True)
            return None
        return player

    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.blurple)
    async def pause_resume(self, interaction: discord.Interaction, _: discord.ui.Button):
        player = await self._ensure(interaction)
        if not player:
            return
        if player.paused:
            await player.resume()
            content = make_embed(description="Resumed ▶️", user=interaction.user)
        else:
            await player.pause()
            content = make_embed(description="Paused ⏸️", user=interaction.user)
        await interaction.response.edit_message(embed=content, view=self)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def skip(self, interaction: discord.Interaction, _: discord.ui.Button):
        player = await self._ensure(interaction)
        if not player:
            return
        await player.stop()
        await player.do_next()
        await interaction.response.edit_message(embed=make_embed(description="Skipped ⏭️", user=interaction.user), view=self)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, _: discord.ui.Button):
        player = await self._ensure(interaction)
        if not player:
            return
        player.queue = asyncio.Queue()
        await player.stop()
        await interaction.response.edit_message(embed=make_embed(description="Stopped ⏹️", user=interaction.user), view=None)


class Music(commands.Cog):
    """Music commands powered by Lavalink via Wavelink."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._node_ready = asyncio.Event()
        wavelink.Player = Player  # use our subclass
        bot.loop.create_task(self._connect_nodes())

    def get_player(self, guild: discord.Guild) -> Optional[Player]:
        return guild.voice_client  # type: ignore

    async def cog_unload(self) -> None:
        for node in wavelink.NodePool.nodes.values():
            await node.disconnect()

    async def _connect_nodes(self) -> None:
        await self.bot.wait_until_ready()
        try:
            if not wavelink.NodePool.nodes:
                await wavelink.NodePool.connect(
                    client=self.bot,
                    host=LAVALINK_URI.split(":")[0],
                    port=int(LAVALINK_URI.split(":")[1]),
                    password=LAVALINK_PASSWORD,
                    https=LAVALINK_SSL,
                )
            self._node_ready.set()
            print(f"✅ Connected to Lavalink: {LAVALINK_URI}")
        except Exception as e:
            print(f"❌ Failed to connect Lavalink: {e}")

    async def ensure_voice(self, ctx: commands.Context | discord.Interaction, *, connect: bool = True) -> Optional[Player]:
        guild = ctx.guild
        assert guild is not None
        player: Optional[Player] = self.get_player(guild)
        if player is None and connect:
            author = ctx.author if isinstance(ctx, commands.Context) else ctx.user  # type: ignore
            if not isinstance(author, discord.Member) or not author.voice or not author.voice.channel:
                embed = make_embed(description="You are not in a voice channel.")
                if isinstance(ctx, commands.Context):
                    await ctx.reply(embed=embed)
                else:
                    await ctx.response.send_message(embed=embed, ephemeral=True)
                return None
            channel = author.voice.channel
            player = await channel.connect(cls=Player)  # type: ignore[arg-type]
        return player

    async def search_track(self, query: str) -> Optional[wavelink.Playable]:
        try:
            if query.startswith("http://") or query.startswith("https://"):
                return await wavelink.Playable.search(query).first()
            return await wavelink.Playable.search(f"ytsearch:{query}").first()
        except Exception as e:
            print(f"Track search failed: {e}")
            return None

    async def start_playback(self, ctx: commands.Context | discord.Interaction, track: wavelink.Playable, *, user: discord.abc.User) -> None:
        assert ctx.guild
        player = await self.ensure_voice(ctx)
        if not player:
            return
        if not player.is_playing():
            await player.play(track)
        else:
            await player.queue.put(track)  # type: ignore[arg-type]
        e = make_embed(title="Queued", description=f"[{track.title}]({track.uri})", user=user)
        view = MusicView(self)
        if isinstance(ctx, commands.Context):
            await ctx.reply(embed=e, view=view)
        else:
            if ctx.response.is_done():
                await ctx.followup.send(embed=e, view=view)
            else:
                await ctx.response.send_message(embed=e, view=view)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: Optional[Player] = payload.player  # type: ignore
        if player and player.guild and not player.is_playing():
            await player.do_next()

    @commands.hybrid_command(name="play", description="Play a song by name or URL")
    @app_commands.describe(query="Song name or YouTube URL")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        await self._node_ready.wait()
        track = await self.search_track(query)
        if not track:
            await ctx.reply(embed=make_embed(description="No results found."))
            return
        await self.start_playback(ctx, track, user=ctx.author)

    @commands.hybrid_command(name="pause", description="Pause the player")
    async def pause(self, ctx: commands.Context) -> None:
        player = await self.ensure_voice(ctx, connect=False)
        if player:
            await player.pause()
            await ctx.reply(embed=make_embed(description="Paused ⏸️", user=ctx.author))

    @commands.hybrid_command(name="resume", description="Resume the player")
    async def resume(self, ctx: commands.Context) -> None:
        player = await self.ensure_voice(ctx, connect=False)
        if player:
            await player.resume()
            await ctx.reply(embed=make_embed(description="Resumed ▶️", user=ctx.author))

    @commands.hybrid_command(name="stop", description="Stop and clear the queue")
    async def stop(self, ctx: commands.Context) -> None:
        player = await self.ensure_voice(ctx, connect=False)
        if player:
            player.queue = asyncio.Queue()
            await player.stop()
            await ctx.reply(embed=make_embed(description="Stopped ⏹️", user=ctx.author))

    @commands.hybrid_command(name="skip", description="Skip the current track")
    async def skip(self, ctx: commands.Context) -> None:
        player = await self.ensure_voice(ctx, connect=False)
        if player:
            await player.stop()
            await ctx.reply(embed=make_embed(description="Skipped ⏭️", user=ctx.author))

    @commands.hybrid_command(name="volume", description="Set the player volume (1-100)")
    @app_commands.describe(value="Volume from 1 to 100")
    async def volume(self, ctx: commands.Context, value: int) -> None:
        player = await self.ensure_voice(ctx, connect=False)
        if player:
            value = max(1, min(100, value))
            await player.set_volume(value)
            await ctx.reply(embed=make_embed(description=f"Volume set to {value}% 🔊", user=ctx.author))

    @commands.hybrid_command(name="queue", description="Show the current queue")
    async def queue_cmd(self, ctx: commands.Context) -> None:
        player = await self.ensure_voice(ctx, connect=False)
        if not player:
            return
        items: List[str] = []
        if player.current:
            items.append(f"Now: [{player.current.title}]({player.current.uri})")
        if not player.queue.empty():
            q = list(player.queue._queue)  # type: ignore
            for i, t in enumerate(q[:10], start=1):
                items.append(f"{i}. [{t.title}]({t.uri})")
        if not items:
            items = ["Queue is empty."]
        await ctx.reply(embed=make_embed(title="Queue", description="\n".join(items), user=ctx.author))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
