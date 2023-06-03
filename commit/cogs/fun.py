import discord, random, aiohttp, json
from discord import app_commands
from discord.ext import commands

class fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
      
    @commands.command(help="shows your iq")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def iq(self, ctx, user: discord.Member=None):

        if user==None:
            embed=discord.Embed(color=0x2f3136, title="iq test", description= f"{ctx.author.mention} has `{random.randrange(201)}` iq :brain:")
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed=discord.Embed(color=0x2f3136, title="iq test", description= f"{user.mention} has `{random.randrange(201)}` iq :brain:")
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="shows how hot you are")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hot(self, ctx, user: discord.Member=None):

        if user==None:
            embed=discord.Embed(color=0x2f3136, title="hot r8", description= f"{ctx.author.mention} is `{random.randrange(101)}%` hot :hot_face:")
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed=discord.Embed(color=0x2f3136, title="hot r8", description= f"{user.mention} is `{random.randrange(101)}%` hot :hot_face:")
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="shows how many bitches you have")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bitches(self, ctx, user: discord.Member=None):

        if user==None:
            embed=discord.Embed(color=0x2f3136, description= f"{ctx.author.mention} has `{random.randrange(51)}` bitches")
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed=discord.Embed(color=0x2f3136, description= f"{user.mention} has `{random.randrange(51)}` bitches")
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="ask the :8ball: anything", aliases=["8ball"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def eightball(self, ctx, *, question):
        responses  = ["It is certain.",
                    "It is decidedly so.",
                    "Without a doubt.",
                    "Yes - definitely.",
                    "You may rely on it.",
                    "As I see it, yes.",
                    "Most likely.",
                    "Outlook good.",
                    "Yes.",
                    "Signs point to yes.",
                    "Reply hazy, try again.",
                    "Ask again later.",
                    "Better not tell you now.",
                    "Cannot predict now.",
                    "Concentrate and ask again.",
                    "Don't count on it.",
                    "My reply is no.",
                    "My sources say no.",
                    "Outlook not so good.",
                    "Very doubtful.",
                    "Maybe."]
        embed=discord.Embed(color=0x2f3136, description= f" :8ball: {random.choice(responses)}")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="make the bot say anything")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def say(self, ctx, *, text):
        message = ctx.message
        await message.delete()

        embed=discord.Embed(color=0x2f3136, title=f"{ctx.author} said...",description=f"{text}")
        await ctx.send(embed=embed)

    @commands.command(help="roast anyone")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def roast(self, ctx):
        roast_list = [
            "at least my mom pretends to love me",
            "Bards will chant parables of your legendary stupidity for centuries, You",
            "Don't play hard to get when you are hard to want",
            "Don't you worry your pretty little head about it. The operative word being little. Not pretty.",
            "Get a damn life you uncultured cranberry fucknut.",
            "God wasted a good asshole when he put teeth in your mouth",
            "Goddamn did your parents dodge a bullet when they abandoned you.",
            "I bet your dick is an innie and your belly button an outtie.",
            "I can't even call you Fucking Ugly, because Nature has already beaten me to it.",
            "I cant wait to forget you.",
            "I curse the vagina that farted you out.",
            "I don't have the time, or the crayons to explain this to you.",
            "I FART IN YOUR GENERAL DIRECTION",
            "I fucking hate the way you laugh.",
            "I hope you win the lottery and lose your ticket.",
            "I once smelled a dog fart that had more cunning, personality, and charm than you.",
            "I shouldn't roast you, I can't imagine the pain you go through with that face!",
            "I want to call you a douche, but that would be unfair and unrealistic. Douches are often found near vaginas.",
            "I wonder if you'd be able to speak more clearly if your parents were second cousins instead of first.",
            "I would call you a cunt, but you lack the warmth or the depth.",
            "I would challenge you to a battle of wits, but it seems you come unarmed",
            "I would rather be friends with Ajit Pai than you.",
            "I'd love to stay and chat but I'd rather have type-2 diabetes",
            "I'm just surprised you haven't yet retired from being a butt pirate.",
            "I'm not mad. I'm just... disappointed.",
            "I've never met someone who's at once so thoughtless, selfish, and uncaring of other people's interests, while also having such lame and boring interests of his own. You don't have friends, because you shouldn't.",
            "Im betting your keyboard is filthy as fuck now from all that Cheeto-dust finger typing, you goddamn weaboo shut in. ",
            "If 'unenthusiastic handjob' had a face, your profile picture would be it.",
            "If there was a single intelligent thought in your head it would have died from loneliness.",
            "If you were a potato you'd be a stupid potato.",
            "If you were an inanimate object, you'd be a participation trophy.",
            "If you where any stupider we'd have to water you",
            "If you're dad wasn't so much of a pussy, he'd have come out of the closet before he had you.",
            "It's a joke, not a dick. You don't have to take it so hard.",
            "Jesus Christ it looks like your face was on fire and someone tried to put it out with an ice pick",
            "May the fleas of ten thousand camels live happily upon your buttocks",
            "Maybe if you eat all that makeup you will be beautiful on the inside.",
            "Mr. Rogers would be disappointed in you.",
            "Next time, don't take a laxative before you type because you just took a steaming stinking dump right on the page. Now wipe that shit up and don't fuck it up like your life.",
            "Not even your dog loves you. He's just faking it.",
            "Once upon a time, Santa Clause was asked what he thought of your mom, your sister and your grandma, and thus his catchphrase was born.",
            "People don't even pity you.",
            "People like you are the reason God doesn't talk to us anymore",
            "Take my lowest priority and put yourself beneath it.",
            "The IQ test only goes down to zero but you make a really compelling case for negative numbers",
            "the only thing you're fucking is natural selection",
            "There are two ugly people in this chat, and you're both of them.",
            "There will never be enough middle fingers in this world for You",
            "They don't make a short enough bus in the Continental United States for a person like you.",
            "Those aren't acne scars, those are marks from the hanger.",
            "Twelve must be difficult for you. I dont mean BEING twelve, I mean that being your IQ.",
            "We all dislike you, but not quite enough that we bother to think about you.",
            "Were you born a cunt, or is it something you have to recommit yourself to every morning?",
            "What's the difference between three dicks and a joke? You can't take a joke.",
            "When you die, people will struggle to think of nice things to say about you.",
            "Where'd ya get those pants? The toilet store?",
            "Why do you sound like you suck too many cocks?",
            "Why dont you crawl back to whatever micro-organism cesspool you came from, and try not to breath any of our oxygen on the way there",
            "WHY SHOULD I LISTEN TO YOU ARE SO FAT THAT YOU CAN'T POO OR PEE YOU STINK LYRE YOU HAVE A CRUSH ON POO",
            "You are a pizza burn on the roof of the world's mouth.",
            "You are a stupid.",
            "You are dumber than a block of wood and not nearly as useful",
            "You are like the end piece of bread in a loaf, everyone touches you but no one wants you",
            "You have a face made for radio",
            "You have more dick in your personality than you do in your pants",
            "You have the face of a bulldog licking piss off a stinging nettle.",
            "You know they say 90% of dust is dead human skin? That's what you are to me.",
            "You know, one of the many, many things that confuses me about you is that you remain unmurdered.",
            "You look like your father would be disappointed in you. If he stayed.",
            "You losing your virginity is like a summer squash growing in the middle of winter. Never happening.",
            "You may think people like being around you- but remember this: there is a difference between being liked and being tolerated.",
            "You might want to get a colonoscopy for all that butthurt",
            "You need to go up to your daddy, get on your knees and apologize to each and every brother and sister that didn't make it to your mother's egg before you",
            "You should put a condom on your head, because if you're going to act like a dick you better dress like one too.",
            "You stuck up, half-witted, scruffy looking nerf herder!",
            "You were birthed out your mothers ass because her cunt was too busy.",
            "You're an example of why animals eat their young.",
            "You're impossible to underestimate",
            "You're kinda like Rapunzel except instead of letting down your hair you let down everyone in your life",
            "You're like a penny on the floor of a public restroom - filthy, untouchable and practically worthless.",
            "You're like a square blade, all edge and no point.",
            "You're looking well for a man twice your age! Any word on the aneurism?",
            "You're not pretty enough to be this dumb",
            "You're objectively unattractive.",
            "You're so dense, light bends around you.",
            "You're so salty you would sink in the Dead Sea",
            "You're so stupid you couldn't pour piss out of a boot if the directions were written on the heel",
            "You're such a pussy that fucking you wouldnt be gay.",
            "You're ugly when you cry.",
            "Your birth certificate is an apology letter from the abortion clinic.",
            "Your memes are trash.",
            "Your mother may have told you that you could be anything you wanted, but a douchebag wasn't what she meant.",
            "Your mother was a hamster, and your father reeks of elderberries!",
            "Your penis is smaller than the payment a homeless orphan in Mongolia received for stitching my shoes."
    ]
        
        embed=discord.Embed(color=0x2f3136, description= f"{random.choice(roast_list)}")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="send a random picture of a cat")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://www.reddit.com/r/cat.json") as r:
                cat = await r.json()
                embed = discord.Embed(color=0x2f3136, title="kitty")
                embed.set_image(url=cat["data"]["children"][random.randint(0, 25)]["data"]["url"])
                await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="send a random picture of a dog")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://www.reddit.com/r/dog.json") as r:
                dog = await r.json()
                embed = discord.Embed(color=0x2f3136, title="doggo")
                embed.set_image(url=dog["data"]["children"][random.randint(0, 25)]["data"]["url"])
                await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="send a random meme")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def meme(self, ctx):
       async with aiohttp.ClientSession() as cs:
          async with cs.get('https://api.popcat.xyz/meme') as response3: 
           data3 = await response3.json()
 
           image = data3["image"]
           title = data3["title"]
           url = data3["url"]
           upvotes = data3["upvotes"]
           comments = data3["comments"]
           embed3 = discord.Embed(color=0x2f3136)
           embed3.set_image(url=image)
           e = discord.Embed(color=0x2f3136, description=f"[{title}]({url})")
           e.set_footer(text=f"❤️ {upvotes}  💬 {comments}")
           await ctx.reply(embeds=[embed3, e], mention_author=False)

    @commands.command(help="shows how gay you are")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def howgay(self, ctx, user: discord.Member=None):

        if user==None:
            embed=discord.Embed(color=0x2f3136, title="gay r8", description= f"{ctx.author.mention} is `{random.randrange(201)}%` gay")
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed=discord.Embed(color=0x2f3136, title="gay r8", description= f"{user.mention} is `{random.randrange(201)}%` gay")
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="shows how cool you are")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def howcool(self, ctx, user: discord.Member=None):

        if user==None:
            embed=discord.Embed(color=0x2f3136, title="cool r8", description= f"{ctx.author.mention} is `{random.randrange(201)}%` cool")
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed=discord.Embed(color=0x2f3136, title="cool r8", description= f"{user.mention} is `{random.randrange(201)}%` cool")
            await ctx.reply(embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(fun(bot))