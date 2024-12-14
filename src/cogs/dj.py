import discord
from discord.ext import commands
import yt_dlp
import os
import json
import asyncio


class DjCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repeat = False
        self.queue = []  # Kön för låtar
        self.current_song = None
        self.playlists = self.load_playlists()

    def load_playlists(self):
        """Ladda spellistor från JSON och mapp med MP3-filer."""
        playlists = {}

        # Ladda spellistor från JSON
        json_path = "./assets/playlists.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                playlists.update(json.load(f))

        # Lägg till MP3-spellistor
        mp3_path = "./assets/mp3"
        if os.path.exists(mp3_path):
            for folder in os.listdir(mp3_path):
                folder_path = os.path.join(mp3_path, folder)
                if os.path.isdir(folder_path):
                    mp3_files = [
                        os.path.join(folder_path, f)
                        for f in os.listdir(folder_path)
                        if f.endswith(".mp3")
                    ]
                    if mp3_files:
                        playlists[folder] = {"files": mp3_files}


        return playlists

    async def play_next(self, ctx):
        """Spela nästa låt i kön."""
        if not self.queue:
            self.current_song = None
            await ctx.send("Kön är tom. Lägg till fler låtar med `!play`.")
            return

        self.current_song = self.queue.pop(0)
        if os.path.isfile(self.current_song):  # MP3-fil
            await self.play_song_from_file(ctx, self.current_song)
        else:  # YouTube-länk
            await self.play_song_from_url(ctx, self.current_song)

    @commands.command()
    async def play(self, ctx, *args):
        """Spela musik från en länk eller spellista."""
        if len(args) == 0:
            await ctx.send("Felaktigt kommando. Ange en länk eller spellista.")
            return

        if args[0].lower() == "spellista":
            if len(args) < 2:
                await ctx.send("Ange namnet på en spellista, t.ex. `!play spellista Favoriter`.")
                return

            playlist_id = " ".join(args[1:])
            playlist = self.playlists.get(playlist_id)

            if not playlist:
                await ctx.send(f"Spellistan `{playlist_id}` finns inte.")
                return

            # Lägg till spellistans låtar i kön
            self.queue.extend(playlist.get("urls", []))
            self.queue.extend(playlist.get("files", []))
            await ctx.send(f"Lade till {len(playlist.get('urls', [])) + len(playlist.get('files', []))} låtar från spellistan `{playlist_id}` till kön.")

            # Anslut och spela om inget redan spelas
            if not ctx.voice_client:
                if not ctx.author.voice:
                    await ctx.send("Du måste vara i en röstkanal för att spela musik.")
                    return
                channel = ctx.author.voice.channel
                await channel.connect()

            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)
            return

        # Spela en enskild länk
        url = args[0]
        self.queue.append(url)
        await ctx.send(f"Lade till låten i kön: {url}")

        if not ctx.voice_client:
            if not ctx.author.voice:
                await ctx.send("Du måste vara i en röstkanal för att spela musik.")
                return
            channel = ctx.author.voice.channel
            await channel.connect()

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    @commands.command()
    async def byt(self, ctx):
        """Hoppa till nästa låt."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()  # Stoppa nuvarande låt
        await self.play_next(ctx)

    @commands.command()
    async def stop(self, ctx):
        """Stoppa musiken."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.queue.clear()
            self.current_song = None
            await ctx.send("Musiken har stoppats och kön har rensats.")
        else:
            await ctx.send("Det spelas ingen musik just nu.")

    @commands.command()
    async def leave(self, ctx):
        """Koppla bort boten från röstkanalen."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Boten har kopplats bort från röstkanalen.")
        else:
            await ctx.send("Boten är inte ansluten till en röstkanal.")

    @commands.command()
    async def repeat(self, ctx):
        """Aktivera/inaktivera repetera-läge."""
        self.repeat = not self.repeat
        status = "aktiverat" if self.repeat else "avstängt"
        await ctx.send(f"Repetera-läge är nu {status}.")

    @commands.command()
    async def info(self, ctx, playlist_id: str):
        """Visa info om en spellista."""
        playlist = self.playlists.get(playlist_id)
        if not playlist:
            await ctx.send(f"Spellistan `{playlist_id}` finns inte.")
            return

        urls = playlist.get("urls", [])
        files = playlist.get("files", [])
        response = f"**Spellista: {playlist_id}**\n"

        if urls:
            response += "YouTube-länkar:\n" + "\n".join(f"- {url}" for url in urls)
        if files:
            response += "Lokala MP3-filer:\n" + "\n".join(f"- {os.path.basename(f)}" for f in files)

        await ctx.send(response)

    @commands.command()
    async def spellistor(self, ctx):
        """Lista alla spellistor."""
        if not self.playlists:
            await ctx.send("Det finns inga tillgängliga spellistor.")
            return

        response = "**Tillgängliga spellistor:**\n"
        for name in self.playlists.keys():
            response += f"- {name}\n"

        await ctx.send(response)

    async def play_song_from_file(self, ctx, file):
        """Spela en MP3-fil."""
        if not ctx.voice_client:
            await ctx.send("Boten är inte ansluten till en röstkanal.")
            return

        # Ensure the file path is absolute
        file_path = os.path.abspath(file)
        if not os.path.isfile(file_path):
            await ctx.send(f"Filen hittades inte: {file}")
            return

        try:
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(file_path),
                after=lambda e: self.bot.loop.create_task(self.play_next(ctx))
            )
            ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
            ctx.voice_client.source.volume = 0.5
            await ctx.send(f"🎶 Spelar nu: **{os.path.basename(file_path)}**")
        except Exception as e:
            await ctx.send(f"Fel vid uppspelning av filen: {e}")

    async def play_song_from_url(self, ctx, url):
        """Spela en YouTube-länk."""
        ydl_opts = {'format': 'bestaudio', 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
        except Exception as e:
            await ctx.send(f"Fel vid hämtning av URL: {e}")
            return

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

        ctx.voice_client.play(
            discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
            after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop).result(),
        )
        ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
        ctx.voice_client.source.volume = 0.5
