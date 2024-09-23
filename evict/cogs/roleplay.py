import discord, datetime, asyncio, random
from discord.ext import commands 
from discord.ui import Button, View
from patches.permissions import Permissions
from patches.fun import MarryView, DiaryModal, Joint

class roleplay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.joint_emoji = "🍃"
        self.smoke = "🌬️" 
        self.joint_color = 0x57D657
        self.book = "📖" 
    
    async def joint_send(self, ctx: commands.Context, message: str) -> discord.Message:
      embed = discord.Embed(color=self.joint_color, description=f"{self.joint_emoji} {ctx.author.mention}: {message}") 
      return await ctx.reply(embed=embed)
    
    async def smoke_send(self, ctx: commands.Context, message: str) -> discord.Message: 
      embed = discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: {message}")
      return await ctx.reply(embed=embed)

    @commands.group(name="joint", invoke_without_command=True, description="have fun with a joint")
    async def jointcmd(self, ctx): 
      return await ctx.create_pages()

    @jointcmd.command(name="toggle", description="toggle the server joint", brief="manage guild")
    @Permissions.has_permission(manage_guild=True)
    async def joint_toggle(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = {}".format(ctx.guild.id)) 
     if not check: 
      await self.bot.db.execute("INSERT INTO joint VALUES ($1,$2,$3)", ctx.guild.id, 0, ctx.author.id)
      return await self.joint_send(ctx, "The joint is yours")
     await self.bot.db.execute("DELETE FROM joint WHERE guild_id = $1", ctx.guild.id)
     return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: Got rid of the server's joint")) 
    
    @jointcmd.command(name="stats", description="check joint stats", aliases=["status", "settings"])
    @Joint.check_joint()
    async def joint_stats(self, ctx: commands.Context):      
      check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
      embed = discord.Embed(color=self.joint_color, description=f"{self.smoke} hits: **{check['hits']}**\n{self.joint_emoji} Holder: <@{check['holder']}>")      
      embed.set_author(icon_url=ctx.guild.icon, name=f"{ctx.guild.name}'s joint")
      return await ctx.reply(embed=embed)

    @jointcmd.command(name="hit", description="hit the server joint")
    @Joint.check_joint()
    @Joint.joint_owner()
    async def joint_hit(self, ctx: commands.Context):
      check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
      newhits = int(check["hits"]+1) 
      mes = await self.joint_send(ctx, "Hitting the **joint**.....")
      await asyncio.sleep(2)
      embed = discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: You just hit the **joint**. This server has a total of **{newhits}** hits!")
      await mes.edit(embed=embed)
      await self.bot.db.execute("UPDATE joint SET hits = $1 WHERE guild_id = $2", newhits, ctx.guild.id)
    
    @joint_hit.error 
    async def on_error(self, ctx: commands.Context, error: Exception): 
     if isinstance(error, commands.CommandOnCooldown): return await self.joint_send(ctx, "You are getting too high! Please wait until you can hit again") 

    @jointcmd.command(name="pass", description="pass the joint to someone else", usage="[member]")
    @Joint.check_joint()
    @Joint.joint_owner()
    async def joint_pass(self, ctx: commands.Context, *, member: discord.Member):
     if member.id == self.bot.user.id: return await ctx.reply("Thank you, but i do not smoke")
     elif member.bot: return await ctx.warning("Bots do not smoke")
     elif member.id == ctx.author.id: return await ctx.warning("You already have the **joint**")
     await self.bot.db.execute("UPDATE joint SET holder = $1 WHERE guild_id = $2", member.id, ctx.guild.id)
     await self.joint_send(ctx, f"Passing the **joint** to **{member.name}**")
    
    @jointcmd.command(name="steal", description="steal the server's joint")
    @Joint.check_joint()
    async def joint_steal(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
     if check["holder"] == ctx.author.id: return await self.joint_send(ctx, "You already have the **joint**")
     chances = ["yes", "yes", "yes", "no", "no"]
     if random.choice(chances) == "no": return await self.smoke_send(ctx, f"You tried to steal the **joint** and **{(await self.bot.fetch_user(int(check['holder']))).name}** hit you")
     await self.bot.db.execute("UPDATE joint SET holder = $1 WHERE guild_id = $2", ctx.author.id, ctx.guild.id)
     return await self.joint_send(ctx, "You got the server **joint**")

    @commands.command(description='cuddle a user', usage='[user]')
    async def cuddle(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/cuddle', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just cuddled **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='poke a user', usage='[user]')
    async def poke(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/poke', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just poked **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='kiss a user', usage='[user]')
    async def kiss(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/kiss', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just kissed **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='hug a user', usage='[user]')
    async def hug(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/hug', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just hugged **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='pat a user', usage='[user]')
    async def pat(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/pat', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just patted **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='tickle a user', usage='[user]')
    async def tickle(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/tickle', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just tickled **{user.mention}**!")
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='lick a user', usage='[user]')
    async def lick(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/lick', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just licked **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='slap a user', usage='[user]')
    async def slap(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/slap', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just slapped **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='spank a user', usage='[user]')
    async def spank(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/spank', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just spanked **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='feed a user', usage='[user]')
    async def feed(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/feed', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just fed **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='punch a user', usage='[user]')
    async def punch(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/punch', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just punched **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='highfive a user', usage='[user]')
    async def highfive(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/lick', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just highfived **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)
    
    @commands.command(description='kill a user', usage='[user]')
    async def kill(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/kill', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just killed **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)
            
    @commands.command(description='bite a user', usage='[user]')
    async def bite(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/bite', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just bit **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='yeet a user', usage='[user]')
    async def lick(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/yeet', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just yeeted **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='nutkick a user', usage='[user]')
    async def nutkick(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/nutkick', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just nutkicked **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='fuck a user', usage='[user]')
    async def fuck(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/fuck', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just fucked **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='have a threesome', usage='[user]')
    async def threesome(self, ctx: commands.Context, user: discord.Member, user1: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/threesome', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just fucked {str(user.mention)} and {f'{str(user1.mention)}' if user else 'themselves'}!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description='hump a user', usage='[user]')
    async def hump(self, ctx: commands.Context, user: discord.Member):
            headers = {"api-key": self.bot.evict_api}
            response = await self.bot.session.get_json('https://kure.pl/roleplay/hump', headers=headers)
            embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.mention}** just humped **{user.mention}**!")
            embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar)
            embed.set_image(url=response["image_url"])
            await ctx.reply(embed=embed)

    @commands.command(description="marry an user", usage="[user]")
    async def marry(self, ctx: commands.Context, *, member: discord.Member):
     if member == ctx.author: return await ctx.error("You can't **marry** yourself")
     elif member.bot: return await ctx.error("robots can't consent marriage".capitalize())  
     else: 
        meri = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", member.id)
        if meri is not None: return await ctx.warning(f"**{member}** is already married")
        elif meri is None:
           mer = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", member.id)
           if mer is not None: return await ctx.warning(f"**{member}** is already married")
                    
        check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", ctx.author.id) 
        if check is not None: return await ctx.warning("You are already **married**. Are you trying to cheat?? 🤨")
        elif check is None:
           check2 = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", ctx.author.id) 
           if check2 is not None: await ctx.warning("You are already **married**. Are you trying to cheat?? 🤨")
           else:
             embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** wants to marry you. do you accept?")
             view = MarryView(ctx, member)
             view.message = await ctx.reply(content=member.mention, embed=embed, view=view)
    
    @commands.command(description="check an user's marriage", usage="<member>")
    async def marriage(self, ctx: commands.Context, *, member: discord.User=None):
      if member is None: member = ctx.author
      check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", member.id)       
      if check is None:
           check2 = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", member.id)
           if check2 is None: return await ctx.error(f"{'**You** are' if member == ctx.author else f'**{member.name}** is'} not **married**")
           elif check2 is not None:
            embed = discord.Embed(color=self.bot.color, description=f"💒 {f'**{member}** is' if member != ctx.author else '**You** are'} currently married to **{await self.bot.fetch_user(int(check2[0]))}** since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(check2['time'])))}**")
            return await ctx.reply(embed=embed)  
      elif check is not None:
         embed = discord.Embed(color=self.bot.color, description=f"💒 {f'**{member}** is' if member != ctx.author else '**You** are'} currently married to **{await self.bot.fetch_user(int(check[1]))}** since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(check['time'])))}**")
         return await ctx.reply(embed=embed)   

    @commands.command(description="divorce with an user")
    async def divorce(self, ctx: commands.Context):       
        check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", ctx.author.id)
        if check is None:
           check2 = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", ctx.author.id)
           if check2 is None: return await ctx.error("**You** are not **married**")

        button1 = Button(emoji=self.bot.yes, style=discord.ButtonStyle.grey)
        button2 = Button(emoji=self.bot.no, style=discord.ButtonStyle.grey)
        embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** are you sure you want to divorce?")
        async def button1_callback(interaction):
         if interaction.user != ctx.author: return await self.bot.ext.warning(interaction, "You are not the author of this embed", ephemeral=True) 
         if check is None:
            if check2 is not None: await self.bot.db.execute("DELETE FROM marry WHERE soulmate = $1", ctx.author.id)
         elif check is not None: await self.bot.db.execute("DELETE FROM marry WHERE author = $1", ctx.author.id)                    
         embe = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** divorced with their partner")
         await interaction.response.edit_message(content=None, embed=embe, view=None)       
        button1.callback = button1_callback  

        async def button2_callback(interaction):
          if interaction.user != ctx.author: return await self.bot.ext.warning(interaction, "You are not the author of this embed", ephemeral=True)                       
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
    
    @diary.command(name="create", aliases=['add'], description="create a diary for today")
    async def diary_create(self, ctx: commands.Context): 
      now = datetime.datetime.now()
      date = f"{now.month}/{now.day}/{str(now.year)[2:]}"   
      check = await ctx.bot.db.fetchrow("SELECT * FROM diary WHERE user_id = $1 AND date = $2", ctx.author.id, date)
      if check: return await ctx.warning("You **already** have a diary page created today! Please come back tomorrow or delete the diary page you created")    
      embed = discord.Embed(color=self.bot.color, description=f"{self.book} Press the button below to create a diary page")
      button = discord.ui.Button(emoji=self.book, style=discord.ButtonStyle.blurple)

      async def button_callback(interaction: discord.Interaction): 
        if interaction.user.id != ctx.author.id: return await interaction.client.ext.warning(interaction, "You are not the author of this embed") 
        mt = DiaryModal()
        return await interaction.response.send_modal(mt)
      
      button.callback = button_callback 

      view = discord.ui.View()
      view.add_item(button)
      return await ctx.reply(embed=embed, view=view) 
    
    @diary.command(name="view", description="view your diary book")
    async def diary_view(self, ctx: commands.Context): 
      results = await self.bot.db.fetch("SELECT * FROM diary WHERE user_id = $1", ctx.author.id)
      if len(results) == 0: return await ctx.warning("You don't have any diary page created")
      embeds = []
      for result in results: embeds.append(discord.Embed(color=self.bot.color, title=result['title'], description=result['text']).set_author(name=f"diary for {result['date']}").set_footer(text=f"{results.index(result)+1}/{len(results)}"))
      return await ctx.paginator(embeds)
    
    @diary.command(name="delete", description="delete a diary page")
    async def diary_delete(self, ctx: commands.Context): 
     options = []
     results = await self.bot.db.fetch("SELECT * FROM diary WHERE user_id = $1", ctx.author.id)
     if len(results) == 0: return await ctx.warning("You don't have any diary page created")  
     for result in results: 
       try: options.append(discord.SelectOption(label=f"diary {results.index(result)+1} - {result['date']}", value=result['date']))
       except: continue
     embed = discord.Embed(color=self.bot.color, description="Select the **dropdown** menu below to delete a diary page")  
     select = discord.ui.Select(options=options, placeholder="delete a diary page")
     
     async def select_callback(interaction: discord.Interaction): 
      if interaction.user.id != ctx.author.id: return await interaction.client.ext.warning(interaction, "You are not the author of this embed") 
      await self.bot.db.execute("DELETE FROM diary WHERE user_id = $1 AND date = $2", ctx.author.id, select.values[0])
      return await interaction.response.send_message("Deleted a diary page", ephemeral=True) 
     select.callback = select_callback
     view = discord.ui.View()
     view.add_item(select)
     return await ctx.reply(embed=embed, view=view)
    
async def setup(bot) -> None:
    await bot.add_cog(roleplay(bot))        