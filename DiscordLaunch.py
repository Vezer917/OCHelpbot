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
cogs = ['cogs.quiz', 'cogs.courseinfo', 'cogs.help', 'cogs.rolldice', 'cogs.customcommand', 'cogs.links', 'cogs.time']


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


@bot.command(name='it', help='Responds with a random quote from The IT Crowd', hidden=True)
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

    if name is None:
        return

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


# auto emoji reactions
@bot.listen('on_message')
async def on_message(message):
    words = message.content.lower().split()
    for word in words:
        # add sunglasses emoji if someone says "cool" in a message
        if word == "cool":
            await message.add_reaction(u"\U0001F60E")
        # add robot emoji
        if word == "bot":
            await message.add_reaction(u"\U0001F916")
        # custom emoji trial
        # put a backwards slash '\' infront of an emoji and send in discord to get the emoji's ID
        if word == "deb":
            debbed = bot.get_emoji(428621135790473217)
            if debbed is not None:
                await message.add_reaction(debbed)
        if word == "ken" or word == "chidlow":
            kenned = bot.get_emoji(510487098902577153)
            if kenned is not None:
                await message.add_reaction(kenned)
        if word == "alan":
            alaned = bot.get_emoji(428236272973381633)
            if alaned is not None:
                await message.add_reaction(alaned)
        if word == "olga" or word == "however":
            olgad = bot.get_emoji(516694436919377921)
            if olgad is not None:
                await message.add_reaction(olgad)
        if word == "jim" or word == "jn":
            jimmed = bot.get_emoji(537695339973443608)
            if jimmed is not None:
                await message.add_reaction(jimmed)
        # custom autoreaction command here:
        # ie !cc a -> name=ken -> context=autoreact -> return=:kenemoji:
        # problem here is you don't want to query the bot everytime there's a message just to look for autoreacts
        # solution could be job scheduling a list of keywords to react to


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
