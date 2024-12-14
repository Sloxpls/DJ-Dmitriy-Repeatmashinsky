from discord.ext import commands

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.info_text_general = """
**Available Cogs:**
- `anime`, `dj`, `eleven`, `hello`, `info`, `pavel`, `steam`, `stock, fishing, textstorage`

**Usage:**
- `!info [category]` to get specific help.  
Example: `!info dj`
"""

        self.info_text_anime = """
**Anime Commands:**
- `!jim` - Get a random anime quote.
"""

        self.info_text_dj = """
**Music Commands:**
- `!play [link]` - Play music from a YouTube link.
- `!play spellista[x]` - Play a playlist.
- `!stop` - Stop playing music.
- `!add spellista[x] [link]` - Add a link to a playlist.
- `!remove spellista[x]` - Remove a playlist.
- `!remove spellista[x] [link]` - Remove a link from a playlist.
- `!repeat` - Repeat the current song or playlist.
"""

        self.info_text_eleven = """
**Text-to-Speech Commands:**
- `!tts <text>` - Converts the given text to speech.
- Requires connection to a voice channel.
"""

        self.info_text_info = """
**Bot Information Commands:**
- Noting to se here
"""

        self.info_text_hello = """
**Text-to-Speech Commands:**
- Noting to se here.
"""


        self.info_text_pavel = """
**Pavel Commands:**
- `!pavel` - Activates Pavel mode.
- `!disable_pavel` - Deactivates Pavel mode.
- `!picture` / `!peter` - Sends a random picture.
"""

        self.info_text_steam = """
**Steam Commands:**
- `!steam_status <name/ID>` - Fetches the Steam status of a user.
- Displays user information, profile picture, and current status.
"""

        self.info_text_stock = """
**Stock Market Commands:**
- `!stock <ticker>` - Fetch general stock information.
- `!stock <ticker>.history <period> <interval>` - Fetch historical stock data.
- `!stockhelp` - View all stock-related commands.
"""

        self.info_text_textstorage = """
**Text Storage Commands:**
- `!save_text <text>` - Save provided text into a file (overwrites existing content).
- `!append_text <text>` - Append provided text to the file.
- `!view_text` - View the content of the file.
- `!clear_text` - Clear the content of the file.
- `!bugfix <text>` - Add a bugfix note with a `[BUGFIX]` tag.
- `!feature <text>` - Add a feature request with a `[FEATURE]` tag.
"""

    @commands.command(name="info")
    async def info(self, ctx, parameter: str = None):
        if not parameter:
            await ctx.send(self.info_text_general)
        elif parameter.lower() == "anime":
            await ctx.send(self.info_text_anime)
        elif parameter.lower() == "dj":
            await ctx.send(self.info_text_dj)
        elif parameter.lower() == "eleven":
            await ctx.send(self.info_text_eleven)
        elif parameter.lower() == "info":
            await ctx.send(self.info_text_info)
        elif parameter.lower() == "pavel":
            await ctx.send(self.info_text_pavel)
        elif parameter.lower() == "steam":
            await ctx.send(self.info_text_steam)
        elif parameter.lower() == "stock":
            await ctx.send(self.info_text_stock)
        elif parameter.lower() == "textstorage":
            await ctx.send(self.info_text_textstorage)

        else:
            await ctx.send(f"**Invalid category:** `{parameter}`\n\n{self.info_text_general}")
