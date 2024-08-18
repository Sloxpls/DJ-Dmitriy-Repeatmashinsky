import os
import json
import discord
from discord.ext import commands
import yt_dlp
import asyncio
from dotenv import load_dotenv

# Load environment variables from ..env file if it exists
load_dotenv()

class MyClient:
    def __init__(self):
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.bot = commands.Bot(command_prefix="!", intents=self.intents)

        # Load playlists from JSON file
        with open('playlists.json', 'r') as f:
            self.playlists = json.load(f)

        @self.bot.event
        async def on_ready():
            print(f'Logged in as {self.bot.user.name}')

        @self.bot.command()
        async def join(ctx):
            if not ctx.author.voice:
                await ctx.send("You need to be in a voice channel to use this command.")
                return
            channel = ctx.author.voice.channel
            await channel.connect()

        @self.bot.command()
        async def leave(ctx):
            if ctx.voice_client:
                await ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("I'm not in a voice channel.")

        @self.bot.command()
        async def play(ctx, url: str):
            await self.play_song_from_url(ctx, url)

        @self.bot.command()
        async def stop(ctx):
            voice_client = ctx.guild.voice_client
            if voice_client and voice_client.is_playing():
                voice_client.stop()
            else:
                await ctx.send("I'm not playing any song.")

        @self.bot.command()
        async def spellista(ctx, list_num: str):
            playlist_dir = os.path.join('mp3', list_num)

            if list_num not in self.playlists:
                await ctx.send(f"Spellistan {list_num} finns inte.")
                return

            if not ctx.author.voice:
                await ctx.send("You need to be in a voice channel to use this command.")
                return

            if not ctx.voice_client:
                channel = ctx.author.voice.channel
                await channel.connect()

            mp3_files = [os.path.join(playlist_dir, f) for f in os.listdir(playlist_dir) if f.endswith('.mp3')]
            if not mp3_files:
                await ctx.send(f"Inga MP3-filer hittades i spellistan {list_num}.")
                return

            for file in mp3_files:
                await self.play_song_from_soundfile(ctx, file)
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)

        @self.bot.command()
        async def info(ctx, list_num: str):
            playlist_info = self.playlists.get(list_num, {}).get("info", f"Spellistan {list_num} finns inte.")
            await ctx.send(f"Spellista {list_num}: {playlist_info}")

    async def play_song_from_url(self, ctx, url):
        voice_client = ctx.guild.voice_client
        ydl_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'extractaudio': True,
        }

        retries = 3
        while retries > 0:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    audio_url = info['url']
                    title = info['title']
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    await ctx.send(f"Failed to retrieve audio from URL after multiple attempts.")
                    return

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

        try:
            voice_client.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = 0.5
        except Exception as e:
            await ctx.send(f"An error occurred while playing the audio: {str(e)}")

    async def play_song_from_soundfile(self, ctx, file):
        voice_client = ctx.guild.voice_client

        if not voice_client:
            await ctx.send("Boten är inte ansluten till någon röstkanal.")
            return

        if os.path.isfile(file):
            try:
                voice_client.play(discord.FFmpegPCMAudio(file, executable='ffmpeg'))
                voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
                voice_client.source.volume = 0.5

                while voice_client.is_playing():
                    await asyncio.sleep(1)
                await asyncio.sleep(1)

            except Exception as e:
                await ctx.send(f"An error occurred while playing the file: {str(e)}")
        else:
            await ctx.send(f"Filen {file} finns inte.")

# Retrieve the token from the environment variable
token = os.getenv("DISCORD_BOT_TOKEN")

# Check if the token is loaded correctly
if not token:
    raise ValueError("No DISCORD_BOT_TOKEN found in the environment variables. Make sure the ..env file is set correctly.")

Discord_Bot = MyClient()
Discord_Bot.bot.run(token)
