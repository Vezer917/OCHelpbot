import random
from discord.ext import commands
import dbcon

conn = dbcon.conn
c = dbcon.c


class ProfQuote(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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
            c.execute(f"SELECT quote, prof FROM profquotes WHERE prof='{args}';")
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
            c.execute("INSERT INTO profquotes VALUES('\"" + quote + "\"', '" + prof + "');")
            conn.commit()
            await ctx.send("Quote added")


def setup(bot):
    bot.add_cog(ProfQuote(bot))
