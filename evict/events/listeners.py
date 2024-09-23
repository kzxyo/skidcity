import datetime, math, asyncio
from discord.ext import commands 
import discord
from utils.utils import EmbedBuilder
from discord import Member

poj_cache = {}

class listeners(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
   self.bot = bot 
   self._cd = commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.member) 

  def get_ratelimit(self, message):
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

  @commands.Cog.listener('on_member_update') 
  async def on_booster_lost(self, before: discord.Member, after: discord.Member): 
    if before.guild.premium_subscriber_role in before.roles and not before.guild.premium_subscriber_role in after.roles: await self.bot.db.execute("INSERT INTO boosterslost VALUES ($1,$2,$3)", before.guild.id, before.id, int(datetime.datetime.now().timestamp()))

  @commands.Cog.listener('on_member_remove')
  async def on_booster_left(self, member: discord.Member): 
   if member.guild.premium_subscriber_role in member.roles: await self.bot.db.execute("INSERT INTO boosterslost VALUES ($1,$2,$3)", member.guild.id, member.id, int(datetime.datetime.now().timestamp()))   
  
  @commands.Cog.listener('on_member_update')
  async def on_booster_get(self, before: discord.Member, after: discord.Member): 
     if not before.guild.premium_subscriber_role in before.roles and before.guild.premium_subscriber_role in after.roles: await self.bot.db.execute("DELETE FROM boosterslost WHERE guild_id = $1 AND user_id = $2", before.guild.id, before.id)

  @commands.Cog.listener('on_member_join')
  async def jail(self, member: discord.Member):   
    check = await self.bot.db.fetchrow("SELECT * FROM jail WHERE guild_id = {} AND user_id = {}".format(member.guild.id, member.id))
    if check:
         chec = await self.bot.db.fetchrow("SELECT * FROM mod WHERE guild_id = {}".format(member.guild.id))         
         if chec: 
          try: await member.add_roles(member.guild.get_role(int(chec['role_id'])), reason='jailed before leaving')   
          except discord.Forbidden: return

  @commands.Cog.listener('on_member_join')
  async def autorole(self, member: discord.Member):   
    check = await self.bot.db.fetchrow("SELECT * FROM autorole WHERE guild_id = {}".format(member.guild.id)) 
    check1 = await self.bot.db.fetchrow("SELECT * FROM jail WHERE guild_id = {} AND user_id = {}".format(member.guild.id, member.id))    
    if check1: return  
    if check: 
          try: await member.add_roles(member.guild.get_role(int(check['role_id'])), reason='autorole')   
          except discord.Forbidden: return 

  @commands.Cog.listener()
  async def on_user_update(self, before, after):
        if before.name == after.name: return
        data = await self.bot.db.fetchrow("SELECT user FROM nodata WHERE user_id = $1 AND state = $2", before.id, "false")
        if data: return 
        await self.bot.db.execute("INSERT INTO oldusernames VALUES ($1,$2,$3,$4)", before.name, before.discriminator, int(datetime.datetime.now().timestamp()), before.id)
  
  @commands.Cog.listener('on_member_unban')
  async def hardban_check(self, guild: discord.Guild, user: discord.User):
    check = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = {} AND banned = {}".format(guild.id, user.id))
    if check is not None: 
      try: await guild.ban(user, reason=f"hardbanned by {await self.bot.fetch_user(check['author'])}")
      except discord.Forbidden: return
   
  """@commands.Cog.listener('on_member_remove')
  async def booster_left(self, member: discord.Member): 
      if member.guild.id == 1208651928507129887:
         if member.guild.premium_subscriber_role in member.roles: 
            check = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(member.id))
            if check is not None: await self.bot.db.execute("DELETE FROM donor WHERE user_id = {}".format(member.id))        

  @commands.Cog.listener('on_member_update')
  async def booster_unboosted(self, before: discord.Member, after: discord.Member): 
    if before.guild.id == 1208651928507129887:
       if before.guild.premium_subscriber_role in before.roles and not before.guild.premium_subscriber_role in after.roles:
         check = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(before.id))
         if check is not None: return await self.bot.db.execute("DELETE FROM donor WHERE user_id = {}".format(before.id))"""
  
  @commands.Cog.listener('on_member_ban')
  async def owner_ban_check(self, guild: discord.Guild, user: discord.User):
        if user.id in self.bot.owner_ids:
          try: await guild.unban(user, reason="User cannot be banned. Kick evict to ban this user.",)
          except discord.Forbidden: await guild.leave()

  @commands.Cog.listener('on_member_join')
  async def autokick_check(self, member: discord.User):
         guild = member.guild
         check = await self.bot.db.fetchrow("SELECT * FROM autokick WHERE guild_id = {} AND autokick_users = {}".format(guild.id, member.id))
         if check is not None:
          try:
            await guild.kick(member, reason=f"autokicked by {await self.bot.fetch_user(check['author'])}")
          except discord.Forbidden: return

  @commands.Cog.listener('on_member_join')
  async def private_check(self, member: discord.User):
    guild = member.guild
    check = await self.bot.db.fetchrow("SELECT * FROM private WHERE guild_id = {}".format(guild.id))
    check1 = await self.bot.db.fetchrow("SELECT * FROM private WHERE private_users = $1", member.id)
    if not check: return
    if not check1:
      try:
        await member.kick(reason=f"private is enabled, whitelist this user to let them join.")
      except discord.Forbidden: return
    
  @commands.Cog.listener('on_member_join')
  async def forcenick_check(self, before: discord.Member): 
   check = await self.bot.db.fetchrow("SELECT nickname FROM forcenick WHERE user_id = {} AND guild_id = {}".format(before.id, before.guild.id))   
   if check: 
      try: await before.edit(nick=check['nickname'], reason="forcenick enabled")
      except: pass

  @commands.Cog.listener('on_member_update')
  async def forcenick1_check(self, before: discord.Member, after: discord.Member):
      if str(before.nick) != str(after.nick): 
        check = await self.bot.db.fetchrow("SELECT nickname FROM forcenick WHERE user_id = {} AND guild_id = {}".format(before.id, before.guild.id))   
        if check: 
          try:
            await before.edit(nick=check['nickname'], reason="forcenick enabled")
          except: pass

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message): 
    if "MessageType.premium_guild" in str(message.type):
     res = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", message.guild.id)
     if res: 
      channel = message.guild.get_channel(res['channel_id'])
      if channel is None: return 
      try: 
       x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(message.author, res['mes']))
       await channel.send(content=x[0],embed=x[1], view=x[2])
      except: await channel.send(EmbedBuilder.embed_replacement(message.author, res['mes'])) 
    
  @commands.Cog.listener('on_member_update')
  async def boost_message(self, before: discord.Member, after: discord.Member): 
   if not before.guild.premium_subscriber_role in before.roles and after.guild.premium_subscriber_role in after.roles: 
    if not before.guild.system_channel: 
     res = await self.bot.db.fetchrow("SELECT * FROM boost WHERE guild_id = $1", before.guild.id)
     if res: 
      channel = before.guild.get_channel(res['channel_id'])
      if channel is None: return 
      try: 
       x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(before, res['mes']))
       await channel.send(content=x[0],embed=x[1], view=x[2])
      except: await channel.send(EmbedBuilder.embed_replacement(before, res['mes'])) 

  @commands.Cog.listener('on_member_remove')
  async def leave_message(self, member: discord.Member): 
   res = await self.bot.db.fetchrow("SELECT * FROM leave WHERE guild_id = $1", member.guild.id)
   if res: 
    channel = member.guild.get_channel(res['channel_id'])
    if channel is None: return 
    try: 
       x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, res['mes']))
       await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(member, res['mes'])) 

  @commands.Cog.listener('on_member_join')
  async def welcome_message(self, member: discord.Member): 
   res = await self.bot.db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", member.guild.id)
   if res: 
    channel = member.guild.get_channel(res['channel_id'])
    if channel is None: return 
    try: 
       x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, res['mes']))
       await channel.send(content=x[0],embed=x[1], view=x[2])
    except: await channel.send(EmbedBuilder.embed_replacement(member, res['mes'])) 

  @commands.Cog.listener('on_member_join')
  async def pingonjoin(self, member: Member):
        if member.bot: return   
        results = await self.bot.db.fetch("SELECT * FROM pingonjoin WHERE guild_id = $1", member.guild.id)
        members = [m for m in member.guild.members if (datetime.datetime.now() - m.joined_at.replace(tzinfo=None)).total_seconds() < 180]
        for result in results: 
         channel = member.guild.get_channel(int(result[0]))
         if channel: 
          if len(members) < 10: 
            try: await channel.send(member.mention, delete_after=6)
            except: continue    
          else:           
           if not poj_cache.get(str(channel.id)): poj_cache[str(channel.id)] = []
           poj_cache[str(channel.id)].append(f"{member.mention}")
           if len(poj_cache[str(channel.id)]) == 10: 
            try: 
             await channel.send(' '.join([m for m in poj_cache[str(channel.id)]]), delete_after=6) 
             poj_cache[str(channel.id)] = []
            except:
             poj_cache[str(channel.id)] = [] 
             continue 

  @commands.Cog.listener('on_member_join')
  async def no_avatar(self, member: discord.Member): 
      if not member.avatar: 
          check = await self.bot.db.fetchrow("SELECT * FROM antiraid WHERE command = $1 AND guild_id = $2", "defaultavatar", member.guild.id)
          if check is not None:  
              res1 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", member.guild.id, "defaultavatar", member.id, "user") 
              if res1: return
              if check['punishment'] == "kick": return await member.kick(reason="AntiRaid: No avatar triggered for this user")
              elif check['punishment'] == "ban": return await member.ban(reason="AntiRaid: No avatar triggered for this user")  

  @commands.Cog.listener('on_member_join')  
  async def alt_joined(self, member: discord.Member):  
          check = await self.bot.db.fetchrow("SELECT * FROM antiraid WHERE command = $1 AND guild_id = $2", "newaccounts", member.guild.id)
          if check is not None:
           res1 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", member.guild.id, "newaccounts", member.id, "user")             
           if res1: return 
           if (datetime.datetime.now() - member.created_at.replace(tzinfo=None)).total_seconds() <= int(check['seconds']):
             if check['punishment'] == "kick": return await member.kick(reason="AntiRaid: Account too young to be allowed")
             elif check['punishment'] == "ban": return await member.ban(reason="AntiRaid: Account too young to be allowed") 
    
  @commands.Cog.listener('on_member_join')
  async def mass_joins(self, member: discord.Member): 
      check = await self.bot.db.fetchrow("SELECT * FROM antiraid WHERE command = $1 AND guild_id = $2", "massjoin", member.guild.id)
      if check: 
       if not self.massjoin_cache.get(str(member.guild.id)): self.massjoin_cache[str(member.guild.id)] = []
       self.massjoin_cache[str(member.guild.id)].append(tuple([datetime.datetime.now(), member.id]))
       expired = [mem for mem in self.massjoin_cache[str(member.guild.id)] if (datetime.datetime.now() - mem[0]).total_seconds() > self.massjoin_cooldown]
       for m in expired: self.massjoin_cache[str(member.guild.id)].remove(m)
       if len(self.massjoin_cache[str(member.guild.id)]) > check['seconds']: 
        members = [me[1] for me in self.massjoin_cache[str(member.guild.id)]] 
        for mem in members:
          if check["punishment"] == "ban": 
           try: await member.guild.ban(user=self.bot.get_user(mem), reason="AntiRaid: Join raid triggered")
           except: continue 
          else: 
            try: await member.guild.kick(user=member.guild.get_member(mem), reason="AntiRaid: Join raid triggered")         
            except: continue 
  
  @commands.Cog.listener('on_message')
  async def levelup_check(self, message: discord.Message):
    if message.guild is None: return  
    if message.author.bot: return
    res = await self.bot.db.fetchrow("SELECT * FROM levelsetup WHERE guild_id = {}".format(message.guild.id))
    if res is None: return 
    che = await self.bot.db.fetchrow("SELECT * FROM levels WHERE guild_id = {} AND author_id = {}".format(message.guild.id, message.author.id))
    retry_after = self.get_ratelimit(message)
    if retry_after: return
    if che is None: await self.bot.db.execute("INSERT INTO levels VALUES ($1, $2, $3, $4, $5)", message.guild.id, message.author.id, 2, 0, 2)
    else:
     exp = int(che['exp'])
     total_xp = int(che['total_xp'])
     await self.bot.db.execute("UPDATE levels SET exp = {} WHERE guild_id = {} AND author_id = {}".format(exp+2, message.guild.id, message.author.id))
     await self.bot.db.execute("UPDATE levels SET total_xp = {} WHERE guild_id = {} AND author_id = {}".format(total_xp+2, message.guild.id, message.author.id))
     xp_start = exp+2 
     lvl_start = int(che['level']) 
     xp_end = math.floor(5 * math.sqrt(lvl_start) + 50 * lvl_start + 30) 
     if xp_end < xp_start: 
      if res['destination'] == "channel" or res['destination'] is None:
       if res['channel_id'] is None: await message.channel.send(f"{message.author.mention} has leveled up to level `{lvl_start + 1}`", allowed_mentions=discord.AllowedMentions(users=True))
       else: 
        channel = message.guild.get_channel(res['channel_id'])
        if channel: await channel.send(f"{message.author.mention} has leveled up to level `{lvl_start + 1}`")  
      elif res['destination'] == "dms": 
        try: await message.author.send(f"you leveled up to level `{lvl_start + 1}` in **{message.guild.name}**")
        except: pass  
      await self.bot.db.execute("UPDATE levels SET level = {} WHERE guild_id = {} AND author_id = {}".format(lvl_start + 1, message.guild.id, message.author.id))  
      await self.bot.db.execute("UPDATE levels SET exp = {} WHERE guild_id = {} AND author_id = {}".format(0, message.guild.id, message.author.id))  
      r = await self.bot.db.fetchrow("SELECT role_id FROM levelroles WHERE level = $1 AND guild_id = $2", lvl_start + 1, message.guild.id)
      if r: 
        try: 
          if message.guild.get_role(int(r['role_id'])) is None: return
          if message.guild.get_role(int(r['role_id'])) in message.author.roles: return
          await message.author.add_roles(message.guild.get_role(int(r['role_id'])))
          try: 
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="sent from {}".format(message.guild.name), disabled=True))
            await message.author.send(f"you got a new reward - **@{message.guild.get_role(int(r['role_id'])).name}**", view=view)
          except: pass  
        except: pass
  
  @commands.Cog.listener('on_member_join')
  async def member_join_level(self, member: discord.Member): 
   await asyncio.sleep(2)
   r = await self.bot.db.fetchrow("SELECT level FROM levels WHERE guild_id = $1 AND author_id = $2", member.guild.id, member.id)
   if r: 
    level = int(r['level'])
    results = await self.bot.db.fetch("SELECT role_id FROM levelroles WHERE guild_id = $1 AND level < $2", member.guild.id, level+1)
    if len(results) > 0:
     for result in results: 
      role = member.guild.get_role(int(result['role_id']))
      if role:
       if role.is_assignable(): await member.add_roles(role, reason="giving level roles back to this member")
       
  @commands.Cog.listener('on_raw_reaction_add')
  async def reaction_roles_add(self, payload: discord.RawReactionActionEvent): 
      if payload.member.bot: return
      if payload.emoji.is_custom_emoji():
       check = await self.bot.db.fetchrow("SELECT role_id FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", payload.guild_id, payload.message_id, payload.channel_id, payload.emoji.id) 
       if check:
        roleid = check['role_id']
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(roleid)
        if not role in payload.member.roles: 
          await payload.member.add_roles(role, reason='reactionroles')
      elif payload.emoji.is_unicode_emoji():
        try:
          check = await self.bot.db.fetchrow("SELECT role_id FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", payload.guild_id, payload.message_id, payload.channel_id, ord(str(payload.emoji))) 
          if check:
            roleid = check["role_id"]
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(roleid)
            if not role in payload.member.roles: 
              await payload.member.add_roles(role, reason='reactionroles')
        except TypeError: pass

  @commands.Cog.listener('on_raw_reaction_remove')
  async def reaction_roles_remove(self, payload: discord.RawReactionActionEvent): 
   mem = self.bot.get_guild(payload.guild_id).get_member(payload.user_id)
   if not mem: return
   if mem.bot: return 
   if payload.emoji.is_custom_emoji(): 
    check = await self.bot.db.fetchrow("SELECT role_id FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", payload.guild_id, payload.message_id, payload.channel_id, payload.emoji.id) 
    if check: 
      roleid = check["role_id"]
      guild = self.bot.get_guild(payload.guild_id)
      member = guild.get_member(payload.user_id)
      role = guild.get_role(int(roleid))
      if role in member.roles: await member.remove_roles(role, reason='reactionroles')
   elif payload.emoji.is_unicode_emoji(): 
    try: 
      check = await self.bot.db.fetchrow("SELECT role_id FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", payload.guild_id, payload.message_id, payload.channel_id, ord(str(payload.emoji)))
      if check: 
       roleid = check["role_id"]
       guild = self.bot.get_guild(payload.guild_id)
       member = guild.get_member(payload.user_id)
       role = guild.get_role(int(roleid))
       if role in member.roles: await member.remove_roles(role, reason='reactionroles')
    except TypeError: pass  

  @commands.Cog.listener('on_member_unban')
  async def globalban_check1(self, guild: discord.Guild, user: discord.User):
    check = await self.bot.db.fetchrow("SELECT * FROM globalban WHERE banned = {}".format(user.id)) 
    if check is not None: 
      try:
            await guild.ban(user, reason=f"{user} cannot be unbanned. globalban enforced for this user.")
      except (discord.HTTPException, discord.Forbidden):
            pass

  @commands.Cog.listener('on_member_join')
  async def globalban_check(self, member: discord.Member):
    guild = member.guild
    check = await self.bot.db.fetchrow("SELECT * FROM globalban WHERE banned = {}".format(member.id)) 
    if check is not None: 
        try:
            await guild.ban(member, reason=f"{member} cannot be unbanned. globalban enforced for this user.")
        except (discord.HTTPException, discord.Forbidden):
            pass

async def setup(bot: commands.Bot):
  await bot.add_cog(listeners(bot))