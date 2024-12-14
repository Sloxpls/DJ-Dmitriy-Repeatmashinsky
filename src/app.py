import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.cogs.anime import AnimeQuoteCog
from src.cogs.pavel import PavelCog
from src.cogs.stock import StockCog
from src.cogs.steam import SteamCog
from src.cogs.eleven import ElevenCog
from src.cogs.hello import HelloCog
from src.cogs.dj import DJ
from src.cogs.fishing import Fishing
load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Программирский"))
    print(f"Logged in as {bot.user}")

    await bot.add_cog(PavelCog(bot))
    await bot.add_cog(StockCog(bot))
    await bot.add_cog(SteamCog(bot, STEAM_API_KEY))
    await bot.add_cog(ElevenCog(bot, ELEVEN_API_KEY))
    await bot.add_cog(AnimeQuoteCog(bot))
    await bot.add_cog(HelloCog(bot, ELEVEN_API_KEY))
    await bot.add_cog(DJ(bot))
    await bot.add_cog(Fishing(bot))

@bot.command()
async def d(ctx):
    async for message in ctx.channel.history(limit=1000):
        if message.author == bot.user:
            try:
                await message.delete()
            except Exception as e:
                print(f"Failed to delete a message: {e}")


if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN not set in .env")
    bot.run(token)