# DiscordLaunch.py
import os
import random
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv
import cogs
import threading

# Okanagan College Discord Bot
# Made by Colin, James, Richard and Tristan in 2020
# For the COSC224 Projects class
#
# Look in "TODO_list.txt" for a list of upcoming features!

# Here's where the bot loads the environmental variables
# (variables you don't want the public to see)
import dbcon

load_dotenv()
token = os.getenv('TOKEN')
guildid = os.getenv('GUILDID')
dbfile = os.getenv('DATABASE_FILE')

# Here you can set your own prefix for commands (we used '!')
bot = commands.Bot(command_prefix='!')

# setting up sqlite
conn = sqlite3.connect(dbfile)
c = conn.cursor()
# We implemented our own version of the 'help' command
bot.remove_command('help')
# define the cogs
cogs = ['cogs.quiz', 'cogs.courseinfo', 'cogs.help', 'cogs.rolldice', 'cogs.customcommand', 'cogs.links', 'cogs.time',
        'cogs.autoreacts', 'cogs.profquote', 'cogs.define']


@bot.event
async def on_ready():
    print(f'Greetings, Batman')
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    for cog in cogs:
        bot.load_extension(cog)
    return

# Below are the actual commands for the bot that will eventually end up in Cogs.
# What is a Cog? A Cog is an easy way to divide parts of your program into separate files.
# This will make it much easier to separate our command groups. (Quiz, Help, etc.)
#
# Set hidden=True if you don't want the command to show up when '!help' is called.


@bot.command(name='echo', help='Send a message from the bot to a specific channel', hidden=True)
@commands.has_permissions(manage_guild=True)
async def echo(ctx):
    await ctx.send("Which channel do you want me to send message to?\n(please enter exact name)")
    channel = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
    channelID = discord.utils.get(ctx.guild.channels, name=channel.content)
    print(f'{ctx.author} sent a message to the channel: {channelID}')
    if channelID is None:
        await ctx.send('channel not found')
        return
    await ctx.send("Please enter the message to send")
    message_to_send = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
    print(f'"{message_to_send.content}"')
    await channelID.send(message_to_send.content)
    return


