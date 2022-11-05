import discord
from discord.ext import commands as cmd
from musicog import MusiCog
import asyncio

intents = discord.Intents.all()

bot = cmd.Bot(command_prefix="eblan ", intents=intents)


asyncio.run(bot.add_cog(MusiCog(bot)))
bot.run("OTg4MDAyODQ0MDEzNjQ5OTYw.G3by2n.Od8iia2VmP3ma-wW_eQtZ-56a9TBYKLz1uR3dI")


#
#import discord
#from discord.ext import commands
#
#intents = discord.Intents.default()
#intents.message_content = True
#bot = commands.Bot(command_prefix='>', intents=intents)
#
#@bot.command()
#async def ping(ctx):
#    await ctx.send('pong')
#
#bot.run('token')
