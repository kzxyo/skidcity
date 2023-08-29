import discord, json, typing, handlers.userhandler as userhandler, traceback
from discord.ext import commands, tasks  
from tools.utils import EmbedBuilder
from handlers.lastfmhandler import Handler
from cogs.donor import premium

def sort_key(lis): 
   return lis[1]

async def lf_add_reactions(ctx: commands.Context, message: typing.Union[discord.Message, None]): 
 if message is None: return 
 check = await ctx.bot.db.fetchrow("SELECT * FROM lfreactions WHERE user_id = $1", ctx.author.id) 
 if not check: 
  for i in ["🔥", "🗑️"]: await message.add_reaction(i)
  return 
 reactions = json.loads(check["reactions"])
 if reactions[0] == "none": return
 for r in reactions: await message.add_reaction(r)
 return  

async def lastfm_message(ctx: commands.Context, content: str) -> discord.Message: 
 return await ctx.reply(embed=discord.Embed(color=0xff0000, description=f"> <:lastfm:1140663954708889712> {ctx.author.mention}: {content}"))  

@tasks.loop(hours=1)
async def clear_caches(bot: commands.AutoShardedBot):
  lol = Lastfm(bot)
  lol.globalwhoknows_cache = []
  lol.lastfm_crowns = [] 

