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
# - Start quiz:  [ ] Run either as individual or group.
#                [X] Individual quizzes run in private channels
#                [ ] Improve switch to prevent quiz overlap
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
        name = " "
        if str(ctx.channel.type) != 'private':
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
            await ctx.send("Please enter '!quiz' followed by a quiz name\nType '!quizlist' to see list of quizzes"
                           " or '!quiz help' to see a list of quiz commands")
            return
        # run quiz for current channel
        if userinput[1] == 'run':
            if info is None:
                await ctx.send("No quiz found for this channel\nType '!quizlist' to see a list of all quizzes")
                return
            await run(self, ctx, str.lower(name))
            return
        # send a list of all quizzes

        c.execute("SELECT name FROM quiz WHERE name='" + str.lower(userinput[1]) + "';")
        info = c.fetchone()
        if info is None:
            await ctx.send("Quiz not found\nType '!quizlist' to see a list of all quizzes")
            return
        else:
            await ctx.send('Starting quiz... Type !end to stop')
            await run(self, ctx, str.lower(userinput[1]))
            return
        # await ctx.send('Something went wrong if you get this message... 0_0')

    @commands.command(
        name='addquestion',
        help='Add a question to a quiz',
        aliases=['addq']
    )
    async def addquestion(self, ctx, *args):
        # check to see if private channel exists, if not makes one
        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        if not args:
            ctx.send('Please specify the quiz you are adding a question to\nEg: !addq cosc111')
            return
        # get quiz
        c.execute("SELECT name, questions FROM quiz WHERE name='" + str.lower(args[1]) + "';")
        quizname = c.fetchone()
        if quizname is None:
            await ctx.author.dm_channel.send("No quiz by that name found. Type '!quizlist' to see a list of quizzes")
            return
        await ctx.author.dm_channel.send("Please tell me the question:")
        question = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        await ctx.author.dm_channel.send("Great, now the answer:")
        answer = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        await ctx.author.dm_channel.send("Please review the question and type 'y' to accept or 'n' to cancel:")
        desc = ""
        desc += "\nQuestion: " + question.content
        desc += "\nAnswer: " + answer.content
        embed = discord.Embed(
            title=quizname[0],
            description=desc,
            color=0x206694
        )
        await ctx.author.dm_channel.send(embed=embed, content=None)
        confirm = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        if confirm.content.startswith('n') or confirm.content.startswith('N'):
            await ctx.author.dm_channel.send("Cancelled")
            return
        else:
            try:
                newnumberofquestions = int(quizname[1]) + 1
                c.execute("INSERT INTO questions VALUES('" + quizname[0] + "', '" + question.content + "', '"
                          + answer.content + "', " + "50);")
                c.execute("UPDATE quiz SET questions=" + str(newnumberofquestions) +
                          " WHERE name='" + str(quizname[0]) + "';")
                conn.commit()
            except:
                await ctx.author.dm_channel.send("Hmmm.... something went wrong")
                return
            else:
                await ctx.author.dm_channel.send("Question added")
        return

    @commands.command(name="quizlist")
    async def quizlist(self, ctx):
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

    @commands.command(
        name="makequiz",
        help="Create a quiz",
        aliases=['mq', 'makeq', 'createquiz', 'addquiz']
    )
    async def makequiz(self, ctx, *, arg):
        # check to see if private channel exists, if not makes one
        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        if len(arg) < 2:
            await ctx.send("Please enter a name of the quiz\nEg: !makequiz Ken Trivia")
            return
        quizname = str(arg)
        c.execute("SELECT name FROM quiz WHERE name='" + quizname + "';")
        q = c.fetchone()
        if q is not None:
            await ctx.send("A quiz by that name already exists")
            return
        await ctx.author.dm_channel.send("The name of the quiz will be: " + quizname +
                                         "\nPlease tell me the first question:")
        question = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        await ctx.author.dm_channel.send("Great, now the answer:")
        answer = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        await ctx.author.dm_channel.send("Please review the quiz and first question then "
                                         "type 'y' to accept or 'n' to cancel:")
        desc = ""
        desc += "\nQuestion: " + question.content
        desc += "\nAnswer: " + answer.content
        embed = discord.Embed(
            title=quizname,
            description=desc,
            color=0x206694
        )
        await ctx.author.dm_channel.send(embed=embed, content=None)
        confirm = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        if confirm.content.startswith('n') or confirm.content.startswith('N'):
            await ctx.author.dm_channel.send("Cancelled")
            return
        else:
            try:
                c.execute("INSERT INTO questions VALUES('" + quizname + "', '" + question.content + "', '"
                          + answer.content + "', 50);")
                conn.commit()
                c.execute("INSERT INTO quiz VALUES('" + quizname + "', 1, '" + str(ctx.author) + "', 100);")
                conn.commit()
            except:
                await ctx.author.dm_channel.send("Hmmm.... something went wrong")
                return
            else:
                await ctx.author.dm_channel.send("Quiz created")
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
            await ctx.author.dm_channel.send('Correct!')
            totalscore += 1
        else:
            await ctx.author.dm_channel.send('Incorrect. The correct answer was:\n' + str(q[1]))
    await ctx.author.dm_channel.send(
        'Quiz finished. *Total score: ' + str(totalscore) + " out of " + str(quizinfo[1]) + "*")
    return


def setup(bot):
    bot.add_cog(Quiz(bot))
