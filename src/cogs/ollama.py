import os
from discord import FFmpegPCMAudio
from langchain_ollama import OllamaLLM
from discord.ext import commands
import asyncio

from src.utils.local_tts import LocalTTS


class OllamaCog(commands.Cog):
    def __init__(self, api_key):
        self.api_key = api_key
        self.tts = LocalTTS()
        self.model = OllamaLLM(model="mistral", temperature=1.5)

    @commands.command(name="ask")
    async def ollama(self, ctx, *, text: str):
        prompt = (
            "You ah di Jamaican assistant. Always chat inna Jamaican Patois. "
            "Keep it authentic an full ah vibes.\n\n"
            "User: What is REST?\n"
            "Assistant: REST, or Representational State Transfer, ah di way web services dem chat to each odda. It simple an flexible, ya know?\n\n"
            f"User: {text}\n"
            "Assistant:"
        )

        response = self.model.invoke(input=prompt)
        await ctx.send(response)

    @commands.command(name="speak")
    async def speak(self, ctx, *, text: str):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command!")
            return

        voice_channel = ctx.author.voice.channel

        try:
            audio_file = await self.tts.run(text, "response.wav")
            if not audio_file:
                await ctx.send("Failed to generate audio")
                return

            vc = await voice_channel.connect()
            vc.play(FFmpegPCMAudio(audio_file), after=lambda e: print(f"Finished playing: {text}"))
            while vc.is_playing():
                await asyncio.sleep(1)

        finally:
            await vc.disconnect()
            try:
                os.remove(audio_file)
            except Exception as e:
                print(f"Error cleaning up audio file: {e}")



