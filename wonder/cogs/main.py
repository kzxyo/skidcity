import discord
import confighandler
import lastfmhandler
from discord.ext import commands
import userhandler
import time
import os
import re
import ast
import json
import random
import urllib
import inspect
import base64
import io
import asyncio
import aiohttp
import jishaku
import psutil
import datetime
import giphy_client
import aiosqlite
import asyncpg
from io import BytesIO
from discord import ui
from pyfiglet import Figlet
from asyncio import sleep
from urllib.request import urlopen
from discord.ext import tasks
from discord.ui import Button, View
from giphy_client.rest import ApiException
from PIL import Image
from PIL import ImageFilter
from cogs.lastfm import get_parts, to_object, embed_replacement



def get_parts(params):
    params=params.replace('{embed}', '')
    return [p[1:][:-1] for p in params.split('$v')]

async def to_object(params):

    x={}
    fields=[]
    content=None
    view=discord.ui.View()

    for part in get_parts(params):
        
        if part.startswith('content:'):
            content=part[len('content:'):]

        if part.startswith('attach:'):
            file=part[len('attach:')]
          
        if part.startswith('title:'):
            x['title']=part[len('title:'):]
        
        if part.startswith('description:'):
            x['description']=part[len('description:'):]

        if part.startswith('footer:'):
            x['footer']=part[len('footer:'):]

        if part.startswith('color:'):
            try:
                x['color']=int(part[len('color:'):].strip('#').strip(), 16)
            except:
                x['color']=0x2f3136

        if part.startswith('image:'):
            x['image']={'url': part[len('image:'):]}

        if part.startswith('thumbnail:'):
            x['thumbnail']={'url': part[len('thumbnail:'):]}
        
        if part.startswith('author:'):
            z=part[len('author:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            try:
                url=z[2] if z[2] else None
            except:
                url=None

            x['author']={'name': name}
            if icon_url:
                x['author']['icon_url']=icon_url
            if url:
                x['author']['url']=url

        if part.startswith('field:'):
            z=part[len('field:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                value=z[1] if z[1] else None
            except:
                value=None
            try:
                inline=z[2] if z[2] else True
            except:
                inline=True

            if isinstance(inline, str):
                if inline == 'true':
                    inline=True

                elif inline == 'false':
                    inline=False

            fields.append({'name': name, 'value': value, 'inline': inline})

        if part.startswith('footer:'):
            z=part[len('footer:'):].split(' && ')
            try:
                text=z[0] if z[0] else None
            except:
                text=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            x['footer']={'text': text}
            if icon_url:
                x['footer']['icon_url']=icon_url
                
        if part.startswith('button:'):
            z=part[len('button:'):].split(' && ')
            try:
                label=z[0] if z[0] else None
            except:
                label='no label'
            try:
                url=z[1] if z[1] else None
            except:
                url='https://none.none'
            try:
                emoji=z[2] if z[2] else None
            except:
                emoji=None
                
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=label, url=url, emoji=emoji))
            
    if not x: embed=None
    else:
        x['fields']=fields
        embed=discord.Embed.from_dict(x)
    return content, embed, view


async def embed_replacement(user, params):

    if '{user}' in params:
        params=params.replace('{user}', user)
    if '{user.mention}' in params:
        params=params.replace('{user.mention}', user.mention)
    if '{user.name}' in params:
        params=params.replace('{user.name}', user.name)
    if '{user.avatar}' in params:
        params=params.replace('{user.avatar}', user.display_avatar.url)
    if '{user.joined_at}' in params:
        params=params.replace('{user.joined_at}', discord.utils.format_dt(user.joined_at, style='R'))
    if '{user.created_at}' in params:
        params=params.replace('{user.created_at}', discord.utils.format_dt(user.created_at, style='R'))
    if '{user.discriminator}' in params:
        params=params.replace('{user.discriminator}', user.discriminator)
    if '{guild.name}' in params:
        params=params.replace('{guild.name}', user.guild.name)
    if '{guild.count}' in params:
        params=params.replace('{guild.count}', str(user.guild.member_count))
    if '{guild.count.format}' in params:
        params=params.replace('{guild.count.format}', ordinal(len(user.guild.members)))
    if '{guild.id}' in params:
        params=params.replace('{guild.id}', user.guild.id)
    if '{guild.created_at}' in params:
        params=params.replace('{guild.created_at}', discord.utils.format_dt(user.guild.created_at, style='R'))
    if '{guild.boost_count}' in params:
        params=params.replace('{guild.boost_count}', str(user.guild.premium_subscription_count))
    if '{guild.booster_count}' in params:
        params=params.replace('{guild.booster_count}', str(len(user.guild.premium_subscribers)))
    if '{guild.boost_count.format}' in params:
        params=params.replace('{guild.boost_count.format}', ordinal(str(len(user.guild.premium_subscriber_count))))
    if '{guild.booster_count.format}' in params:
        params=params.replace('{guild.booster_count.format}', ordinal(str(len(user.guild.premium_subscriber_count))))
    if '{guild.boost_tier}' in params:
        params=params.replace('{guild.boost_tier}', str(user.guild.premium_tier))
    if '{guild.icon}' in params:
        if user.guild.icon:
            params=params.replace('{guild.icon}', user.guild.icon.url)
        else:
            params=params.replace('{guild.icon}', '')
    return params

intents = discord.Intents.all()

DEFAULT_PREFIX = "$"


async def get_prefix(bot, message):
    async with aiosqlite.connect("prefixs.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS prefixs (prefix TEXT, guild INTEGER)")
            await cursor.execute("SELECT prefix FROM prefixs WHERE guild = ?", (message.guild.id,))
            data = await cursor.fetchone()
            if data:
                return data
            else:
                return "$"

async def get_user_prefix(bot, message):
    async with aiosqlite.connect("userprefixes.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT prefix FROM userprefixes WHERE user = ?", (message.author.id,))
                data = await cursor.fetchone()
                if data:
                    return data
                else:
                    return "$"


bot = commands.Bot(command_prefix = get_prefix, intents = intents, case_insensitive = True)
confighandler.config = confighandler.readconfig()
userhandler.users.update(userhandler.read_db())

bot.remove_command("help")

snipe_message_author = None
snipe_message_content = None


fig = Figlet(font='standard')  # Change fonts here, try 'banner' for readability
fig_small = Figlet(font='small')

cogs = ['cogs.utility',
        'cogs.moderation',
        'cogs.owner',
        'cogs.github',
        'cogs.google',
        'cogs.afk',
        'cogs.boosters',
        'cogs.autoresponder',
        'cogs.lastfm',
        'cogs.autoreact',
        'cogs.usernames',
        'cogs.chatfilter',
        'cogs.forcenickname',
        'cogs.imageonly',
        'cogs.voicemaster',
        'cogs.autorole',
        'cogs.fun',
        'jishaku']

punch_gifs = [
    'https://c.tenor.com/EfhPfbG0hnMAAAAC/slap-handa-seishuu.gif', 
    'https://c.tenor.com/5AsLKQTjbJ4AAAAC/kasumi-love-live.gif', 
    'https://c.tenor.com/SwMgGqBirvcAAAAC/saki-saki-kanojo-mo-kanojo.gif', 
    'https://c.tenor.com/EdV_frZ4e_QAAAAC/anime-naruto.gif', 
    'https://c.tenor.com/Ws6Dm1ZW_vMAAAAC/girl-slap.gif']
punch_names = ['punches you']

kiss_gifs = [
    'https://c.tenor.com/AtcFtesvEcEAAAAd/kissing-anime.gif', 
    'https://c.tenor.com/16MBIsjDDYcAAAAC/love-cheek.gif', 
    'https://c.tenor.com/wDYWzpOTKgQAAAAC/anime-kiss.gif', 
    'https://c.tenor.com/Fyq9izHlreQAAAAC/my-little-monster-haru-yoshida.gif', 
    'https://c.tenor.com/vberBgo__S4AAAAC/naruko-anime.gif', 
    'https://c.tenor.com/lYKyQXGYvBkAAAAC/oreshura-kiss.gif']
kiss_names = ['kisses you']

slap_gifs = ['https://c.tenor.com/eU5H6GbVjrcAAAAC/slap-jjk.gif', 'https://c.tenor.com/UDo0WPttiRsAAAAd/bunny-girl-slap.gif', 'https://c.tenor.com/BYu41fLSstAAAAAC/when-you-cant-accept-reality-slap.gif', 'https://c.tenor.com/PeJyQRCSHHkAAAAC/saki-saki-mukai-naoya.gif', 'https://c.tenor.com/rVXByOZKidMAAAAd/anime-slap.gif']
slap_names = ['slaps you']
dog_gifs = ['https://c.tenor.com/uj4Cnt7RVE0AAAAS/fatdog-dog.gif', 'https://c.tenor.com/5LT51B0DSIoAAAAC/funny-animals-dog.gif', 'https://c.tenor.com/2rm6zUADvlgAAAAd/dog-serious.gif', 'https://c.tenor.com/sTLtxR40RAwAAAAC/happymonday-cute.gif', 'https://c.tenor.com/JMv_beVhW98AAAAC/perrete.gif', 'https://c.tenor.com/S_YBQlL9P-MAAAAd/swing-puppies.gif']
pat_names = ['pats you']
pat_gifs = ['https://c.tenor.com/E6fMkQRZBdIAAAAC/kanna-kamui-pat.gif', 'https://c.tenor.com/rZRQ6gSf128AAAAC/anime-good-girl.gif', 'https://c.tenor.com/wLqFGYigJuIAAAAC/mai-sakurajima.gif', 'https://c.tenor.com/N41zKEDABuUAAAAC/anime-head-pat-anime-pat.gif', 'https://c.tenor.com/Y7B6npa9mXcAAAAC/rikka-head-pat-pat-on-head.gif', 'https://c.tenor.com/9R7fzXGeRe8AAAAC/fantasista-doll-anime.gif', 'https://c.tenor.com/Av63tpT8Y14AAAAC/pat-head.gif']
hug_gifs = ['https://c.tenor.com/9e1aE_xBLCsAAAAC/anime-hug.gif', 'https://c.tenor.com/xgVPw2QK5n8AAAAC/sakura-quest-anime.gif', 'https://c.tenor.com/Ct4bdr2ZGeAAAAAC/teria-wang-kishuku-gakkou-no-juliet.gif', 'https://c.tenor.com/rQ2QQQ9Wu_MAAAAC/anime-cute.gif', 'https://c.tenor.com/qF7mO4nnL0sAAAAC/abra%C3%A7o-hug.gif', 'https://c.tenor.com/22VxM2JL_r0AAAAd/hug-sad.gif', 'https://c.tenor.com/-3I0yCd6L6AAAAAC/anime-hug-anime.gif', 'https://c.tenor.com/2lr9uM5JmPQAAAAC/hug-anime-hug.gif']
hug_names = ['hugs you']
bite_gifs = ['https://c.tenor.com/nkNsOraAx4AAAAAC/anime-bite.gif', 'https://c.tenor.com/IKDf1NMrzsIAAAAC/anime-acchi-kocchi.gif', 'https://c.tenor.com/TX6YHUnHJk4AAAAC/mao-amatsuka-gj-bu.gif', 'https://c.tenor.com/4j3hMz-dUz0AAAAC/anime-love.gif', 'https://c.tenor.com/1egHkU3e_8cAAAAC/girl-bite.gif', 'https://c.tenor.com/8UjO54apiUIAAAAC/gjbu-bite.gif', 'https://c.tenor.com/aKzAQ_cFsFEAAAAC/arms-bite.gif']
bite_names = ['bites you']
tickle_gifs = ['https://c.tenor.com/PXL1ONAO9CEAAAAC/tickle-laugh.gif', 'https://c.tenor.com/0UY84zQWda8AAAAC/laugh-droll.gif', 'https://c.tenor.com/FN4yEyW6Ft4AAAAC/kaichou-wa-maid-sama-love-blow.gif', 'https://c.tenor.com/L5-ABrIwrksAAAAC/tickle-anime.gif', 'https://c.tenor.com/sa1QuA9GFaoAAAAC/anime-tickle.gif', 'https://c.tenor.com/WBwonvADeCoAAAAC/mareva-tickle.gif']
tickle_names = ['tickles you']
cry_names = ['is crying']
cry_gifs = ['https://c.tenor.com/q9V98YHPZX4AAAAC/anime-umaru.gif', 'https://c.tenor.com/Q0HUwg81A_0AAAAd/anime-cry.gif', 'https://c.tenor.com/V68-MgqFCdEAAAAC/kaoruko-moeta-comic-girls.gif', 'https://c.tenor.com/N2qSCBkdracAAAAC/neko-anime.gif', 'https://c.tenor.com/tK-bs8K6ZQIAAAAd/remi-horimiya.gif', 'https://c.tenor.com/NMiID29TUvIAAAAC/hunter-x-hunter-gon-freecs.gif']
koala_gifs = ['https://c.tenor.com/gjwqBqcRP0oAAAAC/hug-koala.gif', 'https://c.tenor.com/rZu8jF2NAMoAAAAC/koala-petting.gif', 'https://c.tenor.com/B7520uQ1ftgAAAAd/dont-worry-always-be-happy-cool.gif', 'https://c.tenor.com/qS28kUgsoJIAAAAd/good-night.gif', 'https://c.tenor.com/kRAqeTlp1YgAAAAd/sleeping-koalas101.gif', ]
cat_gifs = ['https://c.tenor.com/ZhfMGWrmCTcAAAAC/cute-kitty-best-kitty.gif', 'https://c.tenor.com/2v1aDCelTJgAAAAC/cat-cats.gif', 'https://c.tenor.com/P9DFtD3HjcwAAAAd/cat-cats-love.gif', 'https://c.tenor.com/Ao9O4SGI-cQAAAAd/sleep-cat-two-cat.gif', 'https://c.tenor.com/uzWDSSLMCmkAAAAd/cute-cat-oh-yeah.gif', 'https://c.tenor.com/D3Owbj5xGUYAAAAC/cat-cats.gif', 'https://c.tenor.com/e_cOg0wWyQUAAAAd/cat-finger.gif', 'https://c.tenor.com/qKFNYB3HB9YAAAAC/cat-tiktok.gif']
shoot_names = ['pulls his gun out <a:uziyea:966066855376744508>']
shoot_gifs = ['https://c.tenor.com/Vja2MkojIgsAAAAC/anime-gun.gif', 'https://c.tenor.com/RdfB0I6L0FIAAAAC/anime-triela.gif', 'https://c.tenor.com/HrdHCfxprF8AAAAC/alucard-hellsing.gif', 'https://c.tenor.com/OF_1Ve7AqxgAAAAC/reisen-anime.gif', 'https://c.tenor.com/FJoZJt6BcAIAAAAC/anime-in-the-feels.gif', 'https://c.tenor.com/Pq3EQbsynG8AAAAd/fire-power.gif', 'https://c.tenor.com/f2aJEoV95rMAAAAC/anime-shot.gif']
roasts = ['The village called. They’d like their idiot back. You better get going.', 'You have the right to remain silent because whatever you say will probably be stupid anyway.', 'I was going to give you a nasty look but I see that you’ve already got one.', 'You’re about as useful as an ashtray on a motorcycle.', ' I believed in evolution until I met you.']
panda_gifs = ['https://c.tenor.com/nOYJcoyj8uIAAAAd/panda-cute.gif', 'https://c.tenor.com/UoVewZBW_owAAAAd/gif.gif', 'https://c.tenor.com/xaJrTrfiRcEAAAAd/happy-panda-bamboo.gif', 'https://c.tenor.com/HYkhxgm-_hEAAAAd/panda-slide.gif', 'https://c.tenor.com/3OMzo-QSVqEAAAAd/baby-hug.gif', 'https://c.tenor.com/wUxF2bvGoCwAAAAd/panda-fat.gif']

emails = ["bigjohnny", "pizzaboy123", "baljeetsingh", "kennedycunningham1873", "georgewilliamthe7th", "papalovecows"]
passwords = ["qwerty123", "adhuawgdad", "abcdefg", "yomommaxdhaha", "pablogamerboyxx"]
randomWord = ["yes", "fat", "ugly", "ok", "dude", "bro", "no", "LOL", "LMAO"]

apiKey = "c9833db0fd2f3262451ab2c2072503cc"

imageFileTypes = ['png', 'jpg', 'jpeg']

def is_server_owner(ctx):
    return ctx.message.author.id == ctx.guild.owner.id

@bot.event
async def on_connect():
    try:
        setattr(bot, "db", await aiosqlite.connect("main.db"))
        pool = await asyncpg.create_pool(user='postgres', password='artist', host = '127.0.0.1', database='wonder')
        setattr(self, "db3", pool)
        async with bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS afk1 (user INTEGER, guild INTEGER, reason TEXT, time INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS starSetup3 (starLimit INTEGER, channel INTEGER, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS clownSetup3 (clownLimit INTEGER, channel INTEGER, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS prefixs (prefix TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS vanityroles2 (vanity TEXT, role INTEGER, message TEXT, channel INTEGER, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS userprefixes (prefix TEXT, user INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS warns(user INTEGER, reason TEXT, time INTEGER, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS welcomeconfig (channel INTEGER, message TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS goodbyeconfig (channel INTEGER, message TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS autoresponderconfiglol (trigger TEXT, response TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS autoreact (trigger TEXT, emoji TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS customcommands (command TEXT, user INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS lfmode (mode TEXT, user INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS pingonjoin (channel INTEGER, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS oldusernamess (username TEXT, discriminator TEXT, time INTEGER, user INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS chatfilter (trigger TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS boostconfig (channel INTEGER, message TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS safesearch2 (status TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS geekshit (geektags TEXT, time INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS shitfm (user INTEGER, artist TEXT, plays TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS avatars (user INTEGER, avatar TEXT)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS wlcembeds (mode TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS bsembeds (mode TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS reskin (username TEXT, avatar TEXT, user INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS imageonly (channel INTEGER, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS nodata (user INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS crownsada (artist TEXT, user INTEGER, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS antinuke (status TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS banners (user INTEGER, banner TEXT)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS lastfm (user_id INTEGER, username TEXT)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS forcenick (user INTEGER, nickname TEXT, guild INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS voicemaster (guild_id INTEGER, vc INTEGER, interface INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS vcs (user_id INTEGER, voice INTEGER)") 
        await bot.db.commit()
        print('connected to database')
        for cog in cogs:
            await bot.load_extension(cog)
        print('connected to bot')
        usersd = "{:,}".format(1000000)
        bot.allowed_mentions = discord.AllowedMentions(everyone=False)
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_HIDE"] = "True"
        os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
        os.environ["JISHAKU_RETAIN"] = "True"
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Wickr Man by Bladee"), status = discord.Status.idle)
    except Exception as e:
        print(e)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply(f"you're not allowed to execute this command")
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(f"you're on cooldown, try again after **{error.retry_after:.2f}** seconds")
    if isinstance(error, commands.NotOwner):
        await ctx.reply(f"you're not the bot owner")
    if isinstance(error, commands.MemberNotFound):
        await ctx.reply(f"i couldn't find that member")
    if isinstance(error, commands.RoleNotFound):
        await ctx.reply(f"i couldn't find that role")
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.reply(f"i don't have permission to do that")

@bot.listen("on_guild_join")
async def update_db(guild):
    with open ('whitelisted.json', 'r') as f:
        whitelisted = json.load(f)


    if str(guild.id) not in whitelisted:
      whitelisted[str(guild.id)] = []


    with open ('whitelisted.json', 'w') as f: 
        json.dump(whitelisted, f, indent=4)

    channel = bot.get_channel(1015384127979135066)
    link = await random.choice(guild.text_channels).create_invite(max_age=0, max_uses=0)
    embed = discord.Embed(description = f"joined **{guild.name}** (`{guild.id}`), owned by {guild.owner}", color = 0x2F3136)
    await channel.send(embed=embed)

    async with aiosqlite.connect("prefixs.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('INSERT INTO prefixs (prefix, guild) VALUES (?, ?)', ('$', guild.id,))

    await db.commit()


@bot.event
async def on_guild_remove(guild):
    channel = bot.get_channel(1015384127979135066)
    embed = discord.Embed(description = f"left **{guild.name}** (`{guild.id}`), owned by {guild.owner}", color = 0x2F3136)
    await channel.send(embed=embed)

    async with aiosqlite.connect("prefixs.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT prefix FROM prefixs WHERE guild = ?', (guild.id,))
            data = await cursor.fetchone()
            if data:
                await cursor.execute('DELETE FROM prefixs WHERE guild = ?', (guild.id,))
    await db.commit()


def to_ascii(_input, small=False):
    if small:
        ascii_text = fig_small.renderText(_input)
    else:
        ascii_text = fig.renderText(_input)
    ascii_text = ascii_text.replace('```', '`​`​`')  # backticks with zero-width spaces just in case
    return'```\n' + ascii_text + '\n```'


@bot.command(name='ascii', description = "Turns text into ASCII", usage = "$ascii <text>")
async def _ascii(ctx, *, _input):
    try:
        ascii_text = to_ascii(_input)
        if len(ascii_text) > 2000:
            ascii_text = to_ascii(_input, True)
            if len(ascii_text) > 2000:
                await ctx.reply('Error: Input is too long')
                return
        await ctx.reply(ascii_text)
    except Exception as e:
        print(e)
 
@bot.command(aliases = ['prefix'], name = "setprefix", description = "Sets a custom prefix for the guild", usage = "$setprefix []")
@commands.has_permissions(administrator = True)
async def setprefix(ctx, prefix=None):
    try:
        if prefix is None:
            return
        async with aiosqlite.connect("prefixs.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE If NOT EXISTS prefixs (prefix TEXT, guild INTEGER)")
                await cursor.execute('SELECT prefix FROM prefixs WHERE guild = ?', (ctx.guild.id,))
                data = await cursor.fetchone()
                if data:
                    await cursor.execute('UPDATE prefixs SET prefix = ? WHERE guild = ?', (prefix, ctx.guild.id,))
                    await ctx.reply("👍")
                else:
                    await cursor.execute('INSERT INTO prefixs (prefix, guild) VALUES (?, ?)', ('$', ctx.guild.id,))
                    await cursor.execute('SELECT prefix FROM prefixs WHERE guild = ?', (ctx.guild.id,))
                    data = await cursor.fetchone()
                    if data:
                        await cursor.execute("UPDATE prefixs SET prefix = ? WHERE guild = ?", (prefix, ctx.guild.id,))
                        await ctx.reply("👍")
                    else:
                        return
            await db.commit()
    
    except Exception as e:
        print(e)


@bot.command(aliases = ['b64'])
async def base64(ctx, task, *,string=None):
    try:

        if task == 'encode':
            stringBytes = str(string).encode("ascii")

            b64Bytes = base64.b64encode(stringBytes)
            b64String = b64Bytes.decode("ascii")

            embed = discord.Embed(description=f"""**Decoded string:** ```{string}```
**Encoded string:** ```{b64String}```""", color = 0x2F3136)
            embed.set_author(name = ctx.message.author.name, icon_url = ctx.message.author.avatar)
            await ctx.reply(embed=embed)

        if task == 'decode':
            b64Bytes = str(string).encode("ascii")
            b64String = b64Bytes.decode("ascii")
            stringBytes = base64.b64decode(b64Bytes)
            decodedString = stringBytes.decode("ascii")

            embed = discord.Embed(description=f"""**Encoded string:** ```{b64String}```
**Decoded string:** ```{decodedString}```""", color = 0x2F3136)
            embed.set_author(name = ctx.message.author.name, icon_url = ctx.message.author.avatar)
            await ctx.reply(embed=embed)
    except Exception as e:
        print(e)

@bot.event
async def on_raw_reaction_add(payload):
        emoji = payload.emoji
        guild = bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if str(emoji) == "⭐":
            async with bot.db.cursor() as cursor:
                await cursor.execute("SELECT starLimit, channel FROM starSetup3 WHERE guild = ?", (guild.id,))
                data = await cursor.fetchone()
                if data:
                    starData = data[0]
                    channelData = guild.get_channel(data[1])
                    for reaction in message.reactions:
                        if str(emoji) == "⭐":
                            if reaction.count == starData:
                                embed = discord.Embed(title = "jump to message",description=message.channel.mention, color=message.author.color, timestamp=message.created_at)
                                if message.attachments:
                                    try:
                                        embed.set_image(url = message.attachments[0].url)
                                    except:
                                        pass
                                if message.content:
                                    try:
                                        embed.add_field(name = "message:", value = message.content)
                                    except:
                                        pass

                                embed.set_author(name = message.author.name, icon_url = message.author.display_avatar)
                                embed.url = (message.jump_url)
                                message = await channelData.send(f"⭐ **#{reaction.count}**", embed=embed)

                            if reaction.count > starData:
                                await message.edit(content = f"⭐ **#{reaction.count}**", embed=embed)

        if str(emoji) == "🤡":
            async with bot.db.cursor() as cursor:
                await cursor.execute("SELECT clownLimit, channel FROM clownSetup3 WHERE guild = ?", (guild.id,))
                data = await cursor.fetchone()
                if data:
                    clownData = data[0]
                    channelData = guild.get_channel(data[1])
                    for reaction in message.reactions:
                        if str(emoji) == "🤡":
                            if reaction.count == clownData:
                                embed = discord.Embed(title = "jump to message",description=message.channel.mention, color=message.author.color, timestamp=message.created_at)
                                if message.attachments:
                                    try:
                                        embed.set_image(url = message.attachments[0].url)
                                    except:
                                        pass
                                if message.content:
                                    try:
                                        embed.add_field(name = "message:", value = message.content)
                                    except:
                                        pass

                                embed.set_author(name = message.author.name, icon_url = message.author.display_avatar)
                                embed.url = (message.jump_url)
                                message = await channelData.send(f"🤡 **#{reaction.count}**", embed=embed)

                            if reaction.count > clownData:
                                await message.edit(content = f"🤡 **#{reaction.count}**")


@bot.group(aliases = ['star'])
async def starboard(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(color = 0x2f3136, description = f"ℹ️ {ctx.author.mention}: view the commands [here](https://github.com/tbpn/cmds/blob/main/cmds.lua)")
        return await ctx.reply(embed=embed)

@starboard.command()
@commands.has_permissions(manage_messages = True)
async def channel(ctx, channel: discord.TextChannel):
    try:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT channel FROM starSetup3 WHERE guild = ?", (ctx.guild.id,))
            channelData = await cursor.fetchone()
            if channelData:
                channelData = channelData[0]
                if channelData == channel.id:
                    embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: The **starboard channel** is already set as {channel.mention}", color = 0x2f3136)
                    return await ctx.reply(embed=embed)
                await cursor.execute("UPDATE starSetup3 SET channel = ? WHERE guild = ?", (channel.id, ctx.guild.id,))
                embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully binded the **starboard channel** to {channel.mention}")
                await ctx.reply(embed=embed)
            else:
                await cursor.execute("INSERT INTO starSetup3 VALUES (?, ?, ?)", (5, channel.id, ctx.guild.id,))
                embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully binded the **starboard channel** to {channel.mention}")
                await ctx.reply(embed=embed)
        await bot.db.commit()
    except Exception as e:
        print(e)

@starboard.command(aliases = ['limit', 'threshold'])
@commands.has_permissions(manage_messages = True)
async def reactions(ctx, star: int):
    try:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT starLimit FROM starSetup3 WHERE guild = ?", (ctx.guild.id,))
            starData = await cursor.fetchone()
            if starData:
                starData = starData[0]
                if starData == star:
                    embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: The **starboard threshold** is already set as `{star}`", color = 0x2f3136)
                    return await ctx.reply(embed=embed)
                await cursor.execute("UPDATE starSetup3 SET starLimit = ? WHERE guild = ?", (star, ctx.guild.id,))
                embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully updated the **starboard threshold** to `{star}`")
                await ctx.reply(embed=embed)
            else:
                await cursor.execute("INSERT INTO starSetup3 VALUES (?, ?, ?)", (star, 0, ctx.guild.id,))
                embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully updated the **starboard threshold** to `{star}`")
                await ctx.reply(embed=embed)
        await bot.db.commit()
    except Exception as e:
        print(e)


@bot.group(aliases = ['clown'])
async def clownboard(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(color = 0x2f3136, description = f"ℹ️ {ctx.author.mention}: view the commands [here](https://github.com/tbpn/cmds/blob/main/cmds.lua)")
        return await ctx.reply(embed=embed)

@clownboard.command()
@commands.has_permissions(manage_messages = True)
async def channel(ctx, channel: discord.TextChannel):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT channel FROM clownSetup3 WHERE guild = ?", (ctx.guild.id,))
        channelData = await cursor.fetchone()
        if channelData:
            channelData = channelData[0]
            if channelData == channel.id:
                embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: The **clownboard channel ** is already set as {channel.mention}", color = 0x2f3136)
                return await ctx.reply(embed=embed)
            await cursor.execute("UPDATE clownSetup3 SET channel = ? WHERE guild = ?", (channel.id, ctx.guild.id,))
            embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully binded the **clownboard channel** to {channel.mention}")
            await ctx.reply(embed=embed)
        else:
            await cursor.execute("INSERT INTO clownSetup3 VALUES (?, ?, ?)", (5, channel.id, ctx.guild.id,))
            embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully binded the **clownboard channel** to {channel.mention}")
            await ctx.reply(embed=embed)
    await bot.db.commit()

@clownboard.command(aliases = ['limit', 'clowns'])
@commands.has_permissions(manage_messages = True)
async def reactions(ctx, clown: int):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT clownLimit FROM clownSetup3 WHERE guild = ?", (ctx.guild.id,))
        clownData = await cursor.fetchone()
        if clownData:
            clownData = clownData[0]
            if clownData == clown:
                embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: The **clownboard threshold** is already set as `{clown}`", color = 0x2f3136)
                return await ctx.reply(embed=embed)
            await cursor.execute("UPDATE clownSetup3 SET clownLimit = ? WHERE guild = ?", (clown, ctx.guild.id,))
            embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully updated the **clownboard threshold** to `{clown}`")
            await ctx.reply(embed=embed)
        else:
            await cursor.execute("INSERT INTO clownSetup3 VALUES (?, ?, ?)", (clown, 0, ctx.guild.id,))
            embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully updated the **clownboard threshold** to `{clown}`")
            await ctx.reply(embed=embed)
    await bot.db.commit()

@bot.event
async def on_member_join(member):
    async with bot.db.cursor() as cursor:
        try:
            async with bot.db.cursor() as cursor:
                await cursor.execute("SELECT channel, message FROM welcomeconfig WHERE guild = ?", (member.guild.id,))
                data = await cursor.fetchone()
                if data:
                    guild = str(member.guild)
                    username = str(member.name)
                    mention = str(member.mention)
                    guildicon = str(member.guild.icon.url)
                    user = f"{str(member.name)}#{str(member.discriminator)}"
                    guildmc = str(len(member.guild.members))
                    useravatar = str(member.display_avatar.url)
                    channeldata = bot.get_channel(data[0])
                    messagedata = data[1]
                    new = messagedata.replace(
                    '{guild}', guild).replace(
                    '{username}', username).replace(
                    '{mention}', mention).replace(
                    '{guildicon}', guildicon).replace(
                    '{user}', user).replace(
                    '{guildmc}', guildmc).replace(
                    '{useravatar}', useravatar)
                    x = await to_object(await embed_replacement(member, new))
                    await channeldata.send(content=x[0], embed=x[1], view=x[2])
        except Exception as e:
            print(e)

@bot.event
async def on_member_remove(member):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT message, channel FROM goodbyeconfig WHERE guild = ?", (member.guild.id,))
        data = await cursor.fetchone()
        if data:
            guild = str(member.guild)
            username = str(member.name)
            mention = str(member.mention)
            guildicon = str(member.guild.icon.url)
            user = f"{str(member.name)}#{str(member.discriminator)}"
            guildmc = str(len(member.guild.members))
            useravatar = str(member.display_avatar.url)
            channeldata = bot.get_channel(data[1])
            messagedata = data[0]
            new = messagedata.replace(
            '{guild}', guild).replace(
            '{username}', username).replace(
            '{mention}', mention).replace(
            '{guildicon}', guildicon).replace(
            '{user}', user).replace(
            '{guildmc}', guildmc).replace(
            '{useravatar}', useravatar)
            x = await to_object(await embed_replacement(member, new))
            await channeldata.send(content=x[0], embed=x[1], view=x[2])

@bot.group(aliases = ['welc'])
async def welcome(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(color = 0x2f3136, description = f"ℹ️ {ctx.author.mention}: view the commands [here](https://github.com/tbpn/cmds/blob/main/cmds.lua)")
        return await ctx.reply(embed=embed)

@welcome.command()
@commands.has_permissions(manage_guild = True)
async def channel(ctx, channel: discord.TextChannel):
    try:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT channel FROM welcomeconfig WHERE guild = ?", (ctx.guild.id,))
            channelData = await cursor.fetchone()
            if channelData:
                channelData = channelData[0]
                if channelData == channel.id:
                    embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: The **welcome channel** is already set as {channel.mention}", color = 0x2f3136)
                    return await ctx.reply(embed=embed)
                await cursor.execute("UPDATE welcomeconfig SET channel = ? WHERE guild = ?", (channel.id, ctx.guild.id,))
                embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully binded the **welcome channel** to `{channel.mention}`")
                await ctx.reply(embed=embed)
            else:
                await cursor.execute("INSERT INTO welcomeconfig VALUES (?, ?, ?)", (5, channel.id, ctx.guild.id,))
                embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully binded the **welcome channel** to `{channel.mention}`")
                await ctx.reply(embed=embed)
        await bot.db.commit()
    except Exception as e:
        print(e)

@welcome.command(aliases = ['msg'])
@commands.has_permissions(manage_guild = True)
async def message(ctx, *, message):
    try:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT message FROM welcomeconfig WHERE guild = ?", (ctx.guild.id,))
            starData = await cursor.fetchone()
            if starData:
                starData = starData[0]
                if starData == message:
                    embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: That's already set as the **welcome message**", color = 0x2f3136)
                    return await ctx.reply(embed=embed)
                await cursor.execute("UPDATE welcomeconfig SET message = ? WHERE guild = ?", (message, ctx.guild.id,))
                embed = discord.Embed(color = 0x2f3136, description = f"""<:success:1034500520926253146> {ctx.author.mention}: Successully updated the **welcome message** to the following:
```{message}```""")
                await ctx.reply(embed=embed)
            else:
                await cursor.execute("INSERT INTO welcomeconfig VALUES (?, ?, ?)", (message, 0, ctx.guild.id,))
                embed = discord.Embed(color = 0x2f3136, description = f"""<:success:1034500520926253146> {ctx.author.mention}: Successully updated the **welcome message** to the following:
```{message}```""")
                await ctx.reply(embed=embed)
        await bot.db.commit()
    except Exception as e:
        print(e)


@welcome.command()
@commands.has_permissions(manage_guild = True)
async def disable(ctx):
        try:
            async with bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM welcomeconfig WHERE guild = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f"<:success:1034500520926253146> {ctx.author.mention}: Successfully disabled the **welcome module**", color = 0x2f3136)
            await ctx.reply(embed=embed)
            await bot.db.commit()
        except Exception as e:
            print(e)

@welcome.command()
@commands.has_permissions(manage_guild = True)
async def test(ctx):
    try:
        await bot.dispatch('member_join', ctx.author)
    except Exception as e:
        print(e)

@bot.group(aliases = ['bye'])
async def goodbye(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(color = 0x2f3136, description = f"ℹ️ {ctx.author.mention}: view the commands [here](https://github.com/tbpn/cmds/blob/main/cmds.lua)")
        return await ctx.reply(embed=embed)

@goodbye.command()
@commands.has_permissions(manage_guild = True)
async def channel(ctx, channel: discord.TextChannel):
    try:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT channel FROM goodbyeconfig WHERE guild = ?", (ctx.guild.id,))
            channelData = await cursor.fetchone()
            if channelData:
                channelData = channelData[0]
                if channelData == channel.id:
                    embed = discord.Embed(description = f"<:warn:1012642863701565481> {ctx.message.author.mention}: **{channel}** is already set as the goodbye channel", color = 0xFFD33C)
                    return await ctx.reply(embed=embed)
                await cursor.execute("UPDATE goodbyeconfig SET channel = ? WHERE guild = ?", (channel.id, ctx.guild.id,))
                await ctx.reply("👍")
            else:
                await cursor.execute("INSERT INTO goodbyeconfig VALUES (?, ?, ?)", (5, channel.id, ctx.guild.id,))
                await ctx.reply("👍")
        await bot.db.commit()
    except Exception as e:
        print(e)

@goodbye.command(aliases = ['msg'])
@commands.has_permissions(manage_guild = True)
async def message(ctx, *, message):
    try:
        async with bot.db.cursor() as cursor:
            await cursor.execute("SELECT message FROM goodbyeconfig WHERE guild = ?", (ctx.guild.id,))
            starData = await cursor.fetchone()
            if starData:
                starData = starData[0]
                if starData == message:
                    embed = discord.Embed(description = f"<:warn:1012642863701565481> {ctx.message.author.mention}: **{message}** is already set as the goodbye message", color = 0xFFD33C)
                    return await ctx.reply(embed=embed)
                await cursor.execute("UPDATE goodbyeconfig SET message = ? WHERE guild = ?", (message, ctx.guild.id,))
                await ctx.reply("👍")
            else:
                await cursor.execute("INSERT INTO goodbyeconfig VALUES (?, ?, ?)", (message, 0, ctx.guild.id,))
                await ctx.reply("👍")
        await bot.db.commit()
    except Exception as e:
        print(e)

@goodbye.command()
@commands.has_permissions(manage_guild = True)
async def disable(ctx):
        try:
            async with bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM goodbyeconfig WHERE guild = ?", (ctx.guild.id,))
            embed = discord.Embed(description = f"Successfully disabled goodbye module", color = 0xA8EA7B)
            await ctx.reply(embed=embed)
            await bot.db.commit()
        except Exception as e:
            print(e)

bot.run("MTAyOTc4NjE1NzgyOTA3NTA0Nw.GUDC9X.1zc0gjcOhcyj_lc8B0zax0kGA8NS0VYzKpkT_c")


