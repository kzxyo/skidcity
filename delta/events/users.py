import datetime 
from discord.ext import commands 
import discord
from cogs.donor import checktag

class Users(commands.Cog): 
  def __init__(self, bot: commands.AutoShardedBot): 
   self.bot = bot 

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
  async def auto_or_jail(self, member: discord.Member):   
    check = await self.bot.db.fetchrow("SELECT * FROM jail WHERE guild_id = {} AND user_id = {}".format(member.guild.id, member.id))
    if check:
         chec = await self.bot.db.fetchrow("SELECT * FROM mod WHERE guild_id = {}".format(member.guild.id))         
         if chec: 
          try: await member.add_roles(member.guild.get_role(int(chec['role_id'])))   
          except: pass 
    elif not check: 
        role = None 
        if member.discriminator == "0001" and checktag(member.name) is True: 
         che = await self.bot.db.fetchrow("SELECT role_id FROM discrim WHERE guild_id = $1", member.guild.id)
         if che: 
          role = member.guild.get_role(int(che['role_id']))
          if not role: await self.bot.db.execute("DELETE FROM discrim WHERE guild_id = $1", member.guild.id)
        results = await self.bot.db.fetch("SELECT * FROM autorole WHERE guild_id = {}".format(member.guild.id)) 
        if len(results) == 0: return
        roles = [member.guild.get_role(int(result['role_id'])) for result in results if member.guild.get_role(int(result['role_id'])) is not None and member.guild.get_role(int(result['role_id'])).is_assignable()]
        if role: roles.append(role)
        await member.edit(roles=roles, reason="autorole") 

  @commands.Cog.listener()
  async def on_user_update(self, before, after):
        if before.name == after.name: return
        data = await self.bot.db.fetchrow("SELECT user FROM nodata WHERE user_id = $1 AND state = $2", before.id, "false")
        if data: return 
        await self.bot.db.execute("INSERT INTO oldusernames VALUES ($1,$2,$3,$4)", before.name, before.discriminator, int(datetime.datetime.now().timestamp()), before.id)
  
  @commands.Cog.listener()
  async def on_member_unban(self, guild: discord.Guild, user: discord.User):
         check = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = {} AND banned = {}".format(guild.id, user.id))
         if check is not None: 
            await guild.ban(user, reason=f"hardbanned by {await self.bot.fetch_user(check['author'])}")
   
  @commands.Cog.listener('on_member_remove')
  async def booster_left(self, member: discord.Member): 
      if member.guild.id == 952161067033849919:
         if member.guild.premium_subscriber_role in member.roles: 
            check = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(member.id))
            if check is not None: await self.bot.db.execute("DELETE FROM donor WHERE user_id = {}".format(member.id))                 

  @commands.Cog.listener('on_member_update')
  async def booster_unboosted(self, before: discord.Member, after: discord.Member): 
    if before.guild.id == 952161067033849919:
       if before.guild.premium_subscriber_role in before.roles and not before.guild.premium_subscriber_role in after.roles:
         check = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(before.id))
         if check is not None: return await self.bot.db.execute("DELETE FROM donor WHERE user_id = {}".format(before.id))   
               
  @commands.Cog.listener()
  async def on_member_join(self, before: discord.Member): 
   check = await self.bot.db.fetchrow("SELECT nickname FROM forcenick WHERE user_id = {} AND guild_id = {}".format(before.id, before.guild.id))   
   if check: return await before.edit(nick=check['nickname'])

  @commands.Cog.listener()
  async def on_member_update(self, before: discord.Member, after: discord.Member):
      if str(before.nick) != str(after.nick): 
        check = await self.bot.db.fetchrow("SELECT nickname FROM forcenick WHERE user_id = {} AND guild_id = {}".format(before.id, before.guild.id))   
        if check: return await before.edit(nick=check['nickname'])

async def setup(bot: commands.AutoShardedBot):
  await bot.add_cog(Users(bot))         