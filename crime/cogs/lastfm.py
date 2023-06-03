import discord, button_paginator as pg, aiosqlite, aiohttp
from discord.ext import commands  
from cogs.utilevents import commandhelp, blacklist, sendmsg
from .utils.util import Emojis
from .utils import fmuser, fmhandler
from .utils import util
def Sort_Tuple(tup):
    return(reversed(sorted(tup, key = lambda x: x[1])))

class lastfm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS lastfm (user_id INTEGER, username TEXT, customreact TEXT);")
        await self.bot.db.commit()


    @commands.group(description="lastfm", help="Get your spotify statistics through lastfm.", usage="[NONE]", aliases=['fm', 'lf'])
    @blacklist()
    async def lastfm(self, ctx):
            return

    @lastfm.command(description="lastfm", help="register your lastfm account", usage="[name]", aliases=['connect', 'link'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def set(self, ctx, ref=None):
            if ref is None: 
                await commandhelp(self, ctx, "lastfm set")
                return 
            ref = ref.replace("https://www.last.fm/user/", "")
            if not await fmuser.userexists(ref):
                embed = discord.Embed(description=f'{Emojis.warn} Invalid Last.fm username',
                                    color=0x2f3136)
                return await sendmsg(self, ctx, None, embed, None, None, None)
            else:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(ctx.author.id))
                    check = await cursor.fetchone()
                    if check is None:
                        await cursor.execute("INSERT INTO lastfm VALUES (?, ?, ?)", (ctx.author.id, ref))
                    elif check is not None:
                        await cursor.execute("UPDATE lastfm SET username = ? WHERE user_id = ?", (ref, ctx.author.id))
                    embed = discord.Embed(description=f' {ctx.message.author.mention}: Your **Last.fm** username has been set to **{ref}**', color=0x2f3136)
                    await sendmsg(self, ctx, None, embed, None, None, None)
                await self.bot.db.commit()  

    @lastfm.command(description="lastfm", help="remove your lastfm account", usage="[name]", aliases=['disconnect', 'unlink' 'unset'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def remove(self, ctx: commands.Context, *, member: discord.Member=None):
     async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        check = await cursor.fetchone()
        if check is None: return await ctx.reply(discord.Embed(description=f"{Emojis.warn} set a **[lastfm](https://last.fm) account** linked", color=0x2f3136))             
        await cursor.execute("DELETE FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        await self.bot.db.commit()
        await ctx.reply(discord.Embed(color=0x2f3136, description=f"{Emojis.check} your **[lastfm](https://last.fm) account** has been removed"))       
    @lastfm.command(description="see what you are listening to", help="nowplaying lastfm command", usage="[user]", aliases=['np'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    @blacklist()
    async def nowplaying(self, ctx: commands.Context, *, member: discord.Member=None):
        if member is None:
            member = ctx.author
        try:
             async with self.bot.db.cursor() as cursor:   
              await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
              check = await cursor.fetchone()
              if check is not None:  
                user = str(check[1]).replace("('", "").replace("',)", "")
                if user != "error":      
                    crime = await fmhandler.gettracks(user, 1)
                    artist = crime['recenttracks']['track'][0]['artist']['name'].replace(" ", "+")
                    image = crime['recenttracks']['track'][0]['image'][3]['#text']
                    album = crime['recenttracks']['track'][0]['album']['#text'] or "Not an album."
                    track = crime['recenttracks']['track'][0]['name']
                    trackp = crime['recenttracks']['track'][0]['playcount']
                    artistp = crime['recenttracks']['artist'][0]['playcount']
                    albump = crime['recenttracks']['album'][0]['playcount']
                    xxe = crime['recenttracks']['@attr']['total']
                    async with ctx.typing():
                        em = [discord.Embed(
                            color = 0x2f3136
                            ).add_field(
                                name = "Track",
                                value = f"**[{track}]({crime['recenttracks']['track'][0]['url']})** `{trackp}`",
                                inline = False
                            ).add_field(
                                name = "Artist",
                                value = f"by [{artist}](https://last.fm/music/{artist}) `{artistp}`",
                                inline = False
                            ).add_field(
                                name = "Album",
                                value = f"on [{album}](https://last.fm/music/{album}) `{albump}`",
                                inline = False
                            ).set_thumbnail(
                                url = image
                            ).set_author(
                                name = f"Last.FM: {user} | total scrobbles: {xxe}",
                                icon_url = ctx.author.display_avatar.url
                            )]
                        msg = await ctx.reply(embed=em)
                    await msg.add_reaction("👍")
                    await msg.add_reaction("👎")
              elif check is None: 
                embed = discord.Embed(description=f"<:crimelastfm:1082118965041577984> **{member}** doesn't have a **Last.fm account** linked. Use `;lf set <username>` to link your **account**.", color=0x2f3136)
                await ctx.send(embed=em)    
        except Exception as e:
          embed = discord.Embed(description=f"{Emojis.warn} {ctx.author.mention}: unable to get **{member.name}'s** recent track ", color=0x2f3136)
          print(e)
          await ctx.send(embed=embed)    

    @lastfm.command(description="have custom reactions for your lastfm nowplaying embed", help="custom lastfm reaction", usage="[emojis]", aliases=['customreactions', 'customreaction'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def customreact(self, ctx):
        return
async def setup(bot):
    await bot.add_cog(lastfm(bot))            