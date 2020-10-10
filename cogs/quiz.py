import asyncio
from discord.ext import commands
import discord
import sqlite3
import dbcon

conn = dbcon.conn
c = dbcon.c


# The quiz command should have the following functionality:
# - Add quiz:    Start with quiz name, followed by questions.
#                Possibly send user to Flask link to fill out form?
# - Modify quiz: This should ask the user which question they would like to modify, delete or
#                rename quiz
# - Start quiz:  [ ] Run either as individual or group.
#                [X] Individual quizzes run in private channels
#                [ ] Improve switch to prevent quiz overlap
#                [ ] Run each quiz as a separate process so multiple people doing multiple quizzes don't interfere with
#                      each other
#
# The quiz command will need two tables: 'quiz' and 'questions'
#  quiz : #name (text), questions (int), madeby (text), score (int)
#  questions : #quizname (text, FK), question (text), answer (text), score (int)


class Quiz(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='quiz',
        help='The quiz command',
        aliases=['q']
    )
    async def quiz(self, ctx, *, args=None):
        # If there is no course specified
        info = None
        name = None
        channelname = ctx.channel.name.split('_')
        name = channelname[0]
        print(name)
        c.execute(f"SELECT name, questions, madeby, score FROM quiz WHERE name='{str(name)}' COLLATE NOCASE;")
        info = c.fetchone()
        if args is None:
            # If there is no course specified but you are in a course channel (ie 'cosc111_computer-programming')
            if info is not None:
                author = str(info[2]).split('#')
                quizname = name
                desc = ""
                desc += "\nNumber of Questions: " + info[1]
                desc += "\nMade by: " + author[0]
                embed = discord.Embed(
                    title=quizname,
                    description=desc,
                    color=0x206694
                )
                await ctx.send("I found a quiz for this channel: \n(Type `!quiz run` to start the quiz)")
                await ctx.send(embed=embed, content=None)
                return
            # no quiz specified and not a course channel

            await ctx.send("`!quiz [NAME]` to run a quiz\n"
                           "`!quizlist` to see list of quizzes\n"
                           "`!addquiz [NAME]` to add a quiz\n"
                           "`!delquiz [NAME]` to delete a quiz\n"
                           "`!addq [QUIZNAME]` to add questions to a quiz")
            return
        # run quiz for current channel
        if args == 'run':
            if info is None:
                await ctx.send("No quiz found for this channel\nType '!quizlist' to see a list of all quizzes")
                return
            await run(self, ctx, name)
            return
        # clean the args to prevent SQL injection
        args = dbcon.sanitize(args)
        c.execute(f"SELECT name FROM quiz WHERE name='{args}' COLLATE NOCASE;")
        quizinfo = c.fetchone()
        if quizinfo is None:
            await ctx.send("Quiz not found\nType '!quizlist' to see a list of all quizzes")
            return
        else:
            await ctx.send('Starting quiz... Type !end to stop')
            await run(self, ctx, args)
            return

    @commands.command(
        name='addquestion',
        help='Add a question to a quiz',
        aliases=['addq']
    )
    async def addquestion(self, ctx, *, args=None):
        # check to see if private channel exists, if not makes one
        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        if args is None:
            await ctx.send('Please specify the quiz you are adding a question to\nEg: !addq cosc111')
            return
        # get quiz
        c.execute(f"SELECT name, questions FROM quiz WHERE name='{str(args)}' COLLATE NOCASE;")
        quizname = c.fetchone()
        if quizname is None:
            await ctx.author.dm_channel.send("No quiz by that name found. Type `!quizlist` to see a list of quizzes")
            return
        stop = False
        while not stop:
            await ctx.send("*Type `!end` at any time to exit*")
            await ctx.author.dm_channel.send("Please tell me the question:")
            question = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
            if question.content == '!end':
                return
            await ctx.author.dm_channel.send("Great, now the answer:")
            answer = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
            if answer.content == '!end':
                return
            await ctx.author.dm_channel.send("Please review the question and type `y` to accept and add another or "
                                             "`n` to cancel:")
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
                    sql = "INSERT INTO questions (quizname, question, answer, score) VALUES (?, ?, ?, ?)"
                    c.execute(sql, (quizname[0], question.content, answer.content, 50))
                    conn.commit()
                    sql = "UPDATE quiz SET questions=? WHERE name=? COLLATE NOCASE"
                    c.execute(sql, (newnumberofquestions, quizname[0]))
                except sqlite3.Error as e:
                    print(type(e).__name__)
                except:
                    await ctx.author.dm_channel.send("Hmmm.... something went wrong")
                    return
                else:
                    conn.commit()
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
        aliases=['mq', 'makeq', 'createquiz', 'addquiz', 'quizmake', 'quizadd']
    )
    async def makequiz(self, ctx, *, arg=None):
        # check to see if private channel exists, if not makes one
        # if ctx.author.dm_channel is None:
        #    await ctx.author.create_dm()
        if arg is None:
            await ctx.send("Please enter a name of the quiz\nEg: `!makequiz Ken Trivia`")
            return
        # clean the arg to prevent SQL injection
        arg = dbcon.sanitize(arg)
        quizname = str(arg)
        c.execute(f"SELECT name FROM quiz WHERE name='{quizname}' COLLATE NOCASE;")
        q = c.fetchone()
        if q is not None:
            await ctx.send("A quiz by that name already exists")
            return
        try:
            sql = "INSERT INTO quiz (name, questions, madeby, score) VALUES (?, ?, ?, ?)"
            c.execute(sql, (quizname, 0, str(ctx.author), 100))
            conn.commit()
        except sqlite3.Error as e:
            print(type(e).__name__)
        except:
            await ctx.send("Something went wrong adding the quiz\nQuizname: " + quizname +
                           "\nauthor: " + str(ctx.author))
            return
        else:
            await ctx.send(
                "Quiz created. Type '!addq " + quizname + "' to add questions to this quiz")
        return

    @commands.command(
        name="delquiz",
        help="Delete a quiz",
        aliases=['dq', 'delq', 'deletequiz', 'dquiz', 'quizdel', 'quizd']
    )
    async def delquiz(self, ctx, *, arg=None):
        if arg is None:
            await ctx.send("Please enter a name of the quiz to delete.\nEg: !delquiz Ken Trivia")
            return
        # clean the arg to prevent SQL injection
        arg = dbcon.sanitize(arg)
        quizname = str(arg)
        c.execute("SELECT name, questions, madeby, score FROM quiz WHERE name='" + quizname + "';")
        q = c.fetchone()
        quizauthor = str(q[2]).split("#")
        desc = f"Quiz Name: {q[0]}\nNo of Questions: {q[1]}\nMade by: {quizauthor[0]}"
        embed = discord.Embed(
            title=q[0],
            description=desc,
            color=0x206694
        )
        await ctx.send("Please review the quiz and type 'y' to delete or 'n' to cancel:")
        await ctx.send(embed=embed, content=None)
        confirm = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                          timeout=60.0)
        if confirm.content.startswith('n') or confirm.content.startswith('N'):
            await ctx.send("Cancelled")
            return
        author = str(ctx.author).split("#")
        # check to see if the quiz author is the same as the message author
        if author[0] != quizauthor[0]:
            print(f'{ctx.author} failed to delete command {quizname}')
            await ctx.send("Quizzes can only be deleted by their author")
            return
        try:
            c.execute("DELETE FROM quiz WHERE name='" + quizname + "';")
            conn.commit()
        except sqlite3.Error as e:
            print(type(e).__name__)
        except:
            await ctx.send("Hmmm.... something went wrong")
            return
        c.execute("DELETE FROM questions WHERE quizname='" + quizname + "';")
        await ctx.send(f"{quizname} deleted")
        print(f"{quizname} deleted by {ctx.author}")
        return


