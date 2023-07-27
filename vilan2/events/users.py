import discord, datetime
from discord.ext import commands

class Users(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
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
      await self.bot.db.execute("INSERT INTO oldusernames VALUES ($1,$2,$3)", before.name, int(datetime.datetime.now().timestamp()), before.id)
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        check = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = $1 AND banned = $2", guild.id, user.id)
        if check: await guild.ban(user, reason=f"hardbanned by {await self.bot.fetch_user(check['author'])}")
    
    @commands.Cog.listener('on_member_remove')
    async def booster_left(self, member: discord.Member): 
      if member.guild.id == 1060502285383376916:
         if member.guild.premium_subscriber_role in member.roles: 
            check = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(member.id))
            if check is not None: await self.bot.db.execute("DELETE FROM donor WHERE user_id = {}".format(member.id))   

    @commands.Cog.listener('on_member_update')
    async def booster_unboosted(self, before: discord.Member, after: discord.Member): 
      if before.guild.id == 1060502285383376916:
       if before.guild.premium_subscriber_role in before.roles and not before.guild.premium_subscriber_role in after.roles:
         check = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(before.id))
         if check is not None: return await self.bot.db.execute("DELETE FROM donor WHERE user_id = {}".format(before.id))   
    
async def setup(bot):
    await bot.add_cog(Users(bot))