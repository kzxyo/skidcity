import discord, math, asyncio
from discord.ext import commands
from tools.checks import Perms

def get_progress(xp, level):
  corner_black_left = "<:level_black_left:1062057953559072819>"
  black = "<:level_black:1062058036539175033>"
  corner_black_right = "<:level_black_right:1062058125802352701>" 
  corner_white_left = "<:level_white_left:1062058377586413661>"
  white = "<:level_white:1062058249605619793>"
  corner_white_right = "<:level_white_right:1062058819842211840>"
  xp_end = math.floor(5 * math.sqrt(level) + 50 * level + 30)
  percentage = xp/xp_end * 100 
  if percentage < 10: 
    rest = ""
    for _ in range(8):
      rest = rest + black 
    return corner_black_left + rest + corner_black_right
  elif percentage > 10 and percentage < 20: 
      return corner_white_left + white + black + black + black + black + black + black + black + corner_black_right
  elif percentage > 20 and percentage < 30: 
    rest = ""
    rest2 = ""
    for _ in range(6): 
       rest = rest + black 
    for _ in range(2):         
      rest2 = rest2 + white

    return corner_white_left + rest2 + rest + corner_black_right
  elif percentage > 30 and percentage < 40: 
    rest = ""
    rest2 = ""
    for _ in range(5): 
       rest = rest + black 
    for _ in range(3):         
      rest2 = rest2 + white

    return corner_white_left + rest2 + rest + corner_black_right   
  elif percentage > 40 and percentage < 50:
    rest = ""
    rest2 = ""
    for _ in range(4): 
       rest = rest + black 
    for _ in range(4):         
      rest2 = rest2 + white

    return corner_white_left + rest2 + rest + corner_black_right      
  elif percentage > 50 and percentage < 60: 
    rest = ""
    rest2 = ""
    for _ in range(3): 
       rest = rest + black 
    for _ in range(5):         
      rest2 = rest2 + white

    return corner_white_left + rest2 + rest + corner_black_right  
  elif percentage > 60 and percentage < 70: 
    rest = ""
    rest2 = ""
    for _ in range(2): 
       rest = rest + black 
    for _ in range(6):         
      rest2 = rest2 + white

    return corner_white_left + rest2 + rest + corner_black_right    
  elif percentage > 70 and percentage < 80: 
    rest = ""
    for _ in range(7): 
      rest = rest + white 
    return corner_white_left + rest + black + corner_black_right      
  elif percentage > 80 and percentage < 90: 
    rest = ""
    for _ in range(8):
      rest = rest + white 
    return corner_white_left + rest + corner_black_right
  elif percentage > 90: 
    rest = ""
    for _ in range(8):
      rest = rest + white 
    return corner_white_left + rest + corner_white_right  
  return "N/A"  

