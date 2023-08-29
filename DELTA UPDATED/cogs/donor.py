import discord, datetime, uwuipy
from datetime import datetime
from discord.ext import commands
from tools.checks import Perms, Mod
from tools.utils import PaginatorView, GoodRole, NoStaff
from typing import Union

class GoToModal(discord.ui.Modal, title="change the page"):
  page = discord.ui.TextInput(label="page", placeholder="change the page", max_length=3)

  async def on_submit(self, interaction: discord.Interaction) -> None:
   if int(self.page.value) > len(self.embeds): return await interaction.client.ext.send_warning(interaction, f"You can only select a page **between** 1 and {len(self.embeds)}", ephemeral=True) 
   attachments = [discord.File(fp=await self.bot.getbyte(self.files[int(self.page.value)-1][1]), filename="instagram.mp4")] if self.files[int(self.page.value)-1][0] == "video" else [discord.File(fp=await self.bot.getbyte(self.files[int(self.page.value)-1][1]), filename="instagram.png")]
   await interaction.response.edit_message(embed=self.embeds[int(self.page.value)-1], attachments=attachments) 
  
  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
    await interaction.client.ext.send_warning(interaction, "Unable to change the page", ephemeral=True)

class InstagramPaginatorView(discord.ui.View): 
    def __init__(self, ctx: commands.Context, embeds: list, files: list): 
      super().__init__()  
      self.embeds = embeds
      self.files = files
      self.ctx = ctx
      self.i = 0

    @discord.ui.button(emoji=f"<:right:1018156484170883154>", style=discord.ButtonStyle.blurple)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")          
      if self.i == 0: 
        attachments = [discord.File(fp=await self.bot.getbyte(self.files[-1][1]), filename="instagram.mp4")] if self.files[-1][0] == "video" else [discord.File(fp=await self.bot.getbyte(self.files[-1][1]), filename="instagram.png")]
        await interaction.response.edit_message(embed=self.embeds[-1], attachments=attachments)
        self.i = len(self.embeds)-1
        return
      self.i = self.i-1
      attachments = [discord.File(fp=await self.bot.getbyte(self.files[self.i][1]), filename="instagram.mp4")] if self.files[self.i][0] == "video" else [discord.File(fp=await self.bot.getbyte(self.files[self.i][1]), filename="instagram.png")]
      return await interaction.response.edit_message(embed=self.embeds[self.i], attachments=attachments)

    @discord.ui.button(emoji=f"<:right:1018156484170883154>", style=discord.ButtonStyle.blurple)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")     
      if self.i == len(self.embeds)-1: 
        attachments = [discord.File(fp=await self.bot.getbyte(self.files[0][1]), filename="instagram.mp4")] if self.files[0][0] == "video" else [discord.File(fp=await self.bot.getbyte(self.files[0][1]), filename="instagram.png")]
        await interaction.response.edit_message(embed=self.embeds[0], attachments=attachments)
        self.i = 0
        return 
      self.i = self.i + 1  
      att = attachments = [discord.File(fp=await self.bot.getbyte(self.files[self.i][1]), filename="instagram.mp4")] if self.files[self.i][0] == "video" else [discord.File(fp=await self.bot.getbyte(self.files[self.i][1]), filename="instagram.png")]
      return await interaction.response.edit_message(embed=self.embeds[self.i], attachments=att)   
 
    @discord.ui.button(emoji="<:filter:1039235211789078628>")
    async def goto(self, interaction: discord.Interaction, button: discord.ui.Button): 
     if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")     
     modal = GoToModal()
     modal.embeds = self.embeds
     modal.files = self.files
     modal.bot = interaction.client
     await interaction.response.send_modal(modal)
     await modal.wait()
     try:
      self.i = int(modal.page.value)-1
     except: pass 
    
    @discord.ui.button(emoji="<:stop:1018156487232720907>", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")     
      await interaction.message.delete()

    async def on_timeout(self) -> None: 
        mes = await self.message.channel.fetch_message(self.message.id)
        if mes is None: return
        if len(mes.components) == 0: return
        for item in self.children:
            item.disabled = True

        try: await self.message.edit(view=self)   
        except: pass

valid = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

def key(s):
  return s[2]

def checktag(table: str) -> bool: 
  if len(table) > 10: return False
  for i in table: 
    if not i in valid: return False 
  return True 

async def uwuthing(bot, text: str) -> str: 
   uwu = uwuipy.uwuipy()
   return uwu.uwuify(text)

def premium():
  async def predicate(ctx: commands.Context): 
    if ctx.command.name in ["hardban", "uwulock", "unhardban"]: 
      if ctx.author.id == ctx.guild.owner_id: return True     
    check = await ctx.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(ctx.author.id))     
    res = await ctx.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1 AND tags = $2", ctx.guild.id, "true")           
    if check is None and res is None: 
      await ctx.send_warning("Donator only use these")
      return False 
    return True 
  return commands.check(predicate)         

