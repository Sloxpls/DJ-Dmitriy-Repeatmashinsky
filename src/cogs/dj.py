import discord
from discord.ext import commands
import yt_dlp
import os
import json
import asyncio
from src.cogs.errorcode import ErrorcodeCog

class DjCog(commands.Cog):
    def __init__(self, bot):
        self.playlists = None
        self.bot = bot
        self.repeat = False
        self.queue = []
        self.current_song = None
        self.json_path = "./assets/playlists.json"
        self.load_playlists()

    def load_playlists(self):
        """Load playlists from the JSON file."""
        try:
            with open(self.json_path, "r", encoding="utf-16") as f:
                self.playlists = json.load(f)
                if not isinstance(self.playlists, dict):
                    raise ValueError("JSON file does not contain a valid dictionary.")
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            self.playlists = {}

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

    @commands.command(help="Usage 1: !play <url> 2: !play playlist <name> ")
    async def play(self, ctx, *args):
        """Play a song or playlist."""
        if not args:
            ErrorcodeCog.add_error("No input provided. Provide a playlist name or YouTube URL.")
            return

        if not ctx.author.voice:
            print("User is not in a voice channel.")
            return

        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            await channel.connect()

        if args[0] == "playlist":
            if len(args) < 2:
                print("Playlist name not specified.")
                return

            playlist_name = args[1]

            if playlist_name not in self.playlists:
                ErrorcodeCog.add_error(f"Playlist '{playlist_name}' not found.")
                return

            playlist_data = self.playlists[playlist_name]

            if isinstance(playlist_data, dict) and "path" in playlist_data:
                path = playlist_data["path"]
                if os.path.isdir(path):
                    for file in os.listdir(path):
                        if file.endswith(".mp3"):
                            self.queue.append((os.path.join(path, file), 0))
                else:
                    ErrorcodeCog.add_error(f"Directory '{path}' not found.")
                    return

            elif isinstance(playlist_data, list):
                for song in playlist_data:
                    self.queue.append((song, 1))
            else:
                ErrorcodeCog.add_error(f"Invalid format for playlist '{playlist_name}'.")
                return

            print(f"Added playlist '{playlist_name}' to the queue.")

        elif args[0].startswith("http"):
            self.queue.append((args[0], 1))
            print("Added YouTube URL to the queue.")

        else:
            ErrorcodeCog.add_error("Invalid input. Use a YouTube URL or 'playlist <name>'.")
            return

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    @commands.command(help="Usage: !next, skips to next song ")
    async def next(self, ctx):
        """Skip to the next song."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        await self.play_next(ctx)

    @commands.command(help="Usage: !stop, stop playback ")
    async def stop(self, ctx):
        """Stop playback and clear the queue."""
        if ctx.voice_client:
            ctx.voice_client.stop()
            self.queue.clear()
            self.current_song = None
        else:
            pass
            ErrorcodeCog.add_error("Nothing is playing to stop.")

    @commands.command(help="Usage: !leave, leaves voice",)
    async def leave(self, ctx):
        """Disconnect from the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queue.clear()
            self.current_song = None
        else:
            pass
            ErrorcodeCog.add_error("Bot is not connected to any voice channel.")

    @commands.command(help="Usage: !repeat, toggle for repeat songs")
    async def repeat(self, ctx):
        """Toggle repeat mode."""
        self.repeat = not self.repeat

    @commands.command(help="Usage: !info <playlist or queue>")
    async def info(self, ctx, *args):
        """Show information about playlists or the current queue."""
        if not args:
            await ctx.send("Error: Specify 'playlist' or 'queue'.")
            return

        option = args[0].lower()

        if option == "playlist":
            if not self.playlists:
                await ctx.send("No playlists available.")
                return
            await ctx.send(f"Available playlists: {self.playlists}")
        elif option == "queue":
            if not self.queue:
                await ctx.send("The queue is currently empty.")
                return
            await ctx.send(f"Current queue: {self.queue}")
        else:
            ErrorcodeCog.add_error("Invalid argument. Use 'playlist' or 'queue'.")

    def save_playlists(self):
        """Save playlists to the JSON file."""
        with open(self.json_path, "w", encoding="utf-16") as f:
            json.dump(self.playlists, f, indent=4)

    @commands.command(name="playlist", help="!playlist 'add <name> <path/link>' or 'rm <name>'")
    async def playlist_funk(self, ctx, *args):
        """Manage playlists: add or remove."""
        if not args:
            await ctx.send("No argument provided. Use 'add <name> <path/link>' or 'rm <name>'.")
            return

        command = args[0].lower()

        if command == "add":
            if len(args) < 3:
                await ctx.send("Usage: `playlist add <name> <path/link>`")
                return

            playlist_name = args[1]
            playlist_path = args[2]

            if playlist_name not in self.playlists:
                self.playlists[playlist_name] = []

            if playlist_path.startswith("http"):
                self.playlists[playlist_name].append(playlist_path)
                self.save_playlists()
                await ctx.send(f"Playlist '{playlist_name}' has been updated with a new link.")

            elif os.path.exists(playlist_path):
                self.playlists[playlist_name] = {"path": os.path.abspath(playlist_path)}
                self.save_playlists()
                await ctx.send(f"Playlist '{playlist_name}' has been added with a local path.")
            else:
                await ctx.send(f"Invalid path or link: '{playlist_path}'. Path does not exist.")

        elif command == "rm":
            if len(args) < 2:
                await ctx.send("Usage: `playlist rm <name>`")
                return

            playlist_name = args[1]
            if playlist_name in self.playlists:
                del self.playlists[playlist_name]
                self.save_playlists()
                await ctx.send(f"Playlist '{playlist_name}' has been removed.")
            else:
                await ctx.send(f"Playlist '{playlist_name}' not found.")

        # Unknown command
        else:
            await ctx.send("Unknown command. Use `add` to add a playlist or `rm` to remove one.")

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
            pass
            ErrorcodeCog.add_error(f"Error playing file: {e}")

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
            pass
            ErrorcodeCog.add_error(f"Error fetching YouTube URL: {e}")