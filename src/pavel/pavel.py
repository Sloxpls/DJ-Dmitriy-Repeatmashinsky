from discord.ext import commands

class PavelCog(commands.cog):
    def __init__(self, bot):
        self.bot = bot
        self.pavel_mode = False

    @commands.command()
    async def activate_pavel(self, ctx):
        self.pavel_mode = True
        await ctx.send("Pavel online")

    @commands.command()
    async def disable_pavel(self, ctx):
        self.pavel_mode = False
        await ctx.send("Pavel offline")

    @commands.command()
    async def picture(self, ctx):
        if self.pavel_mode:
            # do something
        else:
            await ctx.send("Pavel is offline")

def setup(bot):
    bot.add_cog(PavelCog(bot))