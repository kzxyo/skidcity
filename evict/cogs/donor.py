import discord
from discord.ext import commands
from typing import Union
from patches.permissions import Permissions

class donor(commands.Cog):
  def __init__(self, bot: commands.Bot):
      self.bot = bot
  
  @commands.command(description="revoke the hardban from an user", usage="[user]", brief="donor & administrator")
  @Permissions.has_permission(administrator=True)
  async def hardunban(self, ctx: commands.Context, *, member: discord.User):     
    
    che = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = {} AND banned = {}".format(ctx.guild.id, member.id))      
    if che is None: return await ctx.warning(f"{member} is **not** hardbanned.") 
    
    await self.bot.db.execute("DELETE FROM hardban WHERE guild_id = {} AND banned = {}".format(ctx.guild.id, member.id))
    
    await ctx.guild.unban(member, reason="unhardbanned by {}".format(ctx.author)) 
    await ctx.success(f"I have **successfully** unhardbanned {member.name}.")

  @commands.command(description="hardban a user from the server", usage="[user]", brief="donor & administrator")
  @Permissions.has_permission(administrator=True)
  async def hardban(self, ctx: commands.Context, member: Union[discord.Member, discord.User], reason: str='No Reason Provided'):
      
      if isinstance(member, discord.Member) and not Permissions.check_hierarchy(self.bot, ctx.author, member): return await ctx.warning(f"You cannot hardban*{member.mention}")
      
      che = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = {} AND banned = {}".format(ctx.guild.id, member.id))
      if che is not None: 
        return await ctx.warning(f"**{member}** has been hardbanned by **{await self.bot.fetch_user(che['author'])}**.")
      
      await self.bot.db.execute("INSERT INTO hardban VALUES ($1,$2,$3)", ctx.guild.id, member.id, ctx.author.id)
      
      await ctx.guild.ban(member, reason=reason + " | {}".format(ctx.author))
      await ctx.success(f"I have **successfully** hardbanned {member.mention}.")
    
  @Permissions.has_permission(administrator=True)
  @commands.command(aliases=["hardbanlist"], description="check hardban list", brief='donor & administrator')
  async def hardbanned(self, ctx: commands.Context): 
          
          results = await self.bot.db.fetch("SELECT * FROM hardban WHERE guild_id = $1", ctx.guild.id)
          
          if len(results) == 0: return await ctx.warning("No **hardbanned** members found.")
              
          hardban_list = [f"``{index + 1}.`` {await self.bot.fetch_user(result['banned'])} (``{result['banned']}``)" 
                          for index, result in enumerate(results)]
          
          await ctx.paginate(hardban_list, f"hardban list [{len(results)}]")
        
  @commands.command(description="uwuify a person's messages", usage="[member]", brief="donor & manage messages")
  @Permissions.has_permission(manage_messages=True)
  async def uwulock(self, ctx: commands.Context, *, member: discord.Member):
    
    if isinstance(member, discord.Member) and not Permissions.check_hierarchy(self.bot, ctx.author, member): return await ctx.warning(f"You **cannot** uwulock*{member.mention}.")
    
    if member.id == ctx.bot.user.id: return await ctx.warning("I **cannot** uwulock myself.")
    
    check = await self.bot.db.fetchrow("SELECT user_id FROM uwulock WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))
    check1 = await self.bot.db.fetchrow("SELECT user_id FROM guwulock WHERE user_id = {}".format(member.id))
    
    if check1 is not None: return await ctx.warning(f"**{member}** is already globaluwulocked, this must be removed by bot owner.")
    if check is None: await self.bot.db.execute("INSERT INTO uwulock VALUES ($1,$2)", ctx.guild.id, member.id)
    
    else: await self.bot.db.execute("DELETE FROM uwulock WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))    
    return await ctx.message.add_reaction("<:approve:1263726951613464627>")
  
  @Permissions.has_permission(manage_messages=True)
  @commands.command(aliases=["uwulocklist"], description="check uwulock list", brief='donor & manage messages')
  async def uwulocked(self, ctx: commands.Context): 
          
          results = await self.bot.db.fetch("SELECT * FROM uwulock WHERE guild_id = $1", ctx.guild.id)
          
          if len(results) == 0: return await ctx.warning("No **uwulocked** members found.")
              
          uwulock_list = [f"``{index + 1}.`` {await self.bot.fetch_user(result['user_id'])} (``{result['user_id']}``)" 
                          for index, result in enumerate(results)]
          
          await ctx.paginate(uwulock_list, f"uwulocked list [{len(results)}]")
  
  @Permissions.server_owner()
  @commands.command(description="remove everyone from uwulock", brief="donor & server owner")
  async def uwulockreset(self, ctx:commands.Context):
    
    check = await self.bot.db.fetchrow("SELECT guild_id FROM uwulock WHERE guild_id = {}".format(ctx.guild.id))
    if check is None: return await ctx.warning("There is **no one** in uwulock.")
    
    else: await self.bot.db.execute("DELETE FROM uwulock WHERE guild_id = {}".format(ctx.guild.id))
    await ctx.success("I have **successfully** removed everyone from uwulock.")
  
  @Permissions.server_owner()
  @commands.command(description="remove everyone from hardban", brief="donor & server owner")
  async def hardbanreset(self, ctx:commands.Context):
    
    check = await self.bot.db.fetchrow("SELECT guild_id FROM hardban WHERE guild_id = {}".format(ctx.guild.id))
    if check is None: return await ctx.warning("There is **no one** in hardban.")
    
    else: await self.bot.db.execute("DELETE FROM hardban WHERE guild_id = {}".format(ctx.guild.id))
    await ctx.success("I have **successfully** removed everyone from hardban.")

  @commands.command(aliases=['stfu'], description="delete a person's messages", usage="[member]", brief="donor & manage messages")
  @Permissions.has_permission(manage_messages=True)
  async def shutup(self, ctx: commands.Context, *, member: discord.Member):
    
    if isinstance(member, discord.Member) and not Permissions.check_hierarchy(self.bot, ctx.author, member): return await ctx.warning(f"You cannot shutup*{member.mention}")
    if member.id == ctx.bot.user.id: return await ctx.warning("Do not shutup me.")
    
    check = await self.bot.db.fetchrow("SELECT user_id FROM shutup WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))    
    if check is None: await self.bot.db.execute("INSERT INTO shutup VALUES ($1,$2)", ctx.guild.id, member.id)
    
    else: await self.bot.db.execute("DELETE FROM shutup WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))    
    return await ctx.message.add_reaction("<:approve:1263726951613464627>")
  
  @Permissions.server_owner()
  @commands.command(aliases=["stfureset"], description="remove everyone from uwulock", brief="donor & server owner")
  async def shutupreset(self, ctx:commands.Context):
    
    check = await self.bot.db.fetchrow("SELECT guild_id FROM shutup WHERE guild_id = {}".format(ctx.guild.id))
    if check is None: return await ctx.warning("There is **no one** in uwulock.")
    
    else: await self.bot.db.execute("DELETE FROM shutup WHERE guild_id = {}".format(ctx.guild.id))
    await ctx.success("I have **successfully** removed everyone from uwulock.")
    
  @Permissions.has_permission(manage_messages=True)
  @commands.command(aliases=["stfulist"], description="check shutup list", brief="donor & manage messages")
  async def shutuplist(self, ctx: commands.Context): 
       
       results = await self.bot.db.fetch("SELECT * FROM shutup WHERE guild_id = $1", ctx.guild.id)
          
       if len(results) == 0: return await ctx.warning("No **uwulocked** members found.")
              
       shutup_list = [f"``{index + 1}.`` {await self.bot.fetch_user(result['user_id'])} (``{result['user_id']}``)" 
                          for index, result in enumerate(results)]
          
       await ctx.paginate(shutup_list, f"shutup list [{len(results)}]")

  @commands.command(description="force nickname a user", usage="[member] [nickname]", aliases=["locknick", "fn"], brief="manage nicknames & donor")
  @Permissions.has_permission(manage_nicknames=True)
  async def forcenick(self, ctx: commands.Context, member: discord.Member, *, nick: str=None): 
    
    if isinstance(member, discord.Member) and not Permissions.check_hierarchy(self.bot, ctx.author, member): return await ctx.warning(f"You **cannot** forcenick*{member.mention}.")
    
    if nick is None:
      
      check = await self.bot.db.fetchrow("SELECT * FROM forcenick WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))
      if check is None: return await ctx.warning(f"**No** forcenick found for {member}.")
      
      await self.bot.db.execute("DELETE FROM forcenick WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))              
      await member.edit(nick=None, reason='forcenick disabled')
      await ctx.success(f"I have **successfully** removed the forcenick for {member.mention}.")
    
    else: 
      
      check = await self.bot.db.fetchrow("SELECT * FROM forcenick WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))               
      if check is None: await self.bot.db.execute("INSERT INTO forcenick VALUES ($1,$2,$3)", ctx.guild.id, member.id, nick)
      
      else: await self.bot.db.execute("UPDATE forcenick SET nickname = '{}' WHERE user_id = {} AND guild_id = {}".format(nick, member.id, ctx.guild.id))  
      
      await member.edit(nick=nick, reason='forcenick enabled')
      await ctx.success(f"**successfully** added the forcenick for {member.mention}")
    
  @commands.cooldown(1, 60, commands.BucketType.guild)
  @commands.command(aliases=["fnclear"], description="clear everyone's forcenickname", brief="donor & administrator")
  @Permissions.has_permission(administrator=True)
  async def forcenickclear(self, ctx: commands.Context):
    
    await self.bot.db.execute("DELETE FROM forcenick WHERE guild_id = {}".format(ctx.guild.id))
    await ctx.success("I have **cleared** everyone from forcenick.")

  @commands.command(description="purges an amount of messages sent by you", usage="[amount]", brief="donor")
  async def selfpurge(self, ctx: commands.Context, amount: int):
    
    mes = [] 
    
    async for message in ctx.channel.history(): 
      
      if (len(mes) == amount+1): break 
      if message.author == ctx.author: mes.append(message)
          
    await ctx.channel.delete_messages(mes)   

  @commands.group(invoke_without_command=True, name="reskin", description="customize evicts output embeds")    
  async def reskin(self, ctx: commands.Context):
    return await ctx.create_pages()
  
  @reskin.command(name="enable", description="customize evicts output embeds", aliases=['on'], brief="donor")
  async def reskin_enable(self, ctx: commands.Context):
    
    reskin = await self.bot.db.fetchrow("SELECT * FROM reskin WHERE user_id = $1 AND toggled = $2", ctx.author.id, False)
    
    if reskin == None or reskin['toggled'] == False:   
      
      if not await self.bot.db.fetchrow("SELECT * FROM reskin WHERE user_id = $1", ctx.author.id):
        await self.bot.db.execute("INSERT INTO reskin (user_id, toggled, name, avatar) VALUES ($1, $2, $3, $4)", ctx.author.id, True, ctx.author.name, ctx.author.avatar.url)
      
      else:   
        await self.bot.db.execute("UPDATE reskin SET toggled = $1 WHERE user_id = $2", True, ctx.author.id)
      
      return await ctx.success("**Reskin** has been **enabled**.")
      
    return await ctx.warning("**Reskin** is already **enabled**.")
  
  @reskin.command(name="disable", description="disable the customization output messages", aliases=['off'], brief="donor")
  async def reskin_disable(self, ctx: commands.Context):
    reskin = await self.bot.db.fetchrow("SELECT * FROM reskin WHERE user_id = $1 AND toggled = $2", ctx.author.id, True)
    
    if reskin != None and reskin['toggled'] == True:   
      
      await self.bot.db.execute("UPDATE reskin SET toggled = $1 WHERE user_id = $2", False, ctx.author.id)
      return await ctx.success("**Reskin** has been **disabled**.")
    
    await self.bot.db.execute("UPDATE reskin SET toggled = $1 WHERE user_id = $2", False, ctx.author.id)
    return await ctx.warning("**Reskin** is already **disabled**.")
  
  @reskin.command(name="name", description="change the name used on evicts output embeds", brief="donor")
  async def reskin_name(self, ctx: commands.Context, *, name: str=None):
    
    reskin = await self.bot.db.fetchrow("SELECT * FROM reskin WHERE user_id = $1", ctx.author.id)
    
    if not reskin:
      await self.bot.db.execute("INSERT INTO reskin (user_id, toggled, name, avatar) VALUES ($1, $2, $3, $4)", ctx.author.id, True, name, ctx.author.avatar.url)
    
    else:
      await self.bot.db.execute("UPDATE reskin SET name = $1 WHERE user_id = $2", name, ctx.author.id)
      
    if name == None or name.lower() == "none":
      return await ctx.success(f"I have set your **reskin** name to `{ctx.author.name}`.")

    return await ctx.success(f"I have set **reskin** name to `{name}`.")

  @reskin.command(name="avatar", description="change the icon used on evicts output embeds", aliases=['av'], brief="donor")
  async def reskin_avatar(self, ctx: commands.Context, url: str = None):
    
    if url == None and len(ctx.message.attachments) == 0:
      return await ctx.warning("you **need** to provide an avatar, either as a **file** or **url**")

    if url == None and len(ctx.message.attachments) > 0:
      url = ctx.message.attachments[0].url

    reskin = await self.bot.db.fetchrow("SELECT * FROM reskin WHERE user_id = $1", ctx.author.id)
    
    if not reskin:
      await self.bot.db.execute("INSERT INTO reskin (user_id, toggled, name, avatar) VALUES ($1, $2, $3, $4)", ctx.author.id, True, ctx.author.name, url)
    
    else:
      await self.bot.db.execute("UPDATE reskin SET avatar = $1 WHERE user_id = $2", url, ctx.author.id)
      
    return await ctx.success(f"I have set your **reskin** avatar to [**image**]({url}).")
  
  @commands.cooldown(1, 3, commands.BucketType.guild)
  @Permissions.has_permission(manage_webhooks=True)
  @commands.command(name='impersonate', aliases=['mock'], description='send a message as another user', brief='manage webhooks', usage='[user] [message]')
  async def impersonate(self, ctx, member: discord.Member, *, content):
      
      if member.id in self.bot.owner_ids: return await ctx.warning("you **cannot** mock a bot owner.")
      if member.id == ctx.bot.user.id: return await ctx.warning("you **cannot** mock me.")
      if member.id == ctx.guild.owner.id: return await ctx.warning("you **cannot** mock the server owner.")
      
      try:
          webhook = await ctx.channel.create_webhook(name=member.display_name, reason=f'{ctx.author} used mock command')
          
          await ctx.message.delete()
          await webhook.send(str(content), username=member.display_name, avatar_url=member.display_avatar.url)
          await webhook.delete(reason=f'{ctx.author} used mock command')
      
      except discord.HTTPException as e:
        await ctx.warning(f"an error occurred:\n {e}")

async def setup(bot) -> None:
    await bot.add_cog(donor(bot))               
