from discord.ext import commands
from app import dbcon
import discord

conn = dbcon.conn
c = dbcon.c


# The help command should have the following functionality:
# !help - gives list of commands
# !help x - where 'x' is a specific command gives info about command
#  - Also needs to consider cogs and custom commands
#  - If command 'hidden=True' then it shouldn't show up in help list


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='help',
        description='The help command',
        aliases=['h']
    )
    async def help(self, ctx):
        message = ctx.message.content
        message = message.split(' ')
        if len(message) <= 1:

            # If no arguments are provided it will put out a list of all commands
            desc = "List of all commands for this bot:\n"
            embed = discord.Embed(
                title="Help",
                description=desc,
                color=0x206694
            )
            hardcoded = ""
            for command in self.bot.commands:
                if not command.hidden:
                    hardcoded += f"!{command}\n"
            embed.add_field(name="Hardcoded Commands:", value=hardcoded, inline=False)

            # Custom commands
            c.execute('SELECT name FROM customcommands')
            rows = c.fetchall()
            customcmds = ""
            for row in rows:
                customcmds += "!" + row[0] + '\n'
            embed.add_field(name="Custom Commands:", value=customcmds, inline=False)

            # Outputs to channel

            await ctx.send(embed=embed, content=None)
            return
        else:
            arg = message[1]
            embed = discord.Embed(
                title="Help",
                color=0x206694
            )
            cmdhelp = ""
            # Checks for custom commands
            c.execute("SELECT * FROM customcommands WHERE name='" + arg + "';")
            row = c.fetchone()

            if row is not None:
                # Sets the output to the help message of that command
                cmdhelp += row[3]

            # find the hardcoded cmd
            else:
                cmd = self.bot.get_command(arg)
                cmdhelp = cmd.help

            embed.add_field(name='!'+arg, value=cmdhelp, inline=False)
            await ctx.send(embed=embed, content=None)
            return


def setup(bot):
    bot.add_cog(Help(bot))
