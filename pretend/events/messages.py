import discord, datetime, asyncio
from discord.ext import commands 
from tools.utils import PaginatorView

def duration(n: int) -> str: 
    uptime = int(n/1000)
    seconds_to_minute   = 60
    seconds_to_hour     = 60 * seconds_to_minute
    seconds_to_day      = 24 * seconds_to_hour

    days    =   uptime // seconds_to_day
    uptime    %=  seconds_to_day

    hours   =   uptime // seconds_to_hour
    uptime    %=  seconds_to_hour

    minutes =   uptime // seconds_to_minute
    uptime    %=  seconds_to_minute

    seconds = uptime
    if days > 0: return ("{} days, {} hours, {} minutes, {} seconds".format(days, hours, minutes, seconds))
    if hours > 0 and days == 0: return ("{} hours, {} minutes, {} seconds".format(hours, minutes, seconds))
    if minutes > 0 and hours == 0 and days == 0: return ("{} minutes, {} seconds".format(minutes, seconds))
    if minutes < 0 and hours == 0 and days == 0: return ("{} seconds".format(seconds))

class Messages(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
      self.bot = bot
      self.snipes = {}
      self.edit_snipes = {}

    @commands.Cog.listener('on_message')
    async def boost_listener(self, message: discord.Message): 
     if "MessageType.premium_guild" in str(message.type):
      if message.guild.id == 952161067033849919: 
       member = message.author
       check = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = $1", member.id)
       if check: return 
       ts = int(datetime.datetime.now().timestamp())
       await self.bot.db.execute("INSERT INTO donor VALUES ($1,$2)", member.id, ts)  
       return await message.channel.send(f"{member.mention}, enjoy your perks! <a:catclap:1081008257776226354>")     

    @commands.Cog.listener("on_message")
    async def seen_listener(self, message: discord.Message): 
      if not message.guild: return 
      if message.author.bot: return
      check = await self.bot.db.fetchrow("SELECT * FROM seen WHERE guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id))
      if check is None: return await self.bot.db.execute("INSERT INTO seen VALUES ($1,$2,$3)", message.guild.id, message.author.id, int(datetime.datetime.now().timestamp()))  
      ts = int(datetime.datetime.now().timestamp())
      await self.bot.db.execute("UPDATE seen SET time = $1 WHERE guild_id = $2 AND user_id = $3", ts, message.guild.id, message.author.id)
 
    @commands.Cog.listener("on_message")
    async def reposter(self, message: discord.Message): 
     if not message.guild: return 
     if message.author.bot: return 
     args = message.content.split(" ")
     if (args[0] == "pretend"):
        url = args[1] 
        check = await self.bot.db.execute("SELECT * FROM nodata WHERE user_id = $1 AND state = $2", message.author.id, "true")
        if not check: return
        if "tiktok" in url:
         async with message.channel.typing():  
          if x.get("data").get("images"): 
           x = await self.bot.session.json("https://tikwm.com/api/", params={"url": url}) 
           try:
              embeds = []
              for img in x['data']['images']:
               embed = discord.Embed(color=self.bot.color, description=f"requested by {message.author} | Page {x['data']['images'].index(img)+1}/{len(x['data']['images'])}").set_author(name=f"@{x['data']['author']['unique_id']}", icon_url=x["data"]["author"]["avatar"], url=url)
               embed.set_footer(text=f"❤️ {self.bot.ext.human_format(x['data']['digg_count'])}  💬 {self.bot.ext.human_format(x['data']['comment_count'])} 👀 {self.bot.ext.human_format(x['data']['play_count'])}") 
               embed.set_image(url=img)    
               embeds.append(embed)
              v = PaginatorView(await self.bot.get_context(message), embeds)
              try: await message.delete()
              except: pass
              return await message.channel.send(embed=embeds[0], view=v)  
           except:
               pass
          else:
            video = x["data"]["play"]
            file = discord.File(fp=await self.bot.getbyte(video), filename="pretendtiktok.mp4")
            embed = discord.Embed(color=self.bot.color, description=f"[{x['data']['title']}]({url})").set_author(name=f"@{x['data']['author']['unique_id']}", icon_url=x["data"]["author"]["avatar"])
            x = x["data"]
            embed.set_footer(text=f"❤️ {self.bot.ext.human_format(x['digg_count'])}  💬 {self.bot.ext.human_format(x['comment_count'])}  🔗 {self.bot.ext.human_format(x['share_count'])}  👀 {self.bot.ext.human_format(x['play_count'])} | {message.author}", icon_url="https://cdn.discordapp.com/emojis/987668422332657724.png")
            await message.channel.send(embed=embed, file=file)
            try: await message.delete()
            except: pass
  #        except: pass
        elif "twitter" in url:
         await message.channel.typing()  
         x = await self.bot.session.json("https://api.rival.rocks/twitter/post", headers=self.bot.rival_api, params={'url': url})
         if "Could not get tweet content" in x: return 
         if x["nsfw"] is True and message.channel.is_nsfw() is False: 
          ctx = self.bot.get_context(message)
          return await ctx.send_warning("You can't repost **nsfw** twitters here") 
         if x["media"]["1"]["video"]: file=discord.File(fp=await self.bot.getbyte(x["media"]["1"]["video"]), filename="pretendTwitter.mp4")   
         else: file=None 
         ts = datetime.datetime.fromtimestamp(int(x["timestamp"])) 
         embed = discord.Embed(color=self.bot.color, description=f"[**{x['text']}**]({x['url']})", timestamp=ts)
         embed.set_author(name=x["author"]['screen_name'], icon_url=x['author']['avatar'])
         if x["media"]["1"]["image"]: embed.set_image(url=x["media"]["1"]["image"])
         embed.set_footer(icon_url=x["footer_url"], text="❤️ {}  🔁 {} ∙ {}".format(x["like_count"], x["retweet_count"], message.author))
         if file: await message.channel.send(embed=embed, file=file)
         else: await message.channel.send(embed=embed)
         try: await message.delete()
         except: pass  

    @commands.Cog.listener('on_message')
    async def bump_event(self, message: discord.Message): 
     if message.type == discord.MessageType.chat_input_command:
       if message.interaction.name == "bump" and message.author.id == 302050872383242240:   
        if "Bump done!" in message.embeds[0].description or "Bump done!" in message.content:
          check = await self.bot.db.fetchrow("SELECT * FROM bumps WHERE guild_id = {}".format(message.guild.id))  
          if check is not None: 
           await message.channel.send(f"{message.interaction.user.mention} thanks for bumping the server. You will be reminded in 2 hours!") 
           await asyncio.sleep(7200)
           embed = discord.Embed(color=self.bot.color, description="Bump the server using the `/bump` command")
           await message.channel.send(f"{message.interaction.user.mention} time to bump !!", embed=embed)  

    @commands.Cog.listener("on_message")
    async def afk_listener(self, message: discord.Message):
     if not message.guild: return 
     if message.author.bot: return
     if message.mentions: 
      if len(message.mentions) == 1: 
        mem = message.mentions[0]
        check = await self.bot.db.fetchrow("SELECT * from afk where guild_id = $1 AND user_id = $2", message.guild.id, mem.id) 
        if check:
         em = discord.Embed(color=self.bot.color, description=f"💤 **{mem}** is AFK since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(check['time'])))}** - {check['reason']}")
         await message.reply(embed=em)
      else: 
       embeds = [] 
       for mem in message.mentions:
         check = await self.bot.db.fetchrow("SELECT * from afk where guild_id = $1 AND user_id = $2", message.guild.id, mem.id) 
         if check:
          em = discord.Embed(color=self.bot.color, description=f"💤 **{mem}** is AFK since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(check['time'])))}** - {check['reason']}")
          embeds.append(em)
         if len(embeds) == 10: 
           await message.reply(embeds=embeds)
           embeds = []
       if len(embeds) > 0: await message.reply(embeds=embeds)
       embeds = []

     che = await self.bot.db.fetchrow("SELECT * from afk where guild_id = $1 AND user_id = $2", message.guild.id, message.author.id) 
     if che:
      embed = discord.Embed(color=self.bot.color, description=f"<a:wave:1020721034934104074> Welcome back **{message.author}**! You were AFK since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(che['time'])))}**")
      await message.reply(embed=embed)
      await self.bot.db.execute("DELETE FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)    

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
     if not message.guild: return 
     if message.author.bot: return
     invites = ["discord.gg/", ".gg/", "discord.com/invite/"]
     if any(invite in message.content for invite in invites):
       check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = $1", message.guild.id)
       if check: return

     attachment = message.attachments[0].url if message.attachments else "none"
     author = str(message.author)
     content = message.content
     avatar = message.author.display_avatar.url 
     await self.bot.db.execute("INSERT INTO snipe VALUES ($1,$2,$3,$4,$5,$6,$7)", message.guild.id, message.channel.id, author, content, attachment, avatar, datetime.datetime.now())
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message): 
     if not before.guild: return 
     if before.author.bot: return 
     await self.bot.db.execute("INSERT INTO editsnipe VALUES ($1,$2,$3,$4,$5,$6)", before.guild.id, before.channel.id, before.author.name, before.author.display_avatar.url, before.content, after.content)    

async def setup(bot: commands.AutoShardedBot) -> None: 
  await bot.add_cog(Messages(bot))     
