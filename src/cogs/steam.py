import discord
from discord.ext import commands
import aiohttp


class SteamCog(commands.Cog):
    def __init__(self, bot, api_key):
        self.bot = bot
        self.api_key = api_key
        self.name_to_id = {
            "Rasmus": "76561198080866836",
            "Hugå": "76561198124067897",
            "Peter": "76561198173652857"
        }

    @commands.command(name="steam_status")
    async def get_steam_status(self, ctx, name_or_id: str):

        steam_id = self.name_to_id.get(name_or_id, name_or_id)

        async with aiohttp.ClientSession() as session:
            url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={self.api_key}&steamids={steam_id}"
            async with session.get(url) as response:
                if response.status != 200:
                    await ctx.send("Failed to fetch data from Steam API.")
                    return

                data = await response.json()
                if "response" in data and "players" in data["response"] and len(data["response"]["players"]) > 0:
                    player = data["response"]["players"][0]

                    status_map = {
                        0: "Offline",
                        1: "Online",
                        2: "Busy",
                        3: "Away",
                        4: "Snooze",
                        5: "Looking to trade",
                        6: "Looking to play"
                    }
                    status = status_map.get(player["personastate"], "Unknown")

                    embed = discord.Embed(title=player["personaname"], url=player["profileurl"],
                                          description="Steam Online Status")
                    embed.set_thumbnail(url=player["avatarfull"])
                    embed.add_field(name="Status", value=status, inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Could not find a Steam profile with that ID.")
