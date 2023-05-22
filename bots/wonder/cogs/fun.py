import random
import discord
import aiohttp

from discord.ext import commands



class fun(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball', '8b'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def question(self, ctx, *, question):

        responses = ["definitely", "maybe","yes", "no", "as i see it, yes", "factual", "as i see it, no", "idk", "Ok", "Due to your nationality being Bosnian, I cannot answer the question you just asked me.", "🤓", "Fk dem culturally component nkkas onb they is not gng blud 💯🙅‍♂️🤦🏽"]
        embed = discord.Embed(color = 0x2F3136)
        embed.add_field(name = "Question", value = f"{question}")
        embed.add_field(name = "Answer", value = f"{random.choice(responses)}")
        await ctx.reply(embed=embed)

    @commands.command(name = "gayrate", description = "shows how gay you are",aliases = ['gr', 'gay'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def gayrate(self, ctx):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You are {random.randrange(101)}% gay {member.mention}")

    @commands.command(aliases = ['cr', 'cool'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coolrate(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You are {random.randrange(101)}% cool {member.mention}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pp(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"Your pp is {random.randrange(11)} inches {member.mention}")

    @commands.command(aliases = ['cute'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cuterate(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You are {random.randrange(101)}% cute {member.mention}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def punch(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} punches themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} punches {member.mention}")


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kiss(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} kisses themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} kisses {member.mention}")


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lick(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} licks themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} licks {member.mention}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hug(self, ctx, member: discord.Member):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} hugs themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} hugs {member.mention}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bite(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} bites themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} bites {member.mention}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pat(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} pats themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} pats {member.mention}")


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bitches(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You get {random.randrange(21)} bitches {member.mention}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def horny(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You are {random.randrange(101)}% horny {member.mention}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def tickle(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.reply(f"{ctx.author.mention} tickle themselves like a fucking loser")

        else:
            await ctx.reply(f"{ctx.author.mention} tickle {member.mention}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cry(self, ctx, member: discord.Member = None):
        await ctx.reply(f"{member.mention} is crying... 😭 (i almost cared)")


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fatrate(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You weigh {random.randrange(301)} kg {member.mention}")


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def iq(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await ctx.reply(f"You have an IQ of {random.randrange(200)} {member.mention}")
    

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def emojify(self, ctx, *,text):
        emojis = []
        for s in text:
            if s.isdecimal():
                num2emo = {'0':'zero','1':'one','2':'two','3':'three','4':'four','5':'five','6':'six','7':'seven','8':'eight','9':'nine'}
                emojis.append(f':{num2emo.get(s)}:')
            elif s.isalpha():
                emojis.append(f':regional_indicator_{s}:')
            else:
                emojis.append(s)
        await ctx.reply(''.join(emojis))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coinflip(self, ctx):
        choices = ['heads', 'tails']
        rancoin = random.choice(choices)
        await ctx.reply(rancoin)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sus(self, ctx):
        if member == None:
            member = ctx.author

        await ctx.reply(f"You are {random.randrange(101)}% sus 😳 {member.mention}")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def fuck(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
            return await ctx.reply(f"mention someone to fuck them loser")


        await ctx.reply(f"**{ctx.author.name}** fucks **{member.name}** 🍆🍑")


async def setup(bot):
    await bot.add_cog(fun(bot))