# run the actual quiz (private messaged to user)
async def run(self, ctx, args):
    # check to see if private channel exists, if not makes one
    if ctx.author.dm_channel is None:
        await ctx.author.create_dm()
    # grab quiz
    print(args)
    c.execute(f"SELECT name, questions, madeby, score FROM quiz WHERE name='{args}' COLLATE NOCASE;")
    quizinfo = c.fetchone()
    print(quizinfo[0])
    quizname = str(quizinfo[0])
    desc = ""
    desc += "\nNumber of Questions: " + str(quizinfo[1])
    desc += "\nMade by: " + str(quizinfo[2])
    embed = discord.Embed(
        title=quizname,
        description=desc,
        color=0x206694
    )
    await ctx.send(embed=embed, content=None)
    # grab questions
    c.execute(f"SELECT question, answer, score FROM questions WHERE quizname='{args}' COLLATE NOCASE;")
    questions = c.fetchall()
    totalscore = 0
    counter = 0
    for q in questions:
        # async with ctx.typing():
        counter += 1
        msg = ""
        await ctx.author.dm_channel.send(f"Question {str(counter)}:\n{q[0]}")
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
            await ctx.author.dm_channel.send(f'Incorrect. The correct answer was:\n**{str(q[1])}**')
    scoremessage = ''
    outof = float(quizinfo[1])
    if totalscore >= counter:
        scoremessage = '*Perfect score! Nice!*'
    if totalscore >= counter / 2:
        scoremessage = '*Good job, you passed!*'
    if totalscore < counter /2:
        scoremessage = '*Better luck next time!*'

    await ctx.author.dm_channel.send(
        f'Quiz finished. *Total score: {str(totalscore)} out of {str(quizinfo[1])}*\n{scoremessage}')

    return


def setup(bot):
    bot.add_cog(Quiz(bot))
