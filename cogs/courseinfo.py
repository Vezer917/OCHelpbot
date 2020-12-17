from discord.ext import commands
import discord
import dbcon

c = dbcon.engine.connect()

# The courseinfo command should have the following functionality:
# - Add course info
# - See course info
#
# Currently the courseinfo command has the following:
# - Return course info of current channel if no course is specified
# - Return course info of specified course
# - Alerts user if no parameters were given and not in a course specific channel


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
        # If there is no course specified
        if len(userinput) < 2:
            channelname = ctx.channel.name.split('_')
            name = channelname[0]
            info = c.execute(f"SELECT desc, pre_req, core_req FROM course_info WHERE course_id='{str.lower(name)}';")
            info = info.fetchone()
            if info is None:
                await ctx.send("Please enter '!courseinfo' followed by a course code\nEg: !courseinfo COSC111")
                return
            # If there is no course specified but you are in a course channel (ie 'cosc111_computer-programming')
            else:
                coursename = str.upper(name)
                desc = info.desc
                if len(info.pre_req) > 0:
                    desc += "\nPre-reqs: " + info.pre_req
                if len(info.core_req) > 0:
                    desc += "\nCo-reqs: " + info.core_req

                embed = discord.Embed(
                    title=coursename,
                    description=desc,
                    color=0x206694
                )
                await ctx.send(embed=embed, content=None)
                return
        # returns the specific course (even if you are in course channel)
        coursename = dbcon.sanitize(userinput[1])
        info = c.execute(f"SELECT desc, pre_req, core_req FROM course_info WHERE course_id='{str.lower(coursename)}';")
        info = info.fetchone()
        if info is None:
            await ctx.send("Class not found")
            return
        coursename = str.upper(coursename)
        desc = info.desc
        if len(info.pre_req) > 0:
            desc += "\nPre-reqs: " + info.pre_req
        if len(info.core_req) > 0:
            desc += "\nCo-reqs: " + info.core_req

        embed = discord.Embed(
            title=coursename,
            description=desc,
            color=0x206694
        )
        await ctx.send(embed=embed, content=None)
        return


def setup(bot):
    bot.add_cog(CourseInfo(bot))
