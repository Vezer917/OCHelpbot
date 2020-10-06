import sqlite3

from discord.ext import commands
import discord
import dbcon

conn = dbcon.conn
c = dbcon.c

# list of words that cannot be customcommand name, basically all the hardcoded commands
# (I'm sure there's a way to gather them all without manually having to type them out)
nouse = ['rank', 'help', 'marco', 'quiz', 'customcommand', 'echo','profquote','addquote','define','createchannel',
         'rolldice','time','makequiz','help','addquestion','courseinfo','quizlist','arginfo','register',
         'links','addlink','delquiz','makeFlaskAdmin','deletelink','echo_on_join','channeltype','whois','whoami']


# The customcommand command should have the following functionality:
# [X] Add command
# [ ] Modify command
# [X] Delete command


class CustomCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='customcommand',
        help="Add, Remove, Modify or Delete custom commands. Type '!customcommand' to see a list of options",
        aliases=['cc', 'custom']
    )
    async def customcommand(self, ctx, *, args=None):
        if args is not None:
            args = dbcon.sanitize(args)
        # add command
        if args == 'add' or args == 'a':
            await ctx.send("What will the name of the command be:\n*(one word only please)*")
            cmdname = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                              timeout=60.0)
            if " " in cmdname.content:
                await ctx.send("No spaces please... cc add cancelled")
                return
            if cmdname.content in nouse:
                await ctx.send(f"{cmdname.content} is a restricted word... cc add cancelled")
                return
            # check to see if cmd already exists
            c.execute(f"SELECT name FROM customcommands WHERE name='{str(cmdname.content)}';")
            name = c.fetchone()
            if name is not None:
                await ctx.send("A command by that name already exists.\n"
                               "Type '!customcommand list' to see the list of custom commands")
                return
            await ctx.send("What context will it be called on:\n"
                           "**1. onMessage** - will activate when called by user (eg '!pizza')\n"
                           "**2. onJoin** - will notify user upon joining server\n"
                           "**3. multiVal** - an onMessage that returns a random response from a list of values\n"
                           "(other types coming in future)")
            cmdcontext = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                                 timeout=60.0)
            # check to see what the context will be (default is set as 'onMessage')
            # this should really be a unnamed function
            context = "onMessage"
            if cmdcontext.content.startswith("1") or cmdcontext.content.startswith(
                    "onM") or cmdcontext.content.startswith("onm"):
                context = "onMessage"
            if cmdcontext.content.startswith("2") or cmdcontext.content.startswith(
                    "onJ") or cmdcontext.content.startswith("onj"):
                context = "onJoin"
            if cmdcontext.content.startswith("3") or cmdcontext.content.startswith(
                    "mu"):
                context = "multiVal"
            # the value the bot returns when the command is called
            cmdval = ""
            if context == 'onMessage' or context == 'onJoin':
                await ctx.send("What will the return value be:\n*(Discord markdown will apply in the return)*")
                cmdreturn = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                                    timeout=60.0)
                cmdval = cmdreturn.content
            if context == 'multiVal':
                addval = []
                while(1):
                    await ctx.send("Enter a return:\n*(enter !stop to stop)*")
                    val = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                                        timeout=60.0)

                    if val.content == '!stop':
                        break
                    else:
                        addval += [val.content]
                        continue
                cmdval = "multival"
            # the help value
            await ctx.send(f"What will the help value be:\n(what will '!help {cmdname.content}' return?)")
            cmdhelp = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                              timeout=60.0)
            await ctx.send("Please review the command and type 'y' to accept or 'n' to cancel:")
            desc = ""
            desc += "\nName: " + cmdname.content
            desc += "\nContext: " + context
            desc += "\nReturn: " + cmdval
            desc += "\nHelp: " + cmdhelp.content
            embed = discord.Embed(
                title=cmdname.content,
                description=desc,
                color=0x206694
            )
            await ctx.send(embed=embed, content=None)
            confirm = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                              timeout=60.0)
            if confirm.content.startswith('n') or confirm.content.startswith('N'):
                await ctx.send("Cancelled")
                return
            else:
                try:
                    sql = "INSERT INTO customcommands (name, context, value, help, author) VALUES (?, ?, ?, ?, ?)"
                    c.execute(sql, (cmdname.content, context, cmdval, cmdhelp.content, str(ctx.author)))
                    conn.commit()
                    if context == 'multiVal':
                        for add in addval:
                            sql = "INSERT INTO multival (name, value) VALUES (?,?)"
                            c.execute(sql, (cmdname.content, add))
                            conn.commit()
                    await ctx.send("Command added")
                except sqlite3.Error as e:
                    print(type(e).__name__)
                except:
                    await ctx.send("Hmmm.... something went wrong")
                    return
            return
        # delete command
        if args == 'del' or args == 'd':
            await ctx.send("What is the name of the custom command you would like to delete?"
                           "\n(please do not include the '!')")
            cmdname = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                                timeout=60.0)
            if cmdname.content.startswith("!"):
                await ctx.send("Cancelled cc d")
                return
            try:
                c.execute("SELECT name, value, context, help, author FROM customcommands WHERE name='" + str(cmdname.content) + "';")
            except sqlite3.Error as e:
                print(type(e).__name__)
            except:
                await ctx.send("Hmmm.... something went wrong")
                return
            cmd = c.fetchone()
            if cmd is None:
                await ctx.send("No command by that name exists.\n"
                               "Type '!customcommand list' to see the list of custom commands")
                return
            cmdauthor = str(cmd[4]).split("#")
            desc = f"Value: {cmd[1]}\nContext: {cmd[2]}\nHelp: {cmd[3]}\nMade by: {cmdauthor[0]}"
            embed = discord.Embed(
                title=cmdname.content,
                description=desc,
                color=0x206694
            )
            await ctx.send("Please review the command and type 'y' to delete or 'n' to cancel:")
            await ctx.send(embed=embed, content=None)

            confirm = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                              timeout=60.0)
            if confirm.content.startswith('n') or confirm.content.startswith('N'):
                await ctx.send("Cancelled")
                return
            author = str(ctx.author).split("#")
            # if caller is admin, they can delete any command
            if ctx.message.author.top_role.permissions.administrator:
                print(f'user is admin')
                c.execute(f"DELETE FROM customcommands WHERE name='{cmdname.content}';")
                await ctx.send(f"{cmdname.content} deleted")
                print(f"{cmdname.content} deleted by {ctx.author}")
            else:
                if author[0] != cmdauthor[0]:
                    print(f'{ctx.author} failed to delete command {cmdname.content}')
                    await ctx.send("Commands can only be deleted by their author")
                else:
                    c.execute("DELETE FROM customcommands WHERE name='" + cmdname.content + "';")
                    await ctx.send(f"{cmdname.content} deleted")
                    print(f"{cmdname.content} deleted by {ctx.author}")
            conn.commit()
            return
        # modify command
        if args == 'mod' or args == 'm':
            await ctx.send("you have chosen modify\nComing soon")
            return
        # list commands
        if args == 'list' or args == 'l':
            try:
                c.execute('SELECT * FROM customcommands')
            except sqlite3.Error as e:
                print(type(e).__name__)
            rows = c.fetchall()
            customcmds = ""
            for row in rows:
                if row[1] == 'onMessage':
                    customcmds += "!" + row[0] + '\n'
                if row[1] == 'onJoin':
                    customcmds += row[0] + " *(onJoin)*\n"
            embed = discord.Embed(
                title="Custom Command List",
                description=customcmds,
                color=0x206694
            )
            await ctx.send(embed=embed, content=None)
            return
        await ctx.send("'!customcommand add' to add command\n'!customcommand mod' to modify command"
                       "\n'!customcommand del' to delete command\n'!customcommand list' to list custom commands")
        return


def setup(bot):
    bot.add_cog(CustomCommand(bot))
