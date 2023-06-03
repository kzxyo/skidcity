import discord, aiohttp, random, humanfriendly, datetime, json, asyncio, button_paginator as pg
from cogs.events import commandhelp, noperms, blacklist, sendmsg
from humanfriendly import format_timespan
from discord.ui import Button, View
from backend.classes import Colors, Emojis
from discord.ext import commands
from typing import Union

datetime.datetime.now() 

class mod(commands.Cog):
   def __init__(self, bot):
        self.bot = bot
   
   @commands.Cog.listener()
   async def on_member_remove(self, member: discord.Member):
    async with self.bot.db.cursor() as cursor:
      await cursor.execute("SELECT user FROM nodata WHERE user = ?", (member.id,))
      data = await cursor.fetchone()
      if data: return
      list = []
      for role in member.roles:
       list.append(role.id)
    
      sql_as_text = json.dumps(list)
      sql = ("INSERT INTO restore VALUES(?,?,?)")
      val = (member.guild.id, member.id, sql_as_text)
      await cursor.execute(sql, val)
      await self.bot.db.commit()
   
   @commands.Cog.listener()
   async def on_ready(self): 
    async with self.bot.db.cursor() as cursor: 
      await cursor.execute("CREATE TABLE IF NOT EXISTS warns (guild_id INTEGER, user_id INTEGER, author_id INTEGER, time TEXT, reason TEXT)")
    await self.bot.db.commit()

   @commands.Cog.listener()
   async def on_message(self, message: discord.Message):
    if message.guild:
     async with self.bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM stfu WHERE guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id))
      results = await cursor.fetchone()
      if results is not None:
        await message.delete()

   @commands.command(help="role all users", usage="[subcommand] [target] [role]", description="moderation", brief="subcommands:\nremove - removes role from users\nadd - adds role to users\n\ntarget:\nhumans - targets human users\nbots - targets bot users\nall - targets all server users")
   @commands.cooldown(1, 10, commands.BucketType.guild)
   @blacklist()
   async def roleall(self, ctx: commands.Context, subcommand=None, target=None, *, role: discord.Role=None):
    if not ctx.author.guild_permissions.manage_roles: return await noperms(self, ctx, "manage_roles")
    if subcommand is None and target is None and role is None: 
      await commandhelp(self, ctx, ctx.command.name)
      return 
    if subcommand == "remove":
      if target == None or role == None:
        await commandhelp(self, ctx, ctx.command.name)
        return
      if target == "humans":
        embed = discord.Embed(color=Colors.default, description=f"{ctx.author.mention} removing {role.mention} from all humans....")
        message = await ctx.reply(embed=embed, mention_author=False)
        try:
         for member in ctx.guild.members: 
          if not member.bot:
            if not role in member.roles: continue
            async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
              async with cs.delete(f"https://discord.com/api/v{random.randint(6, 7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                if r.status == 429:
                  await asyncio.sleep(6)

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: removed {role.mention} from all {target}"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: unable to {subcommand} {role.mention} to all {target} - {e}"))  
      elif target == "bots": 
        embed = discord.Embed(color=Colors.default, description=f"{ctx.author.mention} removing {role.mention} from all bots....")
        message = await ctx.reply(embed=embed, mention_author=False)
        try:
         for member in ctx.guild.members: 
          if member.bot:
            if not role in member.roles: continue
            async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
              async with cs.delete(f"https://discord.com/api/v{random.randint(6, 7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                if r.status == 429:
                  await asyncio.sleep(6)

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: removed {role.mention} from all {target}"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: unable to {subcommand} {role.mention} to all {target} - {e}"))  
      elif target == "all": 
        embed = discord.Embed(color=Colors.default, description=f"{ctx.author.mention} removing {role.mention} to all members....")
        message = await ctx.reply(embed=embed, mention_author=False)
        try:
         for member in ctx.guild.members: 
            if not role in member.roles: continue
            async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
              async with cs.delete(f"https://discord.com/api/v{random.randint(6, 7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                if r.status == 429:
                  await asyncio.sleep(6)

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: removed {role.mention} from all"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: unable to {subcommand} {role.mention} to all - {e}"))  
    elif subcommand == "add":
      if target == None or role == None:
        await commandhelp(self, ctx, ctx.command.name)
        return
      if target == "humans":
        embed = discord.Embed(color=Colors.default, description=f"{ctx.author.mention} adding {role.mention} to all humans....")
        message = await ctx.reply(embed=embed, mention_author=False)
        try:
         for member in ctx.guild.members: 
          if not member.bot:
            if role in member.roles: continue
            async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
              async with cs.put(f"https://discord.com/api/v{random.randint(6, 7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                if r.status == 429:
                  await asyncio.sleep(6)

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: added {role.mention} from all {target}"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: unable to add {role.mention} to all {target} - {e}"))    
      elif target == "bots": 
        embed = discord.Embed(color=Colors.default, description=f"{ctx.author.mention} adding {role.mention} to all bots....")
        message = await ctx.reply(embed=embed, mention_author=False)
        try:
         for member in ctx.guild.members: 
          if member.bot:
            if role in member.roles: continue
            async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
              async with cs.put(f"https://discord.com/api/v{random.randint(6, 7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                if r.status == 429:
                  await asyncio.sleep(6)

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: added {role.mention} from all {target}"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: unable to add {role.mention} to all {target} - {e}"))    
      elif target == "all": 
        embed = discord.Embed(color=Colors.default, description=f"{ctx.author.mention} adding {role.mention} to all members....")
        message = await ctx.reply(embed=embed, mention_author=False)
        try:
         for member in ctx.guild.members: 
            if role in member.roles: continue
            async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
              async with cs.put(f"https://discord.com/api/v{random.randint(6, 7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                if r.status == 429:
                  await asyncio.sleep(6)

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: added {role.mention} from all"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: unable to add {role.mention} to all - {e}"))    
    else: return await commandhelp(self, ctx, ctx.command.name)
    
   @commands.command(help="restore member's roles", usage="[member]", description="moderation")
   @commands.cooldown(1, 10, commands.BucketType.guild)
   @blacklist()
   async def restore(self, ctx: commands.Context, *, member: discord.Member=None):
    if member == None:
      member = ctx.author
    async with ctx.message.channel.typing():
     async with self.bot.db.cursor() as cursor:
      if member == ctx.author: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description="{} {}: You can't restore your roles".format(Emojis.warning, ctx.author.mention)))
      await cursor.execute(f"SELECT * FROM restore WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")   
      result = await cursor.fetchone()
      if result is None:
        await sendmsg(self, ctx, None, discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: there are no roles saved for {member.mention}"), None, None, None)
        return 

      succeed = ""
      failed = "" 
      to_dump = json.loads(result[2])
      for roleid in to_dump: 
           try: 
            role = ctx.guild.get_role(roleid)
            if role.name == "@everyone":
              continue
            await member.add_roles(role)  
            succeed = f"{succeed} {role.mention}"
           except: 
            failed = f"{failed} <@&{roleid}>"
    
      if len(succeed) == 0:
        added = "none"
      else:
        added = succeed  

      if len(failed) == 0:
        fail = "none"
      else:
        fail = failed

      await cursor.execute(f"DELETE FROM restore WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
      await self.bot.db.commit()
      embed = discord.Embed(color=Colors.default, title="roles restored", description=f"target: {member.mention}")
      embed.set_thumbnail(url=member.display_avatar.url)
      embed.add_field(name="added", value=added, inline=False)
      embed.add_field(name="failed", value=fail, inline=False)
      await sendmsg(self, ctx, None, embed, None, None, None)
   
   @commands.group(invoke_without_command=True)
   @commands.cooldown(1, 3, commands.BucketType.user)
   @blacklist()
   async def warn(self, ctx): 
    embed = discord.Embed(color=Colors.default, title="warn", description="warn members in your server")
    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
    embed.add_field(name="usage", value="```warn [command] [member] <reason>```", inline=False)
    embed.add_field(name="commands", value="warn add - adds a warn to a member\nwarn remove - removes a warn from a member\nwarn list - returns a list of member's warns", inline=False)
    await ctx.reply(embed=embed, mention_author=False)

   @warn.command(help="warn a user", description="moderation", usage="[member] <reason>")
   @commands.cooldown(1, 3, commands.BucketType.user)
   @blacklist()
   async def add(self, ctx: commands.Context, member: discord.Member=None, *, reason: str=None): 
    if not ctx.author.guild_permissions.manage_messages: return await noperms(self, ctx, "manage_messages")
    if member is None: await commandhelp(self, ctx, "warn add") 
    if reason is None: reason = ""
    async with self.bot.db.cursor() as cursor:
      date = datetime.datetime.now()
      await cursor.execute("INSERT INTO warns VALUES (?,?,?,?,?)", (ctx.guild.id, member.id, ctx.author.id, f"{date.month}/{date.day}/{str(date.year)[-2:]} at " + {datetime.datetime.strptime(f"{date.hour}:{date.minute}", "%H:%M").strftime("%I:%M %p")}, reason))
      r = '- {}'.format(reason) if reason != "" else reason
      embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author}: warned {member.mention} {r}")
      await ctx.reply(embed=embed, mention_author=False)

   @warn.command(help="remove all warns from a user", description="moderation", usage="[member]")
   @commands.cooldown(1, 3, commands.BucketType.user)
   @blacklist()
   async def remove(self, ctx: commands.Context, *, member: discord.Member=None): 
    if not ctx.author.guild_permissions.manage_messages: return await noperms(self, ctx, "manage_messages")
    if member is None: await commandhelp(self, ctx, "warn remove")
    async with self.bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM warns WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))  
      check = await cursor.fetchall()  
      if check is None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: this user has no warnings"), mention_author=False)
      await cursor.execute("DELETE FROM warns WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
      await self.bot.db.commit()
      embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author}: removed all {member.mention}'s warns")
      await ctx.reply(embed=embed, mention_author=False)

   @warn.command(name="list", help="shows all warns of a user", description="moderation", usage="[member]") 
   @commands.cooldown(1, 3, commands.BucketType.user)
   @blacklist()
   async def xd(self, ctx: commands.Context, *, member: discord.Member): 
    if member is None: await commandhelp(self, ctx, "warn remove")
    async with self.bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM warns WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))  
      check = await cursor.fetchall()  
      if check is None: return await ctx.reply(embed=discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: this user has no warnings"), mention_author=False)
      i=0
      k=1
      l=0
      mes = ""
      number = []
      messages = []
      for result in check:
              mes = f"{mes}`{k}` {result[3]} by **{await self.bot.fetch_user(result[2])}** - {result[4]}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=Colors.default, title=f"whitelisted ({len(check)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
    messages.append(mes)
    embed = discord.Embed(color=Colors.default, title=f"whitelisted ({len(check)})", description=messages[i])
    number.append(embed)
    if len(number) > 1:
     paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
     paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
     paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
     paginator.add_button('next', emoji="<:right:1018156484170883154>")
     await paginator.start()
    else:
     await ctx.send(embed=embed) 

   @commands.command(aliases=["yeet"], help="ban a member", usage="[member] <reason>", description="moderation")
   @commands.cooldown(1, 10, commands.BucketType.guild)
   @blacklist()
   async def ban(self, ctx, member: Union[discord.Member, discord.User]=None, *, reason=None):
    if (not ctx.author.guild_permissions.ban_members):
     await noperms(self, ctx, "ban_members")
     return  

    if member == None:
       await commandhelp(self, ctx, ctx.command.name) 
       return 
    if isinstance(member, discord.Member):
     if member == ctx.message.author:
        e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: you cannot ban yourself")
        await sendmsg(self, ctx, None, e, None, None, None)
        return
    
     if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: you can't ban {member.mention}")
       await sendmsg(self, ctx, None, nope, None, None, None)
       return

     if reason == None:
        reason = "No reason provided"

     if ctx.guild.premium_subscriber_role in member.roles:
      button1 = Button(label="yes", style=discord.ButtonStyle.green)
      button2 = Button(label="no", style=discord.ButtonStyle.red)
      embed = discord.Embed(color=Colors.default, description=f"are you sure you want to ban {member.mention}? they are a server booster")
      async def button1_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=Colors.red, description=f"{interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        
        try: 
          await member.ban(reason=f"banned by {ctx.author} - {reason}")
          embe = discord.Embed(color=Colors.green, description=f"{Emojis.check} {member.mention} got banned - {reason}")
          await interaction.response.edit_message(embed=embe, view=None)  
        except:
         no = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: i don't have enough permissions to do this")
         await interaction.response.edit_message(embed=no, ephemeral=True, view=None)
      button1.callback = button1_callback

      async def button2_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return

        embe = discord.Embed(color=Colors.default, description=f"alright you changed your mind!")
        await interaction.response.edit_message(embed=embe, view=None)

      button2.callback = button2_callback

      view = View()
      view.add_item(button1)
      view.add_item(button2)
      await sendmsg(self, ctx, None, embed, view, None, None)       

     else:    
      try: 
       await member.ban(reason=f"banned by {ctx.author} - {reason}")
       embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {member.mention} got banned - {reason}")
       await sendmsg(self, ctx, None, embed, None, None, None)
      except:
        no = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: i don't have enough permissions to do this")
        await sendmsg(self, ctx, None,no, None, None, None)
    elif isinstance(member, discord.User):
      if reason == None:
        reason = "No reason provided"

      async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
        async with cs.put(f"https://discord.com/api/v9/guilds/{ctx.guild.id}/bans/{member.id}") as r:
            if r.status == 204:
                em = discord.Embed(color=Colors.green, description=f"{Emojis.check} {member.mention} got banned | {reason}")
                await sendmsg(self, ctx, None, em, None, None, None) 
            else: 
                em = discord.Embed(color=Colors.yellow, description=f"{Emojis.Emojis.warninging} {ctx.author.mention}: there was a problem banning this user {r.text}")    
                await sendmsg(self, ctx, None, None, None, None)

   @commands.command(help="unban an user", description="moderation", usage="[member]")
   @commands.cooldown(1, 3, commands.BucketType.user)
   @blacklist()
   async def unban(self, ctx, *, member: discord.User=None):
    if (not ctx.author.guild_permissions.ban_members):
     await noperms(self, ctx, "unban")
     return   

    if member == None:
       await commandhelp(self, ctx, "unban")
       return 
  
    try: 
     guild = ctx.guild
     embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: {member} has been unbanned")
     await guild.unban(user=member)
     await sendmsg(self, ctx, None, embed, None, None, None)
    except:
       emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: couldn't unban this member")
       await sendmsg(self, ctx, None, emb, None, None, None) 

   @commands.command(aliases=["setnick", "nick"], help="change an user's nickname", usage="[member] <nickname>", description="moderation")
   @commands.cooldown(1, 5, commands.BucketType.user)
   @blacklist()
   async def nickname(self, ctx, member: discord.Member=None, *, nick=None):
    if (not ctx.author.guild_permissions.manage_nicknames):
     await noperms(self, ctx, "manage_nicknames")
     return  

    if member == None:
       await commandhelp(self, ctx, ctx.command.name)
       return  

    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
        e = discord.Embed(color=Colors.yellow, description=f"{Emojis.Emojis.warninging} {ctx.author.mention}: can't change nickname to members with higher roles than yours")
        await sendmsg(self, ctx, None, e, None, None, None)
        return

    if nick == None or nick.lower() == "none":
       await member.edit(nick=None)
       embe = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: nickname cleared for {member.mention}")
       await sendmsg(self, ctx, None, embe, None, None, None)
       return

    try: 
     await member.edit(nick=nick)
     embe = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: changed {member.mention} nickname")
     await sendmsg(self, ctx, None, embe, None, None, None)
    except Exception as e:
       embed = discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: error occured while changing nickname - {e}")
       await sendmsg(self, ctx, None, embed, None, None, None)

   @commands.command(help="kick a member from the server", usage="[member] <reason>", description="moderation")
   @commands.cooldown(1, 10, commands.BucketType.guild)
   @blacklist()
   async def kick(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
    if (not ctx.author.guild_permissions.kick_members):
     await noperms(self, ctx, "kick_members")
     return   

    if member == None:
       await commandhelp(self, ctx, ctx.command.name) 

    if member == ctx.author:
     e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning}  {ctx.author.mention}: you can't kick yourserlf")
     await sendmsg(self, ctx, None, e, None, None, None)
     return

    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: you can't kick {member.mention}")
       await sendmsg(self, ctx, None, nope, None, None, None)
       return  
 
    if reason == None:
        reason = "No reason provided"

    if ctx.guild.premium_subscriber_role in member.roles:
     button1 = Button(label="yes", style=discord.ButtonStyle.green)
     button2 = Button(label="no", style=discord.ButtonStyle.red)
     embed = discord.Embed(color=Colors.default, description=f"are you sure you want to kick {member.mention}? they are a server booster")
     async def button1_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=Colors.red, description=f"{interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        
        try: 
          await member.kick(reason=f"kicked by {ctx.author} - {reason}")
          embe = discord.Embed(color=Colors.green, description=f"{Emojis.check} {member.mention} got kicked - {reason}")
          await interaction.response.edit_message(embed=embe, view=None)
        except:
         no = discord.Embed(color=Colors.red, description=f"{Emojis.warning} {ctx.author.mention}: i don't have enough permissions to do this")
         await interaction.response.edit_message(embed=no, mention_author=False)
     button1.callback = button1_callback

     async def button2_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return

        embe = discord.Embed(color=Colors.green, description=f"alright you changed your mind!")
        await interaction.response.edit_message(embed=embe, view=None)

     button2.callback = button2_callback

     view = View()
     view.add_item(button1)
     view.add_item(button2)
     await sendmsg(self, ctx, None, embed, view, None, None)     

    else:
        try: 
          await member.kick(reason=f"kicked by {ctx.author} - {reason}")
          await ctx.send(":thumbsup:")
        except:
         no = discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: i don't have enough permissions to do this")
         await sendmsg(self, ctx, None, no, None, None, None)    

   @commands.command(help="gives a role to a member", description="moderation", usage="[member] [role]")
   @commands.cooldown(1, 3, commands.BucketType.user) 
   @blacklist()
   async def role(self, ctx, user : discord.Member=None, *, role : discord.Role=None):
    if (not ctx.author.guild_permissions.manage_roles):
     await noperms(self, ctx, "manage_roles")
     return
  
    if role == None or user == None:
       await commandhelp(self, ctx, ctx.command.name)
       return 

    if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner.id: 
     e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: that role is above your top role")  
     return await sendmsg(self, ctx, None, e, None, None, None)
    if role in user.roles:
      await user.remove_roles(role)
      embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: removed {role.mention} from {user.mention}") 
      await sendmsg(self, ctx, None, embed, None, None, None)
    else:
      await user.add_roles(role)
      emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: {role.mention} to {user.mention}") 
      await sendmsg(self, ctx, None, emb, None, None, None)
   
   @commands.command(aliases=["sm"], help="add slowmode to a channel", description="moderation", usage="<channel>")
   @commands.cooldown(1, 3, commands.BucketType.user)
   @blacklist()
   async def slowmode(self, ctx, seconds: int=None, channel: discord.TextChannel=None):
    if (not ctx.author.guild_permissions.manage_channels):
     await noperms(self, ctx, "manage_channels")
     return 

    chan = channel or ctx.channel
    await chan.edit(slowmode_delay=seconds)
    em = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention} set slowmode time for {chan.mention} to **{seconds} seconds**")
    await sendmsg(self, ctx, None, em, None, None, None)

   @commands.command(help="lock a channel", description="moderation", usage="<channel>")
   @commands.cooldown(1, 4, commands.BucketType.user)
   @blacklist()
   async def lock(self, ctx, channel : discord.TextChannel=None):
    if (not ctx.author.guild_permissions.manage_roles):
     await noperms(self, ctx, "manage_roles")
     return 
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    e = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: locked {channel.mention}")
    await sendmsg(self, ctx, None, e, None, None, None)

   @commands.command(help="unlock a channel", description="moderation", usage="<channel>")
   @commands.cooldown(1, 4, commands.BucketType.user)
   @blacklist()
   async def unlock(self, ctx, channel : discord.TextChannel=None):
    if (not ctx.author.guild_permissions.manage_roles):
     await noperms(self, ctx, "manage_roles")
     return 

    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    e = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: unlocked {channel.mention}")
    await sendmsg(self, ctx, None, e, None, None, None)        

   @commands.command(aliases=["timeout"], help="mute a member", usage="[member] [time] [reason]", description="moderation")
   @commands.cooldown(1, 4, commands.BucketType.user)
   @blacklist()
   async def mute(self, ctx: commands.Context, member: discord.Member=None, time=None, *, reason=None):
    if (not ctx.author.guild_permissions.moderate_members):
     await noperms(self, ctx, "timeout_members")
     return     

    if member == None or time==None:
       await commandhelp(self, ctx, ctx.command.name)
       return

    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
        no = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: you can't timeout {member.mention}")
        await sendmsg(self, ctx, None, no, None, None, None)
        return
  
    if reason == None:
        reason = "No reason provided"

    try:
     time = humanfriendly.parse_timespan(time)
     await member.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=time), reason=reason)
     e = discord.Embed(color=Colors.green, description=f"{Emojis.check} {member.mention} has been muted for {format_timespan(time)} | {reason}")
     await sendmsg(self, ctx, None, e, None, None, None)
    except:
      emb = discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: i can't mute this member")  
      await sendmsg(self, ctx, None, emb, None, None, None)        
 
   @commands.command(help="unmute a member", usage="[member]", description="moderation")
   @commands.cooldown(1, 5, commands.BucketType.user)
   @blacklist()
   async def unmute(self, ctx, member: discord.Member=None):
    if (not ctx.author.guild_permissions.moderate_members):
     await noperms(self, ctx, "timeout_members")
     return     
    try: 
     if member == None:
       await commandhelp(self, ctx, ctx.command.name) 
       return

     await member.timeout(None, reason=f'unmuted by {ctx.author}')
     e = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention} unmuted {member.mention}")
     await sendmsg(self, ctx, None, e, None, None, None)
    except:
      emb = discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: i can't unmute this member")  
      await sendmsg(self, ctx, None, emb, None, None, None)                           

   @commands.command(help="removes all staff roles from a member", description="moderation", usage="[member]")
   @commands.cooldown(1, 5, commands.BucketType.user)
   @blacklist()
   async def stripstaff(self, ctx: commands.Context, member: discord.Member=None):
    if not ctx.author.guild_permissions.administrator:
        await noperms(self, ctx, "administrator")
        return
    if member == None:
        await commandhelp(self, ctx, ctx.command.name)
    else:
     if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: you can't strip {member.mention}'s roles")
       await sendmsg(self, ctx, None, nope, None, None, None)
       return
     async with ctx.channel.typing():  
      for role in member.roles:
        if role.permissions.administrator or role.permissions.ban_members or role.permissions.mention_everyone or role.permissions.moderate_members or role.permissions.manage_channels or role.permissions.manage_emojis_and_stickers or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_webhooks or role.permissions.deafen_members or role.permissions.move_members or role.permissions.mute_members or role.permissions.moderate_members:
          try:
            async with aiohttp.ClientSession(headers={"Authorization": f"Bot {self.bot.http.token}"}) as cs:
              async with cs.delete(f"https://discord.com/api/v{random.randint(6,7)}/guilds/{ctx.guild.id}/members/{member.id}/roles/{role.id}") as r:
                if r.status == 429:
                  await asyncio.sleep(1)
          except:
            continue

      embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: removed staff roles from {member.mention}")        
      await sendmsg(self, ctx, None, embed, None, None, None)

   @commands.command(help="bulk delete messages sent by bots", description="moderation", usage="[amount]", aliases=["bc", "botclear"])
   @commands.cooldown(1, 5, commands.BucketType.guild)
   @blacklist()
   async def botpurge(self, ctx: commands.Context, amount: int=None):
     if not ctx.author.guild_permissions.manage_messages:
      await noperms(self, ctx, "manage_messages")
      return 
     if amount is None:
        await commandhelp(self, ctx, ctx.command.name)
        return 
     await ctx.channel.purge(limit=amount, check=lambda msg: msg.author.bot)
     await ctx.message.delete() 
     await ctx.send("purged {} messages from bots".format(amount), delete_after=1)

   @commands.command(help="bulk delete messages", description="moderation", usage="[amount] <member>")
   @commands.cooldown(1, 5, commands.BucketType.guild)  
   @blacklist()
   async def purge(self, ctx: commands.Context, amount: int=None, *, member: discord.Member=None):
    if not ctx.author.guild_permissions.manage_messages:
      await noperms(self, ctx, "manage_messages")
      return 

    if amount is None:
      await commandhelp(self, ctx, ctx.command.name)
      return 

    if member is None:
      await ctx.message.delete()
      await ctx.channel.purge(limit=amount)  
      await ctx.send(f":thumbsup:", delete_after=2)
    elif member is not None:
      await ctx.message.delete()
      msg = []
      async for message in ctx.channel.history():
        if len(msg) == amount+1:
            break 
        else:
           if message.author == member: 
             msg.append(message)

      await ctx.channel.delete_messages(msg) 
      await ctx.send(f":thumbsup:", delete_after=2)
   
   @commands.command(help="auto delete member's messages", description="moderation", usage="[member]")
   @commands.cooldown(1, 6, commands.BucketType.user)
   @blacklist()
   async def stfu(self, ctx: commands.Context, member: discord.Member = None):
    if (not ctx.author.guild_permissions.moderate_members):
     await noperms(self, ctx, "timeout_members")
     return  
    if member == None:
        await commandhelp(self, ctx, ctx.command.name)
        return
    elif member == ctx.author:
        embed = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: you can't mute yourself")
        await sendmsg(self, ctx, None, embed, None, None, None)
        return
    elif member.top_role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner.id:
        embed = discord.Embed(color=Colors.yellow,description=f"{Emojis.warning} {ctx.author.mention}: you can't mute a member with higher roles than you")
        await sendmsg(self, ctx, None, embed, None, None, None)
        return        
    else: 
     async with self.bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM stfu WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
      results = await cursor.fetchone()
      if results is not None:
       e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: this member's messages are already getting deleted")
       await sendmsg(self, ctx, None, e, None, None, None)
       return
      elif results is None:
       sql = ("INSERT INTO stfu VALUES(?,?)")
       val = (member.id, ctx.guild.id)
       await cursor.execute(sql, val)     
       await ctx.message.add_reaction("<:catthumbsup:1059904302698746017>") 
       await self.bot.db.commit()

   @commands.command(help="stops the auto delete messages of a member", description="moderation", usage="[member]")
   @commands.cooldown(1, 6, commands.BucketType.user)
   @blacklist()
   async def unstfu(self, ctx, member: discord.Member=None):
    if (not ctx.author.guild_permissions.moderate_members):
     await noperms(self, ctx, "timeout_members")
     return  
    if member == None:
        await commandhelp(self, ctx, ctx.command.name)
        return
    elif member.top_role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner.id:
        embed = discord.Embed(color=Colors.yellow,description=f"{Emojis.warning} {ctx.author.mention}: you can't mute a member with higher roles than you")
        await sendmsg(self, ctx, None, embed, None, None, None)
        return        
    else:
     async with self.bot.db.cursor() as cursor:
      await cursor.execute("SELECT * FROM stfu WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
      results = await cursor.fetchone()
      if results is None:
        em = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: this user isn't muted")
        await sendmsg(self, ctx, None, em, None, None, None)
        return
      elif results is not None:
        await cursor.execute("DELETE FROM stfu WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
        await ctx.message.add_reaction("<:catthumbsup:1059904302698746017>")   
        await self.bot.db.commit()
   
async def setup(bot) -> None:
    await bot.add_cog(mod(bot))