class Leveling(commands.Cog): 
  def __init__(self, bot: commands.AutoShardedBot): 
   self.bot = bot 
   self._cd = commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.member) 

  def get_ratelimit(self, message):
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):
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
        try: await message.author.send(f"You leveled up to level `{lvl_start + 1}` in **{message.guild.name}**")
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
            await message.author.send(f"You got a new reward - **@{message.guild.get_role(int(r['role_id'])).name}**", view=view)
          except: pass  
        except: pass
  
  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member): 
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

  @commands.hybrid_command(description="check any member's rank", help="config", usage="[member]")
  async def rank(self, ctx, member: discord.Member=None): 
    if member is None: member = ctx.author
    check = await self.bot.db.fetchrow("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id)) 
    if check is None: return await ctx.send_error("Levels aren't enabled in this server")
    che = await self.bot.db.fetchrow("SELECT * FROM levels WHERE guild_id = {} AND author_id = {}".format(ctx.guild.id, member.id))
    if che is None: return await ctx.reply(embed=discord.Embed(color=self.bot.color, title=f"{member.name}'s rank").set_author(name=member, icon_url=member.display_avatar.url).add_field(name="xp", value="**{}**".format("0")).add_field(name="level", value="**{}**".format("0")).add_field(name="progress (0%)", value=get_progress(0, 0), inline=False))
    level = int(che['level'])
    xp = int(che['exp'])
    xp_end = math.floor(5 * math.sqrt(level) + 50 * level + 30)
    percentage = int(xp/xp_end * 100)
    return await ctx.reply(embed=discord.Embed(color=self.bot.color, title=f"{member.name}'s rank").set_author(name=member, icon_url=member.display_avatar.url).add_field(name="xp", value="**{}**".format(str(xp))).add_field(name="level", value="**{}**".format(str(level))).add_field(name="progress ({}%)".format(percentage), value=get_progress(xp, level), inline=False))               
  
  @commands.group(invoke_without_command=True)
  async def level(self, ctx): 
     await ctx.create_pages()

  @level.group(invoke_without_command=True, help="config", description="manage the rewards for each level")
  async def rewards(self, ctx: commands.Context): 
    await ctx.create_pages()

  @rewards.command(description="add a level reward", help="config", usage="[level] [role]", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def add(self, ctx: commands.Context, level: int, *, role: discord.Role): 
    check = await self.bot.db.fetchrow("SELECT level FROM levelroles WHERE guild_id = {} AND level = {}".format(ctx.guild.id, level))
    if check is not None: return await ctx.send_warning(f"A role has been already assigned for level **{level}**") 
    await self.bot.db.execute("INSERT INTO levelroles VALUES ($1,$2,$3)", ctx.guild.id, level, role.id) 
    await ctx.send_success(f"Added {role.mention} for level **{level}** reward")

  @rewards.command(description="remove a level reward", help="config", usage="[level]", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def remove(self, ctx: commands.Context, level: int=None): 
    check = await self.bot.db.fetchrow("SELECT level FROM levelroles WHERE guild_id = {} AND level = {}".format(ctx.guild.id, level))
    if check is None: return await ctx.send_warning(f"There is no role assigned for level **{level}**")
    await self.bot.db.execute("DELETE FROM levelroles WHERE guild_id = $1 AND level = $2", (ctx.guild.id, level))  
    await ctx.send_success(f"Removed level **{level}** reward")
  
  @rewards.command(name="reset", description="reset all level rewards", help="config", brief="server owner")
  @Perms.server_owner()
  async def rewards_reset(self, ctx: commands.Context): 
   results = await self.bot.db.fetch("SELECT * FROM levelroles WHERE guild_id = {}".format(ctx.guild.id))
   if len(results) == 0: return await ctx.send_error("There are no role rewards in this server")
   await self.bot.db.execute("DELETE FROM levelroles WHERE guild_id = $1", ctx.guild.id)
   return await ctx.send_success("Reset **all** level rewards") 

  @rewards.command(description="return a list of role rewards", help="config")
  async def list(self, ctx: commands.Context): 
      results = await self.bot.db.fetch("SELECT * FROM levelroles WHERE guild_id = {}".format(ctx.guild.id))
      if len(results) == 0: return await ctx.send_error("There are no role rewards in this server")
      def sortkey(e): 
        return e[1]

      results.sort(key=sortkey)
      i=0
      k=1
      l=0
      number = []
      messages = []
      num = 0
      auto = ""   
      for table in results:
       level = table['level']
       reward = table['role_id']
       num += 1
       auto += f"\n`{num}` level **{level}** - {ctx.guild.get_role(reward).mention if ctx.guild.get_role(reward) else reward}"
       k+=1
       l+=1
       if l == 10:
         messages.append(auto)
         number.append(discord.Embed(color=self.bot.color, description = auto).set_author(name = f"level rewards", icon_url = ctx.guild.icon.url or None))
         i+=1
         auto = ""
         l=0
      messages.append(auto)
      embed = discord.Embed(description = auto, color = self.bot.color)
      embed.set_author(name = f"level rewards", icon_url = ctx.guild.icon.url or None)
      number.append(embed)
      await ctx.paginator(number)

  @level.command(name="reset", description="reset levels for everyone", help="config", brief="server owner", usage="<member>")
  @Perms.server_owner()
  async def level_reset(self, ctx: commands.Context, *, member: discord.Member=None):
    check = await self.bot.db.fetchrow("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id))        
    if check is None: return await ctx.send_warning("Levels are not configured")
    if not member:
     await self.bot.db.execute("DELETE FROM levels WHERE guild_id = $1", ctx.guild.id)
     return await ctx.send_success("Reset levels for **all** members") 
    else: 
     await self.bot.db.execute("DELETE FROM levels WHERE guild_id = $1 AND author_id = $2", ctx.guild.id, member.id)
     return await ctx.send_success(f"Reset levels for **{member}**") 

  @level.command(aliases=["lb"], description="check level leaderboard", help="config")
  async def leaderboard(self, ctx: commands.Context):
    await ctx.channel.typing() 
    results = await self.bot.db.fetch("SELECT * FROM levels WHERE guild_id = {}".format(ctx.guild.id))
    if len(results) == 0: return await ctx.send_error("Nobody (even u) is on the **level leaderboard**")
    def sortkey(e): 
      return int(e[4])

    results.sort(key=sortkey, reverse=True)
    i=0
    k=1
    l=0
    messages = []
    num = 0
    auto = ""   
    for table in results:
      user = table['author_id']
      exp = table['exp']
      level = table['level']
      num += 1
      auto += f"\n{'<a:crown:1021829752782323762>' if num == 1 else f'`{num}`'} **{await self.bot.fetch_user(user) or user}** - **{exp}** xp (level {level})"
      k+=1
      l+=1
      if l == 10: break
    messages.append(auto)
    embed = discord.Embed(description = auto, color = self.bot.color)
    embed.set_author(name = f"level leaderboard", icon_url = ctx.guild.icon.url or None)
    await ctx.send(embed=embed)     
         
  @level.command(description="enable leveling system.. or disable it", help="config", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def toggle(self, ctx: commands.Context): 
      check = await self.bot.db.fetchrow("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id))        
      if check is None:
       await self.bot.db.execute("INSERT INTO levelsetup (guild_id) VALUES ($1)", ctx.guild.id)
       return await ctx.send_success("enabled leveling system".capitalize())
      elif check is not None: 
        await self.bot.db.execute("DELETE FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id)) 
        return await ctx.send_success("disabled leveling system".capitalize())
  
  @level.command(description="set where the level up message should be sent", help="config", usage="[destination]\ndestinations: channel, dms, off", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def levelup(self, ctx: commands.Context, destination: str): 
      if not destination in ["dms", "channel", "off"]: return await ctx.send_warning("Wrong destination passed")
      check = await self.bot.db.execute("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id))  
      if check is None: return await ctx.reply("leveling system is not enabled", mention_author=False) 
      await self.bot.db.execute("UPDATE levelsetup SET destination = $1 WHERE guild_id = $2", destination, ctx.guild.id)
      return await ctx.send_success(f"Level up message destination: **{destination}**")
      
  @level.command(description="set a channel to send level up messages", help="config", usage="[channel]", brief="manage guild")
  @Perms.get_perms("manage_guild")
  async def channel(self, ctx: commands.Context, *, channel: discord.TextChannel): 
      check = await self.bot.db.fetch("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id))  
      if check is None: return await ctx.send_warning("leveling system is not enabled".capitalize())
      if channel is None: 
       await self.bot.db.execute("UPDATE levelsetup SET channel_id = {} WHERE guild_id = {}".format(None, ctx.guild.id))
       return await ctx.send_success("removed the channel for leveling system".capitalize())
      elif channel is not None: 
       await self.bot.db.execute("UPDATE levelsetup SET channel_id = {} WHERE guild_id = {}".format(channel.id, ctx.guild.id))
       await ctx.send_success(f"set the channel for leveling system to {channel.mention}".capitalize())   

async def setup(bot): 
 await bot.add_cog(Leveling(bot))  