from discord.ext import commands


class ErrorcodeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_code_list = []

    @classmethod
    def add_error(cls, message):
        """Add an error message to the error code list."""
        if len(cls.error_code_list) >= 10:
            cls.error_code_list.pop()
        cls.error_code_list.insert(0, message)

    @classmethod
    def handle_value_error(cls, error_mes):
        """Handle ValueErrors and add them to the error code list."""
        cls.add_error(error_mes)
        try:
            raise ValueError(error_mes)
        except ValueError as e:
            print(f"Caught an exception: {e}")

    @commands.command(name="error", help="Displays the last 10 error codes.")
    async def error_code(self, ctx):
        """Command to display the last 10 errors."""
        if not self.error_code_list:
            await ctx.send("No errors have been recorded.")
        else:
            formatted_errors = "\n".join(f"{idx + 1}. {err}" for idx, err in enumerate(self.error_code_list))
            await ctx.send(f"**Last 10 Error Codes:**\n{formatted_errors}")

