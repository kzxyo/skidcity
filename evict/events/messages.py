from discord.ext import commands 
import discord, json, asyncio, datetime, re
from uwuipy import uwuipy
from discord import Embed, Message, User
from reposter.reposter import Reposter
from patches.permissions import Perms
from collections import defaultdict
from patches import functions

DISCORD_API_LINK = "https://discord.com/api/invite/"

async def decrypt_message(content: str) -> str: 
    return content.lower().replace("1", "i").replace("4", "a").replace("3", "e").replace("0", "o").replace("@", "a") 

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
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
    self.locks = defaultdict(asyncio.Lock)
    self.antispam_cache = {}
    
  async def webhook(self, channel) -> discord.Webhook:
      for webhook in await channel.webhooks():
        if webhook.user == self.bot.user:
          return webhook
      try: await channel.create_webhook(name='evict')
      except: pass
   
  @commands.Cog.listener('on_message')
  async def reposter(self, message: discord.Message):
        if not message.guild: return
        if message.author.bot: return
        args = message.content.split(' ')
        social = await self.bot.db.fetchrow('SELECT * FROM settings_social WHERE guild_id = $1', message.guild.id)
        
        if not social or not social['toggled']: return
        
        prefix = social['prefix']
        if prefix.lower() == 'none': return await Reposter().repost(self.bot, message, args[0])
        if args[0] == prefix and args[1] is not None: return await Reposter().repost(self.bot, message, args[1])
        
  @commands.Cog.listener()
  async def subscriber_join(self, member: discord.Member): 
    if member.guild.id == 1208651928507129887:
      check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE buyer = $1", member.id)
      if check: await member.add_roles(member.guild.get_role(1209127936414842990))

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
      try: await message.reply(embed=embed)
      except: pass
      await self.bot.db.execute("DELETE FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)    
    
  @commands.Cog.listener("on_message_edit")
  async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Save edited messages to redis"""

        data = {
            "timestamp": before.created_at.timestamp(),
            "content": before.content,
            "embeds": [embed.to_dict() for embed in before.embeds[:8] if not embed.type == "image" and not embed.type == "video"],
            "attachments": [
                attachment.proxy_url
                for attachment in (before.attachments + list((embed.thumbnail or embed.image) for embed in before.embeds if embed.type == "image"))
            ],
            "stickers": [sticker.url for sticker in before.stickers],
            "author": {
                "id": before.author.id,
                "name": before.author.name,
                "discriminator": before.author.discriminator,
                "avatar": before.author.avatar.url if before.author.avatar else None,
            },
        }
        await self.bot.redis.ladd(
            f"edited_messages:{functions.hash(before.channel.id)}",
            data,
            ex=60,
        )

  @commands.Cog.listener("on_raw_reaction_remove")
  async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Save removed reactions to redis"""

        data = {
            "timestamp": discord.utils.utcnow().timestamp(),
            "message": payload.message_id,
            "user": payload.user_id,
            "emoji": str(payload.emoji),
        }

        await self.bot.redis.ladd(
            f"removed_reactions:{functions.hash(payload.channel_id)}",
            data,
            ex=60,
        )

  @commands.Cog.listener('on_message')
  async def uwulock(self, message: discord.Message):
        if not message.guild: return
        check = await self.bot.db.fetchrow("SELECT user_id FROM uwulock WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)
        check1 = await self.bot.db.fetchrow("SELECT user_id FROM guwulock WHERE user_id = $1", message.author.id)
        if check1: return  
        if check is None or not check: return 
        uwu = uwuipy()
        uwu_message = uwu.uwuify(message.content)
        hook = await self.webhook(message.channel)
        await hook.send(
                        content=uwu_message,
                        username=message.author.display_name,
                        avatar_url=message.author.display_avatar,
                        thread=message.channel if isinstance(message.channel, discord.Thread) else discord.utils.MISSING,
                    )
        await message.delete()

  @commands.Cog.listener('on_message')
  async def guwulock(self, message: discord.Message):
        if not message.guild: return
        check1 =  await self.bot.db.fetchrow("SELECT user_id FROM uwulock WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id) 
        check = await self.bot.db.fetchrow("SELECT user_id FROM guwulock WHERE user_id = $1", message.author.id)  
        if check1: return
        if check is None or not check: return 
        uwu = uwuipy()
        uwu_message = uwu.uwuify(message.content)
        hook = await self.webhook(message.channel)
        await hook.send(
                        content=uwu_message,
                        username=message.author.display_name,
                        avatar_url=message.author.display_avatar,
                        thread=message.channel if isinstance(message.channel, discord.Thread) else discord.utils.MISSING,
                    )
        await message.delete()

  @commands.Cog.listener('on_message')
  async def on_message_shutup(self, message: discord.Message):
        if not message.guild: return
        check = await self.bot.db.fetchrow("SELECT user_id FROM shutup WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)   
        if check is None or not check: return 
        try: await message.delete()
        except: pass

  @commands.Cog.listener("on_message")
  async def reposter(self, message: Message):
        if (
            message.guild
            and not message.author.bot
            and message.content.startswith("evict")
        ):
            if re.search(
                r"\bhttps?:\/\/(?:m|www|vm)\.tiktok\.com\/\S*?\b(?:(?:(?:usr|v|embed|user|video)\/|\?shareId=|\&item_id=)(\d+)|(?=\w{7})(\w*?[A-Z\d]\w*)(?=\s|\/$))\b",
                message.content[len("evict") + 1 :],
            ):
                return await self.repost_tiktok(message)

  @commands.Cog.listener('on_message')
  async def imageonly(self, message: Message):
      if not message.guild: return
      if isinstance(message.author, User): return
      if message.author.guild_permissions.manage_guild: return 
      if message.author.bot: return 
      if message.attachments: return       
      check = await self.bot.db.fetchrow("SELECT * FROM mediaonly WHERE channel_id = $1", message.channel.id)
      if check: 
        try: await message.delete()
        except: pass

  @commands.Cog.listener('on_message')
  async def sticky(self, message: discord.Message):
      if message.author.bot: return
      stickym = await self.bot.db.fetchval("SELECT key FROM stickym WHERE channel_id = $1", message.channel.id)
      if not stickym: return
    
      async for message in message.channel.history(limit=3):
        if message.author.id == self.bot.user.id: await message.delete()

      return await message.channel.send(stickym)  
    
  @commands.Cog.listener('on_message')
  async def lastfm_custom(self, message: discord.Message): 
       if not message.guild: return 
       if message.author.bot: return 
       check = await self.bot.db.fetchrow("SELECT * FROM lastfmcc WHERE command = $1 AND user_id = $2", message.clean_content, message.author.id)
       if check:
          context = await self.bot.get_context(message)
          await context.invoke(self.bot.get_command("nowplaying"))   
          
          
  @commands.Cog.listener("on_message")
  async def antispam_send(self, message: discord.Message):
        if not message.guild:
            return
        if isinstance(message.author, discord.User):
            return
        if await Perms.has_perms(await self.bot.get_context(message), "manage_guild"):
            return
        check = await self.bot.db.fetchrow(
            "SELECT * FROM antispam WHERE guild_id = $1", message.guild.id
        )
        if check:
            res1 = await self.bot.db.fetchrow(
                "SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4",
                message.guild.id,
                "antispam",
                message.channel.id,
                "channel",
            )
            if not res1:
                res2 = await self.bot.db.fetchrow(
                    "SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4",
                    message.guild.id,
                    "antispam",
                    message.author.id,
                    "user",
                )
                if not res2:
                    if not self.antispam_cache.get(str(message.channel.id)):
                        self.antispam_cache[str(message.channel.id)] = {}
                    if not self.antispam_cache[str(message.channel.id)].get(
                        str(message.author.id)
                    ):
                        self.antispam_cache[str(message.channel.id)][
                            str(message.author.id)
                        ] = []
                    self.antispam_cache[str(message.channel.id)][
                        str(message.author.id)
                    ].append(tuple([datetime.datetime.now(), message]))
                    expired_time = check["seconds"]
                    expired_msgs = [
                        msg
                        for msg in self.antispam_cache[str(message.channel.id)][
                            str(message.author.id)
                        ]
                        if (datetime.datetime.now() - msg[0]).total_seconds()
                        > expired_time
                    ]
                    for ex in expired_msgs:
                        self.antispam_cache[str(message.channel.id)][
                            str(message.author.id)
                        ].remove(ex)
                    if (
                        len(
                            self.antispam_cache[str(message.channel.id)][
                                str(message.author.id)
                            ]
                        )
                        > check["count"]
                    ):
                        messages = [
                            msg[1]
                            for msg in self.antispam_cache[str(message.channel.id)][
                                str(message.author.id)
                            ]
                        ]
                        self.antispam_cache[str(message.channel.id)][
                            str(message.author.id)
                        ] = []
                        punishment = check["punishment"]
                        if punishment == "delete":
                            return await message.channel.delete_messages(
                                messages, reason="AutoMod: spamming messages"
                            )
                        await message.channel.delete_messages(
                            messages, reason="AutoMod: spamming messages"
                        )
                        if not message.author.is_timed_out():
                            await message.channel.send(
                                embed=discord.Embed(
                                    color=self.bot.color,
                                    title="AutoMod",
                                    description=f"{self.bot.warning} {message.author.mention}: You have been muted for **1 minute** for spamming messages in this channel",
                                )
                            )
                            await message.author.timeout(
                                discord.utils.utcnow() + datetime.timedelta(minutes=1),
                                reason="AutoMod: spamming messages",
                            )

  @commands.Cog.listener('on_message')
  async def chatfilter_send(self, message: discord.Message): 
      if not message.guild: return 
      if isinstance(message.author, discord.User): return 
      if await Perms.has_perms(await self.bot.get_context(message), "manage_guild"): return 
      check = await self.bot.db.fetch("SELECT * FROM chatfilter WHERE guild_id = $1", message.guild.id) 
      if len(check) > 0: 
       res1 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "chatfilter", message.channel.id, "channel")
       if not res1:  
          res2 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "chatfilter", message.author.id, "user")             
          if not res2:
           for result in check: 
            if result["word"] in await decrypt_message(message.content): 
              return await message.delete()                          
    
  @commands.Cog.listener('on_message_edit')
  async def chatfilter_edit(self, before: discord.Message, after: discord.Message): 
      if before.content == after.content: return 
      message = after 
      if not message.guild: return 
      if isinstance(message.author, discord.User): return 
      if await Perms.has_perms(await self.bot.get_context(message), "manage_guild"): return 
      check = await self.bot.db.fetch("SELECT * FROM chatfilter WHERE guild_id = $1", message.guild.id) 
      if len(check) > 0: 
       res1 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "chatfilter", message.channel.id, "channel")
       if not res1:  
          res2 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "chatfilter", message.author.id, "user")             
          if not res2:
            for result in check: 
             if result["word"] in await decrypt_message(message.content): 
               return await message.delete() 
             
  @commands.Cog.listener('on_message_edit')
  async def invite_edit(self, before: discord.Message, after: discord.Message): 
     if after.content == before.content: return   
     message = after   
     if not message.guild: return 
     if isinstance(message.author, discord.User): return 
     if message.author.bot: return 
     if await Perms.has_perms(await self.bot.get_context(message), "manage_guild"): return 
     invites = ["discord.gg/", ".gg/", "discord.com/invite/"]
     if any(invite in message.content for invite in invites):
        check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = $1", message.guild.id)        
        if check is not None: 
          res1 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "antiinvite", message.channel.id, "channel")
          if res1: return 
          res2 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "antiinvite", message.author.id, "user")             
          if res2: return
          if "discord.gg/" in message.content:
            spl_word = "discord.gg/"
          elif ".gg/" in message.content:  
            spl_word = ".gg/"
          elif "discord.com/invite/" in message.content:
            spl_word = "discord.com/invite/"

          linko = message.content.partition(spl_word)[2]  
          link = linko.split()[0] 
          data = await self.bot.session.json(DISCORD_API_LINK + link)
          try:
           if int(data["guild"]["id"]) == message.guild.id: return
           await message.delete()
           await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=1), reason="AutoMod: Sending invites")
           await message.channel.send(embed=discord.Embed(color=self.bot.color, title="AutoMod", description=f"{self.bot.warning} {message.author.mention}: You have been muted for **1 minute** for sending discord invites in this channel"))
          except KeyError: pass  

  @commands.Cog.listener('on_message')
  async def invite_send(self, message: discord.Message):   
     if not message.guild: return 
     if isinstance(message.author, discord.User): return 
     if message.author.bot: return 
     if await Perms.has_perms(await self.bot.get_context(message), "manage_guild"): return 
     invites = ["discord.gg/", ".gg/", "discord.com/invite/"]
     if any(invite in message.content for invite in invites):
        check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = $1", message.guild.id)        
        if check is not None: 
          res1 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "antiinvite", message.channel.id, "channel")
          if res1: return 
          res2 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "antiinvite", message.author.id, "user")             
          if res2: return
          if "discord.gg/" in message.content:
            spl_word = "discord.gg/"
          elif ".gg/" in message.content:  
            spl_word = ".gg/"
          elif "discord.com/invite/" in message.content:
            spl_word = "discord.com/invite/"

          linko = message.content.partition(spl_word)[2]  
          link = linko.split()[0] 
          data = await self.bot.session.json(DISCORD_API_LINK + link)
          try:
           if int(data["guild"]["id"]) == message.guild.id: return
           await message.delete()
           await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=5), reason="AudoMod: Sending invites")
           await message.channel.send(embed=discord.Embed(color=self.bot.color, title="AutoMod", description=f"{self.bot.warning} {message.author.mention}: You have been muted for **5 minutes** for sending discord invites in this channel"))
          except KeyError: pass      


  @commands.Cog.listener("on_message_delete")
  async def on_message_delete(self, message: discord.Message):
        """Save deleted messages to redis"""

        data = {
            "timestamp": message.created_at.timestamp(),
            "content": message.content,
            "embeds": [embed.to_dict() for embed in message.embeds[:8] if not embed.type == "image" and not embed.type == "video"],
            "attachments": [
                attachment.proxy_url
                for attachment in (message.attachments + list((embed.thumbnail or embed.image) for embed in message.embeds if embed.type == "image"))
            ],
            "stickers": [sticker.url for sticker in message.stickers],
            "author": {
                "id": message.author.id,
                "name": message.author.name,
                "discriminator": message.author.discriminator,
                "avatar": message.author.avatar.url if message.author.avatar else None,
            },
        }
        await self.bot.redis.ladd(
            f"deleted_messages:{functions.hash(message.channel.id)}",
            data,
            ex=60,
        )
        
async def setup(bot: commands.Bot):
  await bot.add_cog(Messages(bot))