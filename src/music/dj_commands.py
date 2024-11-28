import os
from discord.ext import commands
import asyncio
from dj_funk import play_song_from_soundfile, play_song_from_url


class DJ(commands.Cog):
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

        await play_song_from_url(ctx, url, self.repeat)

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
                await play_song_from_soundfile(ctx, file, self.repeat)
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)
        else:
            urls = playlist.get("urls", [])
            if not urls:
                await ctx.send("No URLs available in this playlist.")
                return

            for url in urls:
                await play_song_from_url(ctx, url, self.repeat)
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)