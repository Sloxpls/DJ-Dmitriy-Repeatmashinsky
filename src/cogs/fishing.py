import discord
from discord.ext import commands, tasks
import asyncio

class FishingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alone_users = {}
        self.check_alone_users.start()

    def cog_unload(self):
        self.check_alone_users.cancel()

    @tasks.loop(minutes=5)
    async def check_alone_users(self):
        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                members = vc.members
                if len(members) == 1:
                    user = members[0]
                    if user.id not in self.alone_users:
                        self.alone_users[user.id] = asyncio.get_event_loop().time()
                    else:
                        elapsed_time = asyncio.get_event_loop().time() - self.alone_users[user.id]
                        if elapsed_time >= 1800:
                            text_channel = discord.utils.get(guild.text_channels, name="majsmannen")
                            if text_channel:
                                await text_channel.send(f"**{user.display_name}** har fiskt ensam i {vc.name} i 30 minuter utan napp!")
                            self.alone_users.pop(user.id)
                else:
                    for member in members:
                        if member.id in self.alone_users:
                            self.alone_users.pop(member.id)

    @check_alone_users.before_loop
    async def before_check_alone_users(self):
        await self.bot.wait_until_ready()

