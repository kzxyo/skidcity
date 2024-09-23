import discord, math
from discord.ext import commands
from patches.permissions import Permissions

def get_progress(xp, level):
  corner_black_left = "<:blue_left_rounded:1263743883569926224>"
  black = "<:blue:1263743876900978708>"
  corner_black_right = "<:blue_right_rounded:1263743889915904092>" 
  corner_white_left = "<:white_left_rounded:1263743905120387172>"
  white = "<:white:1263743898145001517>"
  corner_white_right = "<:white_right_rounded:1263743912221216862>"
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

class leveling(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
   self.bot = bot 
   self._cd = commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.member) 

  @commands.command(description="check any members rank", usage="[member]")
  async def rank(self, ctx, member: discord.Member=None): 
    if member is None: member = ctx.author
    check = await self.bot.db.fetchrow("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id)) 
    if check is None: return await ctx.error("Levels **aren't** enabled in this server.")
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

  @level.group(invoke_without_command=True, description="manage the rewards for each level")
  async def rewards(self, ctx: commands.Context): 
    await ctx.create_pages()

  @rewards.command(description="add a level reward", usage="[level] [role]", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def add(self, ctx: commands.Context, level: int, *, role: discord.Role): 
    if self.bot.ext.is_dangerous(role): return await ctx.warning('You **cannot** make a level role a role with dangerous permissions.')
    check = await self.bot.db.fetchrow("SELECT level FROM levelroles WHERE guild_id = {} AND level = {}".format(ctx.guild.id, level))
    if check is not None: return await ctx.warning(f"A role has been **already** assigned for level **{level}**.") 
    await self.bot.db.execute("INSERT INTO levelroles VALUES ($1,$2,$3)", ctx.guild.id, level, role.id) 
    await ctx.success(f"I have **added** {role.mention} for level **{level}** reward.")

  @rewards.command(description="remove a level reward", usage="[level]", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def remove(self, ctx: commands.Context, level: int=None): 
    check = await self.bot.db.fetchrow("SELECT level FROM levelroles WHERE guild_id = {} AND level = {}".format(ctx.guild.id, level))
    if check is None: return await ctx.warning(f"There is **no** role assigned for level **{level}**.")
    await self.bot.db.execute("DELETE FROM levelroles WHERE guild_id = $1 AND level = $2", (ctx.guild.id, level))  
    await ctx.success(f"I have **removed** level **{level}** reward.")
  
  @rewards.command(name="reset", description="reset all level rewards", brief="administrator")
  @Permissions.has_permission(administrator=True) 
  async def rewards_reset(self, ctx: commands.Context): 
   results = await self.bot.db.fetch("SELECT * FROM levelroles WHERE guild_id = {}".format(ctx.guild.id))
   if len(results) == 0: return await ctx.error("There are **no** role rewards in this server.")
   await self.bot.db.execute("DELETE FROM levelroles WHERE guild_id = $1", ctx.guild.id)
   return await ctx.success("I have reset **all** level rewards.") 

  @rewards.command(description="return a list of role rewards")
  async def list(self, ctx: commands.Context): 
      results = await self.bot.db.fetch("SELECT * FROM levelroles WHERE guild_id = {}".format(ctx.guild.id))
      if len(results) == 0: return await ctx.error("There are **no** role rewards in this server.")
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
      embed.set_author(name = f"Level Rewards", icon_url = ctx.guild.icon.url or None)
      number.append(embed)
      await ctx.paginate(number)

  @level.command(name="reset", description="reset levels for a member, leave blank for everyone", brief="administrator", usage="<member>")
  @Permissions.has_permission(administrator=True) 
  async def level_reset(self, ctx: commands.Context, *, member: discord.Member=None):
    check = await self.bot.db.fetchrow("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id))        
    if check is None: return await ctx.warning("Levels are not configured.")
    if not member:
     await self.bot.db.execute("DELETE FROM levels WHERE guild_id = $1", ctx.guild.id)
     return await ctx.success("I have reset levels for **all** members.") 
    else: 
     await self.bot.db.execute("DELETE FROM levels WHERE guild_id = $1 AND author_id = $2", ctx.guild.id, member.id)
     return await ctx.success(f"I have reset levels for **{member}**.") 

  @level.command(aliases=["lb"], description="check level leaderboard")
  async def leaderboard(self, ctx: commands.Context):
    await ctx.channel.typing() 
    results = await self.bot.db.fetch("SELECT * FROM levels WHERE guild_id = {}".format(ctx.guild.id))
    if len(results) == 0: return await ctx.error("nobody is on the **level leaderboard**")
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
      auto += f"\n{'<:crown:1263741407969939467>' if num == 1 else f'`{num}`'} **{await self.bot.fetch_user(user) or user}** - **{exp}** xp (level {level})"
      k+=1
      l+=1
      if l == 10: break
    messages.append(auto)
    embed = discord.Embed(description = auto, color = self.bot.color)
    embed.set_author(name = f"Level Leaderboard", icon_url = ctx.guild.icon.url or None)
    await ctx.send(embed=embed)     
         
  @level.command(description="enable leveling system, or disable it", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def toggle(self, ctx: commands.Context): 
      check = await self.bot.db.fetchrow("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id))        
      if check is None:
       await self.bot.db.execute("INSERT INTO levelsetup (guild_id) VALUES ($1)", ctx.guild.id)
       return await ctx.success("I have **enabled** the leveling system.")
      elif check is not None: 
        await self.bot.db.execute("DELETE FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id)) 
        return await ctx.success("I have **disabled** the leveling system.")
  
  @level.command(description="set where the level up message should be sent", usage="[destination]\ndestinations: channel, dms, off", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def levelup(self, ctx: commands.Context, destination: str): 
      if not destination in ["dms", "channel", "off"]: return await ctx.warning("You passed an **invalid** destination.")
      check = await self.bot.db.execute("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id))  
      if check is None: return await ctx.reply("The leveling system is **not** enabled,", mention_author=False) 
      await self.bot.db.execute("UPDATE levelsetup SET destination = $1 WHERE guild_id = $2", destination, ctx.guild.id)
      return await ctx.success(f"I have **updated** the level up message destination: **{destination}**.")
      
  @level.command(description="set a channel to send level up messages", usage="[channel]", brief="manage guild")
  @Permissions.has_permission(manage_guild=True) 
  async def channel(self, ctx: commands.Context, *, channel: discord.TextChannel): 
      check = await self.bot.db.fetch("SELECT * FROM levelsetup WHERE guild_id = {}".format(ctx.guild.id))  
      if check is None: return await ctx.warning("The leveling system is **not** enabled.")
      if channel is None: 
       await self.bot.db.execute("UPDATE levelsetup SET channel_id = {} WHERE guild_id = {}".format(None, ctx.guild.id))
       return await ctx.success("I have **removed** the channel for level up messages.")
      elif channel is not None: 
       await self.bot.db.execute("UPDATE levelsetup SET channel_id = {} WHERE guild_id = {}".format(channel.id, ctx.guild.id))
       await ctx.success(f"I have set the channel for level up messages to {channel.mention}.")   

async def setup(bot): 
 await bot.add_cog(leveling(bot))  