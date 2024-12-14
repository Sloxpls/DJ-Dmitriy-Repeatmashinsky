from discord.ext import commands
import yt_dlp
import discord
import os
import asyncio


class DjCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repeat = False

    @commands.command()
    async def repeat(self, ctx):
        self.repeat = not self.repeat

    @commands.command()
    async def play(self, ctx, url: str):
        if not ctx.voice_client:
            if not ctx.author.voice:
                await ctx.send("You need to be in a voice channel to use this command.")
                return
            channel = ctx.author.voice.channel
            await channel.connect()

        await self.play_song_from_url(ctx, url, self.repeat)

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            self.repeat = False
        else:
            await ctx.send("I'm not playing any song.")

    @commands.command()
    async def spellista(self, ctx, playlist_id: str):
        playlist = self.bot.playlists.get(playlist_id)

        if not playlist:
            await ctx.send(f"Playlist {playlist_id} does not exist.")
            return
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command.")
            return
        if not ctx.voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()

        path = playlist.get("path")
        if path and os.path.exists(path):
            mp3_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.mp3')]
            if not mp3_files:
                await ctx.send(f"No MP3 files found in the playlist at {path}.")
                return

            for file in mp3_files:
                await self.play_song_from_soundfile(ctx, file, self.repeat)
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)
        else:
            urls = playlist.get("urls", [])
            if not urls:
                await ctx.send("No URLs available in this playlist.")
                return

            for url in urls:
                await self.play_song_from_url(ctx, url, self.repeat)
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)

    async def play_song_from_soundfile(self,ctx, file, repeat):
        while repeat:
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
                    return
            else:
                await ctx.send(f"Filen {file} finns inte.")
                return

    async def play_song_from_url(self,ctx, url, repeat):
        while repeat:
            ydl_opts = {
                'format': 'bestaudio',
                'quiet': True,
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    audio_url = info['url']
            except Exception as e:
                await ctx.send(f"Failed to retrieve audio from URL: {url}. Error: {e}")
                return

            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }

            voice_client = ctx.guild.voice_client
            if not voice_client:
                await ctx.send("Bot is not connected to a voice channel.")
                return

            try:
                voice_client.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))
                voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
                voice_client.source.volume = 0.5

                while voice_client.is_playing():
                    await asyncio.sleep(1)
            except Exception as e:
                await ctx.send(f"An error occurred during playback: {e}")

        async def play_song_from_soundfile(self, ctx, file):
            voice_client = ctx.guild.voice_client

            if not voice_client:
                await ctx.send("Bot is not connected to a voice channel.")
                return
            if not os.path.isfile(file):
                await ctx.send(f"File {file} does not exist.")
                return

            try:
                voice_client.play(discord.FFmpegPCMAudio(file))
                voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
                voice_client.source.volume = 0.5

                while voice_client.is_playing():
                    await asyncio.sleep(1)

            except Exception as e:
                await ctx.send(f"An error occurred while playing the file: {e}")
                return