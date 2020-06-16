from discord.ext import commands
import discord
import sqlite3
from app import dbcon

conn = sqlite3.connect(dbcon.dbfile)
c = conn.cursor()

# The help command should have the following functionality:
# !help - gives list of commands
# !help x - where 'x' is a specific command gives info about command
#


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='help',
        description='The help command',
        aliases=['h']
    )
    # This command is terrible and should be rewritten to read help attribute associated with each command
    # Also, should be a cog and presented in embed format
    # String building with a switch command is not a very python way of doing things
    async def help(self, ctx):
        message = ctx.message.content
        message = message.split(' ')
        if len(message) <= 1:
            # If no arguments are provided it will put out a list of all commands
            output = "List of all commands for this bot:\n"

            # Hard coded commands
            output += "!register\n!whoami\n!links\n!roll_dice\n!profquote\n!addquote\n"

            # Custom commands
            c.execute('SELECT name FROM customcommands')
            rows = c.fetchall()

            for row in rows:
                output += '!' + row[0] + '\n'

            # Outputs to channel
            await ctx.channel.send(output)
        else:
            # An argument is provided so it will output the help for the argument
            arg = message[1]
            output = 'Help for ' + arg + ':\n'

            # Hard coded commands
            if arg == 'register':
                output += 'Lets you record your first name, program and year into the bot, use !register for syntax'
            elif arg == 'whoami':
                output += 'Returns the information the you have given the bot with !register'
            elif arg == 'links':
                output += 'Returns a list of useful links with a provided course id, use !links for syntax'
            elif arg == 'roll_dice':
                output += 'Returns a random number between 1-6'
            elif arg == 'profquote':
                output += 'Returns a random profquote'
            elif arg == 'addquote':
                output += 'Add a profquote'
            elif arg == 'pi':
                output += 'Returns pi to the n decimal points'
            else:
                # Checks for custom commands
                c.execute("SELECT * FROM customcommands WHERE name='" + arg + "';")
                row = c.fetchone()

                if row is not None:
                    # Sets the output to the help message of that command
                    output += row[3]
                else:
                    # No commands were found, returns error message
                    output = 'Sorry, no commands were found matching: ' + arg

            await ctx.channel.send(output)
            return


def setup(bot):
    bot.add_cog(Help(bot))