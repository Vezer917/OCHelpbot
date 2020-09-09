import sqlite3

from discord.ext import commands
import discord
import dbcon

conn = dbcon.conn
c = dbcon.c


# The links command should have the following functionality:
# - Add link
# - See links
#
# Currently the links command has the following:
# - See links for current course specific channel, or topic as specified by user
# - Add link to specified course/topic
# - Delete link


class Links(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='links',
        help='Returns links for a specific course or topic',
        aliases=['l', 'link']
    )
    async def links(self, ctx):
        userinput = ctx.message.content.split(' ')
        # If there is no course specified
        if len(userinput) < 2:
            channelname = ctx.channel.name.split('_')
            name = channelname[0]
            c.execute(f"SELECT course, url, description FROM links WHERE course='{name}' COLLATE NOCASE;")
            info = c.fetchall()
            # If there is no course specified but you are in a course channel (ie 'cosc111_computer-programming')
            if info is not None:
                await ctx.send("*Warning: Follow links at your own risk!*")
                coursename = str.upper(name)
                counter = 0
                embed = discord.Embed(
                    title=coursename,
                    color=0xf03413
                )
                for i in info:
                    embed.add_field(name=f"{i[2]}", value=f"{i[1]}", inline=False)
                    counter += 1
                embed.set_footer(text=f'Total links = {counter}')
                await ctx.send(embed=embed, content=None)
                return
            # no course specified and not a course channel
            else:
                await ctx.send("Please enter '!links' followed by a course code\nEg: !links COSC111")
            return
        # returns the specific course/topic (even if you are in course channel)
        coursename = dbcon.sanitize(userinput[1])
        c.execute(f"SELECT course, url, description FROM links WHERE course='{coursename}' COLLATE NOCASE;")
        info = c.fetchall()
        if info is None:
            await ctx.send(f"No links for {coursename} found")
            return
        await ctx.send("*Warning: Follow links at your own risk!*")
        counter = 0
        embed = discord.Embed(
            title=coursename,
            color=0xf03413
        )
        for i in info:
            embed.add_field(name=f"{i[2]}", value=f"{i[1]}", inline=False)
            counter += 1
        embed.set_footer(text=f"Total links: {counter}")
        # there is a 6000 char limit to embeds
        if len(embed) > 5999:
            print(f'its over 6000! {coursename}')
        await ctx.send(embed=embed, content=None)
        return

    @commands.command(
        name='addlink',
        help='Add a link',
        aliases=['al', 'addlinks', 'addl']
    )
    async def addlink(self, ctx, *, args=None):
        # check to see if private channel exists, if not makes one
        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        if args is None:
            await ctx.send("Please use the syntax '!addlink [COURSE/TOPIC]'")
            return
        course = args
        await ctx.author.dm_channel.send("Please **describe** the link:")
        desc = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        await ctx.author.dm_channel.send("Now give me the **valid** URL:")
        url = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        # validate the URL
        if is_valid_url(url.content) is False:
            await ctx.author.dm_channel.send("Not a valid URL :confused:")
            return
        await ctx.author.dm_channel.send("Creating link...")
        sql = "INSERT INTO links (course, url, description) VALUES (?, ?, ?)"
        c.execute(sql, (course, url.content, desc.content))
        conn.commit()
        await ctx.author.dm_channel.send(f"Link added! :grin: \nType '!links {course}' to see the newly added link!")
        return

    @commands.command(
        name='deletelink',
        help='delete a link',
        aliases=['delink'],
        hidden=True
    )
    async def deletelink(self, ctx, *, args=None):
        # check to see if private channel exists, if not makes one
        if args is None:
            await ctx.send("Please use the syntax '!deletelink [COURSE/TOPIC]'")
            return
        # clean the args to prevent sql injection
        args = dbcon.sanitize(args)
        coursename = args
        c.execute(f"SELECT course, url, description FROM links WHERE course='{coursename}' COLLATE NOCASE;")
        info = c.fetchall()
        if info is None:
            await ctx.send(f"No links for {coursename} found")
            return
        counter = 0
        embed = discord.Embed(
            title=coursename,
            color=0xf03413
        )
        for i in info:
            embed.add_field(name=f"{i[2]}", value=f"{i[1]}", inline=False)
            counter += 1
        embed.set_footer(text=f"Total links: {counter}")
        # there is a 6000 char limit to embeds
        if len(embed) > 5999:
            print(f'its over 6000! {coursename}')
        await ctx.send(embed=embed, content=None)
        await ctx.send("Please tell me the title of the link to delete:"
                       "\n**WARNING: CANNOT BE UNDONE**")
        link = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        link = dbcon.sanitize(link.content)
        c.execute(f"SELECT description FROM links WHERE description='{link}' COLLATE NOCASE IN "
                  f"(SELECT course FROM links WHERE course='{coursename}' COLLATE NOCASE); ")
        verify = c.fetchone()
        if verify is None:
            await ctx.send("Link not found")
            return
        try:
            c.execute(f"DELETE FROM links WHERE course='{coursename}' COLLATE NOCASE AND description='{link}' COLLATE NOCASE;")
            conn.commit()
        except sqlite3.Error as e:
            print(type(e).__name__)
        except:
            await ctx.send("Hmmm.... something went wrong")
            return
        print(f'{ctx.author} Deleted {link} from {coursename}')
        await ctx.author.dm_channel.send(f'"{link}" deleted')
        return


# simple regular expression check (not actual validation)
def is_valid_url(url):
    import re
    regex = re.compile(
        "(([\w]+:)?//)?(([\d\w]|%[a-fA-f\d]{2,2})+(:([\d\w]|%[a-fA-f\d]{2,2})+)?@)?([\d\w][-\d\w]{0,253}[\d\w]\.)"
        "+[\w]{2,63}(:[\d]+)?(/([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)*(\?(&?([-+_~.\d\w]|%[a-fA-f\d]{2,2})=?)*)?"
        "(#([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)?"
    )
    return regex.match(url)


def setup(bot):
    bot.add_cog(Links(bot))
