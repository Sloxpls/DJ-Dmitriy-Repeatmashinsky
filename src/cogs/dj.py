import discord
from discord.ext import commands
import yt_dlp
import os
import json
import asyncio
from errorcodecog import ErrorcodeCog



class DjCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repeat = False
        self.queue = []
        self.current_song = None
        self.playlists = self.load_playlists()

    def load_playlists(self):
        """Load playlists from a JSON file."""
        playlists = {}
        json_path = "./assets/playlists.json"

        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                playlists.update(json.load(f))
        return playlists

    async def play_next(self, ctx):
        """Play the next song in the queue."""
        if self.repeat and self.current_song:
            self.queue.insert(0, self.current_song)

        if not self.queue:
            self.current_song = None
            return

        self.current_song = self.queue.pop(0)
        song, song_type = self.current_song

        if song_type == 0:
            await self.play_song_from_file(ctx, song)
        elif song_type == 1:
            await self.play_song_from_url(ctx, song)

    @commands.command()
    async def play(self, ctx, *args):
        """Play a song or playlist."""
        if len(args) == 0:
            ErrorcodeCog.handle_value_error("No input provided. Provide a playlist name or YouTube URL.")
            return

        if not ctx.author.voice:
            ErrorcodeCog.handle_value_error("You are not in a voice channel.")
            return

        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            await channel.connect()

        if args[0] == "playlist":
            if len(args) < 2:
                ErrorcodeCog.handle_value_error("Playlist name not specified.")
                return

            playlist_name = args[1]
            if playlist_name not in self.playlists:
                ErrorcodeCog.handle_value_error(f"Playlist '{playlist_name}' not found.")
                return

            for song in self.playlists[playlist_name]:
                self.queue.append((song, 1))
        elif args[0].startswith("http"):
            self.queue.append((args[0], 1))
        else:
            ErrorcodeCog.handle_value_error("Invalid input. Use a YouTube URL or 'playlist <name>'.")

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    @commands.command()
    async def next(self, ctx):
        """Skip to the next song."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        await self.play_next(ctx)

    @commands.command()
    async def stop(self, ctx):
        """Stop playback and clear the queue."""
        if ctx.voice_client:
            ctx.voice_client.stop()
            self.queue.clear()
            self.current_song = None
        else:
            ErrorcodeCog.handle_value_error("Nothing is playing to stop.")

    @commands.command()
    async def leave(self, ctx):
        """Disconnect from the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queue.clear()
            self.current_song = None
        else:
            ErrorcodeCog.handle_value_error("Bot is not connected to any voice channel.")

    @commands.command()
    async def repeat(self, ctx):
        """Toggle repeat mode."""
        self.repeat = not self.repeat

    @commands.command()
    async def info(self, ctx, *args):
        """Show information about playlists or current queue."""
        if len(args) == 0:
            ErrorcodeCog.handle_value_error("Specify 'playlist' or 'queue'.")
            return

        if args[0] == "playlist":
            if not self.playlists:
                ErrorcodeCog.handle_value_error("No playlists available.")
                return
        elif args[0] == "queue":
            if not self.queue:
                ErrorcodeCog.handle_value_error("The queue is empty.")
                return
        else:
            ErrorcodeCog.handle_value_error("Invalid argument. Use 'playlist' or 'queue'.")

    async def play_song_from_file(self, ctx, file):
        """Play a song from a local file."""
        if not os.path.isfile(file):
            ErrorcodeCog.handle_value_error(f"File not found: {file}")
            return

        try:
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(file),
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop).result()
            )
            ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
            ctx.voice_client.source.volume = 0.5
        except Exception as e:
            ErrorcodeCog.handle_system_error(f"Error playing file: {e}")

    async def play_song_from_url(self, ctx, url):
        """Play a YouTube song."""
        ydl_opts = {"format": "bestaudio", "quiet": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info["url"]

            ffmpeg_options = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn"
            }

            ctx.voice_client.play(
                discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop).result()
            )
            ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
            ctx.voice_client.source.volume = 0.5
        except Exception as e:
            ErrorcodeCog.handle_system_error(f"Error fetching YouTube URL: {e}")