@bot.command(name='createchannel', aliases=['newchannel', 'makechannel', 'addchannel'], hidden=True)
@commands.has_permissions(manage_guild=True)
async def create_channel(ctx, channel_name: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if existing_channel is None:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


# use this command to set admins for the flask portal
# only a guild admin can use this command
@bot.command(name='makeFlaskAdmin', hidden=True)
@commands.has_permissions(manage_guild=True)
async def make_admin(ctx):
    userinput = ctx.message.content.split(' ')
    c.execute('SELECT username FROM user WHERE id=' + userinput[1] + ';')
    curr = c.fetchone()
    if curr is None:
        # Printed out when no username match the arguments class
        await ctx.channel.send('Sorry, there is no Flask user with the username: ' + userinput[1])
        return
    else:
        c.execute("UPDATE user SET admin=1 WHERE id=" + userinput[1] + ";")
        await ctx.channel.send('User made admin')


# add stats (runtime, returned messages, etc.)
@bot.command(name='marco', help='Test to see if bot is running')
async def marco(ctx):
    await ctx.channel.send('polo')


# This command should be in its own cog and streamlined to wait for user input
@bot.command(name='register', help='Allows you to input information about yourself into the bot', hidden=True)
async def register(ctx):
    # Checks if they already have a database row
    c.execute('SELECT * FROM users WHERE id=' + str(ctx.author.id))
    if c.fetchone() is None:
        c.execute("INSERT INTO users VALUES(" + str(ctx.author.id) + ", 'Not provided', 'Not provided', 0, '" +
                  str(ctx.author.name) + "');")
        conn.commit()

    # c.execute("UPDATE users SET username= '" + str(ctx.author.name) + "' WHERE id='" + str(ctx.author.id) + ";")
    # Checks if they already have a dm channel
    if ctx.author.dm_channel is None:
        await ctx.author.create_dm()

    # Checks arguments to see what to add (name, program, etc)
    userinput = ctx.message.content.split(' ')
    if len(userinput) < 3:
        # outputted if register is used incorrectly
        await ctx.author.dm_channel.send(
            "Thank you for registering,\n"
            "To input your first name: !register name [your first name]\n"
            "To input your program: !register program [BCIS / CIS]\n"
            "To input what year you are in: !register year [your year]"
        )
    else:
        if userinput[1] == 'name':
            c.execute("UPDATE users SET fname= '" + userinput[2] +
                      "' WHERE id=" + str(ctx.author.id) + ";")
            conn.commit()
            await ctx.author.dm_channel.send("Thank you, " + userinput[2] + " has been set as your name.")
        if userinput[1] == 'program':
            c.execute("UPDATE users SET program= '" + userinput[2] +
                      "' WHERE id=" + str(ctx.author.id) + ";")
            conn.commit()
            await ctx.author.dm_channel.send("Thank you, " + userinput[2] + " has been set as your program.")
            # Setting their role based on input
            guild = bot.get_guild(guildid)
            target = None
            for role in guild.roles:
                if role.name == userinput[2]:
                    target = role
            if target is None:
                await ctx.author.dm_channel.send("" + userinput[2] + " was not found as a role")
            else:
                member = guild.get_member(ctx.author.id)
                await member.add_roles(target)
        if userinput[1] == 'year':
            c.execute("UPDATE users SET year= " + userinput[2] +
                      " WHERE id=" + str(ctx.author.id) + ";")
            conn.commit()
            await ctx.author.dm_channel.send("Thank you, " + userinput[2] + " has been set as your year.")


@bot.command(name='whoami', help='Returns the information you have given the bot', hidden=True)
@commands.has_permissions(manage_guild=True)
async def who(ctx):
    c.execute("SELECT fname, program, year FROM users WHERE id='" + str(ctx.author.id) + "';")
    await ctx.channel.send(c.fetchone())


@bot.command(name='whois', help='Returns info from bot', hidden=True)
@commands.has_permissions(manage_guild=True)
async def whois(ctx):
    userinput = ctx.message.content.split(' ')
    # Checks if they already have a dm channel
    if ctx.author.dm_channel is None:
        await ctx.author.create_dm()

    c.execute("SELECT * FROM users WHERE username='" + userinput[1] + "';")
    curr = c.fetchone()
    if curr is None:
        await ctx.author.dm_channel.send("" + userinput[1] + " was not found")

    n = curr[1]
    y = curr[3]
    p = curr[2]
    await ctx.author.dm_channel.send("" + userinput[1] + " is: \nFirst name: " + str(n) + "\nYear: " + str(y) +
                                     "\nProgram: " + str(p))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


# handles 'onMessage' custom commands
@bot.listen('on_message')
async def on_message(message):
    if message.author.bot:
        # Stops it from replying to bots
        return

    userinput = message.content.split(' ')
    if len(userinput) > 0:
        name = userinput[0]
        if name[0] == '!':
            # Removes '!' from beginning of command
            name = dbcon.sanitize(name[1:])

            # Checks for a match in the custom commands table
            c.execute(f"SELECT * FROM customcommands WHERE name='{name}' COLLATE NOCASE;")
            row = c.fetchone()

            if row is None:
                # No matching commands were found in database, stops
                return
            # if context is multiVal
            if row[1] == 'multiVal':
                c.execute(f"SELECT * from multival WHERE name='{name}' COLLATE NOCASE;")
                vals = c.fetchall()
                response = random.choice(vals)
                await message.channel.send(response[1])
                return

            if row[1] != 'onMessage':
                # Commands 'trigger' is not onMessage, stops
                return

            if len(userinput) > 1 and userinput[1] == 'help':
                # Outputs help text if 1st arg is 'help'
                await message.channel.send('Help for ' + name + ':\n' + row[3])

            else:
                # Outputs content of command
                await message.channel.send(row[2])


# Handles 'onJoin' custom commands
@bot.listen('on_member_join')
async def on_member_join(member):
    # Gets all on join commands from customcommands
    c.execute("SELECT * FROM customcommands WHERE context='onJoin'")
    rows = c.fetchall()
    # Adds all custom messages to the intro separated by newlines
    output = 'Welcome to ' + member.guild.name + '!\n'
    for row in rows:
        output += row[2] + '\n'
    # Sends result to users dms
    if member.dm_channel is None:
        await member.create_dm()
    await member.dm_channel.send(output)


# play back the 'on join' messages
@bot.command(name='echo_on_join', hidden=True, alias=['eoj'])
async def echo_on_join(ctx):
    c.execute("SELECT name, value FROM customcommands WHERE context='onJoin'")
    rows = c.fetchall()
    member = ctx.author
    # Adds all custom messages to the intro separated by newlines
    output = f'Welcome to **{member.guild.name}**!\nPlease read the rules in the **rules-and-conduct** channel before posting.\n'
    for row in rows:
        output += f'*{row[0]}*: {row[1]}\n'
    await ctx.send(output)


# return channel type
@bot.command(name="channeltype", hidden=True)
async def channeltype(ctx):
    channel_type = ctx.channel.type
    await ctx.channel.send(channel_type)


# return arg information
@bot.command(name="arginfo", hidden=True)
async def arginfo(ctx, *, args=None):
    if ctx.message.content == "!arginfo":
        await ctx.channel.send("no args")
    await ctx.channel.send("args: " + args + "\narg length: " + str(len(args)))


def main():
    threading.Thread(target=bot.run(token)).start()


if __name__ == "__main__":
    main()
