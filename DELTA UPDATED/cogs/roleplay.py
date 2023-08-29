import requests, discord, datetime, asyncio, random 
from discord.ext import commands 
from discord.ui import Button, View
from tools.checks import Perms, Joint 

session = requests.Session()

class MarryView(discord.ui.View): 
   def __init__(self, ctx: commands.Context, member: discord.Member): 
    super().__init__() 
    self.ctx = ctx 
    self.member = member
    self.status = False 

   @discord.ui.button(emoji="<:deltayes:1141426602819985449>")
   async def yes(self, interaction: discord.Interaction, button: discord.ui.Button): 
    if interaction.user == self.ctx.author: return await interaction.client.ext.send_warning(interaction, "you can't accept your own marriage".capitalize(), ephemeral=True)
    elif interaction.user != self.member: return await self.ctx.bot.ext.send_warning(interaction, "you are not the author of this embed".capitalize(), ephemeral=True)
    else:   
      await interaction.client.db.execute("INSERT INTO marry VALUES ($1, $2, $3)", self.ctx.author.id, self.member.id, datetime.datetime.now().timestamp())                   
      embe = discord.Embed(color=interaction.client.color, description=f"<:ajoobiwow:1138047930163527710> **{self.ctx.author}** succesfully married with **{self.member}**")
      await interaction.response.edit_message(content=None, embed=embe, view=None)
      self.status = True              

   @discord.ui.button(emoji="<:deltano:1141426919221497876>")
   async def no(self, interaction: discord.Interaction, button: discord.ui.Button): 
     if interaction.user == self.ctx.author: return await self.ctx.bot.ext.send_warning(interaction, "you can't reject your own marriage".capitalize(), ephemeral=True)
     elif interaction.user != self.member: return await self.ctx.bot.ext.send_warning(interaction, "you are not the author of this embed".capitalize(), ephemeral=True)
     else:                         
        embe = discord.Embed(color=interaction.client.color, description=f"**{self.ctx.author}** i'm sorry, but **{self.member}** is probably not the right person for you")
        await interaction.response.edit_message(content=None, embed=embe, view=None)
        self.status = True 
   
   async def on_timeout(self):
     if self.status == False:
      embed = discord.Embed(color=0xd3d3d3, description=f"**{self.member}** didn't reply in time :(")  
      try: await self.message.edit(content=None, embed=embed, view=None)  
      except: pass 

class DiaryModal(discord.ui.Modal, title="Create a diary page"): 
  titl = discord.ui.TextInput(label="Your diary title", placeholder="Give your diary page a short name", style=discord.TextStyle.short)
  text = discord.ui.TextInput(label="Your diary text", placeholder="Share your feelings or thoughts here", max_length=2000, style=discord.TextStyle.long)
  
  async def on_submit(self, interaction: discord.Interaction): 
   now = datetime.datetime.now()
   date = f"{now.month}/{now.day}/{str(now.year)[2:]}"
   await interaction.client.db.execute("INSERT INTO diary VALUES ($1,$2,$3,$4)", interaction.user.id, self.text.value, self.titl.value, date) 
   embed = discord.Embed(color=interaction.client.color, description=f"> {interaction.client.yes} {interaction.user.mention}: Added a diary page for today")
   return await interaction.response.edit_message(embed=embed, view=None)
  
  async def on_error(self, interaction: discord.Interaction, error: Exception): 
   embed = discord.Embed(color=interaction.client.color, description=f"> {interaction.client.no} {interaction.user.mention}: Unable to create the diary")
   return await interaction.response.edit_message(embed=embed, view=None) 

