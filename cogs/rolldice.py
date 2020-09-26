from discord.ext import commands
import random

# The roll dice command takes in a number of dice and sides then returns a number
# Currently, this command is simple and has plenty of room for improvement


class RollDice(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='rolldice',
        help='Rolls dice. \nParameters: !rolldice [no of dice] [no of sides]'
             '\nExample: !rolldice 2 21\nOutput: 13, 17',
        aliases=['rd', 'roll_dice']
    )
    async def roll(self, ctx, number_of_dice: int = 1, number_of_sides: int = 6):
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(', '.join(dice))
        return


def setup(bot):
    bot.add_cog(RollDice(bot))