import discord, button_paginator as pg, userhandler, lastfmhandler, aiosqlite, aiohttp, json
import ast
from discord.ext import commands  

def Sort_Tuple(tup):
    return(reversed(sorted(tup, key = lambda x: x[1])))


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

class lastfm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS lastfm (user_id INTEGER, username TEXT);")
        await self.bot.db.commit()    

    @commands.group(aliases = ['lf'])
    async def lastfm(self, ctx):
            if ctx.invoked_subcommand is None:
                dev = self.bot.get_user(565627105552105507)
                return await ctx.reply(f"{ctx.author.mention}: view the commands @ https://skidward.ml, for support contact **{dev.name}#{dev.discriminator}**")

    @lastfm.command(description="lastfm", help="register your lastfm account", usage="[name]")
    async def set(self, ctx, user=None):
            user = user.replace("https://www.last.fm/user/", "")
            if not await userhandler.lastfm_user_exists(user):
                    embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: [{user}](https://last.fm/user/{user}) is not a valid **Last.fm** username", color = 0x2f3136)
                    await ctx.reply(embed=embed)
            else:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT username FROM lastfm WHERE user_id = ?", (ctx.author.id,))
                    data = await cursor.fetchone()
                    if data is None:
                        await cursor.execute("INSERT INTO lastfm VALUES (?, ?)", (ctx.author.id, user,))
                        embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Your **Last.fm** username has been set as [{user}](https://last.fm/user/{user})")
                        return await ctx.reply(embed=embed)
                    elif data is not None:
                        await cursor.execute("UPDATE lastfm SET username = ? WHERE user_id = ?", (user, ctx.author.id,))
                        embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Your **Last.fm** username has been set as [{user}](https://last.fm/user/{user})")
                        return await ctx.reply(embed=embed)  
                await self.bot.db.commit()  

    @lastfm.command(description="lastfm", help="unset your lastfm account")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx): 
     async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        check = await cursor.fetchone()         
        await cursor.execute("DELETE FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        await self.bot.db.commit()
        embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Your **Last.fm** username has been deleted")
        await ctx.reply(embed=embed) 

    @lastfm.command(aliases = ['ta'], help="check a member's top 10 artists", description="lastfm", usage="<member>")
    async def topartists(self, ctx, member: discord.Member = None):
        if member == None: member=ctx.author
        try:
           x = ""
           async with self.bot.db.cursor() as cursor:
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
                        for i in range(10):
                            try:
                                x += f"`{int(i)+1}` **{jsonData['topartists']['artist'][int(i)]['name']}** ({jsonData['topartists']['artist'][int(i)]['playcount']} plays) \n"
                            except:
                                pass
                        embed = discord.Embed(description = x, color = 0x2f3136)
                        embed.set_author(name = f"{user}'s overall top artists", icon_url = ctx.message.author.avatar)
                        await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: You don't have a **Last.fm** account linked. Use `lf set <username>` to set your username", color = 0x2f3136)
                await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.send(e)

    @lastfm.command(aliases = ['tt'], help="check a member's top 10 tracks", description="lastfm", usage="<member>")
    async def toptracks(self, ctx, *, member: discord.Member=None):
        if member == None: member=ctx.author
        try:
           x = ""
           async with self.bot.db.cursor() as cursor:
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
                        for i in range(10):
                            try:
                                x += f"`{int(i)+1}` **{jsonData['toptracks']['track'][int(i)]['name']}** ({jsonData['toptracks']['track'][int(i)]['playcount']} plays) \n"
                            except:
                                pass
                        embed = discord.Embed(description = x, color = 0x2f3136)
                        embed.set_author(name = f"{user}'s overall top tracks", icon_url = ctx.message.author.avatar)
                        await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: You don't have a **Last.fm** account linked. Use `lf set <username>` to set your username", color = 0x2f3136)
                await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.send(e)

    @lastfm.command(aliases = ['tal'], help="check a member's top 10 albums", description="lastfm", usage="<member>")
    async def topalbums(self,ctx, *, member: discord.Member=None):
        if member == None: member=ctx.author
        try:
           x = ""
           async with self.bot.db.cursor() as cursor:
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
                        for i in range(10):
                            try:
                                x += f"`{int(i)+1}` **{jsonData['topalbums']['album'][int(i)]['name']}** ({jsonData['topalbums']['album'][int(i)]['playcount']} plays)\n"
                            except:
                                pass
                        embed = discord.Embed(description = x, color = 0x2f3136)
                        embed.set_author(name = f"{user}'s overall top albums", icon_url = ctx.message.author.avatar)
                        await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: You don't have a **Last.fm** account linked. Use `lf set <username>` to set your username", color = 0x2f3136)
                await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.send(e)

    @lastfm.command(aliases = ['wk'], description="lastfm", help="see who knows a certain artist in the server", usage="[artist]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def whoknows(self, ctx: commands.Context, * ,artist):
     try:   
      lis = []  
      async with ctx.typing():
       async with self.bot.db.cursor() as cursor:
        for user in ctx.guild.members: 
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
              tag1 = jsonData["artist"]["tags"]["tag"][0]["name"]
              tag2 = jsonData["artist"]["tags"]["tag"][1]["name"]
              tag3 = jsonData["artist"]["tags"]["tag"][2]["name"]
              tag4 = jsonData["artist"]["tags"]["tag"][3]["name"]
              tag5 = jsonData["artist"]["tags"]["tag"][4]["name"]
              if len(jsonData['artist']['stats']['userplaycount']) > 1: 
               lis.append(tuple((f"{use.name}#{use.discriminator}", int(userplays), username)))
              else:
               continue
             except KeyError: 
                continue           
         elif check is not None:
            continue 

       if lis == []:
         await ctx.reply(f"nobody (not even you) has listened to **{artist}**") 
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
            listeners += f"`👑` **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n"
        else:    
         listeners += f"`{num}` **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n"  
        if listenerscount == 10:
         messages.append(listeners)
         number.append(discord.Embed(color = 0x2f3136, description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{tag1}, {tag2}, {tag3}, {tag4}, {tag5}"))
         i+=1
         listeners = ""
       if num == 0:
         await ctx.reply(f"nobody (not even you) has listened to **{artist}**") 
         return 
       messages.append(listeners)
       embe = discord.Embed(color = 0x2f3136, description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{tag1}, {tag2}, {tag3}, {tag4}, {tag5}")
       number.append(embe)
       if len(number) > 1:
        paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        paginator.add_button('prev')
        paginator.add_button('delete')
        paginator.add_button('next')
        await paginator.start()
       else: 
        await ctx.send(embed=embe)  
     except Exception as e:
        await ctx.reply(f"thats not a **valid** artist")
        print(e) 
    
    @lastfm.command(aliases=["gwk"], description="lastfm", help="see who knows a certain artist across all servers the bot is in", usage="[artist]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def globalwhoknows(self, ctx: commands.Context, * ,artist):
     try:   
      lis = []
      lol = ""
      num = 0
      async with ctx.typing():
       async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM lastfm")
        results = await cursor.fetchall()
        for check in results:
         use = await self.bot.fetch_user(check[0])   
         username = str(check[1]).replace("('", "").replace("',)", "")
         if username != "error": 
          async with aiohttp.ClientSession() as session:
           params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7", "user": username, "artist" : artist, "method": "artist.getInfo", "autocorrect": "1", "format":"json"}
           async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
            resp = await response.read()
            jsonData = json.loads(resp)
            try:
             userplays = jsonData['artist']['stats']['userplaycount']
             tag1 = jsonData["artist"]["tags"]["tag"][0]["name"]
             tag2 = jsonData["artist"]["tags"]["tag"][1]["name"]
             tag3 = jsonData["artist"]["tags"]["tag"][2]["name"]
             tag4 = jsonData["artist"]["tags"]["tag"][3]["name"]
             tag5 = jsonData["artist"]["tags"]["tag"][4]["name"]
             if len(jsonData['artist']['stats']['userplaycount']) > 1: 
              lis.append(tuple((f"{use.name}#{use.discriminator}", int(userplays), username)))
             else:
              continue
            except KeyError: 
                continue            

       if lis == []:
         await ctx.reply(f"nobody (not even you) has listened to **{artist}**") 
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
            listeners += f"`👑` **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n"
        else:    
         listeners += f"`{num}` **[{l[0]}](https://last.fm/user/{l[2]})** has **{l[1]}** plays\n" 
        if listenerscount == 10:
         messages.append(listeners)
         number.append(discord.Embed(color = 0x2f3136, description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{tag1}, {tag2}, {tag3}, {tag4}, {tag5}"))
         i+=1
         listeners = ""
       if num == 0:
         await ctx.reply(f"nobody (not even you) has listened to **{artist}**")
         return 
       messages.append(listeners)
       embe = discord.Embed(color = 0x2f3136, description=messages[i]).set_author(name = f"Who knows {artist}?", icon_url = ctx.author.display_avatar).set_footer(text = f"{tag1}, {tag2}, {tag3}, {tag4}, {tag5}")
       number.append(embe)
       if len(number) > 1:
        paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        paginator.add_button('prev')
        paginator.add_button('delete')
        paginator.add_button('next')
        await paginator.start()
       else: 
        await ctx.send(embed=embe)  
     except:
        embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: **{artist}** is not a **valid artist**", color = 0x2f3136)
        await ctx.reply(embed=embed) 


    @lastfm.command(aliases = ['mode'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def embed(self, ctx, *,cc):
            try:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT mode FROM lfmode WHERE user = ?", (ctx.author.id,))
                    starData = await cursor.fetchone()
                    if starData:
                        starData = starData[0]
                        if cc == "none":
                            if starData is not None:
                                await cursor.execute("DELETE FROM lfmode WHERE user = ?", (ctx.author.id,))
                                await self.bot.db.commit()
                                embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Your **Last.fm** embed has been deleted")
                                return await ctx.reply(embed=embed)
                            else:
                                embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: You don't have a **Last.fm** embed set", color = 0x2f3136)
                                return await ctx.reply(embed=embed)
                        if cc == "view":
                            await cursor.execute("SELECT mode FROM lfmode WHERE user = ?", (ctx.author.id,))
                            starData = await cursor.fetchone()
                            if starData is None: 
                                embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: You don't have a **Last.fm** embed set", color = 0x2f3136)
                                return await ctx.reply(embed=embed)
                            code = starData[0]
                            embed = discord.Embed(color = 0x2f3136, description = f"```​{code}\n```")
                            return await ctx.reply(embed=embed)
                        if cc == starData:
                            embed = discord.Embed(description=f"<:fail:1034500518782980119> {ctx.author.mention}: That's already set as your **Last.fm** embed code", color = 0x2f3136)
                            return await ctx.reply(embed=embed)
                        else:    
                         await cursor.execute("UPDATE lfmode SET mode = ? WHERE user = ?", (cc, ctx.author.id,))
                         await self.bot.db.commit()
                         embed = discord.Embed(color = 0x2f3136, description = f"""<:success:1034500520926253146> {ctx.author.mention}: Your **Last.fm** embed has been updated to the following:
```{cc}```""")
                         return await ctx.reply(embed=embed)
                    elif starData is None:
                        await cursor.execute("INSERT INTO lfmode VALUES (?, ?)", (cc, ctx.author.id,))
                        await self.bot.db.commit()
                        embed = discord.Embed(color = 0x2f3136, description = f"""<:success:1034500520926253146> {ctx.author.mention}: Your **Last.fm** embed has been updated to the following:
```{cc}```""")
                        return await ctx.reply(embed=embed)
            except Exception as er:
              await ctx.reply(er)          

    @lastfm.command(aliases = ['cc'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def customcommand(self, ctx, *,cc):
            try:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT command FROM customcommands WHERE user = ?", (ctx.author.id,))
                    starData = await cursor.fetchone()
                    if starData:
                        starData = starData[0]
                        if cc == "none":
                            await cursor.execute("DELETE FROM customcommands WHERE user = ?", (ctx.author.id,))
                            await self.bot.db.commit()
                            embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Your **Last.fm** custom command has been deleted")
                            return await ctx.reply(embed=embed)
                        if cc == starData:
                            return await ctx.reply("thats already set as your custom command")
                        else:    
                         await cursor.execute("UPDATE customcommands SET command = ? WHERE user = ?", (cc, ctx.author.id,))
                         await self.bot.db.commit()
                         embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Your **Last.fm** custom command has been set as `{cc}`")
                         return await ctx.reply(embed=embed)
                    elif starData is None:
                        await cursor.execute("INSERT INTO customcommands VALUES (?, ?)", (cc, ctx.author.id,))
                        await self.bot.db.commit()
                        embed = discord.Embed(color = 0x2f3136, description = f"<:success:1034500520926253146> {ctx.author.mention}: Your **Last.fm** custom command has been set as `{cc}`")
                        return await ctx.reply(embed=embed)
            except Exception as er:
              await ctx.reply(er) 

    @commands.command(aliases=['np', 'fm'], description="lastfm")
    async def nowplaying(self, ctx):
            async with ctx.typing():
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("SELECT username FROM lastfm WHERE user_id = ?", (ctx.author.id,))
                    data = await cursor.fetchone()
                    if data:
                        await cursor.execute("SELECT mode FROM lfmode WHERE user = ?", (ctx.author.id,))
                        mode = await cursor.fetchone()
                        async with aiohttp.ClientSession() as session:
                            params= {"api_key" : "e739760b740efae08aeef62f0e15d7b7",
                            "user" : data[0],
                            "method":"user.getRecentTracks",
                            "format":"json"}
                            async with session.get(url="http://ws.audioscrobbler.com/2.0", params=params) as response:
                                resp = await response.read()
                                sex = json.loads(resp)
                            async with session.get(f"https://ws.audioscrobbler.com/2.0?method=track.getInfo&username={data[0]}&api_key=e739760b740efae08aeef62f0e15d7b7&artist={sex['recenttracks']['track'][0]['artist']['#text']}&track={sex['recenttracks']['track'][0]['name'].replace('#', '%23')}&format=json&autocorrect=1") as res:
                                z = await res.read()
                                x = json.loads(z)
                            async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=artist.getInfo&api_key=e739760b740efae08aeef62f0e15d7b7&artist={sex['recenttracks']['track'][0]['artist']['#text']}&format=json&username={data[0]}") as res:
                                g = await res.read()
                                v = json.loads(g)
                            if mode:
                                code = mode[0].replace(
                                    "{user}", data[0]
                                    ).replace(
                                    "{track}", sex['recenttracks']['track'][0]['name']
                                    ).replace(
                                    "{artist}", sex['recenttracks']['track'][0]['artist']['#text']
                                    ).replace(
                                    "{album}", sex['recenttracks']['track'][0]['album']['#text']
                                    ).replace(
                                    "{trackimage}", sex['recenttracks']['track'][0]['image'][3]['#text']
                                    ).replace(
                                    "{trackplays}", x['track']['userplaycount']
                                    ).replace(
                                    "{artistplays}", v['artist']['stats']['userplaycount']
                                    ).replace(
                                    "{scrobbles}", sex['recenttracks']['@attr']['total']
                                    ).replace(
                                    "{trackurl}", sex['recenttracks']['track'][0]['url']
                                    ).replace(
                                    "{artisturl}", f"https://last.fm/music/{sex['recenttracks']['track'][0]['artist']['#text'].replace(' ', '+')}"
                                    )
                                em = await to_object(await embed_replacement(ctx.author, code))
                                await ctx.send(content = em[0], embed = em[1], view = em[2])
                            else:
                                embed = discord.Embed(color = 0x2f3136)
                                try:
                                    embed.add_field(
                                        name = "**Track**",
                                        value = f"[{sex['recenttracks']['track'][0]['name']}]({sex['recenttracks']['track'][0]['url']})",
                                        inline = False)
                                except Exception as e:
                                    await ctx.send(e)
                                embed.add_field(
                                    name = "**Artist**",
                                    value = f"[{sex['recenttracks']['track'][0]['artist']['#text']}](https://last.fm/music/{sex['recenttracks']['track'][0]['artist']['#text'].replace(' ', '+')})",
                                    inline = False)
                                embed.set_author(name = data[0], icon_url = ctx.author.display_avatar)
                                embed.set_thumbnail(url= sex['recenttracks']['track'][0]['image'][3]['#text'])
                                embed.set_footer(text = f"Playcount: {x['track']['userplaycount']} | Scrobbles: {sex['recenttracks']['@attr']['total']}")
                                await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT command, user FROM customcommands WHERE user = ?", (message.author.id,))
            data = await cursor.fetchone()
            if data:
                cc = data[0]
                user = data[1]
                if message.author.id == user:
                    if message.content == cc:
                        ctx = await self.bot.get_context(message)
                        await ctx.invoke(self.bot.get_command("nowplaying"))
                    else:
                        pass
                else:
                    pass
            else:
                pass
                 
    
async def setup(bot):
    await bot.add_cog(lastfm(bot))            