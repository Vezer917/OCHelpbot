from discord.ext import commands
from datetime import datetime
import pytz

# The time command should return the current time, but not neccesarily the local time
# of whereever the bot is being hosted


class Time(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='time',
        help='Return the current time')
    async def time(self, ctx):

        current_time = datetime.now(pytz.timezone('US/Pacific')).strftime('%H:%M:%S')
        await ctx.channel.send(f'The current time is: {current_time} PST')


def setup(bot):
    bot.add_cog(Time(bot))