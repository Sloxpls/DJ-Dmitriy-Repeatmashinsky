import discord
from discord.ext import commands
import asyncio
import aiohttp
import os
from discord import FFmpegPCMAudio
import random

class HelloCog(commands.Cog):
    def __init__(self, bot, api_key):
        self.bot = bot
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        self.voice_id = "g5CIjZEefAph4nQFvHAz"
        self.peter_id =  271667378364874752  # Peter's ID

        self.general_greetings = [
            "Åh... {name}, {name}... OOOOOOh..."
            #"Åh, {name}… precis vad vi behövde, ännu en självgod tjomme.",
            #"{name}, du kom i tid för att se hur det ser ut när alla andra suckar högt.",
            #"Se på fan, {name} har krupit fram ur sin digitala grotta!",
            #"{name}, försök att inte sänka IQ:n i rummet direkt när du joinar.",
            #"{name}, nu när du är här kan vi sänka standarden lite till.",
            #"Tja {name}, tur att vi inte hade något viktigt för oss.",
           # "Välkommen, {name}. Trevligt att se att latmaskar kan hitta hit också!"
        ]

        self.peter_greeting = "Saataaans vad det började lukta svart nu när {name} joinade. Huur faan ståår vii uut?"

    async def fetch_tts_audio(self, text: str) -> str:
        url = f"{self.base_url}/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    err_text = await response.text()
                    raise Exception(f"Failed to fetch TTS audio: {response.status} - {err_text}")

                audio_path = "temp_audio.mp3"
                with open(audio_path, "wb") as f:
                    f.write(await response.read())
                return audio_path

    async def slow_down_audio(self, input_path: str, output_path: str, atempo: float = 0.75):
        # Skapa ett ffmpeg-kommando för att sakta ner ljudet
        command = [
            'ffmpeg', '-y',    # '-y' skriver över filen om den finns
            '-i', input_path,
            '-filter:a', f"atempo={atempo}",
            output_path
        ]

        process = await asyncio.create_subprocess_exec(*command,
                                                       stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            print("FFmpeg process failed:", stderr.decode())
            raise Exception("Failed to slow down audio")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Kolla om användaren precis gick med i en röstkanal
        if before.channel is None and after.channel is not None:
            # Vänta
            await asyncio.sleep(1)


            if member.id == self.peter_id:
                greeting_text = self.peter_greeting.format(name=member.display_name)
            else:
                greeting_text = random.choice(self.general_greetings).format(name=member.display_name)


            print(f"Spelar upp hälsning: {greeting_text}")

            #anslut till samma voice channel som användaren
            try:
                voice_channel = after.channel
                vc = await voice_channel.connect()
            except Exception as e:
                print(f"Kunde inte ansluta till röstkanalen: {e}")
                return

            temp_audio_path = None
            slowed_audio_path = "slowed_audio.mp3"
            try:
                # Hämta TTS-ljudfil
                temp_audio_path = await self.fetch_tts_audio(greeting_text)

                # Sänk uppspelningshastigheten med ffmpeg
                await self.slow_down_audio(temp_audio_path, slowed_audio_path, atempo=0.8)

                # Spela upp det sänkta ljudet
                vc.play(FFmpegPCMAudio(slowed_audio_path), after=lambda e: print(f"Spelade klart hälsning för {member.display_name}."))

                while vc.is_playing():
                    await asyncio.sleep(1)
            finally:
                # Koppla från
                await vc.disconnect()
                if temp_audio_path and os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                if os.path.exists(slowed_audio_path):
                    os.remove(slowed_audio_path)