async def get_tags(bot, type, tag):   
    if type == "str": 
      results = await bot.db.fetch("SELECT * FROM oldusernames WHERE username = $1", tag)      
      data = [r for r in results] 
    elif type == "int": 
      results = await bot.db.fetch("SELECT * FROM oldusernames WHERE discriminator = $1", str(tag))       
      data = [r for r in results if (datetime.now() - datetime.fromtimestamp(float(r['time']))).total_seconds() < 6*3600]   
    data.sort(key=key, reverse=True)
    return data

class Premium(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.chatgpt_api = "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" 
        self.model_engine = "text-davinci-002"
   
   
   @commands.Cog.listener()
   async def on_message(self, message: discord.Message): 
    if not message.guild: return
    if isinstance(message.author, discord.User): return
    check = await self.bot.db.fetchrow("SELECT * FROM uwulock WHERE guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id))
    if check: 
     try: 
       await message.delete()
       uwumsg = await uwuthing(self.bot, message.clean_content)
       webhooks = await message.channel.webhooks()
       if len(webhooks) == 0: webhook = await message.channel.create_webhook(name="delta uwulock", reason="for uwulock")
       else: webhook = webhooks[0] 
       await webhook.send(content=uwumsg, username=message.author.name, avatar_url=message.author.display_avatar.url)
     except: pass 

   
     
   @commands.command(description="revoke the hardban from an user", help="donor", usage="[user]", brief="ban_members")
   @Perms.get_perms("ban_members")
   @premium()
   async def hardunban(self, ctx: commands.Context, *, member: discord.User):     
      che = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = {} AND banned = {}".format(ctx.guild.id, member.id))      
      if che is None: return await ctx.send_warning(f"{member} is **not** hardbanned") 
      await self.bot.db.execute("DELETE FROM hardban WHERE guild_id = {} AND banned = {}".format(ctx.guild.id, member.id))
      await ctx.guild.unban(member, reason="unhardbanned by {}".format(ctx.author.mention)) 
      await ctx.message.add_reaction("👍🏻")   
   
   """
   @commands.command(description="get an user's instagram stories", help="donor", usage="[username]", aliases=['instagramstory'])
   @premium()
   async def igstory(self, ctx: commands.Context, username: str): 
    url = "https://api.rival.rocks/instagram/story/user_stories"
    params = {'sessionid': self.bot.session_id, 'username': username}
    async with ctx.typing():
     r = await self.bot.session.post(url, headers=self.bot.rival_api, data=params)
     if r.status == 500: return await ctx.send_error(f"No account found with the name **@{username}**") 
     results = await r.json()
     if len(results) == 0: return await ctx.send_warning(f"[**@{username}**](https://instagram.com/{username}) doesn't have any story") 
     files = []
     embeds = []
     for result in results: 
      embeds.append(discord.Embed(color=0x30618A, description=f"[**Instagram story from @{username}**](https://instagram.com/{username})").set_author(name=f"@{result['user']['username']}", icon_url=result['user']['profile_pic_url']).set_footer(text=f"{results.index(result)+1}/{len(results)}・requested by {ctx.author}")) 
      if result['video_url']: files.append(tuple(["video", result['video_url']]))
      else: files.append(tuple(["picture", result['thumbnail_url']]))
     view = InstagramPaginatorView(ctx, embeds, files) 
     view.bot = self.bot
     if files[0][0] == "video": file = discord.File(fp=await self.bot.getbyte(files[0][1]), filename="instagram.mp4") 
     else: file = discord.File(fp=await self.bot.getbyte(files[0][1]), filename="instagram.png")
     if len(embeds) > 1: view.message =  await ctx.reply(embed=embeds[0], file=file, view=view)
     else: return await ctx.reply(embed=embeds[0], file=file)
   """
   @commands.command(description="hardban | hardunban an user from the server", help="donor", usage="[user]", brief="ban_members")
   @Perms.get_perms("ban_members")
   @premium()
   async def hardban(self, ctx: commands.Context, *, member: Union[discord.Member, discord.User]): 
    if isinstance(member, discord.Member):
      if member == ctx.message.author: return await ctx.send_warning("You cannot hardban **yourself**")
      if member.id == self.bot.user.id: return await ctx.reply("get back on your work and leave me alone..")
      if await Mod.check_hieracy(ctx, member):   
       che = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = {} AND banned = {}".format(ctx.guild.id, member.id))
       if che is not None: return await ctx.send_warning(f"**{member}** has been hardbanned by **{await self.bot.fetch_user(che['author'])}**")
       await ctx.guild.ban(member, reason="hardbanned by {}".format(ctx.author))
       await self.bot.db.execute("INSERT INTO hardban VALUES ($1,$2,$3)", ctx.guild.id, member.id, ctx.author.id)
       await ctx.message.add_reaction("👍🏻")
  
   @commands.command(description="uwuify a person's messages", help="donor", usage="[member]", brief="administrator")
   @Perms.get_perms("administrator")
   @premium()
   async def uwulock(self, ctx: commands.Context, *, member: NoStaff): 
     if member.bot: return await ctx.send_warning("You can't **uwulock** a bot")
     check = await self.bot.db.fetchrow("SELECT user_id FROM uwulock WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))    
     if check is None: await self.bot.db.execute("INSERT INTO uwulock VALUES ($1,$2)", ctx.guild.id, member.id)
     else: await self.bot.db.execute("DELETE FROM uwulock WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))    
     return await ctx.message.add_reaction("👍🏻")    

   @commands.command(description="force nicknames an user", help="donor", usage="[member] [nickname]\nif none is passed as nickname, the force nickname gets removed", aliases=["fn"], brief="manage nicknames")
   @Perms.get_perms("manage_nicknames")
   @premium()
   async def forcenick(self, ctx: commands.Context, member: NoStaff, *, nick: str): 
             if nick.lower() == "none": 
               check = await self.bot.db.fetchrow("SELECT * FROM forcenick WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))
               if check is None: return await ctx.send_warning(f"**No** forcenick found for {member}")
               await self.bot.db.execute("DELETE FROM forcenick WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))              
               await member.edit(nick=None)
               await ctx.message.add_reaction("👍🏻")
             else: 
               check = await self.bot.db.fetchrow("SELECT * FROM forcenick WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))               
               if check is None: await self.bot.db.execute("INSERT INTO forcenick VALUES ($1,$2,$3)", ctx.guild.id, member.id, nick)
               else: await self.bot.db.execute("UPDATE forcenick SET nickname = '{}' WHERE user_id = {} AND guild_id = {}".format(nick, member.id, ctx.guild.id))  
               await member.edit(nick=nick)
               await ctx.message.add_reaction("👍🏻")  

   @commands.command(description="purges an amount of messages sent by you", help="donor", usage="[amount]")
   @premium()
   async def selfpurge(self, ctx: commands.Context, amount: int):
     mes = [] 
     async for message in ctx.channel.history(): 
      if (len(mes) == amount+1): break 
      if message.author == ctx.author: mes.append(message)
           
     await ctx.channel.delete_messages(mes)   

   @commands.command(description="check the premium perks", help="donor")
   async def perks(self, ctx: commands.Context): 
      embed = discord.Embed(color=self.bot.color, title="", description=">>> **You can acces donor command for boosting our [support server](https://discord.gg/QpKVpXABxx) or with 2$ payment**")
      embed.add_field(name="commands", value="> **steal member's lastfm custom embeds** - embed steal\n" + '\n'.join([f"> **{command.description}** - {command.name}" for command in set(ctx.cog.walk_commands()) if not command.name in [ctx.command.name, 'donate'] and not "discrim" in command.name]) , inline=False) 
      return await ctx.reply(embed=embed) 
 
   @commands.command(description="see how can you become a donator", help="donor", aliases=["payment"])
   async def donate(self, ctx: commands.Context): 
    embed = discord.Embed(color=self.bot.color, title="", description=f">>> **Boost our server for donor, let him cook..**")
    boost = discord.ui.Button(emoji="<:boosts:978686077365800970>")
    view = discord.ui.View(timeout=None)
    
    

    async def boost_callback(interaction: discord.Interaction): 
      await interaction.response.send_message("boost https://discord.gg/QpKVpXABxx for perks and server authorization", ephemeral=True)


    
    boost.callback = boost_callback
    view.add_item(boost)
    await ctx.reply(embed=embed, view=view, mention_author=False)
   

async def setup(bot) -> None:
    await bot.add_cog(Premium(bot))               
