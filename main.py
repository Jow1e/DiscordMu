from discord.ext import commands as cmd
from musicog import MusiCog


bot = cmd.Bot(command_prefix="horny ")
bot.add_cog(MusiCog(bot))
bot.run("<your discord api key>")