class Lastfm(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.lastfmhandler = Handler("43693facbb24d1ac893a7d33846b15cc")
        self.lastfm_crowns = {}
        self.globalwhoknows_cache = {}
    
    async def lastfm_replacement(self, user: str, params: str) -> str: 
     a = await self.lastfmhandler.get_tracks_recent(user, 1) 
     userinfo = await self.lastfmhandler.get_user_info(user)
     userpfp = userinfo["user"]["image"][2]["#text"]
     artist = a['recenttracks']['track'][0]['artist']['#text']
     albumplays = await self.lastfmhandler.get_album_playcount(user, a['recenttracks']['track'][0]) or "N/A"
     artistplays = await self.lastfmhandler.get_artist_playcount(user, artist) 
     trackplays = await self.lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0]) or "N/A"
     album = a["recenttracks"]['track'][0]['album']['#text'].replace(" ", "+") or "N/A"     
     params = params.replace('{track}', a['recenttracks']['track'][0]['name']).replace('{trackurl}', a['recenttracks']['track'][0]['url']).replace('{artist}', a['recenttracks']['track'][0]['artist']['#text']).replace('{artisturl}', f"https://last.fm/music/{artist.replace(' ', '+')}").replace('{trackimage}', str((a['recenttracks']['track'][0])['image'][3]['#text']).replace('{https', "https")).replace('{artistplays}', str(artistplays)).replace('{albumplays}', str(albumplays)).replace('{trackplays}', str(trackplays)).replace('{album}', a['recenttracks']['track'][0]['album']['#text'] or "N/A").replace('{albumurl}', f"https://www.last.fm/music/{artist.replace(' ', '+')}/{album.replace(' ', '+')}" or "https://none.none").replace('{username}', user).replace('{scrobbles}', a['recenttracks']['@attr']['total']).replace('{useravatar}', userpfp)    
     return params
    
    @commands.Cog.listener()
    async def on_ready(self): 
     clear_caches.start(self.bot)  

    @commands.group(invoke_without_command=True, aliases = ['lf'])
    async def lastfm(self, ctx: commands.Context):
        await ctx.create_pages()

    @lastfm.command(name="set", help="lastfm", description="register your lastfm account", usage="[name]")
    async def lf_set(self, ctx: commands.Context, *, ref: str):
      if not await userhandler.lastfm_user_exists(ref): return await lastfm_message(ctx, "**Invalid** Last.Fm username")                        
      check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = {}".format(ctx.author.id))
      if not check: await self.bot.db.execute("INSERT INTO lastfm VALUES ($1,$2)", ctx.author.id, ref)
      else: await self.bot.db.execute("UPDATE lastfm SET username = $1 WHERE user_id = $2", ref, ctx.author.id)
      return await lastfm_message(ctx, f"Your **Last.fm** username has been set to **{ref}**")

    @lastfm.command(name="remove", help="lastfm", description="unset your lastfm account")
    async def lf_remove(self, ctx: commands.Context):      
        check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = {}".format(ctx.author.id))        
        if not check: return await lastfm_message(ctx, "you don't have a **last.fm** account connected".capitalize())
        await self.bot.db.execute("DELETE FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        await lastfm_message(ctx, "Your **last.fm** account has been removed")
         
    @lastfm.command(name="variables", description="view lastfm custom embed variables", help="lastfm")
    async def lf_variables(self, ctx: commands.Context):
        await ctx.invoke(self.bot.get_command("embed variables"))

    @lastfm.group(invoke_without_command=True, name="embed", description="create your own lastfm custom embed", aliases=["mode"], help="lastfm")
    async def lf_embed(self, ctx: commands.Context):
     await ctx.create_pages()
    
    @lf_embed.command(name="steal", description="steal someone's custom lastfm embed (premium feature)", help="lastfm", usage="[member]")
    @premium()
    async def lf_embed_steal(self, ctx: commands.Context, *, member: discord.Member): 
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", member.id)
     if not check: return await ctx.send_warning(f"**{member}** doesn't have a custom lastfm embed")
     re = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not re: await self.bot.db.execute("INSERT INTO lfmode VALUES ($1,$2)", ctx.author.id, check['mode'])
     else: await self.bot.db.execute("UPDATE lfmode SET mode = $1 WHERE user_id = $2", check['mode'], ctx.author.id)
     return await lastfm_message(ctx, f"Succesfully copied **{member.name}'s** custom lastfm embed")  

    @lf_embed.command(name="set", description="set a personal embed as the lastfm embed", help="lastfm", usage="[message | embed code]")                 
    async def lf_embed_set(self, ctx: commands.Context, *, embed: str):   
     invites = [".gg/", "discord.gg/", "https://discord.com/invite/", "https://discordapp.com/oauth2/authorize?"]
     if any(invite in ctx.message.content for invite in invites): 
      await ctx.send_warnning("You cannot have discord invite links in your **last.fm** embed")
      await ctx.message.delete()
      return
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not check: await self.bot.db.execute("INSERT INTO lfmode VALUES ($1,$2)", ctx.author.id, embed)
     else: await self.bot.db.execute("UPDATE lfmode SET mode = $1 WHERE user_id = $2", embed, ctx.author.id) 
     await lastfm_message(ctx, f"Set your **last.fm** mode to\n```{embed}```")              
    
    @lf_embed.command(name="view", description="check your lastfm custom embed", help="lastfm")
    async def lf_embed_view(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not check: return await lastfm_message(ctx, "You do not have any **last.fm** embed") 
     embed = discord.Embed(color=self.bot.color, description=f"```{check['mode']}```")
     return await ctx.reply(embed=embed)    

    @lf_embed.command(name="none", description="clear your last.fm custom embed", help="lastfm", aliases=["delete"])
    async def lf_embed_none(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not check: return await lastfm_message(ctx, "You do not have any **last.fm** embed") 
     await self.bot.db.execute("DELETE FROM lfmode WHERE user_id = $1", ctx.author.id)
     await lastfm_message(ctx, "Deleted your **last.fm** embed")  

    
    @lastfm.command(name="topartists", aliases = ['ta', "tar"], description="check a member's top 10 artists", help="lastfm", usage="<member>")
    async def lf_topartists(self, ctx, member: discord.Member=None):
        try:
           if member is None: member = ctx.author
           check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))           
           if check:   
                user = check["username"]
                if user != "error": 
                 jsonData = await self.lastfmhandler.get_top_artists(user, 10)
                 mes = '\n'.join(f"`{i+1}` **[{jsonData['topartists']['artist'][i]['name']}]({jsonData['topartists']['artist'][i]['url']})** {jsonData['topartists']['artist'][i]['playcount']} plays" for i in range(10))
                 embed = discord.Embed(description = mes,color=self.bot.color)
                 embed.set_thumbnail(url = member.display_avatar)
                 embed.set_author(name = f"{user}'s overall top artists", icon_url = member.display_avatar)
                 return await ctx.reply(embed=embed)  
           else: return await lastfm_message(ctx, "There is no **last.fm** account linked for this member")
        except Exception as e:
            print(e)

    @lastfm.command(name="toptracks", aliases = ['tt'], description="check a member's top 10 tracks", help="lastfm", usage="<member>")
    async def lf_toptracks(self, ctx: commands.Context, *, member: discord.Member=None):
        if member == None: member = ctx.author
        try:
            check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
            if check:  
                user = check["username"]
                if user != "error":    
                  jsonData = await self.lastfmhandler.get_top_tracks(user, 10)                               
                  embed = discord.Embed(description = '\n'.join(f"`{i+1}` **[{jsonData['toptracks']['track'][i]['name']}]({jsonData['toptracks']['track'][i]['url']})** {jsonData['toptracks']['track'][i]['playcount']} plays" for i in range(10)),color = self.bot.color)
                  embed.set_thumbnail(url = ctx.message.author.avatar)
                  embed.set_author(name = f"{user}'s overall top tracks", icon_url = ctx.message.author.avatar)
                  return await ctx.reply(embed=embed)   
            else: return await lastfm_message(ctx, "There is no **last.fm** account linked for this member")
        except Exception as e:
            print(e)

    @lastfm.command(name="topalbums", aliases = ['tal'], description="check a member's top 10 albums", help="lastfm", usage="<member>")
    async def lf_topalbums(self,ctx: commands.Context, *, member: discord.Member=None):
        if member == None: member=ctx.author
        try:
           check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))
           if check:  
             user = check["username"]
             if user != "error":                     
                  jsonData = await self.lastfmhandler.get_top_albums(user, 10)
                  embed = discord.Embed(description = '\n'.join(f"`{i+1}` **[{jsonData['topalbums']['album'][i]['name']}]({jsonData['topalbums']['album'][i]['url']})** {jsonData['topalbums']['album'][i]['playcount']} plays" for i in range(10)),color = self.bot.color)
                  embed.set_thumbnail(url = ctx.message.author.avatar)
                  embed.set_author(name = f"{user}'s overall top albums", icon_url = ctx.message.author.avatar)
                  return await ctx.reply(embed=embed)   
           else: return await lastfm_message(ctx, "There is no **last.fm** account linked for this member")
        except Exception as e:
            print(e)

    @lastfm.command(name="user", aliases=["ui"], description="lastfm", help="check info about a lastfm user", usage="<username>")
    async def lf_user(self, ctx: commands.Context, user: typing.Union[discord.User, discord.Member] = commands.Author):
            await ctx.channel.typing()                    
            check = await self.bot.db.fetchrow('SELECT username FROM lastfm WHERE user_id = $1', user.id)
            username = check["username"]
            if not check: return await ctx.send_warning(f"{'You don' if user == ctx.author else f'**{user}** doesn'}'t have a **last.fm** account connected")
            info = await self.lastfmhandler.get_user_info(username)
            try:
             i = info["user"]
             name = i["name"]
             age = int(i["age"])
             subscriber = f"{'false' if i['subscriber'] == '0' else 'true'}"
             realname = i["realname"]
             playcount = int(i["playcount"])
             artistcount = int(i["artist_count"])
             trackcount = int(i["track_count"])
             albumcount = int(i["album_count"])
             image = i["image"][3]["#text"]

             embed = discord.Embed(color=self.bot.color)
             embed.set_footer(text=f"{playcount:,} total scrobbles")
             embed.set_thumbnail(url=image)
             embed.set_author(name=f"{name}", icon_url=image)
             embed.add_field(name=f"Plays", value=f"**artists:** {artistcount:,}\n**plays:** {playcount:,}\n**tracks:** {trackcount:,}\n**albums:** {albumcount:,}", inline=False)
             embed.add_field(name=f"Info", value=f"**name:** {realname}\n**registered:** <t:{int(i['registered']['#text'])}:R>\n**subscriber:** {subscriber}\n**age:** {age:,}", inline=False)
             await ctx.reply(embed=embed)
            except TypeError: return await lastfm_message(ctx, "This user doesn't have a **last.fm** account connected")

    @lastfm.command(name="whoknows", aliases = ['wk'], help="lastfm", description="see who knows a certain artist in the server", usage="[artist]")
    async def lf_whoknows(self, ctx: commands.Context, * , artist: str=None):
     await ctx.typing()
     check = await self.bot.db.fetchrow("SELECT username FROM lastfm WHERE user_id = {}".format(ctx.author.id))
     if check is None: return await lastfm_message(ctx, "You don't have a **last.fm** account connected")
     fmuser = check['username']
     if not artist:    
       resp = await self.lastfmhandler.get_tracks_recent(fmuser, 1)
       artist = resp["recenttracks"]["track"][0]["artist"]["#text"]

     tuples = []
     rows = []      
     ids = [str(m.id) for m in ctx.guild.members]
     results =  await self.bot.db.fetch(f"SELECT * FROM lastfm WHERE user_id IN ({','.join(ids)})")     
     if len(results) == 0: return await lastfm_message(ctx, "No one has a **last.fm** account linked")
     for result in results: 
          user_id = int(result[0])
          fmuser2 = result[1] 
          us = ctx.guild.get_member(user_id)
          z = await self.lastfmhandler.get_artist_playcount(fmuser2, artist)
          tuples.append((str(us), int(z), f"https://last.fm/user/{fmuser2}", us.id))
          
     num = 0
     for x in sorted(tuples, key=lambda n: n[1])[::-1][:10]:
        if x[1] != 0:
          num += 1
          rows.append(f"{'<a:crown:1021829752782323762>' if num == 1 else f'`{num}`'} [**{x[0]}**]({x[2]}) has **{x[1]}** plays")

     if len(rows) == 0: return await ctx.reply(f"Nobody (not even you) has listened to {artist}")               
     embeds = []
     embed = discord.Embed(color=self.bot.color, description="\n".join(rows))
     embed.set_author(name=f"Who knows {artist} in {ctx.guild.name}", icon_url=ctx.guild.icon)
     embed.set_thumbnail(url=ctx.guild.icon)
     embeds.append(embed)     
     return await ctx.reply(embeds=embeds) 
    
    
    @lastfm.command(name="globalwhoknows", aliases=["gwk"], help="lastfm", description="see who knows a certain artist across all servers the bot is in", usage="[artist]")
    async def lf_globalwhoknows(self, ctx: commands.Context, * ,artist: str=None):
      await ctx.typing()
      check = await self.bot.db.fetchrow("SELECT username FROM lastfm WHERE user_id = {}".format(ctx.author.id))
      if check is None: return await lastfm_message(ctx, "You don't have a **last.fm** account connected")
      fmuser = check['username']
      if not artist:    
       resp = await self.lastfmhandler.get_tracks_recent(fmuser, 1)
       artist = resp["recenttracks"]["track"][0]["artist"]["#text"]
      tuples = []  
      o = 0 
      if not self.globalwhoknows_cache.get(artist):
       o = 1
       ids = [str(m.id) for m in self.bot.users]     
       results = await self.bot.db.fetch(f"SELECT * FROM lastfm WHERE user_id IN ({','.join(ids)})")     
       if len(results) == 0: return await lastfm_message(ctx, "No one has a **last.fm** account linked")
       for result in results: 
          user_id = int(result[0])
          fmuser2 = result[1] 
          us = self.bot.get_user(user_id)
          if not us: continue
          z = await self.lastfmhandler.get_artist_playcount(fmuser2, artist)
          tuples.append(tuple([str(us), int(z), f"https://last.fm/user/{fmuser2}", us.id]))
       self.globalwhoknows_cache[artist] = sorted(tuples, key=lambda n: n[1])[::-1][:10]   
       gwk_list = sorted(tuples, key=lambda n: n[1])[::-1][:10]
      else: gwk_list = self.globalwhoknows_cache[artist]    
      num = 0
      rows = []
      for x in gwk_list:
        if x[1] != 0:
          num += 1
          rows.append(f"{'<a:crown:1021829752782323762>' if num == 1 else f'`{num}`'} [**{x[0]}**]({x[2]}) has **{x[1]}** plays")

      if len(rows) == 0: return await ctx.reply(f"Nobody (not even you) has listened to {artist}")               
      embeds = []
      embed = discord.Embed(color=self.bot.color, description="\n".join(rows))
      embed.set_author(name=f"Who knows {artist}")
      embed.set_thumbnail(url=ctx.guild.icon)
      embeds.append(embed)
      if o == 0: return await ctx.reply(embed=embeds[0])
      re = await self.bot.db.fetchrow("SELECT * FROM lfcrowns WHERE user_id = $1 AND artist = $2", sorted(tuples, key=lambda n: n[1])[::-1][0][3], artist)
      if not re: 
        embeds.append(discord.Embed(color=self.bot.color, description=f"> `{(await self.bot.fetch_user(sorted(tuples, key=lambda n: n[1])[::-1][0][3]))}` claimed the crown for **{artist}**"))
        ar = await self.bot.db.fetchrow("SELECT * FROM lfcrowns WHERE artist = $1", artist)
        if ar: await self.bot.db.execute("UPDATE lfcrowns SET user_id = $1 WHERE artist = $2", sorted(tuples, key=lambda n: n[1])[::-1][0][3], artist) 
        else: await self.bot.db.execute("INSERT INTO lfcrowns VALUES ($1,$2)", sorted(tuples, key=lambda n: n[1])[::-1][0][3], artist)
      return await ctx.reply(embeds=embeds)  
    

    @lastfm.command(name="reactions", help="lastfm", description="add custom reactions to your lastfm embed", usage="[emojis | none]\nnone -> no reactions for np command\nno emoji -> default emojis will be used")
    async def lf_reactions(self, ctx: commands.Context, *emojis: str): 
     check = await self.bot.db.fetchrow("SELECT * FROM lfreactions WHERE user_id = $1", ctx.author.id)
     if len(emojis) == 0: 
      if not check: return await lastfm_message(ctx, "You don't have any **last.fm** custom reaction to remove")
      await self.bot.db.execute("DELETE FROM lfreactions WHERE user_id = $1", ctx.author.id)
      return await lastfm_message(ctx, "Deleted your **last.fm** custom reactions")
     sql_as_text = json.dumps(emojis)    
     if check: await self.bot.db.execute("UPDATE lfreactions SET reactions = $1 WHERE user_id = $2", sql_as_text, ctx.author.id)
     else: await self.bot.db.execute("INSERT INTO lfreactions VALUES ($1,$2)", ctx.author.id, sql_as_text)
     return await lastfm_message(ctx, f"Your **last.fm** reactions are {''.join([e for e in emojis])}")
    
    @lastfm.command(name="howto", help="lastfm", description="tutorial for using lastfm", aliases=["tutorial"])
    async def lf_howto(self, ctx: commands.Context): 
      await ctx.reply(f"1) create an account at https://last.fm\n2) link your **spotify** account to your **last.fm** account\n3) use the command `{ctx.clean_prefix}lf set [your lastfm username]`\n4) while you listen to your songs, you can use the `{ctx.clean_prefix}nowplaying` command") 

    @lastfm.command(name="crowns", help="lastfm", description="get the crowns of a member", usage="<user>") 
    async def lf_crowns(self, ctx: commands.Context, *, member: discord.User=None): 
      if member is None: member = ctx.author 
      check = await self.bot.db.fetch("SELECT * FROM lfcrowns WHERE user_id = $1", member.id)
      if len(check) == 0: return await lastfm_message(ctx, "I looked far and wide, but couldn't find any crown for **{}**".format(member))
      await ctx.typing()
      if not self.lastfm_crowns.get(str(member.id)): 
        re = await self.bot.db.fetchrow('SELECT * FROM lastfm WHERE user_id = $1', member.id)
        idk = [(x['artist'], await self.lastfmhandler.get_artist_playcount(re['username'], x['artist'])) for x in check]
        crowns = sorted(idk, key=lambda s: s[1])[::-1]
        self.lastfm_crowns[str(member.id)] = crowns
      else: crowns = self.lastfm_crowns[str(member.id)]
      i=1 
      l=1 
      embeds = []
      mes = ""
      for c in crowns: 
       mes += f"`{i}` **{c[0]}** - **{c[1]}** plays\n"
       i+=1
       l+=1
       if l == 11: 
        embeds.append(discord.Embed(color=self.bot.color, title=f"{member.name}'s cronws ({len(check)})", description=mes))  
        mes = ""
        l = 1 
      embeds.append(discord.Embed(color=self.bot.color, title=f"{member.name}'s cronws ({len(check)})", description=mes))    
      return await ctx.paginator(embeds) 
    
    @commands.command(aliases=["gwk"], help="lastfm", description="see who knows a certain artist across all servers the bot is in", usage="[artist]")
    async def globalwhoknows(self, ctx: commands.Context, *, artist: str=None): 
      await ctx.invoke(self.bot.get_command("lastfm globalwhoknows"), artist=artist)

    @commands.command(aliases = ['wk'], help="lastfm", description="see who knows a certain artist in the server", usage="[artist]") 
    async def whoknows(self, ctx: commands.Context, *, artist: str=None):
      await ctx.invoke(self.bot.get_command("lastfm whoknows"), artist=artist)    
    
    @commands.command(aliases = ['tal'], description="check a member's top 10 albums", help="lastfm", usage="<member>")
    async def topalbums(self, ctx: commands.Context, *, member: discord.Member=None): 
     await ctx.invoke(self.bot.get_command("lastfm topalbums"), member=member)

    @commands.command(aliases = ['tt'], description="check a member's top 10 tracks", help="lastfm", usage="<member>")
    async def toptracks(self, ctx: commands.Context, *, member: discord.Member=None): 
      await ctx.invoke(self.bot.get_command("lastfm toptracks"), member=member) 
    
    @commands.command(aliases = ['ta', "tar"], description="check a member's top 10 artists", help="lastfm", usage="<member>")
    async def topartists(self, ctx: commands.Context, *, member: discord.Member=None): 
     await ctx.invoke(self.bot.get_command("lastfm topartists"), member=member)   

    @commands.command(aliases=['np', 'fm'], help="lastfm", description="check what song is playing right now", usage="<user>")
    async def nowplaying(self, ctx: commands.Context, *, member: discord.User=None):
        if member is None: member = ctx.author
        try:
            await ctx.typing()             
            check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))            
            if check:   
               starData = await self.bot.db.fetchrow("SELECT mode FROM lfmode WHERE user_id = $1", member.id)
               if starData is None:  
                user = check['username']
                if user != "error":      
                    a = await self.lastfmhandler.get_tracks_recent(user, 1)
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    album = a['recenttracks']['track'][0]['album']['#text'] or "N/A"
                    embed = discord.Embed(colour=self.bot.color)
                    embed.add_field(name="**Track:**", value = f"""[{"" + a['recenttracks']['track'][0]['name']}]({"" + a['recenttracks']['track'][0]['url']})""", inline = False)
                    embed.add_field(name="**Artist:**", value = f"""[{a['recenttracks']['track'][0]['artist']['#text']}](https://last.fm/music/{artist})""", inline = False)
                    embed.set_author(name = user, icon_url = member.display_avatar, url = f"https://last.fm/user/{user}")                               
                    embed.set_thumbnail(url=(a['recenttracks']['track'][0])['image'][3]['#text'])
                    embed.set_footer(text = f"Track Playcount: {await self.lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0])} ・Album: {album}", icon_url = (a['recenttracks']['track'][0])['image'][3]['#text'])
                    message = await ctx.reply(embed=embed)
                    return await lf_add_reactions(ctx, message)
               else:
                user = check['username']
                try: 
                 x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, await self.lastfm_replacement(user, starData[0])))
                 message = await ctx.send(content=x[0], embed=x[1], view=x[2])
                except: message = await ctx.send(await self.lastfm_replacement(user, starData[0]))
                return await lf_add_reactions(ctx, message)
            elif check is None: return await lastfm_message(ctx, f"**{member}** doesn't have a **Last.fm account** linked. Use `{ctx.clean_prefix}lf set <username>` to link your **account**.")                      
        except Exception: 
           print(traceback.format_exc())
           return await lastfm_message(ctx, f"unable to get **{member.name}'s** recent track".capitalize())  
    
async def setup(bot):
    await bot.add_cog(Lastfm(bot))            