import random
from discord.ext import commands
import dbcon

conn = dbcon.conn
c = dbcon.c
deleteEmoji = '❌'
multiDelete = False


class ProfQuote(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        available_table=(c.fetchall())
        print(available_table);

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
      if  reaction.message.author.bot and reaction.emoji == deleteEmoji:
          channel = await self.bot.fetch_channel((int)(reaction.message.channel.id))
          quoteMessage = reaction.message.content.split("-")
          quote = ""
          prof = ""
          try:
              quote = quoteMessage[0].strip().strip('"')
              prof = quoteMessage[1].strip()
          except IndexError:
              print("Out of bounds in message")
              
          print(quoteMessage)
          print(quote)
          print(prof)
          print(channel)
          print(user)
          
          c.execute(f"SELECT quote FROM profquotes WHERE quote='\"{quote}\"'")
          if c.fetchone() is not None:
              if not multiDelete: #multidelete should bypass the confirmation to delete multiple quotes quickly
                  await channel.send(f"Are you sure you want to delete\n \"{quote}\" from {prof}?\n Type 'yes' to confirm")
                  response = await self.bot.wait_for('message', check=lambda message: message.author == user,
                                        timeout=60.0)
                  response = f'{response.content}'
                  if response == "yes":
                      c.execute(f"DELETE FROM profquotes WHERE quote='\"{quote}\"' COLLATE NOCASE;")
                      conn.commit()
                      await channel.send("Quote from "+ prof + " have been deleted.")
                  else:
                      await channel.send("Delete cancelled");
              else:
                  c.execute(f"DELETE FROM profquotes WHERE quote='\"{quote}\"' COLLATE NOCASE;")
                  conn.commit()
                  await channel.send("Quote from: "+ prof + " have been deleted.")
                      
          else:
              print("No quote found in message")
        

    # do stuff

    @commands.command(
        name='profquote',
        help="Responds with a random profquote\n(You can specify the prof, ie `!profquote Ken`)",
        aliases=['pq', 'profq', 'pquote']
    )
    async def prof_quote(self, ctx, *, args=None):
        if args is None:
            c.execute('SELECT quote, prof FROM profquotes')
        else:
            dbcon.sanitize(args)
            c.execute(f"SELECT quote, prof FROM profquotes WHERE prof='{args}' COLLATE NOCASE;")
        pq = c.fetchall()
        if len(pq) == 0:
            await ctx.send(f"No quote from {args} found :man_shrugging:")
        response = random.choice(pq)
        await ctx.send(str(response[0]) + " - " + str(response[1]))

    @commands.command(
        name='addquote',
        help='Add a profquote',
        aliases=['aq', 'addprofquote', 'addpq']
    )
    async def add_quote(self, ctx):
        await ctx.send("Please tell me who said the quote:\n*Example: Leslie*")
        prof = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                       timeout=60.0)
        prof = prof.content
        await ctx.send("Great, now tell me the quote:\n*Please do not include the quotation marks!*")
        quote = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                        timeout=60.0)
        quote = f'{quote.content}'
        c.execute(f"SELECT quote FROM profquotes WHERE quote='\"{quote}\"'")
        if c.fetchone() is not None:
            await ctx.send("That quote already exists")
        else:
            c.execute(f"INSERT INTO profquotes VALUES('\"{quote}\"', '{prof}');")
            conn.commit()
            await ctx.send("Quote added")
   
    @commands.command(
        name='removequote',
        help='remove a quote',
        aliases=['remquote', 'rq', 'remq']
    )
    @commands.has_permissions(manage_guild=True)
    async def modify_quote(self, ctx):
        await ctx.send("Please tell me who's quote you want to remove:\n Example: Ken*")
        prof = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                       timeout=60.0)
        prof = prof.content
        await ctx.send("Great, now type out the quote exactly:\n*Please do not include the quotation marks on the outside!*")
        quote = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                        timeout=60.0)
        quote = f'{quote.content}'
        c.execute(f"SELECT quote FROM profquotes WHERE quote='\"{quote}\"'")
        if c.fetchone() is not None:
            c.execute(f"DELETE FROM profquotes WHERE quote='\"{quote}\"'")
            conn.commit()
            await ctx.send(quote + " has been deleted.")
        else:
            await ctx.send("There is no quote from that proffessor")
            
    @commands.command(
        name='removeallquote',
        help='remove all quotes from a professor. Gives option to confirm. Should only be available to moderators',
        aliases=['raquote']
    )
    @commands.has_permissions(manage_guild=True)
    async def modify_quote(self, ctx):
        await ctx.send("Please tell who's quote you want to remove:\n Example: Ken*")
        prof = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                       timeout=60.0)
        prof = prof.content
        await ctx.send("Are you sure you want to delete all the quotes from: " + prof + "?\n Type yes to confirm")
        response = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                        timeout=60.0)
        response = f'{response.content}'
        if(response == "yes"):
            c.execute(f"SELECT * FROM profquotes WHERE prof='{prof}' COLLATE NOCASE;")
            if c.fetchone() is not None:
                c.execute(f"DELETE FROM profquotes WHERE prof='{prof}' COLLATE NOCASE;")
                conn.commit()
                await ctx.send("Quotes from: "+ prof + " have been deleted.")
            else:
                await ctx.send("There are no quotes from that proffessor")
        else:
            await ctx.send("You will not delete any quotes today")


def setup(bot):
    bot.add_cog(ProfQuote(bot))
