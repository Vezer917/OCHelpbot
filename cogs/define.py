import os

from discord.ext import commands
import requests


# define uses the Oxford Dictionary API
# - should iterate through different meanings
# - should not respond to offensive words


class Define(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="define", help='Returns the definition of a word.')
    async def define(self, ctx, arg=None):
        if arg is None:
            await ctx.send("What **word** would you like the definition of?")
            word = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                           timeout=60.0)
            arg = word.content

        app_id = os.getenv('DEFINE_ID')
        app_key = os.getenv('DEFINE_KEY')

        endpoint = "entries"
        language_code = "en-us"
        word_id = arg
        url = "https://od-api.oxforddictionaries.com/api/v2/" + endpoint + "/" + language_code + "/" + word_id.lower()
        async with ctx.typing():
            r = requests.get(url, headers={"app_id": app_id, "app_key": app_key})
            p = r.json()

        # print("code {}\n".format(r.status_code))
        # print("text \n" + r.text)
        # print("json \n" + json.dumps(r.json()))

        await ctx.send(f'**{p["word"]}** *{p["results"][0]["lexicalEntries"][0]["lexicalCategory"]["text"]}*: '
                       f'{p["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0]}')


def setup(bot):
    bot.add_cog(Define(bot))
