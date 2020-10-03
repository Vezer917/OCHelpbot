from discord.ext import commands
import dbcon
import discord

conn = dbcon.conn
c = dbcon.c


# The help command should have the following functionality:
# !help - gives list of commands
# !help x - where 'x' is a specific command gives info about command
# [X] Also needs to consider cogs and custom commands
# [X] If command 'hidden=True' then it shouldn't show up in help list
# [ ] Needs to alphabetize the commands
# [ ] Group by cog (use command groups?)


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='help',
        help='Returns the help text for commands',
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
            c.execute('SELECT name, context FROM customcommands ORDER BY name')
            rows = c.fetchall()
            customcmds = ""
            for row in rows:
                if row[1] == 'onMessage' or row[1] == 'multiVal':
                    customcmds += f'!{row[0]}\n'
                if row[1] == 'onJoin':
                    customcmds += row[0] + " *(onJoin)*\n"
            embed.add_field(name="Custom Commands:", value=customcmds, inline=False)

            # if caller is admin, they get to see all commands
            HiddenCommands = discord.Embed(
                title="Help",
                description=None,
                color=0x206694
            )
            hide = ""
            for command in self.bot.commands:
                if command.hidden:
                    hide += f"!{command}\n"
            HiddenCommands.add_field(name="Admin-only Commands:", value=hide, inline=False)

            if ctx.message.author.top_role.permissions.administrator:
                if ctx.author.dm_channel is None:
                    await ctx.author.create_dm()
                await ctx.author.dm_channel.send(embed=HiddenCommands, content=None)

            # Outputs to channel

            await ctx.send(embed=embed, content=None)
            await ctx.send("Type '!help [COMMAND]' for additional information about that specific command")
            return
        else:
            arg = dbcon.sanitize(message[1])
            argtitle = "!" + arg
            embed = discord.Embed(
                title=argtitle,
                color=0x206694
            )
            cmdhelp = ""
            cmdname = arg
            # Checks for custom commands
            c.execute("SELECT * FROM customcommands WHERE name='" + arg + "' COLLATE NOCASE;")
            row = c.fetchone()

            if row is not None:
                # Sets the output to the help message of that command
                cmdhelp += row[3]

            # find the hardcoded cmd
            else:
                cmd = self.bot.get_command(arg)
                if cmd is None:
                    await ctx.send("Command not found. Use '!help' to see a list of all commands.")
                    return
                cmdhelp = cmd.help
                cmdname = f"!{cmd.name}"
                cmdaliases = cmd.aliases
                if len(cmdaliases) > 0:
                    cmdhelp += '\nAliases: ' + str(cmdaliases)

            embed.add_field(name=cmdname, value=cmdhelp, inline=False)
            await ctx.send(embed=embed, content=None)
            return


def setup(bot):
    bot.add_cog(Help(bot))
