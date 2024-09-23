import discord, json, typing, traceback, asyncio, os
from discord import Embed
from discord.ext import commands, tasks  
from utils.utils import EmbedBuilder
from patches.lastfm import LastFMHandler as Handler
from typing import Literal
from io import BytesIO
from discord import File
from bot.headers import Session

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
 for r in reactions: 
    try: await message.add_reaction(r)
    except discord.NotFound: return await ctx.send("I cannot access your custom Last.FM reactions, please run ``;lf reactions`` to delete them.")  

@tasks.loop(hours=1)
async def clear_caches(bot: commands.Bot):
  lol = lastfm(bot)
  lol.globalwhoknows_cache = []
  lol.lastfm_crowns = [] 

class lastfm(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lastfmhandler = Handler("43693facbb24d1ac893a7d33846b15cc")
        self.lastfm_crowns = {}
        self.globalwhoknows_cache = {}
        self.session = Session()
    
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

    @lastfm.command(name="remove", description="unset your lastfm account")
    async def lf_remove(self, ctx: commands.Context):      
        
        check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(ctx.author.id))        
        if not check: return await ctx.lastfm_message("You don't have a **last.fm** account connected.")
        
        await self.bot.db.execute("DELETE FROM lastfm_users WHERE discord_user_id = {}".format(ctx.author.id))
        await ctx.lastfm_message("I have removed your **last.fm** account from the bot.")
         
    @lastfm.command(name="variables", description="view lastfm custom embed variables")
    async def lf_variables(self, ctx: commands.Context):
        await ctx.invoke(self.bot.get_command("embed variables"))

    @lastfm.group(invoke_without_command=True, name="embed", description="create your own lastfm custom embed", aliases=["mode"])
    async def lf_embed(self, ctx: commands.Context):
     await ctx.create_pages()
    
    @lf_embed.command(name="steal", description="steal someone's custom lastfm embed", usage="[member]")
    async def lf_embed_steal(self, ctx: commands.Context, *, member: discord.Member): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", member.id)
     if not check: return await ctx.warning(f"**{member}** doesn't have a custom lastfm embed.")
     
     re = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not re: await self.bot.db.execute("INSERT INTO lfmode VALUES ($1,$2)", ctx.author.id, check['mode'])
     
     else: await self.bot.db.execute("UPDATE lfmode SET mode = $1 WHERE user_id = $2", check['mode'], ctx.author.id)
     return await ctx.lastfm_message(f"I have successfully copied **{member.name}'s** custom lastfm embed.")  

    @lf_embed.command(name="set", description="set a personal embed as the lastfm embed", usage="[message | embed code]")                 
    async def lf_embed_set(self, ctx: commands.Context, *, embed: str):      
     
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not check: await self.bot.db.execute("INSERT INTO lfmode VALUES ($1,$2)", ctx.author.id, embed)
     
     else: await self.bot.db.execute("UPDATE lfmode SET mode = $1 WHERE user_id = $2", embed, ctx.author.id) 
     await ctx.lastfm_message(f"I have set your **last.fm** mode to\n```{embed}```")              
    
    @lf_embed.command(name="view", description="check your lastfm custom embed")
    async def lf_embed_view(self, ctx: commands.Context): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not check: return await ctx.lastfm_message("You do not have a **last.fm** embed.") 
     
     embed = discord.Embed(color=self.bot.color, description=f"```{check['mode']}```")
     return await ctx.reply(embed=embed)    

    @lf_embed.command(name="none", description="clear your last.fm custom embed", aliases=["delete"])
    async def lf_embed_none(self, ctx: commands.Context): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not check: return await ctx.lastfm_message("You do not have any **last.fm** embed.") 
     
     await self.bot.db.execute("DELETE FROM lfmode WHERE user_id = $1", ctx.author.id)
     await ctx.lastfm_message("I have deleted your **last.fm** embed.")  

    @lastfm.command(name="customcommand", description="set a custom command for nowplaying", usage="[command]", aliases=["cc"])
    async def lf_customcommand(self, ctx: commands.Context, *, cmd: str):
        
        check = await self.bot.db.fetchrow("SELECT * FROM lastfmcc WHERE user_id = {}".format(ctx.author.id))
        if cmd == "none":   
            
            if check is None: return await ctx.lastfm_message(f"You don't have a **last.fm** custom command")
            
            await self.bot.db.execute(f"DELETE FROM lastfmcc WHERE user_id = {ctx.author.id}")
            return await ctx.lastfm_message("Your **Last.fm** custom command got succesfully deleted.")              
        
        if check is None: await self.bot.db.execute("INSERT INTO lastfmcc VALUES ($1,$2)", ctx.author.id, cmd)       
        
        else: await self.bot.db.execute("UPDATE lastfmcc SET command = $1 WHERE user_id = $2", cmd, ctx.author.id)
        return await ctx.lastfm_message(f"Your **Last.fm** custom command is {cmd}")         

    @lastfm.command(name="topartists", aliases = ['ta', "tar"], description="check a member's top 10 artists", usage="<member>")
    async def lf_topartists(self, ctx: commands.Context, member: discord.Member=None):
        
        if member is None: member = ctx.author
        try:
           
           check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(member.id))           
           if check:   
                
                user = check["username"]
                if user != "error": 
                 
                 jsonData = await self.lastfmhandler.get_top_artists(user, 10)
                 mes = '\n'.join(f"`{i+1}` **[{jsonData['topartists']['artist'][i]['name']}]({jsonData['topartists']['artist'][i]['url']})** {jsonData['topartists']['artist'][i]['playcount']} plays" for i in range(10))
                 
                 embed = discord.Embed(description = mes,color=self.bot.color)
                 embed.set_thumbnail(url = member.display_avatar)
                 embed.set_author(name = f"{user}'s overall top artists", icon_url = member.display_avatar)
                 return await ctx.reply(embed=embed)  
           else: return await ctx.lastfm_message("There is no **last.fm** account linked for this member.")
        
        except Exception as e:
            print(e)

    @lastfm.command(name="toptracks", aliases = ['tt'], description="check a member's top 10 tracks", usage="<member>")
    async def lf_toptracks(self, ctx: commands.Context, *, member: discord.Member=None):
        
        if member == None: member = ctx.author
        try:
            
            check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(member.id)) 
            
            if check:  
                
                user = check["username"]
                if user != "error":    
                  
                  jsonData = await self.lastfmhandler.get_top_tracks(user, 10)                               
                  
                  embed = discord.Embed(description = '\n'.join(f"`{i+1}` **[{jsonData['toptracks']['track'][i]['name']}]({jsonData['toptracks']['track'][i]['url']})** {jsonData['toptracks']['track'][i]['playcount']} plays" for i in range(10)),color = self.bot.color)
                  embed.set_thumbnail(url = ctx.message.author.avatar)
                  embed.set_author(name = f"{user}'s overall top tracks", icon_url = ctx.message.author.avatar)
                  return await ctx.reply(embed=embed)   
            else: return await ctx.lastfm_message("There is no **last.fm** account linked for this member.")
        
        except Exception as e:
            print(e)
            
    @lastfm.command(name="login", aliases=["register"])
    async def lf_login(self, ctx: commands.Context):
        """
        Log in with your lastfm account to the bot
        """
        
        check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(ctx.author.id))
        if check is not None: return await ctx.warning("You **already** have a **Last.fm** account linked.")
        
        CALLBACK_URL = f"https://kure.pl/lastfm/callback?discord_user_id={ctx.author.id}"
        auth_url = f"http://www.last.fm/api/auth/?api_key=166f77a5ce11d4860de9acf5d384e426&cb={CALLBACK_URL}"
    
        await asyncio.sleep(1)
        
        embed = Embed(
            color=0xFF0000,
            title="Connect your Last.fm account",
            description=(
                f"Authorize **Evict** to use your Last.fm account [here]({auth_url}). "
                "Your library's data will be indexed to power the whoknows commands and other commands.\n\n"
                "If you want to remove your account with **Evict**, run `lastfm logout` and visit your settings on "
                "[Last.fm](https://www.last.fm/settings/applications) to unauthorize our application.\n"
            ),
        ).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url).set_footer(
            text="Reconnecting your account will not fix sync issues.",
            icon_url="https://cdn.discordapp.com/emojis/1225172194628468921.png"
        )
        
        # Send the embed to the user via DM
        try:
            await ctx.author.send(embed=embed)
            await ctx.message.add_reaction("📩")  # Add reaction to the original message
        except discord.Forbidden:
            await ctx.send("I couldn't send you a DM. Please check your privacy settings.")
    
    @lastfm.command(name="topalbums", aliases = ['tal'], description="check a member's top 10 albums", usage="<member>")
    async def lf_topalbums(self,ctx: commands.Context, *, member: discord.Member=None):
        
        if member == None: member=ctx.author
        
        try:
           check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(member.id)) 
           
           if check:  
             user = check["username"]
             
             if user != "error":                     
                  jsonData = await self.lastfmhandler.get_top_albums(user, 10)
                  embed = discord.Embed(description = '\n'.join(f"`{i+1}` **[{jsonData['topalbums']['album'][i]['name']}]({jsonData['topalbums']['album'][i]['url']})** {jsonData['topalbums']['album'][i]['playcount']} plays" for i in range(10)),color = self.bot.color)
                  embed.set_thumbnail(url = ctx.message.author.avatar)
                  embed.set_author(name = f"{user}'s overall top albums", icon_url = ctx.message.author.avatar)
                  return await ctx.reply(embed=embed)   
           else: return await ctx.lastfm_message("There is no **last.fm** account linked for this member.")
        
        except Exception as e:
            print(e)

    @lastfm.command(name="user", aliases=["ui"], description="lastfm", help="check info about a lastfm user", usage="<username>")
    async def lf_user(self, ctx: commands.Context, user: typing.Union[discord.User, discord.Member] = commands.Author):
            
            await ctx.channel.typing()                    
            
            check = await self.bot.db.fetchrow('SELECT username FROM lastfm_users WHERE discord_user_id = $1', user.id)
            username = check["username"]
            
            if not check: return await ctx.warning(f"{'You don' if user == ctx.author else f'**{user}** doesn'}'t have a **last.fm** account linked.")
            
            info = await self.lastfmhandler.get_user_info(username)
            
            try:
             i = info["user"]
             name = i["name"]
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
             embed.add_field(name=f"Info", value=f"**name:** {realname}\n**registered:** <t:{int(i['registered']['#text'])}:R>\n**subscriber:** {subscriber}", inline=False)
             
             await ctx.reply(embed=embed)
            except TypeError: return await ctx.lastfm_message("This user doesn't have a **Last.fm** account connected.")

    @lastfm.command(name="whoknows", aliases = ['wk'], description="see who knows a certain artist in the server", usage="[artist]")
    async def lf_whoknows(self, ctx: commands.Context, * , artist: str=None):
     
     await ctx.typing()
     
     check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(ctx.author.id)) 
     if check is None: return await ctx.lastfm_message("You don't have a **Last.fm** account connected.")
     
     fmuser = check['username']
     if not artist:    
       resp = await self.lastfmhandler.get_tracks_recent(fmuser, 1)
       artist = resp["recenttracks"]["track"][0]["artist"]["#text"]

     tuples = []
     rows = []      
     ids = [str(m.id) for m in ctx.guild.members]
     results =  await self.bot.db.fetch(f"SELECT * FROM lastfm WHERE user_id IN ({','.join(ids)})")     
     
     if len(results) == 0: return await ctx.lastfm_message("No one has a **Last.fm** account linked.")
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
          rows.append(f"{'<a:developer:1208257462549880913>' if num == 1 else f'`{num}`'} [**{x[0]}**]({x[2]}) has **{x[1]}** plays")

     if len(rows) == 0: return await ctx.warning(f"No one has listened to {artist}.")              
     
     embeds = []
     embed = discord.Embed(color=self.bot.color, description="\n".join(rows), title=f"Top Listeners for {artist} in {ctx.guild.name}")
     embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
     embeds.append(embed)     
     
     return await ctx.reply(embed=embed) 

    @lastfm.command(name="globalwhoknows", aliases=["gwk"], description="see who knows a certain artist across all servers the bot is in", usage="[artist]")
    async def lf_globalwhoknows(self, ctx: commands.Context, * ,artist: str=None):
      
      await ctx.typing()
      
      check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(ctx.author.id)) 
      if check is None: return await ctx.lastfm_message("You don't have a **Last.fm** account connected.")
      
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
       
       if len(results) == 0: return await ctx.lastfm_message("No one has a **Last.fm** account linked.")
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
          rows.append(f"{'<:crown:1263741407969939467>' if num == 1 else f'`{num}`'} [**{x[0]}**]({x[2]}) has **{x[1]}** plays")

      if len(rows) == 0: return await ctx.warning(f"No one has listened to {artist}")               
      
      embeds = []
      embed = discord.Embed(color=self.bot.color, description="\n".join(rows), title=f"Top Listeners for {artist}")
      embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
      embeds.append(embed)
      
      if o == 0: return await ctx.reply(embed=embeds[0])
      re = await self.bot.db.fetchrow("SELECT * FROM lfcrowns WHERE user_id = $1 AND artist = $2", sorted(tuples, key=lambda n: n[1])[::-1][0][3], artist)
      if not re: 
        
        embeds.append(discord.Embed(color=self.bot.color, description=f"> `{(await self.bot.fetch_user(sorted(tuples, key=lambda n: n[1])[::-1][0][3]))}` claimed the crown for **{artist}**"))
        ar = await self.bot.db.fetchrow("SELECT * FROM lfcrowns WHERE artist = $1", artist)
        if ar: await self.bot.db.execute("UPDATE lfcrowns SET user_id = $1 WHERE artist = $2", sorted(tuples, key=lambda n: n[1])[::-1][0][3], artist) 
        else: await self.bot.db.execute("INSERT INTO lfcrowns VALUES ($1,$2)", sorted(tuples, key=lambda n: n[1])[::-1][0][3], artist)
      
      return await ctx.reply(embed=embed)  
    
    @lastfm.command(name="cover", description="get the cover image of your lastfm song", usage="<member>")
    async def lf_cover(self, ctx: commands.Context, *, member: discord.Member=commands.Author): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(member.id)) 
     if check is None: return await ctx.lastfm_message("You don't have a **last.fm** account connected.")  
     
     user = check[0]
     
     a = await self.lastfmhandler.get_tracks_recent(user, 1)
     file = discord.File(await self.bot.getbyte((a['recenttracks']['track'][0])['image'][3]['#text']), filename="cover.png")
     
     return await ctx.reply(f"**{a['recenttracks']['track'][0]['name']}**", file=file)

    @lastfm.command(name="reactions", description="add custom reactions to your lastfm embed", usage="[emojis | none]\nnone -> no reactions for np command\nno emoji -> default emojis will be used")
    async def lf_reactions(self, ctx: commands.Context, *emojis: str): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM lfreactions WHERE user_id = $1", ctx.author.id)
     
     if len(emojis) == 0: 
      if not check: return await ctx.lastfm_message("You don't have any **last.fm** custom reaction to remove.")
      
      await self.bot.db.execute("DELETE FROM lfreactions WHERE user_id = $1", ctx.author.id)
      return await ctx.lastfm_message("I have **deleted** your **last.fm** custom reactions.")
     
     sql_as_text = json.dumps(emojis)    
     if check: await self.bot.db.execute("UPDATE lfreactions SET reactions = $1 WHERE user_id = $2", sql_as_text, ctx.author.id)
     
     else: await self.bot.db.execute("INSERT INTO lfreactions VALUES ($1,$2)", ctx.author.id, sql_as_text)
     return await ctx.lastfm_message(f"Your **last.fm** reactions are {''.join([e for e in emojis])}")
    
    @lastfm.command(name="howto", description="tutorial for using lastfm", aliases=["tutorial"])
    async def lf_howto(self, ctx: commands.Context): 
      await ctx.lastfm_message("instructions can be viewed at <https://new-docs.evict.cc/configuration/lastfm>")

    @lastfm.command(name="crowns", description="get the crowns of a member", usage="<user>") 
    async def lf_crowns(self, ctx: commands.Context, *, member: discord.User=None): 
      
      if member is None: member = ctx.author 
      check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(member.id)) 

      
      if len(check) == 0: return await ctx.lastfm_message("I **couldn't** find any crown for **{}**".format(member))
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
      return await ctx.paginate(embeds) 
    
    @lastfm.command(name="chart", aliases=["c"], description="Generates an album image chart.", usage="[size] [period]\nsizes available: 3x3 (default), 2x2, 4x5, 20x4\nperiods available: alltime (default), yearly, monthly")
    async def lf_chart(self, ctx: commands.Context, user: discord.User=None, size: str = "3x3", period: Literal['overall', '7day', '1month', '3month', '6month', '12month'] = 'overall'):
      
      if user is None: user = ctx.author   
      username = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(user.id)) 

      if not username: 
        return await ctx.lastfm_send(f"{user.mention} does not have a lastfm account linked.")
      
      params = {'username': username, 'size': size, 'period': period}
      headers = {"api-key": self.bot.evict_api}
      
      x = await self.session.get_json("https://kure.pl/lastfm/chart", params=params, headers=headers)
      
      if detail := x.get('detail'):
        return await ctx.error(detail)
      
      image = await self.session.get_bytes(x['image_url'])
      return await ctx.reply(f"Last.FM chart for {user.mention} **{size}** album chart ({period})", file = File(BytesIO(image), filename="chart.png"))
    
    @commands.command(aliases=["gwk"], description="see who knows a certain artist across all servers the bot is in", usage="[artist]")
    async def globalwhoknows(self, ctx: commands.Context, *, artist: str=None): 
      await ctx.invoke(self.bot.get_command("lastfm globalwhoknows"), artist=artist)

    @commands.command(aliases = ['wk'], description="see who knows a certain artist in the server", usage="[artist]") 
    async def whoknows(self, ctx: commands.Context, *, artist: str=None):
      await ctx.invoke(self.bot.get_command("lastfm whoknows"), artist=artist)    
    
    @commands.command(aliases = ['tal'], description="check a member's top 10 albums", usage="<member>")
    async def topalbums(self, ctx: commands.Context, *, member: discord.Member=None): 
     await ctx.invoke(self.bot.get_command("lastfm topalbums"), member=member)

    @commands.command(aliases = ['tt'], description="check a member's top 10 tracks", usage="<member>")
    async def toptracks(self, ctx: commands.Context, *, member: discord.Member=None): 
      await ctx.invoke(self.bot.get_command("lastfm toptracks"), member=member) 
    
    @commands.command(aliases = ['ta', "tar"], description="check a member's top 10 artists", usage="<member>")
    async def topartists(self, ctx: commands.Context, *, member: discord.Member=None): 
     await ctx.invoke(self.bot.get_command("lastfm topartists"), member=member)   

    @commands.command(aliases=['np', 'fm'], help="lastfm", description="check what song is playing right now", usage="<user>")
    async def nowplaying(self, ctx: commands.Context, *, member: discord.User=None):
        
        if member is None: member = ctx.author
        
        await ctx.typing()             
        check = await self.bot.db.fetchrow("SELECT * FROM lastfm_users WHERE discord_user_id = {}".format(member.id))            
            
        if check:   
               starData = await self.bot.db.fetchrow("SELECT mode FROM lfmode WHERE user_id = $1", member.id)
               
               if starData is None:  
                user = check['username']
                
                if user != "error":      
                    
                    a = await self.lastfmhandler.get_tracks_recent(user, 1)
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    album = a['recenttracks']['track'][0]['album']['#text'] or "N/A"
                    
                    embed = discord.Embed(colour=self.bot.color)
                    embed.add_field(name="**Track:**", value = f"```Ruby\n{a['recenttracks']['track'][0]['name']}```", inline = True)
                    embed.add_field(name="**Artist:**", value = f"```Ruby\n{a['recenttracks']['track'][0]['artist']['#text']}```", inline = True)
                    embed.set_author(name = user, icon_url = member.display_avatar, url = f"https://last.fm/user/{user}")                               
                    embed.set_thumbnail(url=(a['recenttracks']['track'][0])['image'][3]['#text'])
                    embed.set_footer(text = f"Track Playcount: {await self.lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0])} ・Album: {album}", icon_url = (a['recenttracks']['track'][0])['image'][3]['#text'])
                    
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(label="Track Link", url=a['recenttracks']['track'][0]['url']))
                    view.add_item(discord.ui.Button(label="Artist Link", url=f"https://last.fm/music/{artist}"))
                    
                    message = await ctx.reply(embed=embed, view=view)
                    return await lf_add_reactions(ctx, message)
               
               else:
                user = check['username']
                
                try: 
                
                 x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, await self.lastfm_replacement(user, starData[0])))
                 message = await ctx.send(content=x[0], embed=x[1], view=x[2])
                
                except: message = await ctx.send(await self.lastfm_replacement(user, starData[0]))
                return await lf_add_reactions(ctx, message)
            
        elif check is None: return await ctx.lastfm_message(f"**{member}** doesn't have a **Last.fm account** linked. Use `{ctx.clean_prefix}lf login` to link your **account**.")  
                             
    
async def setup(bot):
    await bot.add_cog(lastfm(bot))
