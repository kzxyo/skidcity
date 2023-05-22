from discord.ext.commands import Cog, command, Context, AutoShardedBot as Bot, hybrid_command, hybrid_group, group, check
import datetime, discord, humanize, os, arrow, uwuipy, humanfriendly, asyncio 
from discord import Embed, File, TextChannel, Member, User, Role 
from deep_translator import GoogleTranslator
from handlers.lastfmhandler import Handler
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from discord.ui import Button, View
from discord.ext import tasks
from tools.checks import Perms
from aiogtts import aiogTTS
from ttapi import TikTokApi
from random import choice
from typing import Union
from io import BytesIO

tiktok = TikTokApi(debug=True)
DISCORD_API_LINK = "https://discord.com/api/invite/"
downloadCount = 0
clientid = "f567fb50e0b94b4e8224d2960a00e3ce"
clientsecret = "f4294b7b837940f996b3a4dcf5230628"

def is_there_a_reminder(): 
  async def predicate(ctx: Context):
    check = await ctx.bot.db.fetchrow("SELECT * FROM reminder WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
    if not check: await ctx.send_warning("You don't have a reminder set in this server")
    return check is not None
  return check(predicate) 

@tasks.loop(seconds=5)
async def reminder_task(bot: Bot): 
  results = await bot.db.fetch("SELECT * FROM reminder")
  for result in results: 
   if datetime.datetime.now().timestamp() > result['date'].timestamp(): 
    channel = bot.get_channel(int(result['channel_id']))
    if channel:
      await channel.send(f"🕰️ <@{result['user_id']}> {result['task']}")
      await bot.db.execute("DELETE FROM reminder WHERE guild_id = $1 AND user_id = $2 AND channel_id = $3", channel.guild.id, result['user_id'], channel.id)   

@tasks.loop(seconds=10)
async def bday_task(bot: Bot): 
  results = await bot.db.fetch("SELECT * FROM birthday") 
  for result in results:
   if arrow.get(result['bday']).day == arrow.utcnow().day and arrow.get(result['bday']).month == arrow.utcnow().month:
    if result['said'] == "false":  
     member = await bot.fetch_user(result['user_id'])
     if member: 
      try: 
        await member.send("🎂 Happy birthday!!")
        await bot.db.execute("UPDATE birthday SET said = $1 WHERE user_id = $2", "true", result['user_id'])
      except: continue   
   else: 
     if result['said'] == "true": await bot.db.execute("UPDATE birthday SET said = $1 WHERE user_id = $2", "false", result['user_id'])

class Timezone(object):
  def __init__(self, bot: Bot): 
   """
   Get timezones of people
   """
   self.bot = bot
   self.clock = "🕑"
   self.months = {
     '01': 'January',
     '02': 'February',
     '03': 'March',
     '04': 'April',
     '05': 'May',
     '06': 'June',
     '07': 'July',
     '08': 'August',
     '09': 'September',
     '10': 'October',
     '11': 'November',
     '12': 'December'
   }
  
  async def timezone_send(self, ctx: Context, message: str):
   return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.clock} {ctx.author.mention}: {message}"))
  
  async def timezone_request(self, member: discord.Member):
   coord = await self.get_user_lat_long(member)
   if coord is None: return None
   utc = arrow.utcnow()
   local = utc.to(coord)
   timestring = local.format('YYYY-MM-DD HH:mm').split(" ")
   date = timestring[0][5:].split("-")
   try:
    hours, minutes = [int(x) for x in timestring[1].split(":")[:2]]
   except IndexError:
    return "N/A"

   if hours >= 12:
    suffix = "PM"
    hours -= 12
   else:
    suffix = "AM"
   if hours == 0:
     hours = 12
   return f"{self.months.get(date[0])} {self.bot.ordinal(date[1])} {hours}:{minutes:02d} {suffix}" 
  
  async def get_user_lat_long(self, member: discord.Member): 
   check = await self.bot.db.fetchrow("SELECT * FROM timezone WHERE user_id = $1", member.id) 
   if check is None: return None 
   return check['zone']
  
  async def tz_set_cmd(self, ctx: Context, location: str):
   await ctx.typing()
   geolocator = Nominatim(user_agent="Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36")
   lad = location
   location = geolocator.geocode(lad) 
   if location is None: return await ctx.send_warning( "Couldn't find a **timezone** for that location")
   check = await self.bot.db.fetchrow("SELECT * FROM timezone WHERE user_id = $1", ctx.author.id) 
   obj = TimezoneFinder()
   result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
   if not check: await self.bot.db.execute("INSERT INTO timezone VALUES ($1,$2)", ctx.author.id, result)
   else: 
     await self.bot.db.execute("DELETE FROM timezone WHERE user_id = $1", ctx.author.id)
     await self.bot.db.execute("INSERT INTO timezone VALUES ($1,$2)", ctx.author.id, result)
   embed = Embed(color=self.bot.color, description=f"Saved your timezone as **{result}**\n{self.clock} Current time: **{await self.timezone_request(ctx.author)}**")
   await ctx.reply(embed=embed)

  async def get_user_timezone(self, ctx: Context, member: discord.Member): 
   if await self.timezone_request(member) is None: 
    if member.id == ctx.author.id: return await ctx.send_warning( f"You don't have a **timezone** set. Use `{ctx.clean_prefix}tz set` command instead")   
    else: return await ctx.send_warning( f"**{member.name}** doesn't have their **timezone** set")
   if member.id == ctx.author.id: return await self.timezone_send(ctx, f"Your current time: **{await self.timezone_request(member)}**")
   else: return await self.timezone_send(ctx, f"**{member.name}'s** current time: **{await self.timezone_request(member)}**") 

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def human_format(number):
    if number > 999: return humanize.naturalsize(number, False, True) 
    return number 
  