class roleplay(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
        self.joint_emoji = "🍃"
        self.smoke = "🌬️" 
        self.joint_color = 0x57D657
        self.book = "📖" 
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
      if isinstance(error, commands.errors.NSFWChannelRequired):
         msg.title = "NSFW Command"
         msg.description = error.args[0]
         return await ctx.send(embed=msg)
    
    async def joint_send(self, ctx: commands.Context, message: str) -> discord.Message:
      embed = discord.Embed(color=self.joint_color, description=f"{self.joint_emoji} {ctx.author.mention}: {message}") 
      return await ctx.reply(embed=embed)
    
    async def smoke_send(self, ctx: commands.Context, message: str) -> discord.Message: 
      embed = discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: {message}")
      return await ctx.reply(embed=embed)

    @commands.command(description="lick someone", help="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lick(self, ctx: commands.Context, *, member: discord.Member):
            url = 'http://api.nekos.fun:8080/api/lick'
            resp = session.get(url)
            js = resp.json()
            embed=discord.Embed(description=f"**{ctx.author.name}** *licks* **{member.name}**", color=self.bot.color)
            embed.set_image(url=js['image'])
            await ctx.reply(embed=embed)
    
    @commands.command(description="cum on someone", help="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cum(self, ctx: commands.Context, *, member: discord.Member):
     if not ctx.channel.is_nsfw():
        embed = discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.author.mention}: You cant use this nsfw command here")
        await ctx.reply(embed=embed)
     else:
            url = 'http://api.nekos.fun:8080/api/cum'
            resp = session.get(url)
            js = resp.json()
            embed=discord.Embed(description=f"**{ctx.author.name}** *cums on* **{member.name}**", color=self.bot.color)
            embed.set_image(url=js['image'])
            await ctx.reply(embed=embed)
    
    @commands.command(description="make anal with someone", help="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def anal(self, ctx: commands.Context, *, member: discord.Member):
     if not ctx.channel.is_nsfw():
        embed = discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.author.mention}: You cant use this nsfw command here")
        await ctx.reply(embed=embed)
     else:
            url = 'http://api.nekos.fun:8080/api/anal'
            resp = session.get(url)
            js = resp.json()
            embed=discord.Embed(description=f"**{ctx.author.name}** *fucks* **{member.name}**", color=self.bot.color)
            embed.set_image(url=js['image'])
            await ctx.reply(embed=embed)
    
    @commands.command(description="make someone a blowjob", help="roleplay")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blowjob(self, ctx: commands.Context, *, member: discord.Member):
     if not ctx.channel.is_nsfw():
        embed = discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.author.mention}: You cant use this nsfw command here")
        await ctx.reply(embed=embed)
     else:
            url = 'https://api.waifu.pics/nsfw/blowjob'
            resp = session.get(url)
            js = resp.json()
            embed=discord.Embed(description=f"**{ctx.author.name}** *gives a blowjob to* **{member.name}**", color=self.bot.color)
            embed.set_image(url=js['url'])
            await ctx.reply(embed=embed)
    
    @commands.group(name="joint", invoke_without_command=True, description="have fun with a joint", help="roleplay")
    async def jointcmd(self, ctx): 
      return await ctx.create_pages()

    @jointcmd.command(name="toggle", help="roleplay", description="toggle the server joint", brief="manage guild")
    @Perms.get_perms("manage_guild")
    async def joint_toggle(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = {}".format(ctx.guild.id)) 
     if not check: 
      await self.bot.db.execute("INSERT INTO joint VALUES ($1,$2,$3)", ctx.guild.id, 0, ctx.author.id)
      return await self.joint_send(ctx, "The joint is yours")
     await self.bot.db.execute("DELETE FROM joint WHERE guild_id = $1", ctx.guild.id)
     return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: Got rid of the server's joint")) 
    
    @jointcmd.command(name="stats", help="roleplay", description="check joint stats", aliases=["status", "settings"])
    @Joint.check_joint()
    async def joint_stats(self, ctx: commands.Context):      
      check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
      embed = discord.Embed(color=self.joint_color, description=f"{self.smoke} hits: **{check['hits']}**\n{self.joint_emoji} Holder: <@{check['holder']}>")      
      embed.set_author(icon_url=ctx.guild.icon, name=f"{ctx.guild.name}'s joint")
      return await ctx.reply(embed=embed)

    @jointcmd.command(name="hit", help="roleplay", description="hit the server joint")
    @Joint.check_joint()
    @Joint.joint_owner()
    async def joint_hit(self, ctx: commands.Context): 
      mes = await self.joint_send(ctx, "Hitting the **joint**.....")
      await asyncio.sleep(2)
      check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
      newhits = int(check["hits"]+1)
      embed = discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: You just hit the **joint**. This server has a total of **{newhits}** hits!")
      await mes.edit(embed=embed)
      await self.bot.db.execute("UPDATE joint SET hits = $1 WHERE guild_id = $2", newhits, ctx.guild.id)
    
    @joint_hit.error 
    async def on_error(self, ctx: commands.Context, error: Exception): 
     if isinstance(error, commands.CommandOnCooldown): return await self.joint_send(ctx, "You are getting too high! Please wait until you can hit again") 

    @jointcmd.command(name="pass", help="roleplay", description="pass the joint to someone else", usage="[member]")
    @Joint.check_joint()
    @Joint.joint_owner()
    async def joint_pass(self, ctx: commands.Context, *, member: discord.Member):
     if member.id == self.bot.user.id: return await ctx.reply("Thank you, but i do not smoke")
     elif member.bot: return await ctx.send_warning("Bots do not smoke")
     elif member.id == ctx.author.id: return await ctx.send_warning("You already have the **joint**")
     await self.bot.db.execute("UPDATE joint SET holder = $1 WHERE guild_id = $2", member.id, ctx.guild.id)
     await self.joint_send(ctx, f"Passing the **joint** to **{member.name}**")
    
    @jointcmd.command(name="steal", help="roleplay", description="steal the server's joint")
    @Joint.check_joint()
    async def joint_steal(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
     if check["holder"] == ctx.author.id: return await self.joint_send(ctx, "You already have the **joint**")
     chances = ["yes", "yes", "yes", "no", "no"]
     if random.choice(chances) == "no": return await self.smoke_send(ctx, f"You tried to steal the **joint** and **{(await self.bot.fetch_user(int(check['holder']))).name}** hit you")
     await self.bot.db.execute("UPDATE joint SET holder = $1 WHERE guild_id = $2", ctx.author.id, ctx.guild.id)
     return await self.joint_send(ctx, "You got the server **joint**")

    @commands.hybrid_command(description="kiss an user", usage="[member]", help="roleplay")
    async def kiss(self, ctx: commands.Context, *, member: discord.Member):
     lol = await self.bot.session.json("http://api.nekos.fun:8080/api/kiss")
     embed = discord.Embed(color=self.bot.color, description=f"*Aww how cute!* **{ctx.author.name}** kissed **{member.name}**")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.hybrid_command(description="cuddle an user", usage="[member]", help="roleplay")
    async def cuddle(self, ctx, *, member: discord.Member):
     lol = await self.bot.session.json("http://api.nekos.fun:8080/api/cuddle")
     embed = discord.Embed(color=self.bot.color, description=f"*Aww how cute!* **{ctx.author.name}** cuddled **{member.name}**")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.hybrid_command(description="hug an user", usage="[member]", help="roleplay")
    async def hug(self, ctx: commands.Context, *, member: discord.Member): 
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"*Aww how cute!* **{ctx.author.name}** hugged **{member.name}**")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.hybrid_command(description="pat an user", usage="[member]", help="roleplay")
    async def pat(self, ctx, *, member: discord.Member):
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"*Aww how cute!* **{ctx.author.name}** pats **{member.name}**")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.hybrid_command(description="slap an user", usage="[member]", help="roleplay")
    async def slap(self, ctx, *, member: discord.Member): 
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** slaps **{member.name}***")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.hybrid_command(description="start laughing", help="roleplay")
    async def laugh(self, ctx): 
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** laughs")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.hybrid_command(description="start crying", help="roleplay")
    async def cry(self, ctx):
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** cries")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.hybrid_command(description="marry an user", help="roleplay", usage="[user]")
    async def marry(self, ctx: commands.Context, *, member: discord.Member):
     if member == ctx.author: return await ctx.send_error("You can't **marry** yourself")
     elif member.bot: return await ctx.send_error("robots can't consent marriage".capitalize())  
     else: 
        meri = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", member.id)
        if meri is not None: return await ctx.send_warning(f"**{member}** is already married")
        elif meri is None:
           mer = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", member.id)
           if mer is not None: return await ctx.send_warning(f"**{member}** is already married")
                    
        check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", ctx.author.id) 
        if check is not None: return await ctx.send_warning("You are already **married**. Are you trying to cheat?? 🤨")
        elif check is None:
           check2 = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", ctx.author.id) 
           if check2 is not None: await ctx.send_warning("You are already **married**. Are you trying to cheat?? 🤨")
           else:
             embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** wants to marry you. do you accept?")
             view = MarryView(ctx, member)
             view.message = await ctx.reply(content=member.mention, embed=embed, view=view)
    
    @commands.hybrid_command(description="check an user's marriage", usage="<member>", help="roleplay")
    async def marriage(self, ctx: commands.Context, *, member: discord.User=None):
      if member is None: member = ctx.author
      check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", member.id)       
      if check is None:
           check2 = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", member.id)
           if check2 is None: return await ctx.send_error(f"{'**You** are' if member == ctx.author else f'**{member.name}** is'} not **married**")
           elif check2 is not None:
            embed = discord.Embed(color=self.bot.color, description=f"💒 {f'**{member}** is' if member != ctx.author else '**You** are'} currently married to **{await self.bot.fetch_user(int(check2[0]))}** since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(check2['time'])))}**")
            return await ctx.reply(embed=embed)  
      elif check is not None:
         embed = discord.Embed(color=self.bot.color, description=f"💒 {f'**{member}** is' if member != ctx.author else '**You** are'} currently married to **{await self.bot.fetch_user(int(check[1]))}** since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(check['time'])))}**")
         return await ctx.reply(embed=embed)   

    @commands.hybrid_command(description="divorce with an user", help="roleplay")
    async def divorce(self, ctx: commands.Context):       
        check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", ctx.author.id)
        if check is None:
           check2 = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", ctx.author.id)
           if check2 is None: return await ctx.send_error("**You** are not **married**")

        button1 = Button(emoji=self.bot.yes, style=discord.ButtonStyle.grey)
        button2 = Button(emoji=self.bot.no, style=discord.ButtonStyle.grey)
        embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** are you sure you want to divorce?")
        async def button1_callback(interaction):
         if interaction.user != ctx.author: return await self.bot.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True) 
         if check is None:
            if check2 is not None: await self.bot.db.execute("DELETE FROM marry WHERE soulmate = $1", ctx.author.id)
         elif check is not None: await self.bot.db.execute("DELETE FROM marry WHERE author = $1", ctx.author.id)                    
         embe = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** divorced with their partner")
         await interaction.response.edit_message(content=None, embed=embe, view=None)       
        button1.callback = button1_callback  

        async def button2_callback(interaction):
          if interaction.user != ctx.author: return await self.bot.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True)                       
          embe = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** you changed your mind")
          await interaction.response.edit_message(content=None, embed=embe, view=None)
        button2.callback = button2_callback  

        marry = View()
        marry.add_item(button1)
        marry.add_item(button2)
        await ctx.reply(embed=embed, view=marry)      
   
    @commands.group(invoke_without_command=True)
    async def diary(self, ctx):
     return await ctx.create_pages() 
    
    @diary.command(name="create", aliases=['add'], description="create a diary for today", help="roleplay")
    async def diary_create(self, ctx: commands.Context): 
      now = datetime.datetime.now()
      date = f"{now.month}/{now.day}/{str(now.year)[2:]}"   
      check = await ctx.bot.db.fetchrow("SELECT * FROM diary WHERE user_id = $1 AND date = $2", ctx.author.id, date)
      if check: return await ctx.send_warning("You **already** have a diary page created today! Please come back tomorrow or delete the diary page you created")    
      embed = discord.Embed(color=self.bot.color, description=f"{self.book} Press the button below to create a diary page")
      button = discord.ui.Button(emoji=self.book, style=discord.ButtonStyle.blurple)

      async def button_callback(interaction: discord.Interaction): 
        if interaction.user.id != ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed") 
        mt = DiaryModal()
        return await interaction.response.send_modal(mt)
      
      button.callback = button_callback 

      view = discord.ui.View()
      view.add_item(button)
      return await ctx.reply(embed=embed, view=view) 
    
    @diary.command(name="view", description="view your diary book", help="roleplay")
    async def diary_view(self, ctx: commands.Context): 
      results = await self.bot.db.fetch("SELECT * FROM diary WHERE user_id = $1", ctx.author.id)
      if len(results) == 0: return await ctx.send_warning("You don't have any diary page created")
      embeds = []
      for result in results: embeds.append(discord.Embed(color=self.bot.color, title=result['title'], description=result['text']).set_author(name=f"diary for {result['date']}").set_footer(text=f"{results.index(result)+1}/{len(results)}"))
      return await ctx.paginator(embeds)
    
    @diary.command(name="delete", description="delete a diary page", help="roleplay")
    async def diary_delete(self, ctx: commands.Context): 
     options = []
     results = await self.bot.db.fetch("SELECT * FROM diary WHERE user_id = $1", ctx.author.id)
     if len(results) == 0: return await ctx.send_warning("You don't have any diary page created")  
     for result in results: 
       try: options.append(discord.SelectOption(label=f"diary {results.index(result)+1} - {result['date']}", value=result['date']))
       except: continue
     embed = discord.Embed(color=self.bot.color, description="Select the **dropdown** menu below to delete a diary page")  
     select = discord.ui.Select(options=options, placeholder="delete a diary page")
     
     async def select_callback(interaction: discord.Interaction): 
      if interaction.user.id != ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed") 
      await self.bot.db.execute("DELETE FROM diary WHERE user_id = $1 AND date = $2", ctx.author.id, select.values[0])
      return await interaction.response.send_message("Deleted a diary page", ephemeral=True) 
     select.callback = select_callback
     view = discord.ui.View()
     view.add_item(select)
     return await ctx.reply(embed=embed, view=view)
    
async def setup(bot) -> None:
    await bot.add_cog(roleplay(bot))        