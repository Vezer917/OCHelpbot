from discord.ext import commands
import discord
import sqlite3

conn = sqlite3.connect(r".\app\botdb.db")
c = conn.cursor()


# The quiz command should have the following functionality:
# - Add course info
# - See course info


class CourseInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='courseinfo',
        help='Returns course information',
        aliases=['course_info', 'ci']
    )
    async def courseinfo(self, ctx):
        userinput = ctx.message.content.split(' ')
        c.execute("SELECT desc, pre_req, core_req FROM course_info WHERE course_id='" + str.lower(userinput[1]) + "';")
        info = c.fetchone()
        if info is None:
            await ctx.send("Class not found")
            return
        coursename = str.upper(userinput[1])
        desc = info[0]
        if len(info[1]) > 0:
            desc += "\nPre-reqs: " + info[1]
        if len(info[2]) > 0:
            desc += "\nCore reqs: " + info[2]

        embed = discord.Embed(
            title=coursename,
            description=desc,
            color=0x206694
        )
        await ctx.send(embed=embed, content=None)
        return


def setup(bot):
    bot.add_cog(CourseInfo(bot))
