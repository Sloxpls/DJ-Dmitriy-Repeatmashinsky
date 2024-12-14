import os
import random

import discord
from discord import File, Status
import time

from discord.ext import commands


class PavelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pavel_mode = True
        self.last_time = 0
        self.last_status = 0
        self.status_map = {
            "online": {"attachment": "src/assets/pictures/status/peterlever.png", "name": "peterlever.png"},
            "idle": {"attachment": "src/assets/pictures/status/peteridle.png", "name": "peteridle.png"},
            "dnd": {"attachment": "src/assets/pictures/status/peterdnd.png", "name": "peterdnd.png"},
            "offline": {"attachment": "src/assets/pictures/status/peterdöd.png", "name": "peterdöd.png"},
        }

    def cooldown(self):
        if time.time() - self.last_time < 3:  # 3 seconds cooldown
            return True
        self.last_time = time.time()
        return False

    @commands.command(help="Activates Pavel mode. Pavel will respond to events and commands. Usage: !pavel Not done")
    async def pavel(self, ctx):
        self.pavel_mode = True
        await ctx.send("Pavel online")

    @commands.command(help="Deactivates Pavel mode. Pavel will no longer respond to commands or events. Usage: !disable_pavel")
    async def disable_pavel(self, ctx):
        self.pavel_mode = False
        await ctx.send("Pavel offline")

    @commands.command(aliases=["peter"], help="Sends a random picture from the 'random' folder when Pavel mode is active. Usage: !pictureAliases: !peter")
    async def picture(self, ctx):
        if self.pavel_mode:

            picture_folder = "./assets/pictures/random"

            if os.listdir(picture_folder):
                picture = random.choice(os.listdir(picture_folder))
                picture_path = os.path.join(picture_folder, picture)
                await ctx.send(file=File(picture_path))
            else:
                await ctx.send("picture folder empty")
        else:
            return

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == 271667378364874752:  # Peter id
            if before.channel is None and after.channel is not None:
                voice_channel_name = after.channel.name
                # Send message to the first listed text channel
                top_text_channel = member.guild.text_channels[0]
                if top_text_channel:
                    await top_text_channel.send(f"Satans vad det började lukta i {voice_channel_name} nu!")

    '''
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if self.cooldown():
            return  # Prevents spam

        if after.user.id != 271667378364874752:  # Peter's ID
            return

        status = 0
        if after.status == Status.dnd:
            status = 1
        elif after.status == Status.online:
            status = 2
        elif after.status == Status.idle:
            status = 3

        if status == self.last_status:
            return
        else:
            self.last_status = status

        if after.status.name in self.status_map:
            channel = after.guild.text_channels[0]  # Send to the topmost channel
            if channel:
                file_info = self.status_map[after.status.name]
                await channel.send(
                    f"Peter's status changed to {after.status.name}.",
                    file=discord.File(file_info["attachment"], filename=file_info["name"]),
                )

'''