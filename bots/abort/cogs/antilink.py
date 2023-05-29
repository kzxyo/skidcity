import discord, asyncio, aiohttp, random, button_paginator as pg 
from discord.ext import commands 
from cogs.events import commandhelp
from utils.classes import Colors, Emojis

def check_whitelist():
 async def predicate(ctx: commands.Context):
   if ctx.guild is None: return 
   if ctx.author.id == ctx.guild.owner.id: return True
   async with ctx.bot.db.cursor() as cursor: 
    await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
    check = await cursor.fetchone()
    if check is None: 
       await ctx.reply(embed=discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: You are not whitelisted"), mention_author=False)
       return False
    return check is not None
 return commands.check(predicate)   

def check_owner():
  async def predicate(ctx: commands.Context):
    if ctx.guild is None: return False
    if ctx.author.id != ctx.guild.owner.id:
      await ctx.reply(embed=discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: Only the server owner can use this command"), mention_author=False)
      return False  
    return ctx.author.id == ctx.guild.owner.id  
  return commands.check(predicate)    

class Antinuke(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
    
    @commands.Cog.listener()
    async def on_ready(self):
      async with self.bot.db.cursor() as cursor: 
       await cursor.execute("CREATE TABLE IF NOT EXISTS antinuke (guild_id INTEGER, module TEXT, punishment TEXT)")
       await cursor.execute("CREATE TABLE IF NOT EXISTS whitelist (guild_id INTEGER, user_id INTEGER)")
      await self.bot.db.commit() 

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.Member): 
     async with self.bot.db.cursor() as cursor: 
       await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'ban'".format(guild.id)) 
       check = await cursor.fetchone()   
       if check is not None: 
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban): 
          if entry.user.top_role.position >= guild.get_member(self.bot.user.id).top_role.position: return   
          await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(guild.id, entry.user.id))
          chec = await cursor.fetchone()
          if chec is None: 
            punishment = check[2]
            try:
             if punishment == "ban": 
                await entry.user.ban(reason="AntiNuke: banning people")
             elif punishment == "kick": 
                await entry.user.kick(reason="AntiNuke: banning people")
             elif punishment == "strip": 
               for role in entry.user.roles: 
                if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                  try:
                   if role.is_bot_managed(): 
                        await role.edit(permissions=discord.Permissions.none())
                        continue
                   else:
                    async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                      async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                       if r.status == 429:
                        await asyncio.sleep(3)
                  except: continue               
            except: pass 

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member): 
     async with self.bot.db.cursor() as cursor: 
       await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'kick'".format(member.guild.id)) 
       check = await cursor.fetchone()   
       if check is not None: 
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick): 
          if entry.user.top_role.position >= member.guild.get_member(self.bot.user.id).top_role.position: return
          await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(member.guild.id, entry.user.id))
          chec = await cursor.fetchone()
          if chec is None: 
            punishment = check[2]
            try:
             if punishment == "ban": 
                await entry.user.ban(reason="AntiNuke: kicking people")
             elif punishment == "kick": 
                await entry.user.kick(reason="AntiNuke: kicking people")
             elif punishment == "strip": 
               for role in entry.user.roles: 
                if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                  try:
                   if role.is_bot_managed(): 
                        await role.edit(permissions=discord.Permissions.none())
                        continue
                   else:
                    async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                      async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{member.guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                       if r.status == 429:
                        await asyncio.sleep(3)
                  except: continue               
            except: pass   
    
    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild): 
      if str(before.vanity_url_code) != str(after.vanity_url_code): 
       if before.vanity_url_code is None: return
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'vanity'".format(before.id))
        check = await cursor.fetchone()  
        if check is not None: 
          async for entry in before.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
            if entry.user.top_role.position >= before.get_member(self.bot.user.id).top_role.position: return
            await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(before.id, entry.user.id))
            chec = await cursor.fetchone()
            if chec is None: 
              await before.edit(vanity_code=before.vanity_url_code)
              punishment = check[2]
              try:
               if punishment == "ban": 
                await entry.user.ban(reason="AntiNuke: changing vanity")
               elif punishment == "kick": 
                await entry.user.kick(reason="AntiNuke: changing vanity")
               elif punishment == "strip": 
                for role in entry.user.roles: 
                 if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                  try:
                   if role.is_bot_managed(): 
                        await role.edit(permissions=discord.Permissions.none())
                        continue
                   else:
                    async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                      async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{before.id}/members/{entry.user.id}/roles/{role.id}") as r:
                       if r.status == 429:
                        await asyncio.sleep(3)
                  except: continue               
              except: pass   

    @commands.Cog.listener()
    async def on_guild_role_delete(self, rol: discord.Role):
     async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'roledelete'".format(rol.guild.id))
        check = await cursor.fetchone()  
        if check is not None: 
          async for entry in rol.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if entry.user.top_role.position >= rol.guild.get_member(self.bot.user.id).top_role.position: return
            await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(rol.guild.id, entry.user.id))
            chec = await cursor.fetchone()
            if chec is None: 
              punishment = check[2]
              try:
               if punishment == "ban": 
                await entry.user.ban(reason="AntiNuke: deleting roles")
               elif punishment == "kick": 
                await entry.user.kick(reason="AntiNuke: deleting roles")
               elif punishment == "strip": 
                for role in entry.user.roles: 
                 if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                  try:
                   if role.is_bot_managed(): 
                        await role.edit(permissions=discord.Permissions.none())
                        continue
                   else:
                    async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                      async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{role.guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                       if r.status == 429:
                        await asyncio.sleep(3)
                  except: continue               
              except: pass    
   
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel): 
      async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'channeldelete'".format(channel.guild.id))
        check = await cursor.fetchone()
        if check is not None: 
         async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if entry.user.top_role.position >= channel.guild.get_member(self.bot.user.id).top_role.position: return
            await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(channel.guild.id, entry.user.id))
            chec = await cursor.fetchone()
            if chec is None: 
              punishment = check[2]
              try:
               if punishment == "ban": 
                await entry.user.ban(reason="AntiNuke: deleting channels")
               elif punishment == "kick": 
                await entry.user.kick(reason="AntiNuke: deleting channels")
               elif punishment == "strip": 
                for role in entry.user.roles: 
                 if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                  try:
                   if role.is_bot_managed(): 
                        await role.edit(permissions=discord.Permissions.none())
                        continue
                   else:
                    async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                      async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{channel.guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                       if r.status == 429:
                        await asyncio.sleep(3)
                  except: continue               
              except: pass    

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role): 
      if before.position >= before.guild.get_member(self.bot.user.id).top_role.position and after.position >= after.guild.get_member(self.bot.user.id).top_role.position: return 
      async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {} AND module = 'roleupdate'".format(before.guild.id))
        check = await cursor.fetchone()
        if check is not None: 
          async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if entry.user.top_role.position >= before.guild.get_member(self.bot.user.id).top_role.position: return
            await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(before.guild.id, entry.user.id))
            chec = await cursor.fetchone()
            if chec is None:
              if before.permissions != after.permissions: 
                await after.edit(permissions=before.permissions)
              elif before.mentionable != after.mentionable: 
                await after.edit(mentionable=before.mentionable)
              punishment = check[2]
              try:
               if punishment == "ban": 
                await entry.user.ban(reason="AntiNuke: updating roles")
               elif punishment == "kick": 
                await entry.user.kick(reason="AntiNuke: updating roles")
               elif punishment == "strip": 
                for role in entry.user.roles: 
                 if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
                  try:
                   if role.is_bot_managed(): 
                        await role.edit(permissions=discord.Permissions.none())
                        continue
                   else:
                    async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
                      async with cs.delete(f"https://discord.com/api/v{random.randint(6,8)}/guilds/{before.guild.id}/members/{entry.user.id}/roles/{role.id}") as r:
                       if r.status == 429:
                        await asyncio.sleep(3)
                  except: continue               
              except: pass     
    
    @commands.group(aliases=["wl"], invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_owner()
    async def whitelist(self, ctx): 
      embed = discord.Embed(color=Colors.default, title="group command: whitelist", description="whitelist your trusted members to prevent them being detected by the antinuke")
      embed.set_thumbnail(url=self.bot.user.display_avatar.url)
      embed.add_field(name="commands", value=">>> whitelist add - whitelist an user\nwhitelist remove - removes an user from whitelist\nwhitelist list - check whitelisted members", inline=False)
      embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
      embed.set_footer(text="aliases: wl")
      await ctx.reply(embed=embed, mention_author=False)

    @whitelist.command(help="see whitelisted members", description="antinuke")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    async def list(self, ctx): 
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {}".format(ctx.guild.id))
            results = await cursor.fetchall()
            if len(results) == 0:
                return await ctx.reply("there are no whitelisted members")
            for result in results:
              mes = f"{mes}`{k}` {await self.bot.fetch_user(result[1])}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=Colors.default, title=f"whitelisted ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = discord.Embed(color=Colors.default, title=f"whitelisted ({len(results)})", description=messages[i])
            number.append(embed)
            if len(number) > 1:
             paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
             paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
             paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
             paginator.add_button('next', emoji="<:right:1018156484170883154>")
             await paginator.start()
            else:
             await ctx.send(embed=embed) 
    
    @whitelist.command(help="whitelist a member", usage="[member]", description="antinuke")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_owner()
    async def add(self, ctx: commands.Context, *, member: discord.Member=None): 
      if member is None: await commandhelp(self, ctx, "whitelist add")
      async with ctx.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
        check = await cursor.fetchone()
        if check is not None: return await ctx.reply(embed=discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention}: This user is already whitelisted"), mention_author=False)
        await cursor.execute("INSERT INTO whitelist VALUES (?,?)", (ctx.guild.id, member.id))
        await self.bot.db.commit()
        await ctx.reply(embed=discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention}: Whitelisted {member.mention}"), mention_author=False)
    
    @whitelist.command(help="remove an user from whitelist", description="antinuke")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_owner()
    async def remove(self, ctx, *, member: discord.Member):
      if member is None: await commandhelp(self, ctx, "whitelist remove")
      async with ctx.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM whitelist WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
        check = await cursor.fetchone()
        if check is None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: This user is not whitelisted"), mention_author=False)
        await cursor.execute("DELETE FROM whitelist WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
        await self.bot.db.commit()
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Removed whitelist from {member.mention}"), mention_author=False)

    @commands.group(aliases=["an"], invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    async def antinuke(self, ctx): 
      embed = discord.Embed(color=Colors.default, title="group command: antinuke", description="protect your server against nukes and raids")
      embed.set_thumbnail(url=self.bot.user.display_avatar.url)
      embed.add_field(name="commands", value=">>> antinuke settings - returns stats of server's antinuke\nantinuke vanity - toggle anti vanity change module\nantinuke ban - toggle anti ban module\nantinuke kick - toggle anti kick module\nantinuke channel - toggle anti channel delete antinuke\nantinuke roledelete - toggle anti role delete module\nantinuke roleupdate - toggle anti role update module", inline=False)
      embed.add_field(name="punishments", value=">>> ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action", inline=False)
      embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
      embed.set_footer(text="aliases: an")
      await ctx.reply(embed=embed, mention_author=False)
    
    @antinuke.command(help="returns stats of server's antinuke", description="antinuke")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    async def settings(self, ctx): 
      vanity = "<:icons_off:1059889872258727976>"
      ban = "<:icons_off:1059889872258727976>"
      kick = "<:icons_off:1059889872258727976>"
      channel = "<:icons_off:1059889872258727976>"
      roleupdate = "<:icons_off:1059889872258727976>"
      roledelete = "<:icons_off:1059889872258727976>"
      async with self.bot.db.cursor() as cursor: 
         await cursor.execute("SELECT * FROM antinuke WHERE guild_id = {}".format(ctx.guild.id))
         results = await cursor.fetchall()
         for result in results: 
           if result[1] == "vanity": vanity = "<:icons_on:1059889890378141787>"
           elif result[1] == "ban": ban = "<:icons_on:1059889890378141787>"  
           elif result[1] == "kick": kick = "<:icons_on:1059889890378141787>"
           elif result[1] == "channeldelete": channel = "<:icons_on:1059889890378141787>"
           elif result[1] == "roleupdate": roleupdate = "<:icons_on:1059889890378141787>"
           elif result[1] == "roledelete": roledelete = "<:icons_on:1059889890378141787>"

         embed = discord.Embed(color=Colors.default, title="antinuke settings")
         embed.set_thumbnail(url=ctx.guild.icon.url or "")
         embed.add_field(name="vanity", value=vanity)
         embed.add_field(name="ban", value=ban)
         embed.add_field(name="kick", value=kick)
         embed.add_field(name="channel delete", value=channel)
         embed.add_field(name="role update", value=roleupdate)
         embed.add_field(name="role delete", value=roledelete)
         await ctx.reply(embed=embed, mention_author=False)
         
    @antinuke.command(help="toggle anti vanity update module", description="antinuke", usage="[subcommand] [punishment]", brief="antinuke vanity set - sets anti vanity update module\nantinuke vanity unset - unsets anti vanity update module")     
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    async def vanity(self, ctx: commands.Context, option=None, punishment=None):
      if option is None: return await commandhelp(self, ctx, "antinuke vanity")
      if option.lower() == "set":
       if option is None or punishment is None: return await commandhelp(self, ctx, "antinuke vanity") 
       if not punishment.lower() in ["ban", "kick", "strip"]: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between ban, kick or strip"), mention_author=False)
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
        check = await cursor.fetchone()
        if check is not None: return await ctx.reply(embed=discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention}: Anti vanity update module is already configured"), mention_author=False)
        await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, ctx.command.name, punishment))
        await self.bot.db.commit()
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Added anti vanity update module"), mention_author=False)
      elif option.lower() == "unset": 
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
        check = await cursor.fetchone()
        if check is None: return await ctx.reply(embed=discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: Anti vanity update module is not configured"), mention_author=False)  
        await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Removed anti vanity update module"), mention_author=False)

    @antinuke.command(help="toggle anti ban module", description="antinuke", usage="[subcommand] [punishment]", brief="antinuke ban set - sets anti ban module\nantinuke ban unset - unsets anti ban module")     
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    async def ban(self, ctx: commands.Context, option=None, punishment=None):
      if option is None: return await commandhelp(self, ctx, "antinuke ban")
      if option.lower() == "set":
       if option is None or punishment is None: return await commandhelp(self, ctx, "antinuke ban") 
       if not punishment.lower() in ["ban", "kick", "strip"]: return await ctx.reply(embed=discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between ban, kick or strip"), mention_author=False)
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
        check = await cursor.fetchone()
        if check is not None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti ban module is already configured"), mention_author=False)
        await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, ctx.command.name, punishment))
        await self.bot.db.commit()
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Added anti ban module"), mention_author=False)
      elif option.lower() == "unset": 
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
        check = await cursor.fetchone()
        if check is None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti ban is not configured"), mention_author=False)  
        await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Removed anti vaniy module"), mention_author=False)

    @antinuke.command(help="toggle anti kick module", description="antinuke", usage="[subcommand] [punishment]", brief="antinuke kick set - sets anti kick module\nantinuke kick unset - unsets anti kick module")     
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    async def kick(self, ctx: commands.Context, option=None, punishment=None):
      if option is None: return await commandhelp(self, ctx, "antinuke kick")
      if option.lower() == "set":
       if option is None or punishment is None: return await commandhelp(self, ctx, "antinuke kick") 
       if not punishment.lower() in ["ban", "kick", "strip"]: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between kick, kick or strip"), mention_author=False)
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
        check = await cursor.fetchone()
        if check is not None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti kick module is already configured"), mention_author=False)
        await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, ctx.command.name, punishment))
        await self.bot.db.commit()
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Added anti kick module"), mention_author=False)
      elif option.lower() == "unset": 
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
        check = await cursor.fetchone()
        if check is None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti kick is not configured"), mention_author=False)  
        await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}'")
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Removed anti vaniy module"), mention_author=False)
    
    @antinuke.command(help="toggle anti channel delete module", description="antinuke", usage="[subcommand] [punishment]", brief="antinuke channel set - sets anti channel delete module\nantinuke channel unset - unsets anti channel delete module")     
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    async def channel(self, ctx: commands.Context, option=None, punishment=None):
      if option is None: return await commandhelp(self, ctx, "antinuke channel")
      if option.lower() == "set":
       if option is None or punishment is None: return await commandhelp(self, ctx, "antinuke channel") 
       if not punishment.lower() in ["ban", "kick", "strip"]: return await ctx.reply(embed=discord.Embed(color=Colors.red, description=f"{Emojis.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between channel, channel or strip"), mention_author=False)
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}delete'")
        check = await cursor.fetchone()
        if check is not None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti channel delete module is already configured"), mention_author=False)
        await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, ctx.command.name+"delete", punishment))
        await self.bot.db.commit()
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Added anti channel delete module"), mention_author=False)
      elif option.lower() == "unset": 
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}delete'")
        check = await cursor.fetchone()
        if check is None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti channel delete is not configured"), mention_author=False)  
        await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = '{ctx.command.name}delete'")
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Removed anti channel delete module"), mention_author=False)
   
    @antinuke.command(help="toggle anti role delete module", description="antinuke", usage="[subcommand] [punishment]", brief="antinuke role set - sets anti role delete module\nantinuke role unset - unsets anti role delete module")     
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    async def roledelete(self, ctx: commands.Context, option=None, punishment=None):
      if option is None: return await commandhelp(self, ctx, "antinuke roledelete")
      if option.lower() == "set":
       if option is None or punishment is None: return await commandhelp(self, ctx, "antinuke roledelete") 
       if not punishment.lower() in ["ban", "kick", "strip"]: return await ctx.reply(embed=discord.Embed(color=Colors.red, description=f"{Emojis.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between role, role or strip"), mention_author=False)
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roledelete'")
        check = await cursor.fetchone()
        if check is not None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti role delete module is already configured"), mention_author=False)
        await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, "roledelete", punishment))
        await self.bot.db.commit()
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Added anti role delete module"), mention_author=False)
      elif option.lower() == "unset": 
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roledelete'")
        check = await cursor.fetchone()
        if check is None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti role delete is not configured"), mention_author=False)  
        await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roledelete'")
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Removed anti role delete module"), mention_author=False)

    @antinuke.command(help="toggle anti role update module", description="antinuke", usage="[subcommand] [punishment]", brief="antinuke role set - sets anti role update module\nantinuke role unset - unsets anti role update module")     
    @commands.cooldown(1, 2, commands.BucketType.user)
    @check_whitelist()
    async def roleupdate(self, ctx: commands.Context, option=None, punishment=None):
      if option is None: return await commandhelp(self, ctx, "antinuke roleupdate")
      if option.lower() == "set":
       if option is None or punishment is None: return await commandhelp(self, ctx, "antinuke roleupdate") 
       if not punishment.lower() in ["ban", "kick", "strip"]: return await ctx.reply(embed=discord.Embed(color=Colors.red, description=f"{Emojis.warning} {ctx.author.mention}: **{punishment}** is an invalid punishment. Please choose between role, role or strip"), mention_author=False)
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roleupdate'")
        check = await cursor.fetchone()
        if check is not None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti role update module is already configured"), mention_author=False)
        await cursor.execute("INSERT INTO antinuke VALUES (?,?,?)", (ctx.guild.id, "roleupdate", punishment))
        await self.bot.db.commit()
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Added anti role update module"), mention_author=False)
      elif option.lower() == "unset": 
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute(f"SELECT * FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roleupdate'")
        check = await cursor.fetchone()
        if check is None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: Anti role update is not configured"), mention_author=False)  
        await cursor.execute(f"DELETE FROM antinuke WHERE guild_id = {ctx.guild.id} AND module = 'roleupdate'")
        await ctx.reply(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: Removed anti role update module"), mention_author=False)

async def setup(bot):
    await bot.add_cog(Antinuke(bot))        