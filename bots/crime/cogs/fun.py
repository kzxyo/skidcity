import discord, requests, datetime, button_paginator as pg, random, asyncio, json ; from discord.ui import Button, View ; import time
from discord.ext import commands
from uwuipy import uwuipy
from datetime import datetime
from cogs.utilevents import blacklist
with open("db/config.json") as f:
    data = json.load(f)
    mongo = data["mongo"]

class fun(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 

    @commands.command(description="fun")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def uwu(self, ctx, *, message):
            uwu = uwuipy()
            uwu_message = uwu.uwuify(message)
            await ctx.reply(uwu_message, mention_author=False)
    @uwu.error
    async def uwu_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(color=0xf7f9f8, title="", description="> what do you want me to uwuify?")
            await ctx.reply(embed=embed, mention_author=False)
 

    @commands.command(aliases=['8ball', 'ask'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def question(self, ctx, *, question):
        responses = ["It is certain", "Without a doubt", "You may rely on it", "Yes definitely", "It is decidedly so", "As I see it, yes", "Most likely", "Yes", "Outlook good", "Signs point to yes", "Reply hazy, try again", "Better not tell you now", "Ask again later", "Cannot predict now", "Concentrate and ask again", "Don't count on it", "Outlook not so good", "My sources say no", "Very doubtful", "My reply is no"]
        embed = discord.Embed(color = 0xf7f9f8, description=f"question: {question}\nanswer: {random.choice(responses)}")
        embed.set_footer(text = f"requested by {ctx.author}")
        await ctx.reply(embed=embed)

    @commands.command()
    @blacklist()

    async def two(self, ctx):
         await ctx.reply("HOORAY! 200CMDS")

    @commands.command()
    @blacklist()

    async def cam(self, ctx):
        e = discord.Embed(
            description="XANO OWNS CAM",
            color=0xf7f9f8
        )
        e.set_image(url="https://media.discordapp.net/attachments/1082003523060912138/1084619540501110805/image.png")
        e.set_footer(text="made 3/12/23 / 7:30PM")
        await ctx.send(embed=e)


    @commands.hybrid_command()
    @commands.cooldown(1, 10, commands.BucketType.default)
    @blacklist()
    async def pack(self, ctx, user: discord.Member = commands.Author):

        if user == ctx.author:
            embed = discord.Embed(
                color=0xf7f9f8,
                description="**You fr wanna pack yourself??**",
                timestamp=datetime.now(),
            )
            embed.set_footer(
                text="dont do it my boy",
                icon_url=None,
            )
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)

            return await ctx.reply(embed=embed)
        else:
            cc = [
                "why you still talkin to me nig you smell like expired sea food dust dumb ass nig you hideous as shit you dont know how to run because you got inverted kneecaps dumb ass nig you got that shit as an inherited trait from yo grandmother yo dumb ass nig you got mad at her and started slamming a hammer on the back of her knee to fix that shit hoping it would magically fix yours you dumb ass nig",
                "Shut up nig yo bus driver got sick of you smoking ciggaretes at the back of the school-bus so he recorded you with a Black and White Vintage Camera and got you expelled from school nig you dumb as shit",
                "nope nig that's why yo ass ran away from home and got into an altercation with Team Rocket from Pokemon boy them nigs got to throwing pokeballs at yo ass unleashing all the legendary pokemon just to kill you nig;Sike nig yo dumb ass traded yo Samsung Galaxy Note10 for a Pillow Pet because you always lonely at night nig fuck is you talkin bout",
                "This nigga ugly as shit you fat ass boy you been getting flamed by two donkeys when you walk to the store and one of them smacked you in the forehead fuckboy and then you go to come in with uh ???? and smacked you in the bootycheeks fuckboy you dirty as shit boy everytime you go to school nigga you get bullied by 10 white kids that say you gay behind the bus fuckboy suck my dick nigga unknown as shit nigga named nud you been getting hit by two frozen packs when you walk into the store fuckboy suck my dick unknown ass nigga named nud nigga you my son nigga hold on, ay creedo you can flame this nigga for me? Yeah im in this bitch fuck is you saying nigga my nigga.",
                "thats cool in all my nigga but you're ass is build like my grandma with you're no neck body built bath and body works double or nothing for a barbie girl doll that built like ken stupid ass my nigga. You brush your teeth with the cum from your dad's left cock that was in your mom and aunt's asshole. and your calling me a fuckboy? NIGGA YOURE BUILT LIKE AN ENDERMAN WITH HEIGHT SWAPPED TO WIDTH YOUR ASS CHEEKS LOOK LIKE 2 JIGGLYPUFFS RUBBING AGAINST EACH OTHER FOR \"BREEDING\" TO MAKE A BUZZWOLE EGG. You hack pokemon but you cant hack a new dad my nigga you thought your dad died in minecraft and didnt respawn yet.",
                "I kno ass aint talkin boy you look like a discombobulated toe nail nigga whenever you take a bath your jerk off then the next you smell like ass nasty nigga fuck is you saying nigga you got smacked with a gold fish in the grocery store and smacked the gold fish with fish food nasty bitch boy you ugly as shit fuck is you saying FAT BOY ugly bitch my nigga i caught yo ass slap boxing yo granny with an apple fuck is you saying my nigga when you get horny you jerk off to donkeys fuck is you saying ugly bitch",
                "lil bitchass nigga i know you aint talking to me with that greasy ass mcdonalds french fries lubricated fingers nigga you are dirty as shit you are the cousin of the dirtiest man in the entire fucking word nigga you disgusting as shit nigga your nickname be the human repellant cause no bitches want to be near you dirtyass nigga shut the fuck up with any excuses i know u aint talking to me with that nastyass neckbeard lil redhead headass boy",
            ]
            random.shuffle(cc)
            embed = discord.Embed(color=0xf7f9f8, description=f"**{ctx.author}**: {random.choice(cc)}", timestamp=datetime.now())
            embed.set_footer(text=f"{user} just got violated", icon_url=None)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
            await ctx.reply(embed=embed)
    @commands.command(name='cum', aliases=["jerkoff", "ejaculate", "orgasm"])
    @blacklist()
    async def cum(self, ctx):
            message = await ctx.send(''''
                :ok_hand:            :smile:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8=:punch:=D 
                :trumpet:      :eggplant:''')
            await asyncio.sleep(0.5)
            await message.edit(content='''     :ok_hand:            :smiley:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D 
                :trumpet:      :eggplant:  
        ''')
            await asyncio.sleep(0.5)
            await message.edit(content='''     :ok_hand:            :grimacing:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8=:punch:=D 
                :trumpet:      :eggplant:  
        ''')
            await asyncio.sleep(0.5)
            await message.edit(content='''     :ok_hand:            :persevere:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D 
                :trumpet:      :eggplant:   
        ''')
            await asyncio.sleep(0.5)
            await message.edit(content='''     :ok_hand:            :confounded:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8=:punch:=D 
                :trumpet:      :eggplant: 
        ''')
            await asyncio.sleep(0.5)
            await message.edit(content='''     :ok_hand:            :tired_face:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D 
                :trumpet:      :eggplant:    
                ''')
            await asyncio.sleep(0.5)
            await message.edit(content='''     :ok_hand:            :weary:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8=:punch:= D:sweat_drops:
                :trumpet:      :eggplant:        
        ''')
            await asyncio.sleep(0.5)
            await message.edit(content='''     :ok_hand:            :dizzy_face:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D :sweat_drops:
                :trumpet:      :eggplant:                 :sweat_drops:
        ''')
            await asyncio.sleep(0.5)
            await message.edit(content='''     :ok_hand:            :drooling_face:
    :eggplant: :zzz: :necktie: :eggplant:  :oil:     :nose: :zap: 8==:punch:D :sweat_drops:
                :trumpet:      :eggplant:                 :sweat_drops:
        ''')
            
    @commands.command(help="cuddle with someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def cuddle(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=0xf7f9f8, title="`cuddle <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/cuddle")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8, description=f"*aww how cute! {ctx.author.mention} is cuddling with {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)
          
    @commands.command(help="slap someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def slap(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=0xf7f9f8, title="`slap <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/slap")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8, description=f"*{ctx.author.mention} slapped {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="pat someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def pat(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=0xf7f9f8, title="`pat <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/pat")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8, description=f"*aww how cute! {ctx.author.mention} pat {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="hug someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def hug(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=0xf7f9f8, title="`hug <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/hug")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8, description=f"*aww how cute! {ctx.author.mention} hugged {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="kiss someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def kiss(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=0xf7f9f8, title="`kiss <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/kiss")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8, description=f"*aww how cute! {ctx.author.mention} kissed {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="feed someone?....", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def feed(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=0xf7f9f8, title="`feed <user>`")
            await ctx.send(embed=embed, mention_author=False)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/feed")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8, description=f"*aww how cute! {ctx.author.mention} is feeding {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="tickle someone", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def tickle(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=0xf7f9f8, title="`tickle <user>`")
            await ctx.send(embed=embed)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/tickle")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8, description=f"*aw! look at the flirts! {ctx.author.mention} is tickling {user.mention}*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="cry", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def cry(self, ctx, user: discord.Member=None):
            r = requests.get("http://api.nekos.fun:8080/api/cry")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8, description=f"*aww! {ctx.author.mention} is crying")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="funny", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def laugh(self, ctx, user: discord.Member=None):
            r = requests.get("http://api.nekos.fun:8080/api/laugh")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8)
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="senpai notice meeeee!", usage="[member]", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def poke(self, ctx, user: discord.Member=None):
        if user is None:
            embed=discord.Embed(color=0xf7f9f8, title="`poke <user>`")
            await ctx.send(embed=embed)
        else:
            r = requests.get("http://api.nekos.fun:8080/api/poke")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8, description=f"*aw how cute! {ctx.author.mention} is poking {user.mention}!*")
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(help="b-baka!!!", description="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def baka(self, ctx, user: discord.Member=None):
            r = requests.get("http://api.nekos.fun:8080/api/baka")
            res = r.json()
            em = discord.Embed(color=0xf7f9f8)
            em.set_image(url=res['image'])
            await ctx.reply(embed=em, mention_author=False)


    @commands.command(help="roast anyone")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
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
            "You know they say 90 percent of dust is dead human skin? That's what you are to me.",
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
        embed=discord.Embed(color=0xf7f9f8, description= f"{random.choice(roast_list)}")
        await ctx.reply(embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(fun(bot))