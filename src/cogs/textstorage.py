import discord
from discord.ext import commands
import os

class TextstorageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "saved_text.txt"

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                file.write("")

    @commands.command(name="view_text",help="Usage:!view_text ")
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

    @commands.command(name="clear_text",help="Usage:!clear_text")
    async def clear_text(self, ctx):
        with open(self.file_path, "w") as file:
            file.write("")
        await ctx.send("Text file cleared.")

    @commands.command(name="bugfix",help="Usage:!bugfix <text>")
    async def bugfix(self, ctx, *, text: str):
        note = f"[BUGFIX] {text}"
        with open(self.file_path, "a") as file:
            file.write(f"{note}\n")
        await ctx.send("Bugfix note added.")

    @commands.command(name="feature",help="Usage:!feature <text>")
    async def feature(self, ctx, *, text: str):
        note = f"[FEATURE] {text}"
        with open(self.file_path, "a") as file:
            file.write(f"{note}\n")
        await ctx.send("Feature request added.")

