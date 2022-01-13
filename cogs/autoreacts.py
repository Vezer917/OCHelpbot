from discord.ext import commands
import discord

# The auto react listener adds reactions to messages when they contain certain key words
# This can be further expanded to require multiple combinations of words
# Can be used to solve math equations, or to feel more interactive


class AutoReact(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # auto emoji reactions
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            # Stops it from replying to bots
            return
        words = message.content.lower().split()
        for word in words:
            # HARDCODED EMOJIS
            # ================
            if word == "alien":
                await message.add_reaction(u"\U0001F47D")
            if word == "birthday":
                await message.add_reaction(u"\U0001F382")
            if word == "automaton" or word == "robot":
                await message.add_reaction(u"\U0001F916")
            if word == "clown":
                await message.add_reaction(u"\U0001F921")
            if word == "cool":
                await message.add_reaction(u"\U0001F60E")
            if word == "cookie":
                await message.add_reaction(u"\U0001F36A")
            if word == "halloween" or word == "pumpkin":
                await message.add_reaction(u"\U0001F383")
            if word == "nerd":
                await message.add_reaction(u"\U0001F913")
            if word == "pizza":
                await message.add_reaction(u"\U0001F355")
            if word == "rocket" or word == "elon":
                await message.add_reaction(u"\U0001F680")
            # SERVER SPECIFIC EMOJIS
            # ======================
            # put a backwards slash '\' infront of an emoji and send in discord to get the emoji's ID
            if word == "alan":
                alaned = self.bot.get_emoji(428236272973381633)
                if alaned is not None:
                    await message.add_reaction(alaned)
            if word == "aliens":
                aliens = self.bot.get_emoji(428621442100363274)
                if aliens is not None:
                    await message.add_reaction(aliens)
            if word == "deb":
                debbed = self.bot.get_emoji(428621135790473217)
                if debbed is not None:
                    await message.add_reaction(debbed)
                await message.add_reaction(u"\U0001F47D")
            if word == "fritter":
                frit = self.bot.get_emoji(760298475014586398)
                if frit is not None:
                    await message.add_reaction(frit)
            if word == "fritted" or word == "frit" or word == "fritt":
                fritted = self.bot.get_emoji(760295741633069056)
                if fritted is not None:
                    await message.add_reaction(fritted)
            if word == "jim" or word == "jn":
                jimmed = self.bot.get_emoji(537695339973443608)
                if jimmed is not None:
                    await message.add_reaction(jimmed)
            if word == "ken" or word == "chidlow":
                kenned = self.bot.get_emoji(510487098902577153)
                if kenned is not None:
                    await message.add_reaction(kenned)
            if word == "linux":
                lin = self.bot.get_emoji(759599562124951603)
                if lin is not None:
                    await message.add_reaction(lin)
            if word == "olga" or word == "however":
                olgad = self.bot.get_emoji(516694436919377921)
                if olgad is not None:
                    await message.add_reaction(olgad)
            if word == "python":
                py = self.bot.get_emoji(742823114651730041)
                if py is not None:
                    await message.add_reaction(py)
            if word == "sentient" or word == "self-aware":
                sentient = self.bot.get_emoji(759478319829483576)
                if sentient is not None:
                    await message.add_reaction(sentient)
            if word == "youry" or word == "youry.":
                yuried = self.bot.get_emoji(760297062104301570)
                if yuried is not None:
                    await message.add_reaction(yuried)
            if word == "covid" or word == "omnicron" or word == "omicron":
                megatron = self.bot.get_emoji(930950428965871658)
                if megatron is not None:
                    await message.add_reaction(megatron)


def setup(bot):
    bot.add_cog(AutoReact(bot))
