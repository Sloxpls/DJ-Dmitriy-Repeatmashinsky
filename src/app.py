import importlib
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

cog_api_keys = {
    "eleven": ELEVEN_API_KEY,
    "steam": STEAM_API_KEY,
    "hello": ELEVEN_API_KEY
}

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Программирский"))
    print(f"Logged in as {bot.user}")

    cogs_dir = "./cogs"
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            module = importlib.import_module(f"src.cogs.{cog_name}")
            cog_class = getattr(module, f"{cog_name.capitalize()}Cog")

            # if cog requires api key
            if cog_name in cog_api_keys:
                cog = cog_class(bot, cog_api_keys[cog_name])
            else:
                cog = cog_class(bot)
            await bot.add_cog(cog)

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