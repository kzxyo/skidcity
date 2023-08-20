import discord, handlers.userhandler as userhandler, traceback, typing, json
from discord.ext import commands
from handlers.lastfmhandler import Handler
from tools.utils.utils import EmbedBuilder

async def lf_react(ctx: commands.Context, message: typing.Union[discord.Message, None]): 
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
 return await ctx.reply(embed=discord.Embed(color=0xff0000, description=f"<:lastfm:1123217269397393479> {ctx.author.mention}: {content}"))

class Lastfm(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.lastfmhandler = Handler("289e4e09a1126fd938c1e1deeed869c7")
    
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
    async def on_message(self, message: discord.Message): 
       if not message.guild: return 
       if message.author.bot: return 
       check = await self.bot.db.fetchrow("SELECT * FROM lastfmcc WHERE command = $1 AND user_id = $2", message.clean_content, message.author.id)
       if check:
          context = await self.bot.get_context(message)
          await context.invoke(self.bot.get_command("nowplaying"))  
    
    @commands.group(aliases=["lf"], invoke_without_command=True)
    async def lastfm(self, ctx):
      await ctx.create_pages()
    
    @lastfm.command(name="set", description="connect your lastfm account", help="lastfm", usage="[username]")
    async def lf_set(self, ctx: commands.Context, *, ref: str):
      if not await userhandler.lastfm_user_exists(ref): return await lastfm_message(ctx, "**Invalid** last.fm username")
      check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = $1", ctx.author.id)
      if not check: await self.bot.db.execute("INSERT INTO lastfm VALUES ($1,$2)", ctx.author.id, ref)
      else: await self.bot.db.execute("UPDATE lastfm SET username = $1 WHERE user_id = $2", ref, ctx.author.id)
      return await lastfm_message(ctx, f"**Lastf.fm** username set to **{ref}**")
    
    @lastfm.command(name="remove", description="remove your lastfm account", help="lastfm")
    async def lf_remove(self, ctx: commands.Context):
      check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = $1", ctx.author.id)
      if not check: return await lastfm_message(ctx, "You don't have a **last.fm** account set")
      else: await self.bot.db.execute("DELETE FROM lastfm WHERE user_id = $1", ctx.author.id)
      return await lastfm_message(ctx, "Your **last.fm** account has been removed")
    
    @lastfm.group(invoke_without_command=True, name="embed", description="create your own lastfm custom embed", aliases=["mode"], help="lastfm")
    async def lf_embed(self, ctx: commands.Context):
     await ctx.create_pages()

    @lf_embed.command(name="set", description="set a custom embed for the lastfm embed", help="lastfm", usage="[message]")                 
    async def lf_embed_set(self, ctx: commands.Context, *, embed: str):      
     invites = [".gg/", "discord.gg/", "https://discord.com/invite/"]
     if any(invite in ctx.message.content for invite in invites): 
      await lastfm_message(ctx, "You cannot have discord invite links in your **last.fm** embed")
      await ctx.message.delete()
      return
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not check: await self.bot.db.execute("INSERT INTO lfmode VALUES ($1,$2)", ctx.author.id, embed)
     else: await self.bot.db.execute("UPDATE lfmode SET mode = $1 WHERE user_id = $2", embed, ctx.author.id) 
     await lastfm_message(ctx, f"Your **last.fm** emhed has been configured as\n```{embed}```")              
    
    @lf_embed.command(name="view", description="check your lastfm embed code", help="lastfm")
    async def lf_embed_view(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not check: return await lastfm_message(ctx, "You don't have any **last.fm** embed") 
     embed = discord.Embed(color=self.bot.color, description=f"```{check['mode']}```")
     return await ctx.reply(embed=embed)    

    @lf_embed.command(name="none", description="delete your lastfm embed", help="lastfm")
    async def lf_embed_none(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM lfmode WHERE user_id = $1", ctx.author.id)
     if not check: return await lastfm_message(ctx, "You don't have any **last.fm** embed") 
     await self.bot.db.execute("DELETE FROM lfmode WHERE user_id = $1", ctx.author.id)
     await lastfm_message(ctx, "Your **last.fm** embed has been deleted")  
    
    @lastfm.command(name="customcommand", help="lastfm", description="set a custom command for nowplaying", usage="[command]", aliases=["cc"])
    async def lf_customcommand(self, ctx: commands.Context, *, cmd: str):
        check = await self.bot.db.fetchrow("SELECT * FROM lastfmcc WHERE user_id = {}".format(ctx.author.id))
        if cmd == "none":   
            if not check: return await lastfm_message(ctx, f"You do not have a **last.fm** custom command")
            await self.bot.db.execute(f"DELETE FROM lastfmcc WHERE user_id = {ctx.author.id}")
            return await lastfm_message(ctx, "Your **last.fm** custom command got deleted")              
        if not check: await self.bot.db.execute("INSERT INTO lastfmcc VALUES ($1,$2)", ctx.author.id, cmd)       
        else: await self.bot.db.execute("UPDATE lastfmcc SET command = $1 WHERE user_id = $2", cmd, ctx.author.id)
        return await lastfm_message(ctx, f"Your **last.fm** custom command has been configured as {cmd}")         
    
    @lastfm.command(name="reactions", help="lastfm", description="add custom reactions to your lastfm embed", usage="[emojis]")
    async def lf_reactions(self, ctx: commands.Context, *emojis: str): 
     check = await self.bot.db.fetchrow("SELECT * FROM lfreactions WHERE user_id = $1", ctx.author.id)
     if len(emojis) == 0: 
      if not check: return await lf_msg(ctx, "You don't have any **last.fm** custom reactions set")
      await self.bot.db.execute("DELETE FROM lfreactions WHERE user_id = $1", ctx.author.id)
      return await lastfm_message(ctx, "Your **last.fm** custom reactions has been deleted")
     sql_as_text = json.dumps(emojis)   
     if check: await self.bot.db.execute("UPDATE lfreactions SET reactions = $1 WHERE user_id = $2", sql_as_text, ctx.author.id)
     else: await self.bot.db.execute("INSERT INTO lfreactions VALUES ($1,$2)", ctx.author.id, sql_as_text)
     return await lastfm_message(ctx, f"Your **last.fm** reactions are set as {''.join([e for e in emojis])}")
    
    @lastfm.command(name="spotify", aliases=["sp"], description="check what song is playing on spotify", help="lastfm")
    async def lf_spotify(self, ctx: commands.Context, member: discord.Member=None):
      if not member: member = ctx.author
      a = next((a for a in member.activities if isinstance(a, discord.Spotify)), None)
      if not a: return await ctx.send_warning("You are not listening to **spotify**")
      await ctx.reply(f"https://open.spotify.com/track/{a.track_id}")
    
    @commands.command(aliases=['np', 'fm'], help="lastfm", description="check what song is playing right now", usage="<user>")
    async def nowplaying(self, ctx: commands.Context, *, member: discord.User=None):
        if member is None: member = ctx.author
        try:
            await ctx.typing()             
            check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))       
            if check:   
               chec = await self.bot.db.fetchrow("SELECT mode FROM lfmode WHERE user_id = $1", member.id)
               if not chec:  
                user = check['username']
                if user != "error":      
                    a = await self.lastfmhandler.get_tracks_recent(user, 1)
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    album = a['recenttracks']['track'][0]['album']['#text'] or "N/A"
                    embed = discord.Embed(colour=self.bot.color)
                    embed.add_field(name="**Track**", value = f"""[{"" + a['recenttracks']['track'][0]['name']}]({"" + a['recenttracks']['track'][0]['url']})""", inline = False)
                    embed.set_author(name = user, icon_url = member.display_avatar)                       
                    embed.set_thumbnail(url=(a['recenttracks']['track'][0])['image'][3]['#text'])
                    embed.set_footer(text = f"Playcount: {await self.lastfmhandler.get_track_playcount(user, a['recenttracks']['track'][0])} • Album: {album}", icon_url = (a['recenttracks']['track'][0])['image'][3]['#text'])
                    message = await ctx.reply(embed=embed)
                    return await lf_react(ctx, message)
               else:
                user = check['username']
                try: 
                 x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, await self.lastfm_replacement(user, chec[0])))
                 message = await ctx.send(content=x[0], embed=x[1], view=x[2])
                except: message = await ctx.send(await self.lastfm_replacement(user, chec[0]))
                return await lf_react(ctx, message)
            elif not check: return await lastfm_message(ctx, f"**{member}** doesn't have a **Last.fm account** set. Use `{ctx.clean_prefix}lf set <username>` to set your **last.fm** account.")             
        except Exception: 
           print(traceback.format_exc())
           return await lastfm_message(ctx, f"unable to get **{member.name}'s** recent track".capitalize())  
    
async def setup(bot):
    await bot.add_cog(Lastfm(bot))