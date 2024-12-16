import discord
from discord.ext import commands



class BlackjackCog(commands.Cog):
    def __init__(self, bot, ):
        self.bot = bot


    def get_user_balance(self, user_id):
        user = self.db["blackjack"].find_one({"discord_id": user_id})
        if user:
            return user["balance"]

    @commands.command(name="balance")
    async def balance(self, ctx):
        balance = self.get_user_balance(ctx.author.id)
        await ctx.send(f"{ctx.author.mention}, your current balance is ${balance}.")
