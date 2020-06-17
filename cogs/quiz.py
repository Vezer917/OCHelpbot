import asyncio

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
        channelname = ctx.channel.name.split('_')
        name = channelname[0]
        c.execute("SELECT name, questions, madeby, score FROM quiz WHERE name='" + str.lower(name) + "';")
        info = c.fetchone()
        if len(userinput) < 2:

            # If there is no course specified but you are in a course channel (ie 'cosc111_computer-programming')
            if info is not None:
                quizname = str.upper(name)
                desc = ""
                desc += "\nNumber of Questions: " + info[1]
                desc += "\nMade by: " + info[2]
                embed = discord.Embed(
                    title=quizname,
                    description=desc,
                    color=0x206694
                )
                await ctx.send("I found a quiz for this channel: \n(Type '!quiz run' to start the quiz)")
                await ctx.send(embed=embed, content=None)
                return
            # no quiz specified and not a course channel
            else:
                await ctx.send("Please enter '!quiz' followed by a quiz name\nType '!quiz list' to see list of quizzes"
                               " or '!quiz help' to see a list of quiz commands")
                return
        # send a list of all quizzes
        if userinput[1] == 'run':
            if info is None:
                await ctx.send("No quiz found for this channel\nType '!quiz list' to see a list of all quizzes")
                return
            await run(self, ctx, str.lower(name))
            return
        if userinput[1] == 'list':
            c.execute("SELECT name FROM quiz;")
            info = c.fetchall()
            desc = ""
            for i in info:
                desc += i[0] + "\n"
            embed = discord.Embed(
                title="List of all quizzes",
                description=desc,
                color=0x206694
            )
            await ctx.send(embed=embed, content=None)
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


# run the actual quiz (private messaged to user)
async def run(self, ctx, quiz):
    # check to see if private channel exists, if not makes one
    if ctx.author.dm_channel is None:
        await ctx.author.create_dm()
    # grab quiz
    c.execute("SELECT name, questions, madeby, score FROM quiz WHERE name='" + quiz + "';")
    quizinfo = c.fetchone()
    quizname = str.upper(quizinfo[0])
    desc = ""
    desc += "\nNumber of Questions: " + quizinfo[1]
    desc += "\nMade by: " + quizinfo[2]
    embed = discord.Embed(
        title=quizname,
        description=desc,
        color=0x206694
    )
    await ctx.send(embed=embed, content=None)
    # grab questions
    c.execute("SELECT question, answer, score FROM questions WHERE quizname='" + quiz + "';")
    questions = c.fetchall()
    totalscore = 0
    counter = 0
    for q in questions:
        counter += 1
        await ctx.author.dm_channel.send("Question " + str(counter) + ":\n" + q[0])
        try:
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.author.dm_channel.send('Quiz has timed out. *This happens automatically after 60 seconds*')
        # prevents quiz from running multiple times
        if msg.content.startswith('!end') or msg.content.startswith('!quiz'):
            await ctx.author.dm_channel.send('Quiz stopped')
            return
        if str.lower(q[1]) == str.lower(msg.content):
            await ctx.author.dm_channel.send('Correct! *' + str(q[2]) + ' points!*')
            totalscore += q[2]
        else:
            await ctx.author.dm_channel.send('Incorrect. The correct answer was:\n' + str(q[1]))
    await ctx.author.dm_channel.send('Quiz finished. *Total score: ' + str(totalscore) + " out of " + str(quizinfo[3]) + "*")
    return


def setup(bot):
    bot.add_cog(Quiz(bot))
