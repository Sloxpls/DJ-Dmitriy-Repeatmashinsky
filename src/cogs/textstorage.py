import discord
from discord.ext import commands
import os

class TextStorage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "saved_text.txt"

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                file.write("")

    @commands.command(name="save_text")
    async def save_text(self, ctx, *, text: str):
        with open(self.file_path, "w") as file:
            file.write(text)
        await ctx.send("Text saved successfully.")

    @commands.command(name="append_text")
    async def append_text(self, ctx, *, text: str):
        with open(self.file_path, "a") as file:
            file.write(f"{text}\n")
        await ctx.send("Text appended successfully.")

    @commands.command(name="view_text")
    async def view_text(self, ctx):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                content = file.read()
            if content.strip():
                await ctx.send(f"Stored Text:\n```\n{content}\n```")
            else:
                await ctx.send("The file is empty.")
        else:
            await ctx.send("No text file found.")

    @commands.command(name="clear_text")
    async def clear_text(self, ctx):
        with open(self.file_path, "w") as file:
            file.write("")
        await ctx.send("Text file cleared.")

    @commands.command(name="bugfix")
    async def bugfix(self, ctx, *, text: str):
        note = f"[BUGFIX] {text}"
        with open(self.file_path, "a") as file:
            file.write(f"{note}\n")
        await ctx.send("Bugfix note added.")

    @commands.command(name="feature")
    async def feature(self, ctx, *, text: str):
        note = f"[FEATURE] {text}"
        with open(self.file_path, "a") as file:
            file.write(f"{note}\n")
        await ctx.send("Feature request added.")

async def setup(bot):
    await bot.add_cog(TextStorage(bot))