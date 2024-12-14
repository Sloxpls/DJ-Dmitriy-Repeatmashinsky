import yfinance as yf
from discord.ext import commands


class StockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="stock",
        help="Fetch stock information or historical data. Usage: !stock <ticker> [attribute]. For more details, use !stockhelp."
    )
    async def fetch_stock_info(self, ctx, ticker: str, period: str = None, interval: str = None):
        try:
            # early exit if no ticker is provided
            if not ticker:
                await ctx.send("Please provide a ticker symbol.")
                return

            # check if specific information is requested and parse it for api call
            if "." in ticker:
                ticker_symbol, attribute = ticker.split(".", 1)
            else:
                ticker_symbol = ticker
                attribute = None

            ticker = yf.Ticker(ticker_symbol)

            if attribute is None:
                # General information if no attribute is provided
                info = ticker.info
                if info:
                    summary = f"**{ticker_symbol} Summary**:\n"
                    summary += f"Name: {info.get('shortName', 'N/A')}\n"
                    summary += f"Sector: {info.get('sector', 'N/A')}\n"
                    summary += f"Industry: {info.get('industry', 'N/A')}\n"
                    summary += f"Market Cap: {info.get('marketCap', 'N/A')}\n"
                    summary += f"Previous Close: {info.get('previousClose', 'N/A')}\n"
                    await ctx.send(summary)
                else:
                    await ctx.send(
                        f"Could not fetch information for ticker {ticker_symbol}. Please check the symbol.")

            elif attribute == "history":
                if period and interval:
                    history = ticker.history(period=period, interval=interval)
                    if history is not None:
                        await ctx.send(f"{ticker_symbol} Historical Data:\n{history}")
                    else:
                        await ctx.send(f"Could not fetch historical data for ticker {ticker_symbol}.")
                else:
                    await ctx.send("Please provide a period and interval for historical data.")

            else:
                # Handle attributes without additional options
                attr = getattr(ticker, attribute, None)
                if attr:
                    data = attr() if callable(attr) else attr
                    await ctx.send(f"**{ticker_symbol}.{attribute}**:\n{data}")
                else:
                    await ctx.send(f"'{attribute}' is not a valid command.")

        except Exception as e:
            print('exception:', e)
            await ctx.send(f"An error occurred")

    @commands.command(
        name="stockhelp",
        help="Displays detailed instructions for the stock commands."
    )
    async def stock_help(self, ctx):
        help_message = """
        **Stock Commands:**
        `!stock <ticker>` - Fetches general information about a stock.
        `!stock <ticker>.history <period> <interval>` - Fetches historical data for a stock.
        `!stock <TICKER>.<method>`):\n
        `dividends`: Historical dividend data.\n
        `splits`: Historical stock splits.\n
        `actions`: Dividends and splits combined.\n
        `sustainability`: ESG scores and sustainability metrics.\n
        `recommendations`: Analyst recommendations.\n
        `calendar`: Upcoming events (like earnings dates).\n
        `earnings`: Annual earnings data.\n
        `quarterly_earnings`: Quarterly earnings data.\n
        `financials`: Annual financial statements.\n
        `quarterly_financials`: Quarterly financial statements.\n
        `balance_sheet`: Annual balance sheet data.\n
        `quarterly_balance_sheet`: Quarterly balance sheet data.\n
        `cashflow`: Annual cash flow data.\n
        `quarterly_cashflow`: Quarterly cash flow data.\n
        `major_holders`: Major shareholders.\n
        `institutional_holders`: Institutional shareholders.\n
        `isin`: International Securities Identification Number.\n
        `short_interest`: Short interest data.\n
        """
        await ctx.send(help_message)
