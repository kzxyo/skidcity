from discord.ext import commands

def isDonor():
    async def predicate(ctx):
        donor = await ctx.bot.db.fetchrow("SELECT * FROM donors WHERE user_id = $1", ctx.author.id)
        if donor:
            return True
        else:
            raise commands.CheckFailure("you are not a donor")
    return commands.check(predicate)