class Utility(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot 
        self.tz = Timezone(self.bot)
        self.lastfmhandler = Handler("43693facbb24d1ac893a7d33846b15cc")
        self.cake = "🎂"
        self.weather_key = "64581e6f1d7d49ae834142709230804"        

    async def bday_send(self, ctx: Context, message: str) -> discord.Message: 
      return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.cake} {ctx.author.mention}: {message}"))
    
    async def do_again(self, url: str):
     re = await self.make_request(url)
     if re['status'] == "converting": return await self.do_again(url)
     elif re['status'] == "failed": return None
     else: return tuple([re['url'], re['filename']]) 

    async def make_request(self, url: str, action: str="get", params: dict=None): 
       r = await self.bot.session.get(url, params=params)
       if action == "get": return await r.json()
       if action == "read": return await r.read() 

    @Cog.listener()
    async def on_ready(self): 
      await self.bot.wait_until_ready()
      bday_task.start(self.bot)
      reminder_task.start(self.bot)

    @command(help="utility", description="clear your usernames", aliases=["clearusernames", "clearusers"])
    async def clearnames(self, ctx):
        embed = discord.Embed(color=self.bot.color, description=f"{ctx.author.mention} are you sure you want to clear your usernames. This decision is **irreversible**")
        button1 = discord.ui.Button(emoji=self.bot.yes)
        button2 = discord.ui.Button(emoji=self.bot.no)
        
        async def button1_callback(interaction: discord.Interaction): 
          if interaction.user.id != ctx.author.id: return await self.bot.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True) 
          await self.bot.db.execute("DELETE FROM oldusernames WHERE user_id = $1", ctx.author.id) 
          return await interaction.response.edit_message(view=None, embed=discord.Embed(color=self.bot.color, description=f"> {self.bot.yes} {interaction.user.mention}: Name history cleared"))
        
        async def button2_callback(interaction: discord.Interaction): 
         if interaction.user.id != ctx.author.id: return await self.bot.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True) 
         return await interaction.response.edit_message(view=None, embed=discord.Embed(color=self.bot.color, description=f"Aborting action..."))  
        
        button1.callback = button1_callback
        button2.callback = button2_callback
        view = discord.ui.View()
        view.add_item(button1)
        view.add_item(button2)
        return await ctx.reply(embed=embed, view=view)

    @hybrid_command(name='tiktok', description='show tiktok user statistics', help="utility")
    async def tiktok(self,ctx,username:str):
        try:
          r = await self.bot.session.get("https://api.rival.rocks/tiktok/userinfo", params={'username': username}, headers=self.bot.rival_api)
          data = await r.json()
          display="" if data['display'] == None else data['display']
          badges=[]
          if data['verified'] == True: badges.append('☑️')
          if data['private'] == True: badges.append('🔒')
          badge_str="".join([b for b in badges])
          embed = discord.Embed(color=self.bot.color, title=f"{display} (@{data['username']}) {badge_str}", url=data['url'], description=f"{data['bio']}")
          embed.set_thumbnail(url=data["avatar"])
          embed.add_field(name="Following",value=human_format(int(data['following'])),inline=True)
          embed.add_field(name='Followers',value=human_format(int(data['followers'])),inline=True)
          embed.add_field(name='Likes',value=human_format(int(data['likes'])),inline=True)
          embed.set_footer(text="Powered by RivalAPI",icon_url="https://i.pinimg.com/originals/93/d3/a6/93d3a68f57eff7480f44f8df1b6e2841.jpg")
          embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
          return await ctx.reply(embed=embed)
        except: 
          await ctx.send_warning( "TikTok account **couldn't** be found")
    
    @hybrid_command(description="show someone's valorant stats", help="utility", usage="[username]\nexample: ;valorant aubs#1522")
    async def valorant(self, ctx: Context, *, username: str): 
     user = username.split("#")
     r = await self.bot.session.get(f"https://api.henrikdev.xyz/valorant/v1/account/{user[0]}/{user[1]}")
     data = await r.json()
     if data["status"] != 200: return await ctx.send_warning( "Couldn't get valorant data of this player")
     region = data["data"]["region"]
     res = await self.bot.session.get(f"https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{user[0]}/{user[1]}")
     stats = await res.json()
     await ctx.reply(embed=discord.Embed(color=self.bot.color, title=f"{username}'s stats", url=f"https://tracker.gg/valorant/profile/riot/{user[0]}%23{user[1]}/overview", timestamp=datetime.datetime.fromtimestamp(data["data"]["last_update_raw"])).set_thumbnail(url=stats["data"]["current_data"]["images"]["large"]).add_field(name="tier", value=stats["data"]["current_data"]["currenttierpatched"]).add_field(name="highest", value=stats["data"]["highest_rank"]["patched_tier"]).set_footer(text=f"level {data['data']['account_level']}")) 
    
    """
    @hybrid_command(description="look up for an instagram account", help="utility", usage="[username]", aliases=["ig"])
    async def instagram(self, ctx: Context, username: str): 
        await ctx.typing()
        url = "https://api.rival.rocks/instagram/user/info"
        r = await self.bot.session.post(url, headers=self.bot.rival_api, data={"username": username, "sessionid": self.bot.session_id})
        #r = await self.bot.session.get(f"https://igdl.in/apis.php?url=https://instagram.com/{username}") 
        if r.status == 404: return await ctx.send_error(f"**{username}** doesn't exist")     
        #data = (await r.json())["graphql"]["user"]
        badges = []
        data = await r.json()
        if data["is_private"]: badges.append("🔒")
        if data["is_verified"]: badges.append("☑️")
        embed = Embed(color=0x30618A, title=f"{data['full_name']} (@{data['username']})" if data['full_name'] != "" else f'@{data["username"]}' + " " + ' '.join(badges), url=f"https://instagram.com/{username}", description=data['biography']) 
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=data["profile_pic_url_hd"])
        embed.add_field(name="posts", value=human_format(data["media_count"]))
        embed.add_field(name="followers", value=human_format(data["follower_count"]))
        embed.add_field(name="following", value=human_format(data["following_count"]))
        view = View()
        view.add_item(Button(emoji="<:instagram:1051097570753122344>", url=f"https://instagram.com/{username}"))
        await ctx.reply(embed=embed, view=view)
    """    
    @hybrid_command(description="clear all snipe data", help="utility", brief="manage messages", aliases=['cs'])
    @Perms.get_perms("manage_messages")
    async def clearsnipes(self, ctx: Context): 
      lis = ["snipe", "reactionsnipe", "editsnipe"]
      for l in lis: await self.bot.db.execute(f"DELETE FROM {l} WHERE guild_id = $1", ctx.guild.id)
      return await ctx.send_success("Cleared all snipes from this server") 

    @command(aliases = ['names', 'usernames'], help="utility", usage="<user>", description="check an user's past usernames")
    async def pastusernames(self, ctx, member: User = None):
       if not member: member = ctx.author
       data = await self.bot.db.fetch("SELECT * FROM oldusernames WHERE user_id = $1", member.id)
       i=0
       k=1
       l=0
       number = []
       messages = []
       num = 0
       auto = ""
       if data:
         for table in data[::-1]:
          username = table['username']
          discrim = table['discriminator']
          num += 1
          auto += f"\n`{num}` {username}#{discrim}: <t:{int(table['time'])}:R> "
          k+=1
          l+=1
          if l == 10:
            messages.append(auto)
            number.append(Embed(color=self.bot.color, description = auto).set_author(name = f"{member}'s past usernames", icon_url = member.display_avatar))
            i+=1
            auto = ""
            l=0
         messages.append(auto)
         embed = Embed(description = auto, color = self.bot.color)
         embed.set_author(name = f"{member}'s past usernames", icon_url = member.display_avatar)
         number.append(embed)
         return await ctx.paginator( number)     
       else: return await ctx.send_warning( f"no logged usernames for **{member}**".capitalize())

    @command(help="utility", usage="[message]", description="uwify a message", aliases=["uwu"])
    async def uwuify(self, ctx: Context, *, text: str): 
     uwu = uwuipy.uwuipy()
     uwu_message = uwu.uwuify(text)
     await ctx.send(uwu_message)  
            
    @hybrid_command(help="utility", description="search for images on google", aliases=["img", "google"], usage="[query]")
    async def image(self, ctx: Context, *, query: str):
     embeds = []
     await ctx.channel.typing()
     data = await self.bot.session.post_json("https://api.rival.rocks/google/image", headers=self.bot.rival_api, params={"query": query})     
     lis = data["results"]
     for l in lis: embeds.append(Embed(color=self.bot.color, title=f"<:google:1044254038268592159> Search results for {query}", description=l['title'], url=l["source"]).set_image(url=l['url']).set_footer(text=f"{lis.index(l)+1}/{len(lis)}"))
     await ctx.paginator( embeds)   
    
    @hybrid_command(aliases=['ss'], description="get a screenshot of an website", usage="[link]", help="utility")
    async def screenshot(self, ctx: Context, link: str):
      if not link.startswith("https://") or not link.startswith("http://"): link = "https://" + link
      await ctx.typing() 
      url = f"https://processor.screenshotson.click/screenshot?key=819d482a7a9f7efc&width=3840&height=2160&fullPage=false&quality=70&loadEvent=domcontentloaded&fileType=png"
      r = await self.bot.session.read(url, params={"url": link})
      by = BytesIO(r)
      view = View()
      view.add_item(Button(label=link.replace('http://', "").replace("https://", ""), url=link)) 
      await ctx.reply(file=discord.File(by, filename="screenshot.png"), view=view) 

    @hybrid_command(help="utility", description="give someone permission to post pictures in a channel", usage="[member] <channel>", brief="manage roles")
    @Perms.get_perms("manage_roles")
    async def picperms(self, ctx: Context, member: Member, *, channel: TextChannel=None):
      if channel is None: channel = ctx.channel
      if channel.permissions_for(member).attach_files and channel.permissions_for(member).embed_links:
       await channel.set_permissions(member, attach_files=False, embed_links=False)
       return await ctx.send_success(f"Removed pic perms from {member.mention} in {channel.mention}")       
      await channel.set_permissions(member, attach_files=True,embed_links=True)
      return await ctx.send_success(f"Added pic perms to {member.mention} in {channel.mention}")     

    @hybrid_command(help="utility", description="get a random youtube video link based on query", usage="[query]", aliases=["yt"])
    async def youtube(self, ctx: Context, *, query: str): 
     r = await self.bot.session.json("https://www.googleapis.com/youtube/v3/search", params={"key": self.bot.google_api, "part": "snippet", "q": query})
     vids = ["https://youtube.com/watch/" + lol["id"]["videoId"] for lol in r["items"]]
     return await ctx.reply(choice(vids))

    @hybrid_command(aliases=['yttomp3'], help="utility", description="download yt video to mp3", usage="[video link]")
    async def youtubetomp3(self, ctx: Context, url: str): 
     async with ctx.typing():
      rq = await self.make_request("https://srv4.onlymp3.to/listFormats", params={"url": url})
      link = rq['formats']['audio'][2]['url']
      r = await self.make_request(link)
      newurl = r['url']
      re = await self.make_request(newurl)
      if re['status'] == "converting": rele = await self.do_again(newurl)  
      elif re['status'] == "failed": return await ctx.send_warning("Failed to download the video as an mp3")
      else: rele = tuple([re['url'], re['filename']])   
      if rele is None: return await ctx.send_warning("Failed to download the video as an mp3")
      req = await self.make_request(rele[0], action="read")
      file = discord.File(BytesIO(req), filename=rele[1].replace("onlymp3.to - ", ""))
      return await ctx.reply(file=file)

    @hybrid_command(help="utility", description="look up for a twitter account", usage="[username]")
    async def twitter(self, ctx: Context, *, username: str): 
         data = await self.bot.session.json("https://api.rival.rocks/twitter/user", params={"username": username}, headers=self.bot.rival_api)
         if data["error"] is not None: return await ctx.send_warning( f"[**@{username}**](https://twitter.com/{username}) doesn't exist")
         embed = Embed(color=data["color"], title="{} (@{})".format(data["nickname"], data["username"]), url=data["url"], timestamp=datetime.datetime.fromtimestamp(float(data["created_at"])))
         embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
         embed.set_thumbnail(url=data["avatar_url"] if not None else "")
         embed.set_image(url=data["banner_url"] if not None else "")
         embed.set_footer(text="join date", icon_url="https://images-ext-2.discordapp.net/external/3QbCv4XvYmYSy2kSHI_WL2vlhaM9Pa64uPl-6t9rcs0/https/cdn.discordapp.com/emojis/1044284633333911693.png")
         embed.add_field(name="following", value=data["following"])
         embed.add_field(name="tweets", value=data["tweets"])
         embed.add_field(name="followers", value=data["followers"])
         button = Button(emoji="<:twitter:1044284633333911693>", label="", url=data["url"])
         view = View()
         view.add_item(button)
         await ctx.reply(embed=embed, view=view)

    @hybrid_command(description="see when a user was last seen", help="utility", usage="[member]")
    async def seen(self, ctx, *, member: Member):
        check = await self.bot.db.fetchrow("SELECT * FROM seen WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
        if check is None: return await ctx.send_warning( f"I didn't see **{member}**")
        ts = check['time']
        await ctx.reply(embed=Embed(color=self.bot.color, description="{}: **{}** was last seen <t:{}:R>".format(ctx.author.mention, member, ts)))   

    @hybrid_command(help="utility", description="let everyone know you are away", usage="<reason>")
    async def afk(self, ctx: Context, *, reason="AFK"):      
       ts = int(datetime.datetime.now().timestamp())   
       result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id)) 
       if result is None:
        await self.bot.db.execute("INSERT INTO afk VALUES ($1,$2,$3,$4)", ctx.guild.id, ctx.author.id, reason, ts)
        await ctx.send_success(f"You're now AFK with the status: **{reason}**")

    @hybrid_command(aliases=["es"], description="get the most recent edited messages from the channel", help="utility", usage="<number>")
    async def editsnipe(self, ctx: Context, number: int=1): 
     results = await self.bot.db.fetch("SELECT * FROM editsnipe WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, ctx.channel.id)
     if len(results) == 0: return await ctx.send_warning( "There are no edited messages in this channel")
     if number > len(results): return await ctx.send_warning( f"The maximum amount of snipes is **{len(results)}**")
     sniped = results[::-1][number-1]
     embed = Embed(color=self.bot.color)
     embed.set_author(name=sniped['author_name'], icon_url=sniped["author_avatar"])
     embed.add_field(name="before", value=sniped['before_content'])
     embed.add_field(name="after", value=sniped['after_content'])
     embed.set_footer(text=f"{number}/{len(results)}")
     await ctx.reply(embed=embed)

    @hybrid_command(aliases=["rs"], description="get the most recent messages that got one of their reactions removed", help="utility", usage="number")
    async def reactionsnipe(self, ctx: Context, number: int=1):
     results = await self.bot.db.fetch("SELECT * FROM reactionsnipe WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, ctx.channel.id)
     if len(results) == 0: return await ctx.send_warning( "There are no reaction removed in this channel")
     if number > len(results): return await ctx.send_warning( f"The maximum amount of snipes is **{len(results)}**") 
     sniped = results[::-1][number-1]
     message = await ctx.channel.fetch_message(sniped['message_id'])
     embed = Embed(color=self.bot.color, description=f"[{sniped['emoji_name']}]({sniped['emoji_url']})\n[message link]({message.jump_url if message else 'https://none.none'})")
     embed.set_author(name=sniped['author_name'], icon_url=sniped['author_avatar'])
     embed.set_image(url=sniped['emoji_url'])
     embed.set_footer(text=f"{number}/{len(results)}")
     await ctx.reply(embed=embed)

    @hybrid_command(description="get a random tiktok video", help="utility", aliases=["foryou"])
    async def fyp(self, ctx: Context):
      await ctx.typing()
      fyp_videos = await tiktok.feed.for_you(count=1)
      videos = []
      for vid in fyp_videos:
       videos.append(vid)
      
      video = choice(videos)
      no_watermark_download = video["download_urls"]["no_watermark"]
      video_binary = await tiktok.video.get_video_binary(no_watermark_download)
      bytes_io = BytesIO(video_binary) 
      embed = Embed(color=self.bot.color)
      embed.description = f'[{video["description"]}]({video["video_url"]})'
      embed.set_author(name="@"+video["author"]["username"], icon_url=video["author"]["avatar_url"])
      embed.set_footer(text=f"❤️ {human_format(video['stats']['likes'])} 💬 {human_format(video['stats']['comment_count'])} 🔗 {human_format(video['stats']['shares'])} ({human_format(video['stats']['views'])} views)")
      await ctx.reply(embed=embed, file=File(fp=bytes_io, filename="pretendTikTok.mp4"))

    @hybrid_command(aliases=["s"], description="check the latest deleted message from a channel", usage="<number>", help="utility")
    async def snipe(self, ctx: Context, *, number: int=1):
        check = await self.bot.db.fetch("SELECT * FROM snipe WHERE guild_id = {} AND channel_id = {}".format(ctx.guild.id, ctx.channel.id))
        if len(check) == 0: return await ctx.send_warning( "There are no deleted messages in this channel") 
        if number > len(check): return await ctx.send_warning( f"current snipe limit is **{len(check)}**".capitalize()) 
        sniped = check[::-1][number-1]
        em = Embed(color=self.bot.color, description=sniped['content'], timestamp=sniped['time'])
        em.set_author(name=sniped['author'], icon_url=sniped['avatar']) 
        em.set_footer(text="{}/{}".format(number, len(check)))
        if sniped['attachment'] != "none":
         if ".mp4" in sniped['attachment'] or ".mov" in sniped['attachment']:
          url = sniped['attachment']
          r = await self.bot.session.read(url)
          bytes_io = BytesIO(r)
          file = File(fp=bytes_io, filename="video.mp4")
          return await ctx.reply(embed=em, file=file)
         else:
           try: em.set_image(url=sniped['attachment'])
           except: pass 
        return await ctx.reply(embed=em)
    
    @hybrid_command(aliases=["mc"], description="check how many members does your server have", help="utility")
    async def membercount(self, ctx: Context):
      b=len(set(b for b in ctx.guild.members if b.bot))
      h=len(set(b for b in ctx.guild.members if not b.bot))
      embed = Embed(color=self.bot.color)
      embed.set_author(name=f"{ctx.guild.name}'s member count", icon_url=ctx.guild.icon)
      embed.add_field(name=f"members (+{len([m for m in ctx.guild.members if (datetime.datetime.now() - m.joined_at.replace(tzinfo=None)).total_seconds() < 3600*24 and not m.bot])})", value=h)
      embed.add_field(name="total", value=ctx.guild.member_count) 
      embed.add_field(name="bots", value=b)
      await ctx.reply(embed=embed)

    @hybrid_command(description="see user's avatar", help="utility", usage="<user>", aliases=["av"])
    async def avatar(self, ctx: Context, *, member: Union[Member, User]=None):
      if member is None: 
        member = ctx.author 

      if isinstance(member, Member): 
        button1 = Button(label="default avatar", url=member.avatar.url if member.avatar is not None else "https://none.none")
        button2 = Button(label="server avatar", url=member.display_avatar.url)
        embed = Embed(color=self.bot.color, title=f"{member.name}'s avatar", url=member.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        view = View()
        view.add_item(button1)
        view.add_item(button2)    
        await ctx.reply(embed=embed, view=view)
      elif isinstance(member, User):
        button3 = Button(label="default avatar", url=member.display_avatar.url)
        embed = Embed(color=self.bot.color, title=f"{member.name}'s avatar", url=member.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        view = View()
        view.add_item(button3)  
        await ctx.reply(embed=embed, view=view) 
    
    @command(description="get role information", usage="[role]", help="utility", aliases=["ri"])
    async def roleinfo(self, ctx: Context, *, role: Union[Role, str]): 
      if isinstance(role, str): 
        role = ctx.find_role(role)
        if role is None: return await ctx.send_warning( "This is not a valid role")

      perms = ", ".join([str(p[0]) for p in role.permissions if bool(p[1]) is True]) if role.permissions else "none"
      embed = Embed(color=role.color, title=f"@{role.name}", description="`{}`".format(role.id), timestamp=role.created_at)
      embed.set_thumbnail(url=role.display_icon if not isinstance(role.display_icon, str) else None)
      embed.add_field(name="members", value=str(len(role.members)))
      embed.add_field(name="mentionable", value=str(role.mentionable).lower())
      embed.add_field(name="hoist", value=str(role.hoist).lower())
      embed.add_field(name="permissions", value=f"```{perms}```", inline=False)
      await ctx.reply(embed=embed)
       
    @command(description="see all members in a role", help="utility", usage="[role]")
    async def inrole(self, ctx: Context, *, role: Union[Role, str]):
            if isinstance(role, str): 
              role = ctx.find_role(role)
              if role is None: return await ctx.send_warning( "This isn't a valid role")

            if len(role.members) == 0: return await ctx.send_error("Nobody (even u) has this role") 
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for member in role.members:
              mes = f"{mes}`{k}` {member} - ({member.id})\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"members in {role.name} [{len(role.members)}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = Embed(color=self.bot.color, title=f"members in {role.name} [{len(role.members)}]", description=messages[i])
            number.append(embed)
            await ctx.paginator( number)
    
    @command(description="see all members joined within 24 hours", help="utility")
    async def joins(self, ctx: Context): 
      members = [m for m in ctx.guild.members if (datetime.datetime.now() - m.joined_at.replace(tzinfo=None)).total_seconds() < 3600*24]      
      if len(members) == 0: return await ctx.send_error("No members joined in the last **24** hours")
      members = sorted(members, key=lambda m: m.joined_at)
      i=0
      k=1
      l=0
      mes = ""
      number = []
      messages = []
      for member in members[::-1]: 
        mes = f"{mes}`{k}` {member} - {discord.utils.format_dt(member.joined_at, style='R')}\n"
        k+=1
        l+=1
        if l == 10:
         messages.append(mes)
         number.append(Embed(color=self.bot.color, title=f"joined today [{len(members)}]", description=messages[i]))
         i+=1
         mes = ""
         l=0
    
      messages.append(mes)
      embed = Embed(color=self.bot.color, title=f"joined today [{len(members)}]", description=messages[i])
      number.append(embed)
      await ctx.paginator( number) 

    @command(description="see all muted mebmers", help="utility")
    async def muted(self, ctx: Context): 
            members = [m for m in ctx.guild.members if m.is_timed_out()]
            if len(members) == 0: return await ctx.send_error("There are no muted members")
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for member in members: 
              mes = f"{mes}`{k}` {member} - <t:{int(member.timed_out_until.timestamp())}:R> \n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"{ctx.guild.name} muted members [{len(members)}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = Embed(color=self.bot.color, title=f"{ctx.guild.name} muted members [{len(members)}]", description=messages[i])
            number.append(embed)
            await ctx.paginator( number)     
    
    @command(description="see all banned members", help="utility")
    async def bans(self, ctx: Context): 
     banned = [m async for m in ctx.guild.bans()]
     if len(banned) == 0: return await ctx.send_warning( "There are no banned people in this server")  
     i=0
     k=1
     l=0
     mes = ""
     number = []
     messages = []
     for m in banned: 
       mes = f"{mes}`{k}` **{m.user}** - `{m.reason or 'No reason provided'}` \n"
       k+=1
       l+=1
       if l == 10:
        messages.append(mes)
        number.append(Embed(color=self.bot.color, title=f"banned ({len(banned)})", description=messages[i]))
        i+=1
        mes = ""
        l=0
    
     messages.append(mes)
     embed = Embed(color=self.bot.color, title=f"banned ({len(banned)})", description=messages[i])
     number.append(embed)
     await ctx.paginator( number) 

    @group(invoke_without_command=True, description="see all server boosters", help="utility")
    async def boosters(self, ctx: Context):
            if not ctx.guild.premium_subscriber_role or len(ctx.guild.premium_subscriber_role.members) == 0: return await ctx.send_warning( "this server doesn't have any boosters".capitalize())
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for member in ctx.guild.premium_subscriber_role.members: 
              mes = f"{mes}`{k}` {member} - <t:{int(member.premium_since.timestamp())}:R> \n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"boosters [{len(ctx.guild.premium_subscriber_role.members)}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = Embed(color=self.bot.color, title=f"boosters [{len(ctx.guild.premium_subscriber_role.members)}]", description=messages[i])
            number.append(embed)
            await ctx.paginator( number) 
    
    @boosters.command(name="lost", description="display lost boosters", help="utility")
    async def boosters_lost(self, ctx: Context): 
      results = await self.bot.db.fetch("SELECT * FROM boosterslost WHERE guild_id = $1", ctx.guild.id)
      if len(results) == 0: return await ctx.send_warning( "There are no lost boosters")
      i=0
      k=1
      l=0
      mes = ""
      number = []
      messages = []
      for result in results[::-1]: 
          mes = f"{mes}`{k}` <@!{int(result['user_id'])}> - <t:{result['time']}:R> \n"
          k+=1
          l+=1
          if l == 10:
           messages.append(mes)
           number.append(Embed(color=self.bot.color, title=f"lost boosters [{len(results)}]", description=messages[i]))
           i+=1
           mes = ""
           l=0
    
      messages.append(mes)
      embed = Embed(color=self.bot.color, title=f"lost boosters [{len(results)}]", description=messages[i])
      number.append(embed)
      await ctx.paginator( number) 

    @command(description="see all server roles", help="utility")
    async def roles(self, ctx: Context):
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for role in ctx.guild.roles: 
              mes = f"{mes}`{k}` {role.mention} - <t:{int(role.created_at.timestamp())}:R> ({len(role.members)} members)\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"roles [{len(ctx.guild.roles)}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = Embed(color=self.bot.color, title=f"roles [{len(ctx.guild.roles)}]", description=messages[i])
            number.append(embed)
            await ctx.paginator( number)

    @command(description="see all server's bots", help="utility")
    async def bots(self, ctx: Context):
            i=0
            k=1
            l=0
            b=len(set(b for b in ctx.guild.members if b.bot))
            mes = ""
            number = []
            messages = []
            for member in ctx.guild.members:
             if member.bot:   
              mes = f"{mes}`{k}` {member} - ({member.id})\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"bots [{b}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = Embed(color=self.bot.color, title=f"{ctx.guild.name} bots [{b}]", description=messages[i])
            number.append(embed)
            await ctx.paginator( number)

    @hybrid_command(description="show information abt an invite", help="utility", usage="[invite code]", aliases=["ii"])
    async def inviteinfo(self, ctx: Context, code: str): 
        invite_code = code
        data = await self.bot.session.json(DISCORD_API_LINK + invite_code, proxy=self.bot.proxy_url, ssl=False)
        name = data["guild"]["name"]
        id = data['guild']['id']
        description = data["guild"]["description"]
        boosts = data["guild"]["premium_subscription_count"]
        features = ', '.join(f for f in data["guild"]["features"])
        avatar = f"https://cdn.discordapp.com/icons/{data['guild']['id']}/{data['guild']['icon']}.{'gif' if 'a_' in data['guild']['icon'] else 'png'}?size=1024"
        banner = f"https://cdn.discordapp.com/banners/{data['guild']['id']}/{data['guild']['banner']}.{'gif' if 'a_' in data['guild']['banner'] else 'png'}?size=1024"
        splash = f"https://cdn.discordapp.com/splashes/{data['guild']['id']}/{data['guild']['splash']}.png?size=1024"
        embed = Embed(color=self.bot.color, title=f"invite info for {code}", url="https://discord.gg/{}".format(code), description=f"**{description}**")
        embed.set_author(icon_url=avatar, name=f"{name} ({id})")
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="nsfw", value="no" if data["guild"]["nsfw"] is False else "true")
        embed.add_field(name="server", value=name)
        embed.add_field(name="boosts", value="<:boosts:978686077365800970> {}".format(boosts))
        embed.add_field(name="features", value="```{}```".format(features), inline=False)
        view = View()
        view.add_item(Button(label="icon", url=avatar))
        view.add_item(Button(label="banner", url=banner))
        view.add_item(Button(label="splash", url=splash))
        await ctx.reply(embed=embed, view=view)
    
    @hybrid_command(help="utility", description="check the weather from a location", usage="[country]")
    async def weather(self, ctx: Context, *, location: str): 
     url = "http://api.weatherapi.com/v1/current.json"
     params = {
       "key": self.weather_key,
       "q": location 
     }  
     data = await self.bot.session.json(url, params=params)
     place = data["location"]["name"]
     country = data["location"]["country"]
     temp_c = data["current"]["temp_c"]
     temp_f = data["current"]["temp_f"]
     wind_mph = data["current"]["wind_mph"]
     wind_kph = data["current"]["wind_kph"]
     humidity = data["current"]["humidity"]
     condition_text = data["current"]["condition"]["text"]
     condition_image = "http:" + data["current"]["condition"]["icon"]
     time = datetime.datetime.fromtimestamp(int(data["current"]["last_updated_epoch"]))
     embed = discord.Embed(color=self.bot.color, title=f"{condition_text} in {place}, {country}", timestamp=time)
     embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
     embed.set_thumbnail(url=condition_image)
     embed.add_field(name="Temperature", value=f"{temp_c} °C / {temp_f} °F")
     embed.add_field(name="Humidity", value=f"{humidity}%")
     embed.add_field(name="Wind", value=f"{wind_mph} mph / {wind_kph} kph")
     return await ctx.reply(embed=embed)

    @hybrid_command(description="show user information", help="utility", usage="<user>", aliases=["whois", "ui", "user"])
    async def userinfo(self, ctx: Context, *, member: Union[Member, User]=None):
     await ctx.typing()
     if member is None: member = ctx.author           
     user = await self.bot.fetch_user(member.id)
     discrim = ["0001", "1337", "0002", "9999", "0666", "0888", "6969", "0069"]
     badges = []
     if user.id in self.bot.owner_ids: 
       badges.append("<a:skull_spin:1085546035046260867>")
     if user.public_flags.active_developer: 
      badges.append("<:activedev:1054757186749870140>")
     if user.public_flags.early_supporter:
      badges.append("<:early:1030411369671032832>")
     if user.public_flags.verified_bot_developer:
       badges.append("<:developer:1030503840870572082>")
     if user.public_flags.staff: 
      badges.append("<:tl_staff:1030411376172216350>")
     if user.public_flags.bug_hunter:
      badges.append("<:bughunter:1030411377589891093>") 
     if user.public_flags.bug_hunter_level_2:
      badges.append("<:goldbughunter:1030411378680410192>")   
     if user.public_flags.partner:
      badges.append("<:partner:1023508151984734269>")
     if user.public_flags.discord_certified_moderator:
      badges.append("<:moderator:1023508378934321262>")
     if user.public_flags.hypesquad_bravery:
      badges.append("<:badgehypebravery:1030411371935961091>")
     if user.public_flags.hypesquad_balance:
      badges.append("<:badgehypebalance:1030411373043265576>")
     if user.public_flags.hypesquad_brilliance:
      badges.append("<:badgehypebrilliance:1030411370837049354>")  
     if user.discriminator in discrim or user.display_avatar.is_animated() or user.banner is not None:
      badges.append("<:nitro:1030411373953429554>")

     for guild in self.bot.guilds: 
      mem = guild.get_member(user.id)
      if mem is not None:
       if mem.premium_since is not None:
         badges.append("<:boosts:978686077365800970>")
         break
     
     async def tz_find(mem: discord.Member): 
      if await self.tz.timezone_request(mem): return f'{self.tz.clock} Current time: {await self.tz.timezone_request(mem)}'
      return ''
     
     async def lf(mem: Union[Member, User]): 
        check = await self.bot.db.fetchrow("SELECT username FROM lastfm WHERE user_id = {}".format(mem.id))
        if check is not None: 
          u = str(check['username']) 
          if u != "error": 
            a = await self.lastfmhandler.get_tracks_recent(u, 1)
            return f"<:lastfm:977608782874021888> Listening to [{a['recenttracks']['track'][0]['name']}]({a['recenttracks']['track'][0]['url']}) by **{a['recenttracks']['track'][0]['artist']['#text']}** on lastfm.."
      
        return ""

     def vc(mem: Member):
        if mem.voice: 
          channelname = mem.voice.channel.name 
          deaf = "<:deafened:1047125267098914816>" if mem.voice.self_deaf or mem.voice.deaf else "<:undeafened:1035864650169987153>"
          mute = "<:muted:1035858405212041316>" if mem.voice.self_mute or mem.voice.mute else "<:unmuted:1035864651130490970>"
          stream = "<:stream:1047125265404407859>" if mem.voice.self_stream else ""
          video = "<:video:1047125268038430760>" if mem.voice.self_video else ""
          channelmembers = f"with {len(mem.voice.channel.members)-1} other member{'s' if len(mem.voice.channel.members) > 2 else ''}" if len(mem.voice.channel.members) > 1 else ""
          return f"{deaf} {mute} {stream} {video} **in voice channel** {channelname} {channelmembers}"
        return ""  

     e = Embed(color=self.bot.color, title=str(user) + " " + "".join(map(str, badges)))        
     if isinstance(member, Member): 
      e.description = f"{vc(member)}\n{await tz_find(member)}\n{await lf(member)}"
      members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
      ordinal = self.bot.ordinal(int(members.index(member)+1))    
      e.set_author(name=f"{member} • {ordinal} member", icon_url=member.display_avatar.url)
      e.add_field(name="dates", value=f"**joined:** {self.bot.convert_datetime(member.joined_at)}\n**created:** {self.bot.convert_datetime(member.created_at)}\n{f'**boosted:** {self.bot.convert_datetime(member.premium_since)}' if self.bot.convert_datetime(member.premium_since) else ''}", inline=False)     
      roles = member.roles[1:][::-1]
      if len(roles) > 0: e.add_field(name=f"roles ({len(roles)})", value=' '.join([r.mention for r in roles]) if len(roles) < 5 else ' '.join([r.mention for r in roles[:4]]) + f" ... and {len(roles)-4} more")
     elif isinstance(member, User): e.add_field(name="dates", value=f"**created:** {self.bot.convert_datetime(member.created_at)}", inline=False)     
     e.set_thumbnail(url=member.display_avatar.url)
     try: e.set_footer(text='ID: ' + str(member.id) + f" | {len(member.mutual_guilds)} mutual server(s)")
     except: e.set_footer(text='ID: ' + str(member.id)) 
     await ctx.reply(embed=e)
    
    @command(help="utility", description="get the server's banner", aliases=["guildbanner"])
    async def serverbanner(self, ctx: Context): 
      return await ctx.invoke(self.bot.get_command("server banner"))
    
    @command(help="utility", description="get a server's icon", aliases=["guildicon", "guildavatar", "serveravatar"])
    async def servericon(self, ctx: Context): 
      return await ctx.invoke(self.bot.get_command("server icon"))

    @command(help="utility", description="get the server's invite background image", aliases=["guildsplash"])
    async def serversplash(self, ctx: Context): 
      return await ctx.invoke(self.bot.get_command("server splash"))  

    @hybrid_command(aliases=["si"], description="show information about the server", help="utility")
    async def serverinfo(self, ctx: Context):
        guild = ctx.guild        
        icon= f"[icon]({guild.icon.url})" if guild.icon is not None else "N/A"
        splash=f"[splash]({guild.splash.url})" if guild.splash is not None else "N/A"
        banner=f"[banner]({guild.banner.url})" if guild.banner is not None else "N/A"   
        desc=guild.description if guild.description is not None else ""
        embed = Embed(color=self.bot.color, title=f"{guild.name} ・ shard {guild.shard_id}/{self.bot.shard_count-1}", description=f"Created on {self.bot.convert_datetime(guild.created_at.replace(tzinfo=None))}\n{desc}")   
        embed.set_thumbnail(url=guild.icon)
        embed.add_field(name="owner", value=f"{guild.owner.mention}\n{guild.owner}")
        embed.add_field(name=f"channels ({len(guild.channels)})", value=f"**text:** {len(guild.text_channels)}\n**voice:** {len(guild.voice_channels)}\n**categories** {len(guild.categories)}")
        embed.add_field(name="members", value=f"**users:** {len(set(i for i in guild.members if not i.bot))} ({((len(set(i for i in guild.members if not i.bot)))/guild.member_count) * 100:.2f}%)\n**bots:** {len(set(i for i in guild.members if i.bot))} ({(len(set(i for i in guild.members if i.bot))/guild.member_count) * 100:.2f}%)\n**total:** {guild.member_count}")
        embed.add_field(name="icons", value=f"{icon}\n{splash}\n{banner}")
        embed.add_field(name="info", value=f"**verification:** {guild.verification_level}\n**boosts:** {guild.premium_subscription_count} (level {guild.premium_tier})\n**large:** {'yes' if guild.large else 'no'}")
        embed.add_field(name="counts", value=f"**roles:** {len(guild.roles)}/250\n**emojis:** {len(guild.emojis)}/{guild.emoji_limit*2}\n**stickers:** {len(guild.stickers)}/{guild.sticker_limit}")
        if len([g for g in guild.features]) > 0: embed.add_field(name="features", value=f"```{', '.join([g for g in guild.features])}```", inline=False)
        embed.set_footer(text=f"ID: {guild.id}")
        await ctx.reply(embed=embed)

    @hybrid_group(aliases=["guild"], invoke_without_command=True)
    async def server(self, ctx: Context):
        return await ctx.invoke(self.bot.get_command("serverinfo"))
    
    @server.command(description="show information about the server", help="utility")
    async def info(self, ctx: Context): 
      return await ctx.invoke(self.bot.get_command("serverinfo"))

    @server.command(description="get a server's banner", help="utility")
    async def banner(self, ctx: Context): 
        guild = ctx.guild
        if not guild.banner: return await ctx.send_warning( "this server has no banner".capitalize())
        embed = Embed(color=self.bot.color, title=f"{guild.name}'s banner", url=guild.banner.url)   
        embed.set_image(url=guild.banner.url)
        await ctx.reply(embed=embed)

    @server.command(description="get a server's icon", help="utility")
    async def icon(self, ctx: Context, *, id: int=None): 
        guild = ctx.guild
        if not guild.icon: return await ctx.send_warning( "this server has no icon".capitalize())
        embed = Embed(color=self.bot.color, title=f"{guild.name}'s icon", url=guild.icon.url)   
        embed.set_image(url=guild.icon.url)
        await ctx.reply(embed=embed)   

    @server.command(description="get a server's invite background image", help="utility")
    async def splash(self, ctx: Context): 
        guild = ctx.guild
        if not guild.splash: return await ctx.send_warning( "this server has no splash".capitalize())
        embed = Embed(color=self.bot.color, title=f"{guild.name}'s invite background", url=guild.splash.url)   
        embed.set_image(url=guild.splash.url)
        await ctx.reply(embed=embed)
 
    @hybrid_command(description="shows the number of invites an user has", usage="<user>", help="utility")
    async def invites(self, ctx: Context, *, member: Member=None):
      if member is None: member = ctx.author 
      invites = await ctx.guild.invites()
      await ctx.reply(f"{member} has **{sum(invite.uses for invite in invites if invite.inviter.id == member.id)}** invites")
    
    @command(description="see the list of donators", help="utility", aliases=["donors"])
    async def donators(self, ctx):
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          results = await self.bot.db.fetch("SELECT * FROM donor")
          if len(results) == 0: return await ctx.send_error("There are no donators")
          for result in results:
            mes = f"{mes}`{k}` <@!{result['user_id']}> ({result['user_id']}) - (<t:{int(result['time'])}:R>)\n"
            k+=1
            l+=1
            if l == 10:
              messages.append(mes)
              number.append(Embed(color=self.bot.color, title=f"donators ({len(results)})", description=messages[i]))
              i+=1
              mes = ""
              l=0
    
          messages.append(mes)
          number.append(Embed(color=self.bot.color, title=f"donators ({len(results)})", description=messages[i]))
          await ctx.paginator( number)
    
    @command(aliases=["tts", "speech"], description="convert your message to mp3", help="utility", usage="[message]")     
    async def texttospeech(self, ctx: Context, *, txt: str): 
      i=BytesIO()
      aiogtts = aiogTTS()
      await aiogtts.save(txt, 'tts.mp3', lang='en')
      await aiogtts.write_to_fp(txt, i, slow=False, lang='en') 
      await ctx.reply(file=discord.File(fp='tts.mp3', filename="tts.mp3"))
      return os.remove('tts.mp3')
     
    @hybrid_command(description="gets the invite link with administrator permission of a bot", help="utility", usage="[bot id]")
    async def getbotinvite(self, ctx, id: User):   
      if not id.bot: return await ctx.send_error("This isn't a bot")
      embed = Embed(color=self.bot.color, description=f"**[invite the bot](https://discord.com/api/oauth2/authorize?client_id={id.id}&permissions=8&scope=bot%20applications.commands)**")
      await ctx.reply(embed=embed)
   
    @command(description="gets the banner from a server based by invite code\n(pretend doesn't need to be in the server)", help="utility", usage="[invite code]")
    async def sbanner(self, ctx, *, link: str):
     invite_code = link
     data = await self.bot.session.json(DISCORD_API_LINK + invite_code, proxy=self.bot.proxy_url, ssl=False)
     format = ".gif" if "a_" in data["guild"]["banner"] else ".png"
     embed = Embed(color=self.bot.color, title=data["guild"]["name"] + "'s banner")
     embed.set_image(url="https://cdn.discordapp.com/banners/" + data["guild"]["id"] + "/" + data["guild"]["banner"] + f"{format}?size=1024")
     await ctx.reply(embed=embed)

    @command(description="gets the splash from a server based by invite code\n(pretend doesn't need to be in the server)", help="utility", usage="[invite code]")
    async def splash(self, ctx, *, link: str):
      invite_code = link
      data = await self.bot.session.json(DISCORD_API_LINK + invite_code, proxy=self.bot.proxy_url, ssl=False)
      embed = Embed(color=self.bot.color, title=data["guild"]["name"] + "'s splash")
      embed.set_image(url="https://cdn.discordapp.com/splashes/" + data["guild"]["id"] + "/" + data["guild"]["splash"] + ".png?size=1024")
      await ctx.reply(embed=embed)
    
    @command(description="gets the icon from a server based by invite code\n(pretend doesn't need to be in the server)", help="utility", usage="[invite code]")
    async def sicon(self, ctx, *, link: str):
      invite_code = link
      data = await self.bot.session.json(DISCORD_API_LINK + invite_code, proxy=self.bot.proxy_url, ssl=False)
      format = ".gif" if "a_" in data["guild"]["icon"] else ".png"
      embed = Embed(color=self.bot.color, title=data["guild"]["name"] + "'s icon")
      embed.set_image(url="https://cdn.discordapp.com/icons/" + data["guild"]["id"] + "/" + data["guild"]["icon"] + f"{format}?size=1024")
      await ctx.reply(embed=embed)
    
    @hybrid_command(description="gets information about a github user", aliases=["gh"], help="utility", usage="[user]")
    async def github(self, ctx, *, user: str):
      try:
        res = await self.bot.session.json(f'https://api.github.com/users/{user}') 
        name=res['login']
        avatar_url=res['avatar_url']
        html_url=res['html_url']
        email=res['email']
        public_repos=res['public_repos']
        followers=res['followers']
        following=res['following']
        twitter = res['twitter_username']
        location=res['location']
        embed = Embed(color=self.bot.color, title = f"@{name}", url=html_url)
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Followers", value=followers)
        embed.add_field(name="Following", value=following)
        embed.add_field(name="Repos", value=public_repos)
        if email: embed.add_field(name="Email", value=email)
        if location: embed.add_field(name="Location", value=location)
        if twitter: embed.add_field(name="Twitter", value=twitter)
        embed.set_thumbnail(url=avatar_url)
        await ctx.reply(embed=embed)
      except: return await ctx.send_warning( f"Could not find [@{user}](https://github.com/{user})")

    @command(aliases=["tr"], description="translate a message", help="utility", usage="[language] [message]")
    async def translate(self, ctx: Context, lang: str, *, mes: str): 
      translated = GoogleTranslator(source="auto", target=lang).translate(mes)
      embed = Embed(color=self.bot.color, description="```{}```".format(translated), title="translated to {}".format(lang))
      await ctx.reply(embed=embed)

    @hybrid_command(aliases=["firstmsg"], description="get the first message", help="utility", usage="<channel>")
    async def firstmessage(self, ctx: Context, *, channel: TextChannel=None):
     channel = channel or ctx.channel 
     messages = [mes async for mes in channel.history(oldest_first=True, limit=1)]
     message = messages[0]
     embed = Embed(color=self.bot.color, title="first message in #{}".format(channel.name), description=message.content, timestamp=message.created_at)
     embed.set_author(name=message.author, icon_url=message.author.display_avatar)
     view = View()
     view.add_item(Button(label="jump to message", url=message.jump_url))
     await ctx.reply(embed=embed, view=view) 
    
    @group(invoke_without_command=True, help="utility", description="check member's birthday", aliases=['bday'])
    async def birthday(self, ctx: Context, *, member: Member=None): 
     if member is None: member = ctx.author 
     lol = "'s"
     date = await self.bot.db.fetchrow("SELECT bday FROM birthday WHERE user_id = $1", member.id)      
     if not date: return await ctx.send_warning( f"**{'Your' if member == ctx.author else str(member) + lol}** birthday is not set")
     date = date['bday']
     if "ago" in arrow.get(date).humanize(granularity='day'): date=date.replace(year=date.year+1)
     else: date = date
     if arrow.get(date).humanize(granularity='day') == "in 0 days":	date = "tomorrow" 
     elif arrow.get(date).day == arrow.utcnow().day and arrow.get(date).month == arrow.utcnow().month: date = "today"  
     else: date=arrow.get(date+datetime.timedelta(days=1)).humanize(granularity='day') 
     await self.bday_send(ctx, f"{'Your' if member == ctx.author else '**' + member.name + lol + '**'} birthday is **{date}**")

    @birthday.command(name="set", help="utility", description="set your birthday", usage="[month] [day]\nexample: birthday set January 19")
    async def bday_set(self, ctx: Context, month: str, day: str): 
     try:
      if len(month)==1: mn="M"
      elif len(month)==2: mn="MM"
      elif len(month)==3: mn="MMM"
      else: mn="MMMM"
      if "th" in day: day=day.replace("th","")
      if "st" in day: day=day.replace("st","")
      if len(day)==1: dday="D"
      else: dday="DD"
      ts=f"{month} {day} {datetime.date.today().year}"
      if "ago" in arrow.get(ts, f'{mn} {dday} YYYY').humanize(granularity="day"): year=datetime.date.today().year+1
      else: year=datetime.date.today().year
      string=f"{month} {day} {year}"
      date=arrow.get(string, f'{mn} {dday} YYYY')
      check = await self.bot.db.fetchrow("SELECT * FROM birthday WHERE user_id = $1", ctx.author.id)
      if not check: await self.bot.db.execute("INSERT INTO birthday VALUES ($1,$2,$3)", ctx.author.id, date.datetime, "false")
      else: await self.bot.db.execute("UPDATE birthday SET bday = $1 WHERE user_id = $2", date.datetime, ctx.author.id)
      await self.bday_send(ctx, f"Configured your birthday as **{month} {day}**")
     except: return await ctx.send_error(f"usage: `{ctx.clean_prefix}birthday set [month] [day]`") 
    
    @birthday.command(name="unset", help="utility", description="unset your birthday")
    async def bday_unset(self, ctx: Context):
      check = await self.bot.db.fetchrow("SELECT bday FROM birthday WHERE user_id = $1", ctx.author.id)
      if not check: return await ctx.send_warning( "Your birthday is not set")
      await self.bot.db.execute("DELETE FROM birthday WHERE user_id = $1", ctx.author.id)
      await ctx.send_warning( "Unset your birthday")

    @group(invoke_without_command=True, help="utility", description="check member's timezones", aliases=['tz'])
    async def timezone(self, ctx: Context, *, member: discord.Member=None): 
     if member is None: member = ctx.author  
     return await self.tz.get_user_timezone(ctx, member)

    @timezone.command(name="set", help="utility", description="set the timezone", usage="[location]\nexample: ;tz set russia")
    async def tz_set(self, ctx: Context, *, location: str):
     return await self.tz.tz_set_cmd(ctx, location)
    
    @timezone.command(name="list", help="utility", description="return a list of server member's timezones")
    async def tz_list(self, ctx: Context): 
     ids = [str(m.id) for m in ctx.guild.members] 
     results = await self.bot.db.fetch(f"SELECT * FROM timezone WHERE user_id IN ({','.join(ids)})") 
     if len(results) == 0: await self.tz.timezone_send(ctx, "Nobody (even you) has their timezone set") 
     await ctx.typing()
     i=0
     k=1
     l=0
     mes = ""
     number = []
     messages = []
     for result in results: 
        mes = f"{mes}`{k}` <@{int(result['user_id'])}> - {await self.tz.timezone_request(ctx.guild.get_member(int(result['user_id'])))}\n"
        k+=1
        l+=1
        if l == 10:
         messages.append(mes)
         number.append(Embed(color=self.bot.color, title=f"timezone list", description=messages[i]))
         i+=1
         mes = ""
         l=0
    
     messages.append(mes)
     embed = Embed(color=self.bot.color, title=f"timezone list", description=messages[i])
     number.append(embed)
     await ctx.paginator(number) 

    @timezone.command(name="unset", help="utility", description="unset the timezone")
    async def tz_unset(self, ctx: Context):
      check = await self.bot.db.fetchrow("SELECT * FROM timezone WHERE user_id = $1", ctx.author.id)
      if not check: return await ctx.send_warning( "You don't have a **timezone** set")
      await self.bot.db.execute('DELETE * FROM timezone WHERE user_id = $1', ctx.author.id)
      return await ctx.send_success("Removed the timezone")
    
    @group(invoke_without_command=True)
    async def reminder(self, ctx: Context): 
      return await ctx.create_pages()
    
    @reminder.command(name="add", help="utility", description="make the bot remind you about a task", usage="[time] [reminder]")
    async def reminder_add(self, ctx: Context, time: str, *, task: str): 
      return await ctx.invoke(self.bot.get_command('remind'), time=time, task=task)
    
    @reminder.command(name="stop", aliases=['cancel'], description="cancel a reminder from this server", help="utility")
    @is_there_a_reminder()
    async def reminder_stop(self, ctx: Context): 
      await self.bot.db.execute("DELETE FROM reminder WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
      return await ctx.send_success("Deleted a reminder")

    @command(aliases=['remindme'], help="utility", description="make the bot remind you about a task", usage="[time] [reminder]")
    async def remind(self, ctx: Context, time: str, *, task: str):
     try: seconds = humanfriendly.parse_timespan(time)
     except humanfriendly.InvalidTimespan: return await ctx.send_warning(f"**{time}** is not a correct time format")
     await ctx.reply(f"🕰️ {ctx.author.mention}: I'm going to remind you in {humanfriendly.format_timespan(seconds)} about **{task}**")
     if seconds < 5: 
      await asyncio.sleep(seconds)
      return await ctx.channel.send(f"🕰️ {ctx.author.mention}: {task}")   
     else: 
      try: await self.bot.db.execute("INSERT INTO reminder VALUES ($1,$2,$3,$4,$5)", ctx.author.id, ctx.channel.id, ctx.guild.id, (datetime.datetime.now() + datetime.timedelta(seconds=seconds)), task)
      except: return await ctx.send_warning("You already have a reminder set in this channel. Use `{ctx.clean_prefix}reminder stop` to cancel the reminder")

async def setup(bot):
    await bot.add_cog(Utility(bot))        