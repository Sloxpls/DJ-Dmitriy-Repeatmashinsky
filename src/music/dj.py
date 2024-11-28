import os
import discord
from discord.ext import commands
import yt_dlp
import asyncio


class DJ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repeat = False

    @commands.command()
    async def repeat(self):
        self.repeat = True

    @commands.command()
    async def play(self, ctx, url: str):
        await self.play_song_from_url(ctx, url)

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("I'm not playing any song.")

    @commands.command()
    async def spellista(self, ctx, list_num: str):

        playlist_dir = os.path.join('../assets/mp3', list_num)

        if list_num not in self.bot.playlists:
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

    async def play_song_from_url(self, ctx, url):
        while self.repeat:
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
                'before_options': '-reconnect Djungeltrubaduren -reconnect_streamed Djungeltrubaduren -reconnect_delay_max 5',
                'options': '-vn',
            }
            try:
                voice_client.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))
                voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
                voice_client.source.volume = 0.5
            except Exception as e:
                await ctx.send(f"An error occurred while playing the audio: {str(e)}")
                return

    async def play_song_from_soundfile(self, ctx, file):
        while self.repeat:
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