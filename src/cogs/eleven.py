import aiohttp
import requests
import discord
from discord.ext import commands
import asyncio
from discord import FFmpegPCMAudio
import os


class ElevenCog(commands.Cog):
    def __init__(self, bot, api_key):
        self.bot = bot
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        self.voice_id = "g5CIjZEefAph4nQFvHAz"
        self.voice_map = {
            "default": "g5CIjZEefAph4nQFvHAz",
            "waman": "XrExE9yKIg1WjnnlVkGX",
            "man": "29vD33N1CtxCmqQRPOHJ"
        }

    async def fetch_tts_audio(self, text: str, voice_id: str) -> str:

        url = f"{self.base_url}/{voice_id}"
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
                    raise Exception(f"Failed to fetch TTS audio: {response.status} - {await response.text()}")

                # Save audio to a temporary file
                audio_path = "temp_audio.mp3"
                with open(audio_path, "wb") as f:
                    f.write(await response.read())
                return audio_path

    @commands.command(name="tts", help="Generate TTS audio and play it in a voice channel. Usage: !tts [voice] [text]")
    async def tts(self, ctx, voice: str = None, *, text: str):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command!")
            return

        voice_id = self.voice_map.get(voice, self.voice_id)

        voice_channel = ctx.author.voice.channel
        vc = await voice_channel.connect()

        try:
            audio_path = await self.fetch_tts_audio(text, voice_id)

            vc.play(FFmpegPCMAudio(audio_path), after=lambda e: print(f"Finished playing: {text}"))
            while vc.is_playing():
                await asyncio.sleep(1)

        finally:
            await vc.disconnect()
            try:
                os.remove(audio_path)  # Remove the temporary audio file
            except Exception as e:
                print(f"Error cleaning up audio file: {e}")

    @commands.command(name="p",help="Play a pre-recorded audio file. Usage: !p [filename]")
    async def play(self, ctx, file: str):
        voice_channel = ctx.author.voice.channel
        vc = await voice_channel.connect()
        try:
            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=f"./assets/mp3/sounds/{file}.mp3"), after=lambda e: print(f"Finished playing {file}"))
            while vc.is_playing():
                await asyncio.sleep(1)

        finally:
            await vc.disconnect()
