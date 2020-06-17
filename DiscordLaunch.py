# DiscordLaunch.py
import math
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
cogs = ['cogs.quiz', 'cogs.courseinfo', 'cogs.help', 'cogs.rolldice']


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    for cog in cogs:
        bot.load_extension(cog)

    return


@bot.command(name='profquote', help='Responds with a random profquote')
async def prof_quote(ctx):
    userinput = ctx.message.content.split(' ')
    if len(userinput) < 2:
        c.execute('SELECT quote, prof FROM profquotes')
    else:
        c.execute("SELECT quote, prof FROM profquotes WHERE prof='" + userinput[1] + "';")
    pq = c.fetchall()
    response = random.choice(pq)
    await ctx.send(str(response[0]) + " - " + str(response[1]))


@bot.command(name='addquote', help='Add a profquote')
async def add_quote(ctx):
    userinput = ctx.message.content.split(' ')
    if len(userinput) < 3:
        # outputted if addquote is used incorrectly
        await ctx.send(
            "To add a profquote, follow this syntax:\n"
            "!addquote Leslie \"I only sniff markers because I like the smell\"\n"
        )
    else:
        quote = ctx.message.content.split('"')
        c.execute("SELECT quote FROM profquotes WHERE quote='\"" + str(quote[1]) + "\"'")
        if c.fetchone() is not None:
            await ctx.send("That quote already exists")
        else:
            c.execute("INSERT INTO profquotes VALUES('\"" + str(quote[1]) + "\"', '" + str(userinput[1]) + "');")
            conn.commit()
            await ctx.send("Quote added")


@bot.command(name='create-channel', aliases=['cc'])
@commands.has_role('admin')
async def create_channel(ctx, channel_name: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


# use this command to set admins for the flask portal
# only a guild admin can use this command
@bot.command(name='makeAdmin')
@commands.has_role('admin')
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
@bot.command(name='register', help='Allows you to input information about yourself into the bot')
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


@bot.command(name='whoami', help='Returns the information you have given the bot')
async def who(ctx):
    c.execute("SELECT fname, program, year FROM users WHERE id='" + str(ctx.author.id) + "';")
    await ctx.channel.send(c.fetchone())


@bot.command(name='whois', help='Returns info from bot')
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


@bot.command(name='links', help='Sends a list of useful links about a specified class')
async def links(ctx):
    userinput = ctx.message.content.split(' ')

    if len(userinput) < 2:
        # Displayed when command is not correctly inputted
        await ctx.channel.send('Syntax for links: !links [Course acronym eg. COSC111]')
        return

    c.execute("SELECT content FROM links WHERE class='" + userinput[1].upper() + "';")
    curr = c.fetchone()

    if curr is None:
        # Printed out when no links match the arguments class
        await ctx.channel.send('Sorry, nothing was found in the database with the class: ' + userinput[1])
        return
    else:
        message = "Links for " + userinput[1] + ":\n"
        while curr is not None:
            message += curr[0] + '\n'
            curr = c.fetchone()

    await ctx.channel.send(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


@bot.command(name='it', help='Responds with a random quote from The IT Crowd')
async def it_crowd(ctx):
    it_crowd_quotes = [
        'There was a fire...*at a Sea Parks?*',
        'Balloons explode, Jen. They explode suddenly, and unexpectedly. '
        'They are filled with the capacity to give me a little fright, and I find that unbearable.',
        'Shut up, do what I tell you, I\'m not interested; these are just some of the things you\'ll be hearing if you answer this ad.'
        'I\'m an idiot and I don\'t care about anyone but myself. P.S. No dogs!',
        (
            'You wouldn\'t steal a handbag. You wouldn\'t steal a car. You wouldn\'t steal a baby. You wouldn\'t shoot a policeman. '
            'And then steal his helmet. You wouldn\'t go to the toilet in his helmet. And then send it to the policeman\'s grieving widow. '
            'And then steal it again! Downloading films is stealing. If you do it, you will face the consequences.'
        ),

    ]
    response = random.choice(it_crowd_quotes)
    await ctx.send(response)


# handles 'onMessage' custom commands
@bot.listen('on_message')
async def on_message(message):
    if message.author.bot:
        # Stops it from replying to bots
        return

    userinput = message.content.split(' ')
    name = userinput[0]

    if name[0] == '!':
        # Removes '!' from beginning of command
        name = name[1:]

        # Checks for a match in the custom commands table
        c.execute("SELECT * FROM customcommands WHERE name='" + name + "';")
        row = c.fetchone()

        if row is None:
            # No matching commands were found in database, stops
            return

        if row[1] != 'onMessage':
            # Commands 'trigger' is not onMessage, stops
            return

        if len(userinput) > 1 and userinput[1] == 'help':
            # Outputs help text if 1st arg is 'help'
            await message.channel.send('Help for ' + name + ':\n' + row[3])
        # TODO:
        # This is where the code for the multiple returns would go if it existed
        # IE custom quotes
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


@bot.command(name='pi', help='Return Pi to the n decimal points')
async def pi(ctx):
    """
    prints PI to the specified int
    """
    message = ctx.message.content.split(' ')
    if len(message) < 2:
        await ctx.channel.send('3.14\nAdd a number after !pi to specify how many decimal points')
    else:
        somepi = str(round(math.pi, message[1]))
        await ctx.channel.send(somepi)


# auto emoji reactions
@bot.listen('on_message')
async def on_message(message):
    # add sunglasses emoji if someone says "cool" in a message
    if "cool" in message.content.lower():
        await message.add_reaction(u"\U0001F60E")
    # add robot emoji
    if "bot" in message.content.lower():
        await message.add_reaction(u"\U0001F916")
    # custom emoji trial
    # put a backwards slash '\' infront of an emoji and send to get the emoji's ID
    if "deb" in message.content.lower():
        debbed = bot.get_emoji(428621135790473217)
        if debbed is not None:
            await message.add_reaction(debbed)


# return channel type
@bot.command(name="channeltype", hidden=True)
async def channeltype(ctx):
    channel_type = ctx.channel.type
    await ctx.channel.send(channel_type)


def main():
    threading.Thread(target=bot.run(token)).start()


if __name__ == "__main__":
    main()
