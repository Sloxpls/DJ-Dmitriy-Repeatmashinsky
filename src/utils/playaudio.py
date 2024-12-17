from discord import FFmpegPCMAudio
import asyncio
import os


async def play_audio_in_channel(self, ctx, audio_path, text):
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()
    try:
        vc.play(FFmpegPCMAudio(audio_path), after=lambda e: print(f"Finished playing: {text}"))
        while vc.is_playing():
            await asyncio.sleep(1)
    finally:
        await vc.disconnect()
        try:
            os.remove(audio_path)
        except Exception as e:
            print(f"Error cleaning up audio file: {e}")
