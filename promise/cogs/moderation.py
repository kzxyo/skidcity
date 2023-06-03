import discord, aiohttp , aiosqlite, random
from discord.ext import commands 
from discord.ui import View, Button
from core.utils.classes import Colors
from cogs.events import commandhelp, sendmsg, noperms

class moderation(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
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

   @commands.command(help="role all users", usage="[subcommand] [target] [role]", description="config", brief="subcommands:\nremove - removes role from users\nadd - adds role to users\n\n**target:**\nhumans - targets human users\nbots - targets bot users\nall - targets all server users", aliases=["ra"])
   @commands.cooldown(1, 10, commands.BucketType.guild)
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

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: removed {role.mention} from all {target}"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{ctx.author.mention}: unable to {subcommand} {role.mention} to all {target} - {e}"))  
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

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: removed {role.mention} from all {target}"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{ctx.author.mention}: unable to {subcommand} {role.mention} to all {target} - {e}"))  
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

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: removed {role.mention} from all"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{ctx.author.mention}: unable to {subcommand} {role.mention} to all - {e}"))  
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

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: added {role.mention} from all {target}"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{ctx.author.mention}: unable to add {role.mention} to all {target} - {e}"))    
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

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: added {role.mention} from all {target}"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{ctx.author.mention}: unable to add {role.mention} to all {target} - {e}"))    
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

         await message.edit(embed=discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: added {role.mention} from all"))
        except Exception as e:
          await message.edit(embed=discord.Embed(color=Colors.red, description=f"{ctx.author.mention}: unable to add {role.mention} to all - {e}"))    
    else: return await commandhelp(self, ctx, ctx.command.name)
    
   @commands.command(aliases=["bonk"])
   @commands.cooldown(1, 4, commands.BucketType.user)
   async def ban(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
    if (not ctx.author.guild_permissions.ban_members):
     e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: you are missing permissions `ban_members`")
     await ctx.reply(embed=e, mention_author=False)
     return  

    if member == None:
       e = discord.Embed(color=Colors.green, title="ban", description="bans member from the server")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="category", value="moderation", inline=True)
       e.add_field(name="permissions", value="ban_members", inline=True)
       e.add_field(name="usage", value=f"```usage: ban [member] <reason>```", inline=False)
       e.add_field(name="aliases", value="bonk")
       await ctx.reply(embed=e, mention_author=False)  
       return 

    if member == None or member == ctx.message.author:
        e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: you cannot ban yourself")
        await ctx.reply(embed=e, mention_author=False)
        return
    
    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: you can't ban {member.mention}")
       await ctx.reply(embed=nope, mention_author=False)
       return

    if reason == None:
        reason = "No reason provided"

    if ctx.guild.premium_subscriber_role in member.roles:
     button1 = Button(label="yes", style=discord.ButtonStyle.green)
     button2 = Button(label="no", style=discord.ButtonStyle.red)
     embed = discord.Embed(color=Color.green, description=f"are you sure you want to ban {member.mention}? they are a server booster")
     async def button1_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=Color.green, description=f"{interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        
        try: 
          await member.ban(reason=f"kicked by {ctx.author} - {reason}")
          embe = discord.Embed(color=Color.green, description=f"<a:b1wave:1074001869250240543> {member.mention} got banned | {reason}")
          await interaction.response.edit_message(embed=embe, view=None)
          try:
           banned = discord.Embed(color=Color.green, title="ban case", description=f"you have been banned from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
           banned.set_thumbnail(url=ctx.guild.icon.url)
           banned.add_field(name="moderator", value=ctx.author)
           banned.add_field(name="reason", value=reason)
           banned.set_footer(text=f"id: {ctx.guild.id}")  
           await member.send(embed=banned)
          except:
           pass   
        except:
         no = discord.Embed(color=Color.green, description=f"<a:b1nup:1074373130509885440> {ctx.author.mention}: i don't have enough permissions to do this")
         await interaction.response.edit_message(embed=no, mention_author=False)
     button1.callback = button1_callback

     async def button2_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=Color.green, description=f"<a:b1nup:1074373130509885440> {interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return

        embe = discord.Embed(color=Color.green, description=f"alright you changed your mind!")
        await interaction.response.edit_message(embed=embe, view=None)

     button2.callback = button2_callback

     view = View()
     view.add_item(button1)
     view.add_item(button2)
     await ctx.reply(embed=embed, view=view, mention_author=False)        

    else:    
     try: 
      await member.ban(reason=f"banned by {ctx.author} - {reason}")
      embed = discord.Embed(color=Color.green, description=f"<a:b1wave:1074001869250240543> {member.mention} got banned | {reason}")
      await ctx.reply(embed=embed, mention_author=False)
      try: 
         banned = discord.Embed(color=Colors.green, title="ban case", description=f"you have been banned from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
         banned.set_thumbnail(url=ctx.guild.icon.url)
         banned.add_field(name="moderator", value=ctx.author)
         banned.add_field(name="reason", value=reason)
         banned.set_footer(text=f"id: {ctx.guild.id}")   
         await member.send(embed=banned)
      except: 
         pass 
     except:
        no = discord.Embed(color=Colors.green, description=f"<a:b1nup:1074373130509885440> {ctx.author.mention}: i don't have enough permissions to do this")
        await ctx.reply(embed=no, mention_author=False)

   @ban.error
   async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: {error}")
        await ctx.reply(embed=embed, mention_author=False)

   @commands.command()
   async def unban(self, ctx: commands.Context, *, member: discord.User=None):
    if (not ctx.author.guild_permissions.ban_members):
     e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: you are missing permissions `ban_members`")
     await ctx.reply(embed=e, mention_author=False)
     return   

    if member == None:
       e = discord.Embed(color=Colors.green, title="unban", description="unbans member from server")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="category", value="moderation", inline=True)
       e.add_field(name="permissions", value="ban_members", inline=True)
       e.add_field(name="usage", value=f"```usage: unban [member]```", inline=False)
       e.add_field(name="aliases", value="none")
       await ctx.reply(embed=e, mention_author=False)  
       return 
  
    try: 
     guild = ctx.guild
     embed = discord.Embed(color=Colors.green, description=f"{member} has been unbanned")
     await guild.unban(user=member)
     await ctx.reply(embed=embed, mention_author=False)
    except:
       emb = discord.Embed(color=Color.green, description=f"{ctx.author.mention} couldn't unban this member")
       await ctx.reply(embed=emb, mention_author=False)  
   
   @commands.command()
   async def kick(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
    if (not ctx.author.guild_permissions.kick_members):
     e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: you are missing permissions `kick_members`")
     await ctx.reply(embed=e, mention_author=False)
     return   

    if member == None:
       e = discord.Embed(color=Colors.green, title="kick", description="kicks member from server")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="category", value="moderation", inline=True)
       e.add_field(name="permissions", value="kick_members", inline=True)
       e.add_field(name="usage", value=f"```usage: kick [member] <reason>\nexample: kick {ctx.author.mention} test```", inline=False)
       e.add_field(name="aliases", value="none")
       await ctx.reply(embed=e, mention_author=False) 
       return  

    if member == ctx.author:
     e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: you can't kick yourserlf")
     await ctx.reply(embed=e, mention_author=False)
     return

    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: you can't kick {member.mention}")
       await ctx.reply(embed=nope, mention_author=False)
       return   
 
    if reason == None:
        reason = "No reason provided"

    if ctx.guild.premium_subscriber_role in member.roles:
     button1 = Button(label="yes", style=discord.ButtonStyle.green)
     button2 = Button(label="no", style=discord.ButtonStyle.red)
     embed = discord.Embed(color=Color.green, description=f"are you sure you want to kick {member.mention}? they are a server booster")
     async def button1_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=Color.green, description=f"{interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        
        try: 
          await member.kick(reason=f"kicked by {ctx.author} - {reason}")
          embe = discord.Embed(color=Color.green, description=f"{member.mention} got kicked | {reason}")
          await interaction.response.edit_message(embed=embe, view=None)
          try:
           banned = discord.Embed(color=Color.green, title="kick case", description=f"you have been kicked from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
           banned.set_thumbnail(url=ctx.guild.icon.url)
           banned.add_field(name="moderator", value=ctx.author)
           banned.add_field(name="reason", value=reason)
           banned.set_footer(text=f"id: {ctx.guild.id}")  
           await member.send(embed=banned)
          except:
           print('cant dm')    
        except:
         no = discord.Embed(color=Color.green, description=f"{ctx.author.mention}: i don't have enough permissions to do this")
         await interaction.response.edit_message(embed=no, mention_author=False)
     button1.callback = button1_callback

     async def button2_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=Colors.green, description=f"{interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return

        embe = discord.Embed(color=Colors.green, description=f"alright you changed your mind!")
        await interaction.response.edit_message(embed=embe, view=None)

     button2.callback = button2_callback

     view = View()
     view.add_item(button1)
     view.add_item(button2)
     await ctx.reply(embed=embed, view=view, mention_author=False)        

    else:
     try: 
      await member.kick(reason=f"kicked by {ctx.author} - {reason}")
      embed = discord.Embed(color=Colors.green, description=f"{member.mention} got kicked | {reason}")
      await ctx.reply(embed=embed, mention_author=False)
      try:
           banned = discord.Embed(color=Colors.green, title="kick case", description=f"you have been kicked from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
           banned.set_thumbnail(url=ctx.guild.icon.url)
           banned.add_field(name="moderator", value=ctx.author)
           banned.add_field(name="reason", value=reason)
           banned.set_footer(text=f"id: {ctx.guild.id}")  
           await member.send(embed=banned)
      except:
           pass   
     except:
        no = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: i don't have enough permissions to do this")
        await ctx.reply(embed=no, mention_author=False)       

   @kick.error
   async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: {error}")
        await ctx.reply(embed=embed, mention_author=False)

async def setup(bot) -> None: 
    await bot.add_cog(moderation(bot))        