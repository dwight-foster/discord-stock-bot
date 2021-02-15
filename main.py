import discord
import logging
from discord.ext import commands
import requests
import json
from finvizfinance.quote import finvizfinance
import time


key = 'KEY'
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
description = "This is a stock bot. You can give it a ticker and an interval and it will give you the statistics for" \
              "that interval. "
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', description=description, intents=intents)
intervals_list = ["60min", "30min", "15min", "5min", "1min"]
bot.remove_command(name="help")
start = time.time()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(name="stock")
async def return_link(ctx, stock: str, interval: str = "5"):
    stock = stock.upper()
    interval = interval + "min"
    if interval not in intervals_list:
        await ctx.send("The interval you passed was invalid. Please choose a new one. \n Options are: 60, 30, 15, 5, 1")
    else:
        try:
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval={}&apikey={}'.format(
                stock, interval, key)
            response = requests.get(url)
            output = list(response.json()[f"Time Series ({interval})"].values())[0]
            open = list(output.values())[0]
            high = list(output.values())[1]
            low = list(output.values())[2]
            close = list(output.values())[3]
            volume = list(output.values())[4]
            await ctx.send(f"This the data for the newest {interval} interval \nOpen: ${open} "
                           f"\nHigh: ${high} \nLow: ${low} \nClose: ${close} \nVolume: {volume}")
        except:
            await ctx.send("Invalid stock. Try again.")


@bot.command(name="chart")
async def charts(ctx, stock=None):
    if not stock:
        await ctx.send("You need to pass a stock.")
    else:
        try:
            stock = finvizfinance(stock)
            await ctx.send(stock.TickerCharts(urlonly=True))
        except:
            await ctx.send("Invalid stock. Try again. ")


@bot.command(name="news")
async def news(ctx, stock=None):
    if not stock:
        await ctx.send("You need to pass a stock.")
    else:
        try:
            stock = finvizfinance(stock)
            links = stock.TickerNews()["Link"][:5].values
            for i in links:
                await ctx.send(i)
        except:
            await ctx.send("Invalid Stock. Try again.")


@bot.command(name="description")
async def description(ctx, stock=None):
    if not stock:
        await ctx.send("You need to pass a stock.")
    else:
        try:
            stock = finvizfinance(stock)
            await ctx.send(stock.TickerDescription())
        except:
            await ctx.send("Invalid Stock. Try again.")


@bot.command(name="details")
async def details(ctx, stock=None):
    if not stock:
        await ctx.send("You need to pass a stock.")
    else:
        try:
            stock = finvizfinance(stock)
            await ctx.send(stock.TickerFundament())
        except:
            await ctx.send("Invalid Stock. Try again.")


@bot.command(pass_context=True)
async def help(ctx):
    """Help"""
    await ctx.send('You can call the stock bot by using !stock and passing a stock ticker. You can pass a different '
                   'interval if you want. The default interval is 5 minutes. \n Example: !stock aapl 1'
                   '\n Possible intervals are: 60, 30, 15, 5, 1 \nYou can also view stock charts by calling !chart'
                   'and giving a stock. Ex: !chart aapl \nOther functions include: details, description, and news.')


bot.run("BOTKEY")
