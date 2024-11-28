import yt_dlp
import discord
import os
import asyncio


async def play_song_from_soundfile(ctx, file, repeat):
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


async def play_song_from_url( ctx, url, repeat):
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