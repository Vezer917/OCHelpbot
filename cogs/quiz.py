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
# Each quiz will need to have its own table in the Quiz database. Quizzes should be run


class Quiz(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='quiz',
        description='The quiz command',
        aliases=['q']
    )
    async def quiz(self, ctx):
        await ctx.send('coming soon')
        return


def setup(bot):
    bot.add_cog(Quiz(bot))
