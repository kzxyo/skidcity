import discord, button_paginator as pg, json, aiohttp, userhandler, lastfmhandler, ast, aiosqlite
from discord.ext import commands  
from cogs.events import commandhelp
from classes import Colors, Emojis

def Sort_Tuple(tup):
    return(reversed(sorted(tup, key = lambda x: x[1])))

class lastfm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_connect(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS lfmode (mode TEXT, user INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS lastfm (user_id INTEGER, username TEXT);")
            await cursor.execute("CREATE TABLE IF NOT EXISTS lastfmcc (user_id INTEGER, command TEXT);")
        await self.bot.db.commit()    

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
      try:  
       if not message.guild: return 
       if message.author.bot: return 
       async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM lastfmcc WHERE user_id = {}".format(message.author.id))
        check = await cursor.fetchone()
        if check is not None:
          if check[1] == message.content:
            member = message.author 
            async with message.channel.typing():
              await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
              res = await cursor.fetchone()
              if res is not None:   
                await cursor.execute("SELECT mode FROM lfmode WHERE user = ?", (message.author.id,))
                starData = await cursor.fetchone()
                if starData is None:
                 user = str(res[1]).replace("('", "").replace("',)", "")
                 if user != "error":   
                    a = await lastfmhandler.get_tracks_recent(user, 1)
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    embed = discord.Embed(colour=0x2F3136)
                    embed.add_field(name="> **Track:**", value = f"""[{"" + a['recenttracks']['track'][0]['name']}]({"" + a['recenttracks']['track'][0]['url']})""", inline = False)
                    embed.add_field(name="> **Artist:**", value = f"""[{a['recenttracks']['track'][0]['artist']['#text']}](https://last.fm/music/{artist})""", inline = False)
                    embed.set_author(name = user, icon_url = member.display_avatar, url = f"https://last.fm/user/{user}")                               
                    embed.set_thumbnail(url=(a['recenttracks']['track'][0])['image'][3]['#text'])
                    embed.set_footer(text = f"Track Playcount: {await lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0])} ・Album: {a['recenttracks']['track'][0]['album']['#text']}", icon_url = (a['recenttracks']['track'][0])['image'][3]['#text'])
                    message = await message.reply(embed=embed, mention_author=False)
                    await message.add_reaction("🔥")
                    await message.add_reaction("🗑️")
                else:         
                   user = str(res[1]).replace("('", "").replace("',)", "")
                   if user != "error":   
                    a = await lastfmhandler.get_tracks_recent(user, 1) 
                    userinfo = await lastfmhandler.get_user_info(user)
                    userpfp = userinfo["user"]["image"][2]["#text"]
                    albumplays = str(await lastfmhandler.get_album_playcount(user, a['recenttracks']['track'][0]))
                    artistplays = str(await lastfmhandler.get_artist_playcount(user, a['recenttracks']['track'][0]))
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    album = a["recenttracks"]['track'][0]['album']['#text'].replace(" ", "+")
                    stringdict = starData[0]
                    new = stringdict.replace('{track}', a['recenttracks']['track'][0]['name']).replace('{trackurl}', a['recenttracks']['track'][0]['url']).replace('{artist}', a['recenttracks']['track'][0]['artist']['#text']).replace('{artisturl}', f"https://last.fm/music/{artist}").replace('{trackimage}', (a['recenttracks']['track'][0])['image'][3]['#text']).replace('{artistplays}', artistplays).replace('{albumplays}', albumplays).replace('{trackplays}', await lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0])).replace('{album}', a['recenttracks']['track'][0]['album']['#text']).replace('{albumurl}', f"https://www.last.fm/music/{artist}/{album}").replace('{username}', user).replace('{scrobbles}', a['recenttracks']['@attr']['total']).replace('{useravatar}', userpfp)
                    dict1 = ast.literal_eval(new)
                    message = await message.reply(embed=discord.Embed.from_dict(dict1), mention_author=False)
                    await message.add_reaction("🔥")
                    await message.add_reaction("🗑️")
              elif res is None: 
                embed = discord.Embed(description=f"> __You don't have a **Last.fm account** linked. Please use `.lf set <username>` to link your **Last.fm account**.__", color=Colors.red)
                await message.reply(embed=embed, mention_author=False)      
      except Exception as e:
          embed = discord.Embed(description=f"> {message.author.mention}: __unable to get your recent track - {e}__", color=Colors.red)
          await message.reply(embed=embed, mention_author=False)  

    @commands.group(aliases = ['lf'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lastfm(self, ctx):
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(description = f"""Get your **Last.fm** statistics through the bot
**What is lastfm**
> __Last.fm is a global online music service that tracks people's music listening habits__
**How i set my last.fm username?**
> 1. __Go to **[Last.fm](https://last.fm)** & create an account__
> __if you don't already have one__
> __2. Run the command `.lastfm set <yourusername>`__
> __3. And you're good to go to start tracking your statistics
> through the bot!__""",color = 0x2F3136)
                embed.add_field(name = "**Sub commands**", value = f"""
> __lastfm set__
> __lastfm remove__
> __lastfm customcommand__
> __lastfm embed__
> __the other commands are displayed in the help command__""", inline = False)
                embed.set_thumbnail(url = self.bot.user.avatar)
                embed.set_author(name = "Last.fm", icon_url = self.bot.user.avatar)
                return await ctx.reply(embed=embed, mention_author=False)

    @lastfm.command(description="lastfm", help="register your lastfm account", usage="[name]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def set(self, ctx, ref=None):
            if ref is None: 
                await commandhelp(self, ctx, "lastfm set")
                return 

            ref = ref.replace("https://www.last.fm/user/", "")
            if not await userhandler.lastfm_user_exists(ref):
                embed = discord.Embed(description=f'> __**Invalid** Last.fm username__',
                                    color=Colors.red)
                await ctx.reply(embed=embed, mention_author=False)
            else:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(ctx.author.id))
                    check = await cursor.fetchone()
                    if check is None:
                        await cursor.execute("INSERT INTO lastfm VALUES (?, ?)", (ctx.author.id, ref))
                    elif check is not None:
                        await cursor.execute("UPDATE lastfm SET username = ? WHERE user_id = ?", (ref, ctx.author.id))
                    embed = discord.Embed(description=f'> __{ctx.message.author.mention}: Your **Last.fm** username has been set to __**{ref}**__', color=Colors.red)
                    await ctx.reply(embed=embed, mention_author=False)
                await self.bot.db.commit()  

    @lastfm.command(description="lastfm", help="unset your lastfm account")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx): 
     async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        check = await cursor.fetchone()
        if check is None: return await ctx.reply(embed=discord.Embed(description=f"> __You don't have a **Last.fm account** linked. Use `.lf set <username>` to link your **account**.__", color=Colors.red), mention_author=False)              
        await cursor.execute("DELETE FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        await self.bot.db.commit()
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"> __{ctx.author.mention}: your last fm account has been removed__"), mention_author=False)
    
    @lastfm.command(help="**view lastfm custom embed variables**", description="> __lastfm__")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def variables(self, ctx):
        mes = """>>> {scrobbles} - returns all song play count
{trackplays} - returns the track total plays
{artistplays} - returns the artist total plays
{albumplays} - returns the album total plays
{track} - returns the track name
{trackurl} - returns the track url
{trackimage} - returns the track image
{artist} - returns the artist name
{artisturl} - returns the artist profile url
{album} - returns the album name 
{albumurl} - returns the album url
{username} - returns your username
{useravatar} - returns user's profile picture
"""
        embed = discord.Embed(color=0x2f3136)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_author(name="Last.fm", icon_url=self.bot.user.avatar.url)
        embed.add_field(name="**Axie LastFm Variables**", value=mes, inline=False)
        await ctx.reply(embed=embed, mention_author=False)

    @lastfm.command(help="view your own lastfm custom embed", description="**lastfm**", usage="> [subcommand]", brief="> __lastfm embed none - deletes your lastfm custom embed__\n> __lastfm embed view - view the lastfm embed__\n> __any option instead of this will be counted as your embed__")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def embed(self, ctx, *,cc=None):
            if cc is None: return await commandhelp(self, ctx, "lastfm embed") 
            try:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT mode FROM lfmode WHERE user = ?", (ctx.author.id,))
                    starData = await cursor.fetchone()
                    if starData:
                        starData = starData[0]
                        if cc == "none":
                            await cursor.execute("DELETE FROM lfmode WHERE user = ?", (ctx.author.id,))
                            await self.bot.db.commit()
                            return await ctx.reply("👍")
                        if cc == "view":
                            await cursor.execute("SELECT mode FROM lfmode WHERE user = ?", (ctx.author.id,))
                            starData = await cursor.fetchone()
                            if starData is None: return await ctx.reply(embed=discord.Embed(colors=Colors.red, description=f"> __{ctx.author.mention}: you don't have a lastfm custom embed__"), mention_author=False)
                            code = starData[0]
                            embed = discord.Embed(color = 0x2f3136, description = f"```​{code}\n```")
                            return await ctx.reply(embed=embed, mention_author=False)
                        if cc == starData:
                            embed = discord.Embed(description = f"> __{ctx.message.author.mention}: That is already set as your custom embed mode__", color = Colors.yellow)
                            return await ctx.reply(embed=embed, mention_author=False)
                        else:    
                         await cursor.execute("UPDATE lfmode SET mode = ? WHERE user = ?", (cc, ctx.author.id,))
                         await self.bot.db.commit()
                         embed = discord.Embed(description = f"""{ctx.message.author.mention}: Updated your custom embed mode to the following:\n``​`\n{cc}``​`""", color =Colors.green)
                        await ctx.reply(embed=embed, mention_author=False)
                    elif starData is None:
                        await cursor.execute("INSERT INTO lfmode VALUES (?, ?)", (cc, ctx.author.id,))
                        await self.bot.db.commit()
                        embed = discord.Embed(color=Colors.green, description = f"> __{ctx.message.author.mention}: Added your custom embed mode to__\n```{cc}```")
                        await ctx.reply(embed=embed, mention_author=False)
            except Exception as er:
              await ctx.reply(embed = discord.Embed(description=f"> __{ctx.author.mention}: {er}__",color=Colors.red))  
                        
    @lastfm.command(description="**lastfm**", help="set a custom command for nowplaying", usage="[command]", aliases=["cc"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def customcommand(self, ctx, *, cmd=None):
        if cmd is None:
            await commandhelp(self, ctx, "lastfm customcommand")
            return 
        if cmd == "none":   
             async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM lastfmcc WHERE user_id = {}".format(ctx.author.id))
                    check = await cursor.fetchone()
                    if check is None:
                        return await ctx.reply("> __you don't have a lastfm custom command__")
                    elif check is not None:
                        await cursor.execute(f"DELETE FROM lastfmcc WHERE user_id = {ctx.author.id}")
                    embed = discord.Embed(description=f'> __{ctx.message.author.mention}: Your **Last.fm** custom command got deleted__', color=Colors.red)
                    await ctx.reply(embed=embed)
                    await self.bot.db.commit()  
                    return          
        async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT * FROM lastfmcc WHERE user_id = {}".format(ctx.author.id))
                    check = await cursor.fetchone()
                    if check is None:
                        await cursor.execute("INSERT INTO lastfmcc VALUES (?, ?)", (ctx.author.id, cmd))
                    elif check is not None:
                        await cursor.execute("UPDATE lastfmcc SET command = ? WHERE user_id = ?", (cmd, ctx.author.id))
                    embed = discord.Embed(description=f'> __{ctx.message.author.mention}: Your **Last.fm** custom command is {cmd}__', color=Colors.red)
                    await ctx.reply(embed=embed, mention_author=False)
                    await self.bot.db.commit()  

    @commands.command(aliases = ['ta'], help="check a member's top 10 artists", description="lastfm", usage="<member>")
    async def topartist(self, ctx, member: discord.Member = None):
        try:
           if member == None:
                member = ctx.author
           async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT user FROM nodata WHERE user = ?", (member.id,))
            data = await cursor.fetchone()
            if data: return await ctx.reply("this member opted out of their data being tracked")
            await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
            check = await cursor.fetchone()
            if check is not None:   
                user = str(check[1]).replace("('", "").replace("',)", "")
                if user != "error": 
                 async with aiohttp.ClientSession() as session:
                    params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7",
                    "user" : user,
                    "period" : "overall",
                    "limit" : 10,
                    "method":"user.getTopArtists",
                    "format":"json"}
                    async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
                        resp = await response.read()
                        jsonData = json.loads(resp)
                        topartist1 = jsonData["topartists"]["artist"][0]["name"]
                        topartist2 = jsonData["topartists"]["artist"][1]["name"]
                        topartist3 = jsonData["topartists"]["artist"][2]["name"]
                        topartist4 = jsonData["topartists"]["artist"][3]["name"]
                        topartist5 = jsonData["topartists"]["artist"][4]["name"]
                        topartist6 = jsonData["topartists"]["artist"][5]["name"]
                        topartist7 = jsonData["topartists"]["artist"][6]["name"]
                        topartist8 = jsonData["topartists"]["artist"][7]["name"]
                        topartist9 = jsonData["topartists"]["artist"][8]["name"]
                        topartist10 = jsonData["topartists"]["artist"][9]["name"]
                        topartist1url = jsonData["topartists"]["artist"][0]["url"]
                        topartist2url = jsonData["topartists"]["artist"][1]["url"]
                        topartist3url = jsonData["topartists"]["artist"][2]["url"]
                        topartist4url = jsonData["topartists"]["artist"][3]["url"]
                        topartist5url = jsonData["topartists"]["artist"][4]["url"]
                        topartist6url = jsonData["topartists"]["artist"][5]["url"]
                        topartist7url = jsonData["topartists"]["artist"][6]["url"]
                        topartist8url = jsonData["topartists"]["artist"][7]["url"]
                        topartist9url = jsonData["topartists"]["artist"][8]["url"]
                        topartist10url = jsonData["topartists"]["artist"][9]["url"]
                        topartist1plays = jsonData["topartists"]["artist"][0]["playcount"]
                        topartist2plays = jsonData["topartists"]["artist"][1]["playcount"]
                        topartist3plays = jsonData["topartists"]["artist"][2]["playcount"]
                        topartist4plays = jsonData["topartists"]["artist"][3]["playcount"]
                        topartist5plays = jsonData["topartists"]["artist"][4]["playcount"]
                        topartist6plays = jsonData["topartists"]["artist"][5]["playcount"]
                        topartist7plays = jsonData["topartists"]["artist"][6]["playcount"]
                        topartist8plays = jsonData["topartists"]["artist"][7]["playcount"]
                        topartist9plays = jsonData["topartists"]["artist"][8]["playcount"]
                        topartist10plays = jsonData["topartists"]["artist"][9]["playcount"]
                        embed = discord.Embed(description = f"""`1` **[{topartist1}]({topartist1url})** {topartist1plays} plays
`2` **[{topartist2}]({topartist2url})** {topartist2plays} plays
`3` **[{topartist3}]({topartist3url})** {topartist3plays} plays
`4` **[{topartist4}]({topartist4url})** {topartist4plays} plays
`5` **[{topartist5}]({topartist5url})** {topartist5plays} plays
`6` **[{topartist6}]({topartist6url})** {topartist6plays} plays
`7` **[{topartist7}]({topartist7url})** {topartist7plays} plays
`8`	**[{topartist8}]({topartist8url})** {topartist8plays} plays
`9` **[{topartist9}]({topartist9url})** {topartist9plays} plays
`10` **[{topartist10}]({topartist10url})** {topartist10plays} plays""",color = 0x2F3136)
                        embed.set_thumbnail(url = member.display_avatar)
                        embed.set_author(name = f"{user}'s overall top artists", icon_url = member.display_avatar)
                        await ctx.reply(embed=embed, mention_author=False)
            else:
                embed = discord.Embed(description=f"> __ You don't have a **Last.fm account** linked. Use `.lfset <username>` to link your **account**.__",color=Colors.red)
            
        except Exception as e:
            print(e)
    @commands.command(aliases = ['tt'], help="check a member's top 10 tracks", description="lastfm", usage="<member>")
    async def toptracks(self, ctx, *, member: discord.Member=None):
        if member == None:
            member=ctx.author
        try:
           async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT user FROM nodata WHERE user = ?", (member.id,))
            data = await cursor.fetchone()
            if data: return await ctx.reply("this member opted out of their data being tracked")
            await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
            check = await cursor.fetchone()
            if check is not None:   
                user = str(check[1]).replace("('", "").replace("',)", "")
                if user != "error": 
                 async with aiohttp.ClientSession() as session:
                    params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7",
                    "user" : user,
                    "period" : "overall",
                    "limit" : 10,
                    "method":"user.getTopTracks",
                    "format":"json"}
                    async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
                        resp = await response.read()
                        jsonData = json.loads(resp)
                        toptrack1 = jsonData["toptracks"]["track"][0]["name"]
                        toptrack2 = jsonData["toptracks"]["track"][1]["name"]
                        toptrack3 = jsonData["toptracks"]["track"][2]["name"]
                        toptrack4 = jsonData["toptracks"]["track"][3]["name"]
                        toptrack5 = jsonData["toptracks"]["track"][4]["name"]
                        toptrack6 = jsonData["toptracks"]["track"][5]["name"]
                        toptrack7 = jsonData["toptracks"]["track"][6]["name"]
                        toptrack8 = jsonData["toptracks"]["track"][7]["name"]
                        toptrack9 = jsonData["toptracks"]["track"][8]["name"]
                        toptrack10 = jsonData["toptracks"]["track"][9]["name"]
                        toptrack1url = jsonData["toptracks"]["track"][0]["url"]
                        toptrack2url = jsonData["toptracks"]["track"][1]["url"]
                        toptrack3url = jsonData["toptracks"]["track"][2]["url"]
                        toptrack4url = jsonData["toptracks"]["track"][3]["url"]
                        toptrack5url = jsonData["toptracks"]["track"][4]["url"]
                        toptrack6url = jsonData["toptracks"]["track"][5]["url"]
                        toptrack7url = jsonData["toptracks"]["track"][6]["url"]
                        toptrack8url = jsonData["toptracks"]["track"][7]["url"]
                        toptrack9url = jsonData["toptracks"]["track"][8]["url"]
                        toptrack10url = jsonData["toptracks"]["track"][9]["url"]
                        toptrack1plays = jsonData["toptracks"]["track"][0]["playcount"]
                        toptrack2plays = jsonData["toptracks"]["track"][1]["playcount"]
                        toptrack3plays = jsonData["toptracks"]["track"][2]["playcount"]
                        toptrack4plays = jsonData["toptracks"]["track"][3]["playcount"]
                        toptrack5plays = jsonData["toptracks"]["track"][4]["playcount"]
                        toptrack6plays = jsonData["toptracks"]["track"][5]["playcount"]
                        toptrack7plays = jsonData["toptracks"]["track"][6]["playcount"]
                        toptrack8plays = jsonData["toptracks"]["track"][7]["playcount"]
                        toptrack9plays = jsonData["toptracks"]["track"][8]["playcount"]
                        toptrack10plays = jsonData["toptracks"]["track"][9]["playcount"]
                        embed = discord.Embed(description = f"""`1` **[{toptrack1}]({toptrack1url})** {toptrack1plays} plays
`2` **[{toptrack2}]({toptrack2url})** {toptrack2plays} plays
`3` **[{toptrack3}]({toptrack3url})** {toptrack3plays} plays
`4` **[{toptrack4}]({toptrack4url})** {toptrack4plays} plays
`5` **[{toptrack5}]({toptrack5url})** {toptrack5plays} plays
`6` **[{toptrack6}]({toptrack6url})** {toptrack6plays} plays
`7` **[{toptrack7}]({toptrack7url})** {toptrack7plays} plays
`8`	**[{toptrack8}]({toptrack8url})** {toptrack8plays} plays
`9` **[{toptrack9}]({toptrack9url})** {toptrack9plays} plays
`10` **[{toptrack10}]({toptrack10url})** {toptrack10plays} plays""",color = 0x2F3136)
                        embed.set_thumbnail(url = ctx.message.author.avatar)
                        embed.set_author(name = f"{user}'s overall top tracks", icon_url = ctx.message.author.avatar)
                        await ctx.reply(embed=embed, mention_author=False)
            else:
                embed = discord.Embed(description=f"> __You don't have a **Last.fm account** linked. Use `.lf set <username>` to link your **account**.__",color=Colors.red)
        except Exception as e:
            print(e)

    @commands.command(aliases = ['tal'], help="check a member's top 10 albums", description="lastfm", usage="<member>")
    async def topalbums(self,ctx, *, member: discord.Member=None):
        if member == None: member=ctx.author
        try:
           async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT user FROM nodata WHERE user = ?", (member.id,))
            data = await cursor.fetchone()
            if data: return await ctx.reply("this member opted out of their data being tracked")
            await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
            check = await cursor.fetchone()
            if check is not None:   
                user = str(check[1]).replace("('", "").replace("',)", "")
                if user != "error": 
                 async with aiohttp.ClientSession() as session:
                    params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7",
                    "user" : user,
                    "period" : "overall",
                    "limit" : 10,
                    "method":"user.getTopAlbums",
                    "format":"json"}
                    async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
                        resp = await response.read()
                        jsonData = json.loads(resp)
                        topalbum1 = jsonData["topalbums"]["album"][0]["name"]
                        topalbum2 = jsonData["topalbums"]["album"][1]["name"]
                        topalbum3 = jsonData["topalbums"]["album"][2]["name"]
                        topalbum4 = jsonData["topalbums"]["album"][3]["name"]
                        topalbum5 = jsonData["topalbums"]["album"][4]["name"]
                        topalbum6 = jsonData["topalbums"]["album"][5]["name"]
                        topalbum7 = jsonData["topalbums"]["album"][6]["name"]
                        topalbum8 = jsonData["topalbums"]["album"][7]["name"]
                        topalbum9 = jsonData["topalbums"]["album"][8]["name"]
                        topalbum10 = jsonData["topalbums"]["album"][9]["name"]
                        topalbum1url = jsonData["topalbums"]["album"][0]["url"]
                        topalbum2url = jsonData["topalbums"]["album"][1]["url"]
                        topalbum3url = jsonData["topalbums"]["album"][2]["url"]
                        topalbum4url = jsonData["topalbums"]["album"][3]["url"]
                        topalbum5url = jsonData["topalbums"]["album"][4]["url"]
                        topalbum6url = jsonData["topalbums"]["album"][5]["url"]
                        topalbum7url = jsonData["topalbums"]["album"][6]["url"]
                        topalbum8url = jsonData["topalbums"]["album"][7]["url"]
                        topalbum9url = jsonData["topalbums"]["album"][8]["url"]
                        topalbum10url = jsonData["topalbums"]["album"][9]["url"]
                        topalbum1plays = jsonData["topalbums"]["album"][0]["playcount"]
                        topalbum2plays = jsonData["topalbums"]["album"][1]["playcount"]
                        topalbum3plays = jsonData["topalbums"]["album"][2]["playcount"]
                        topalbum4plays = jsonData["topalbums"]["album"][3]["playcount"]
                        topalbum5plays = jsonData["topalbums"]["album"][4]["playcount"]
                        topalbum6plays = jsonData["topalbums"]["album"][5]["playcount"]
                        topalbum7plays = jsonData["topalbums"]["album"][6]["playcount"]
                        topalbum8plays = jsonData["topalbums"]["album"][7]["playcount"]
                        topalbum9plays = jsonData["topalbums"]["album"][8]["playcount"]
                        topalbum10plays = jsonData["topalbums"]["album"][9]["playcount"]
                        embed = discord.Embed(description = f"""`1` **[{topalbum1}]({topalbum1url})** {topalbum1plays} plays
`2` **[{topalbum2}]({topalbum2url})** {topalbum2plays} plays
`3` **[{topalbum3}]({topalbum3url})** {topalbum3plays} plays
`4` **[{topalbum4}]({topalbum4url})** {topalbum4plays} plays
`5` **[{topalbum5}]({topalbum5url})** {topalbum5plays} plays
`6` **[{topalbum6}]({topalbum6url})** {topalbum6plays} plays
`7` **[{topalbum7}]({topalbum7url})** {topalbum7plays} plays
`8`	**[{topalbum8}]({topalbum8url})** {topalbum8plays} plays
`9` **[{topalbum9}]({topalbum9url})** {topalbum9plays} plays
`10` **[{topalbum10}]({topalbum10url})** {topalbum10plays} plays""",color = 0x2F3136)
                        embed.set_thumbnail(url = ctx.message.author.avatar)
                        embed.set_author(name = f"{user}'s overall top albums", icon_url = ctx.message.author.avatar)
                        await ctx.reply(embed=embed, mention_author=False)
            else:
                embed = discord.Embed(description=f"> __You don't have a **Last.fm account** linked. Use `.lf set <username>` to link your **account**.__",color=Colors.red)
        except Exception as e:
            print(e)

    @commands.command(aliases = ['wk'], description="lastfm", help="see who knows a certain artist in the server", usage="[artist]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def whoknows(self, ctx: commands.Context, * ,artist):
     try:   
      lis = []  
      async with ctx.typing():
       async with self.bot.db.cursor() as cursor:
        for user in ctx.guild.members: 
         await cursor.execute("SELECT user FROM nodata WHERE user = ?", (user.id,))
         data = await cursor.fetchone()
         if data: continue   
         await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(user.id))
         check = await cursor.fetchone()
         if check is not None: 
          use = await self.bot.fetch_user(user.id)   
          username = str(check[1]).replace("('", "").replace("',)", "")
          if username != "error": 
           async with aiohttp.ClientSession() as session:
            params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7", "user": username, "artist" : artist, "method": "artist.getInfo", "autocorrect": "true", "format":"json"}
            async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
             jsonData = await response.json()
             try:
              userplays = jsonData['artist']['stats']['userplaycount']
              if len(jsonData['artist']['stats']['userplaycount']) > 1: 
               lis.append(tuple((f"{use.name}#{use.discriminator}", int(userplays), username)))
              else:
               continue
             except KeyError: 
                continue           
         elif check is not None:
            continue 

       if lis == []:
         await ctx.reply(f"> __Nobody (not even you) has listened to {artist}__") 
         return      
       list = Sort_Tuple(lis)
       listeners = ""
       listenerscount = 0
       num = 0
       number = []
       messages =[]
       i = 0
       for l in list:
        num += 1  
        listenerscount += 1
        if num == 1:
            listeners += f"<:channel_voice:1022917137855168545> **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n"
        else:    
         listeners += f"`{num}` **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n"  
        if listenerscount == 10:
         messages.append(listeners)
         number.append(discord.Embed(color=0x2f3136 , description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{listenerscount} listeners for this artist"))
         i+=1
         listeners = ""
       if num == 0:
         await ctx.reply(f"Nobody (not even you) has listened to {artist}") 
         return 
       messages.append(listeners)
       embe = discord.Embed(color=0x2f3136 , description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{listenerscount} listeners for this artist")
       number.append(embe)
       if len(number) > 1:
        paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
        paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
        paginator.add_button('next', emoji="<:right:1018156484170883154>")
        await paginator.start()
       else: 
        await ctx.send(embed=embe)  
     except Exception as e:
        embed = discord.Embed(description = f"{Emojis.warning} {ctx.message.author.mention}: `{artist}` is not a **valid** artist", color = Colors.yellow)
        await ctx.reply(embed=embed, mention_author=False)  
        print(e) 
    
    @commands.command(aliases=["gwk"], description="lastfm", help="see who knows a certain artist across all servers the bot is in", usage="[artist]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def globalwhoknows(self, ctx: commands.Context, * ,artist):
     try:   
      lis = []  
      async with ctx.typing():
       async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM lastfm")
        results = await cursor.fetchall()
        for check in results:
         use = await self.bot.fetch_user(check[0])   
         await cursor.execute("SELECT user FROM nodata WHERE user = ?", (use.id,))
         data = await cursor.fetchone()
         if data: continue
         username = str(check[1]).replace("('", "").replace("',)", "")
         if username != "error": 
          async with aiohttp.ClientSession() as session:
           params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7", "user": username, "artist" : artist, "method": "artist.getInfo", "autocorrect": "true", "format":"json"}
           async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
            resp = await response.read()
            jsonData = json.loads(resp)
            try:
             userplays = jsonData['artist']['stats']['userplaycount']
             if len(jsonData['artist']['stats']['userplaycount']) > 1: 
              lis.append(tuple((f"{use.name}#{use.discriminator}", int(userplays), username)))
             else:
              continue
            except KeyError: 
                continue            

       if lis == []:
         await ctx.reply(f"Nobody (not even you) has listened to {artist}") 
         return 
       list = Sort_Tuple(lis) 
       listeners = ""
       listenerscount = 0
       num = 0
       number = []
       messages =[]
       i = 0
       for l in list:
        num += 1  
        listenerscount += 1
        if num == 1:
            listeners += f"<:channel_voice:1022917137855168545> **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n"
        else:    
         listeners += f"`{num}` **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n" 
        if listenerscount == 10:
         messages.append(listeners)
         number.append(discord.Embed(color=0x2f3136 , description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{listenerscount} listeners for this artist"))
         i+=1
         listeners = ""
       if num == 0:
         await ctx.reply(f"Nobody (not even you) has listened to {artist}") 
         return 
       messages.append(listeners)
       embe = discord.Embed(color=0x2f3136 , description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{listenerscount} listeners for this artist")
       number.append(embe)
       if len(number) > 1:
        paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
        paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
        paginator.add_button('next', emoji="<:right:1018156484170883154>")
        await paginator.start()
       else: 
        await ctx.send(embed=embe)  
     except:
        embed = discord.Embed(description = f"{Emojis.warning} {ctx.message.author.mention}: `{artist}` is not a **valid** artist", color = Colors.yellow)
        await ctx.reply(embed=embed, mention_author=False)  

    @commands.command(aliases=['np', 'fm'], description="lastfm")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nowplaying(self, ctx: commands.Context, *, member: discord.User=None):
        if member is None:
            member = ctx.author
        try:
            async with ctx.typing():
             async with self.bot.db.cursor() as cursor:   
              await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
              check = await cursor.fetchone()
              if check is not None:   
               await cursor.execute("SELECT mode FROM lfmode WHERE user = ?", (ctx.author.id,))
               starData = await cursor.fetchone()
               if starData is None:  
                user = str(check[1]).replace("('", "").replace("',)", "")
                if user != "error":      
                    a = await lastfmhandler.get_tracks_recent(user, 1)
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    embed = discord.Embed(colour=0x2F3136)
                    embed.add_field(name="> **Track:**", value = f"""[{"" + a['recenttracks']['track'][0]['name']}]({"" + a['recenttracks']['track'][0]['url']})""", inline = False)
                    embed.add_field(name="> __**Artist:**__", value = f"""[{a['recenttracks']['track'][0]['artist']['#text']}](https://last.fm/music/{artist})""", inline = False)
                    embed.set_author(name = user, icon_url = member.display_avatar, url = f"https://last.fm/user/{user}")                               
                    embed.set_thumbnail(url=(a['recenttracks']['track'][0])['image'][3]['#text'])
                    embed.set_footer(text = f"Track Playcount: {await lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0])}・Album: {a['recenttracks']['track'][0]['album']['#text']}", icon_url = (a['recenttracks']['track'][0])['image'][3]['#text'])
                    message = await ctx.reply(embed=embed, mention_author=False)
                    await message.add_reaction("🔥")
                    await message.add_reaction("🗑️")
               else:
                   user = str(check[1]).replace("('", "").replace("',)", "")
                   if user != "error":   
                    a = await lastfmhandler.get_tracks_recent(user, 1) 
                    userinfo = await lastfmhandler.get_user_info(user)
                    userpfp = userinfo["user"]["image"][2]["#text"]
                    albumplays = str(await lastfmhandler.get_album_playcount(user, a['recenttracks']['track'][0]))
                    artistplays = str(await lastfmhandler.get_artist_playcount(user, a['recenttracks']['track'][0]))
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    album = a["recenttracks"]['track'][0]['album']['#text'].replace(" ", "+")
                    stringdict = starData[0]
                    new = stringdict.replace('{track}', a['recenttracks']['track'][0]['name']).replace('{trackurl}', a['recenttracks']['track'][0]['url']).replace('{artist}', a['recenttracks']['track'][0]['artist']['#text']).replace('{artisturl}', f"https://last.fm/music/{artist}").replace('{trackimage}', (a['recenttracks']['track'][0])['image'][3]['#text']).replace('{artistplays}', artistplays).replace('{albumplays}', albumplays).replace('{trackplays}', await lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0])).replace('{album}', a['recenttracks']['track'][0]['album']['#text']).replace('{albumurl}', f"https://www.last.fm/music/{artist}/{album}").replace('{username}', user).replace('{scrobbles}', a['recenttracks']['@attr']['total']).replace('{useravatar}', userpfp)
                    dict1 = ast.literal_eval(new)
                    mes = await ctx.reply(embed=discord.Embed.from_dict(dict1), mention_author=False)
                    await mes.add_reaction("🔥")
                    await mes.add_reaction("🗑️") 

              elif check is None: 
                embed = discord.Embed(description=f"> __You don't have a **Last.fm account** linked. Use `.lf set <username>` to link your **account**.__", color=Colors.red)
                await ctx.reply(embed=embed, mention_author=False)      
        except Exception as e:
          embed = discord.Embed(description=f"> {ctx.author.mention}: unable to get your recent track - {e}", color=Colors.red)
          await ctx.reply(embed=embed, mention_author=False)          
    
async def setup(bot):
    await bot.add_cog(lastfm(bot))            
