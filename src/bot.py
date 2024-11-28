import os
import json
from discord.ext import commands
from dotenv import load_dotenv
from src.music.dj_commands import DJ

load_dotenv()


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=commands.Intents.all())
        self.playlists_file = '../assets/playlists.json'
        self.playlists = self.load_playlists()
        self.add_cog(DJ(self))

    def load_playlists(self):
        if os.path.exists(self.playlists_file):
            with open(self.playlists_file, 'r') as f:
                return json.load(f)
        else:
            with open(self.playlists_file, 'w') as f:
                json.dump({}, f)
            return {}

    def save_playlists(self):
        with open(self.playlists_file, 'w') as f:
            json.dump(self.playlists, f, indent=4)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    @commands.command()
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command.")
            return
        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("I'm not in a voice channel.")
    @commands.command()
    async def info(self, ctx):
        commands_info = """
                    **General Commands:**
                    !info - Show all commands.
                    !join - Join the voice channel.
                    !leave - Leave the voice channel.
                    
                    **Music Commands:**
                    !play [link] - Play music from a YouTube link.
                    !play spellista[x] - Play a playlist.
                    !stop - Stop playing music.
                    !add spellista[x] [link] - Add a link to a playlist.
                    !remove spellista[x] - Remove a playlist.
                    !remove spellista[x] [link] - Remove a link from a playlist.
                    !repeat - Repeat current song or playlist.
                    """
        await ctx.send(commands_info)




if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN not set in .env")
    MyBot().run(token)
