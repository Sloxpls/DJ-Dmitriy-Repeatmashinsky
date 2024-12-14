from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.info_text = """
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
        
        **Stock:**
        !stockhelp help with stock commands.
        
        **pavel:**
        
        **Anime:**
        !jim sends a random anime quote
        """


    @commands.command(name="info")
    async def info(self, ctx):
        await ctx.send(self.info_text)