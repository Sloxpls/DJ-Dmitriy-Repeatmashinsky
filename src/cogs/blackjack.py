import discord
from discord.ext import commands
from pymongo import MongoClient
import random


class DatabaseHelper:
    def __init__(self, collection):
        self.collection = collection

    def get_user_balance(self, discord_id: int) -> int:
        user = self.collection.find_one({"discord_id": str(discord_id)})
        if user:
            return int(user.get("balance", 0))
        else:
            initial_balance = 500
            self.collection.insert_one({"discord_id": str(discord_id), "balance": initial_balance})
            return initial_balance

    def update_user_balance(self, discord_id: int, new_balance: int):
        self.collection.update_one(
            {"discord_id": str(discord_id)},
            {"$set": {"balance": new_balance}},
            upsert=True
        )


class BlackjackGame:
    def __init__(self):
        self.cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def draw_card(self) -> str:
        return random.choice(self.cards)

    def calculate_score(self, hand: list[str]) -> int:
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
        score = sum(values[card] for card in hand)
        aces = hand.count('A')
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score


class BlackjackCog(commands.Cog):
    def __init__(self, bot, MONGO_URI):
        self.bot = bot
        self.client = MongoClient(MONGO_URI)
        self.db = self.client["discord"]
        self.collection = self.db["blackjack"]
        self.db_helper = DatabaseHelper(self.collection)
        self.game = BlackjackGame()

    @commands.command(name="balance")
    async def balance(self, ctx):
        balance = self.db_helper.get_user_balance(ctx.author.id)
        await ctx.send(f"{ctx.author.mention}, your current balance is ${balance}.")

    @commands.command(name="bet", help="If it's your firs time use !balance to receive 500 coins")
    async def blackjack(self, ctx, bet: int):
        balance = self.db_helper.get_user_balance(ctx.author.id)
        if bet > balance or bet <= 0:
            await ctx.send(f"{ctx.author.mention}, your bet must be positive and less than or equal to your balance.")
            return

        player_hand = [self.game.draw_card(), self.game.draw_card()]
        dealer_hand = [self.game.draw_card(), self.game.draw_card()]

        player_score = self.game.calculate_score(player_hand)
        dealer_score = self.game.calculate_score(dealer_hand)

        await ctx.send(f"{ctx.author.mention}, your hand: {player_hand} (Score: {player_score})")
        await ctx.send(f"Dealer's hand: [{dealer_hand[0]}, ?]")

        # Player turn
        while player_score < 21:
            await ctx.send("Type `hit` to draw another card or `stand` to hold.")
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.content.lower() in ["hit", "stand"]
            )

            if msg.content.lower() == "hit":
                new_card = self.game.draw_card()
                player_hand.append(new_card)
                player_score = self.game.calculate_score(player_hand)
                await ctx.send(f"You drew a {new_card}. Your hand: {player_hand} (Score: {player_score})")
                if player_score > 21:
                    await ctx.send(f"{ctx.author.mention}, you busted! Dealer wins.")
                    self.db_helper.update_user_balance(ctx.author.id, balance - bet)
                    return
            else:
                break

        await ctx.send(f"Dealer's hand: {dealer_hand} (Score: {dealer_score})")
        while dealer_score < 17:
            new_card = self.game.draw_card()
            dealer_hand.append(new_card)
            dealer_score = self.game.calculate_score(dealer_hand)
            await ctx.send(f"Dealer drew a {new_card}. Dealer's hand: {dealer_hand} (Score: {dealer_score})")

        if dealer_score > 21 or player_score > dealer_score:
            await ctx.send(f"{ctx.author.mention}, you win! {bet}")
            self.db_helper.update_user_balance(ctx.author.id, balance + bet)
        elif player_score < dealer_score:
            await ctx.send(f"{ctx.author.mention}, you lose. {bet}")
            self.db_helper.update_user_balance(ctx.author.id, balance - bet)
        else:
            await ctx.send(f"{ctx.author.mention}, it's a tie!")

