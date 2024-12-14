import discord
from discord.ext import commands
import aiohttp


class AnimeQuoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://animechan.io/api/v1/quotes/random"

    @commands.command(name="jim")
    async def anime_quote(self, ctx):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url) as response:
                    print(response)
                    if response.status == 200:
                        json_data = await response.json()

                        status = json_data.get("status", "failure")
                        if status != "success":
                            await ctx.send("Failed to fetch a quote. Please try again later.")
                            return

                        data = json_data.get("data", {})
                        content = data.get("content", "No quote available.")
                        anime = data.get("anime", {}).get("name", "Unknown Anime")
                        character = data.get("character", {}).get("name", "Unknown Character")

                        await ctx.send(f"**{character}** from *{anime}* says:\n\n\"{content}\"")
                    else:
                        await ctx.send(f"Failed to fetch a quote. API returned status: {response.status}")

        except Exception as e:
            await ctx.send(f"An error occurred while fetching the quote: {str(e)}")
            print(f"Error: {e}")