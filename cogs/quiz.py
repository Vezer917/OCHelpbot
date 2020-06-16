from discord.ext import commands
import discord
import sqlite3
from app import dbcon

conn = sqlite3.connect(dbcon.dbfile)
c = conn.cursor()

# The quiz command should have the following functionality:
# - Add quiz:    Start with quiz name, followed by questions.
#                Possibly send user to Flask link to fill out form?
# - Modify quiz: This should ask the user which question they would like to modify, delete or
#                rename quiz
# - Start quiz:  Run either as individual or group. Individual quizzes should be private messaged.
#                Possibly add time limit?
#
# The quiz command will need two tables: 'quiz' and 'questions'
#  quiz : #name (text), questions (int), madeby (text), score (int)
#  questions : #quizname (text, FK), question (text), answer (text), score (int)



class Quiz(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='quiz',
        description='The quiz command',
        aliases=['q']
    )
    async def quiz(self, ctx):
        userinput = ctx.message.content.split(' ')
        # If there is no course specified
        if len(userinput) < 2:
            channelname = ctx.channel.name.split('_')
            name = channelname[0]
            c.execute("SELECT name, questions, madeby, score FROM quiz WHERE name='" + str.lower(name) + "';")
            info = c.fetchone()
            # If there is no course specified but you are in a course channel (ie 'cosc111_computer-programming')
            if info is not None and userinput[1] == 'run':
                await run(self, ctx, str.lower(userinput[1]))
                return
            if info is not None:
                quizname = str.upper(name)
                desc = ""
                if len(info[1]) > 0:
                    desc += "\nNumber of Questions: " + info[1]
                if len(info[2]) > 0:
                    desc += "\nMade by: " + info[2]

                embed = discord.Embed(
                    title=quizname,
                    description=desc,
                    color=0x206694
                )
                await ctx.send(embed=embed, content=None)
                return
            # no quiz specified and not a course channel
            else:
                await ctx.send("Please enter '!quiz' followed by a quiz name\nType '!quiz list' to see list of quizzes")
                return
        # send a list of all quizzes
        if userinput[1] == 'list' :
            await ctx.send("list of all quizzes")
            return
        c.execute("SELECT name FROM quiz WHERE name='" + str.lower(userinput[1]) + "';")
        info = c.fetchone()
        if info is None:
            await ctx.send("Quiz not found\nType '!quiz list' to see a list of all quizzes")
            return
        else:
            await ctx.send('Starting quiz... Type !end to stop')
            await run(self, ctx, str.lower(userinput[1]))
            return
        # await ctx.send('Something went wrong if you get this message... 0_0')
        return


# run the actual quiz
async def run(self, ctx, quiz):
    c.execute("SELECT question, answer, score FROM questions WHERE quizname='" + quiz + "';")
    questions = c.fetchall()
    totalscore = 0
    for q in questions:
        await ctx.send(q[0])
    return


def setup(bot):
    bot.add_cog(Quiz(bot))
