import discord
from discord.ext import commands
import yt_dlp
import os
import json
import asyncio


class DJ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repeat = False
        self.playlists = self.load_playlists()  # Ladda spellistor från JSON och MP3-mappen
        self.queue = []  # Håll koll på vilka låtar som ska spelas
        self.current_song = None  # Den låt som spelas just nu

    def load_playlists(self):
        """Ladda spellistor från JSON och mapp med MP3-filer."""
        playlists = {}

        # Ladda spellistor från JSON
        json_path = "assets/playlist.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                playlists.update(json.load(f))

        # Lägg till MP3-spellistor
        mp3_path = r"C:\Users\adekl\Kodmust\Discordbot\DJ-Dmitriy-Repeatmashinsky\src\assets\mp3"
        if os.path.exists(mp3_path):
            print(f"Hittade mp3-mappen: {mp3_path}")
            for folder in os.listdir(mp3_path):
                folder_path = os.path.join(mp3_path, folder)
                print(f"Kontrollerar mappen: {folder_path}")
                if os.path.isdir(folder_path):
                    mp3_files = [
                        os.path.join(folder_path, f)
                        for f in os.listdir(folder_path)
                        if f.endswith(".mp3")
                    ]
                    if mp3_files:
                        playlists[folder] = {"files": mp3_files}
                        print(f"Lade till spellista: {folder} med filer: {mp3_files}")
                    else:
                        print(f"Inga MP3-filer hittades i mappen: {folder}")
        else:
            print(f"Mappen {mp3_path} hittades inte.")

        return playlists

    async def play_next_song(self, ctx):
        """Spela nästa låt i kön."""
        if not self.queue:
            await ctx.send("Kön är tom. Ingen låt att spela.")
            self.current_song = None
            return

        self.current_song = self.queue.pop(0)

        if os.path.isfile(self.current_song):  # Spela MP3-fil
            await self.play_song_from_file(ctx, self.current_song)
        else:  # Spela YouTube-länk
            await self.play_song_from_url(ctx, self.current_song)

    @commands.command()
    async def play(self, ctx, *args):
        """
        Spela musik från en YouTube-länk eller spellista.
        - `!play [länk]` för att spela musik från en YouTube-länk.
        - `!play spellista [namn]` för att spela upp en spellista.
        """
        if len(args) == 0:
            await ctx.send("Felaktigt kommando. Ange en länk eller spellista.")
            return

        if args[0].lower() == "spellista":
            if len(args) < 2:
                await ctx.send("Ange namnet på en spellista, t.ex. `!play spellista Djungeltrubaduren`.")
                return

            playlist_id = " ".join(args[1:])  # Kombinera argumenten efter "spellista" som spellistans namn
            playlist = self.playlists.get(playlist_id)

            if not playlist:
                await ctx.send(f"Spellistan {playlist_id} finns inte.")
                return

            if not ctx.voice_client:
                if not ctx.author.voice:
                    await ctx.send("Du måste vara i en röstkanal för att spela musik.")
                    return
                channel = ctx.author.voice.channel
                await channel.connect()

            # Lägg till spellistans låtar i kön
            self.queue.extend(playlist.get("urls", []))
            self.queue.extend(playlist.get("files", []))
            await ctx.send(f"Lade till {len(self.queue)} låtar från spellistan {playlist_id} i kön.")

            # Spela upp om ingen låt spelas
            if not ctx.voice_client.is_playing():
                await self.play_next_song(ctx)
            return

        # Om det är en länk, spela låten
        url = args[0]
        if not ctx.voice_client:
            if not ctx.author.voice:
                await ctx.send("Du måste vara i en röstkanal för att spela musik.")
                return
            channel = ctx.author.voice.channel
            await channel.connect()

        self.queue.append(url)
        await ctx.send(f"Lade till låten i kön: {url}")

        # Spela upp om ingen låt spelas
        if not ctx.voice_client.is_playing():
            await self.play_next_song(ctx)

    @commands.command()
    async def byt(self, ctx):
        """Hoppa till nästa låt."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()  # Stoppa nuvarande låt
        await self.play_next_song(ctx)

    async def play_song_from_file(self, ctx, file):
        """Spela en låt från en lokal MP3-fil."""
        voice_client = ctx.voice_client
        if not voice_client:
            await ctx.send("Boten är inte ansluten till en röstkanal.")
            return

        if not os.path.isfile(file):
            await ctx.send(f"Filen {file} finns inte.")
            return

        try:
            voice_client.play(discord.FFmpegPCMAudio(file), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.bot.loop).result())
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = 0.5
        except Exception as e:
            await ctx.send(f"Ett fel inträffade under uppspelningen av filen: {e}")

    async def play_song_from_url(self, ctx, url):
        """Spela en låt från en YouTube-länk."""
        ydl_opts = {'format': 'bestaudio', 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
        except Exception as e:
            await ctx.send(f"Misslyckades att hämta ljud från URL: {url}. Fel: {e}")
            return

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

        voice_client = ctx.voice_client
        if not voice_client:
            await ctx.send("Boten är inte ansluten till en röstkanal.")
            return

        try:
            voice_client.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.bot.loop).result())
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = 0.5
        except Exception as e:
            await ctx.send(f"Ett fel inträffade under uppspelningen: {e}")


async def setup(bot):
    await bot.add_cog(DJ(bot))
