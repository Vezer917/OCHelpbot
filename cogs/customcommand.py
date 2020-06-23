from discord.ext import commands
import discord
from app import dbcon

conn = dbcon.conn
c = dbcon.c


# The customcommand command should have the following functionality:
# - Add command
# - Modify command
#


class CustomCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='customcommand',
        help='custom command',
        aliases=['cc', 'custom']
    )
    async def courseinfo(self, ctx, *, args):
        await ctx.send("Coming soon")
        return


def setup(bot):
    bot.add_cog(CustomCommand(bot))