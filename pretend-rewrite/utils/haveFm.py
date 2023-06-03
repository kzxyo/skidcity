from discord.ext import commands

def haveFm():
    async def predicate(ctx):
        fm = await ctx.bot.db.fetchrow("SELECT * FROM fm WHERE user_id = $1", ctx.author.id)
        if fm:
            return True
        else:
            raise commands.CheckFailure("you don't have a fm account linked\nuse `fm link` to link your fm account")
    return commands.check(predicate)