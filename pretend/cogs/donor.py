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

    @discord.ui.button(emoji="<:left:1018156480991612999>", style=discord.ButtonStyle.blurple)
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

    @discord.ui.button(emoji="<:right:1018156484170883154>", style=discord.ButtonStyle.blurple)
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
      await ctx.send_warning("Donator only")
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
   
   async def assign_0001(self, member: discord.Member): 
      check = await self.bot.db.fetchrow("SELECT role_id FROM discrim WHERE guild_id = $1", member.guild.id)
      if check: 
        role = member.guild.get_role(int(check['role_id']))
        if not role: return await self.bot.db.execute("DELETE FROM discrim WHERE guild_id = $1", member.guild.id)
        if role in member.roles: return
        try: await member.add_roles(role, reason="member has a good 0001 discriminator name") 
        except: pass 
    
   async def remove_0001(self, member: discord.Member): 
      check = await self.bot.db.fetchrow("SELECT role_id FROM discrim WHERE guild_id = $1", member.guild.id)
      if check: 
        role = member.guild.get_role(int(check['role_id']))
        if not role: return await self.bot.db.execute("DELETE FROM discrim WHERE guild_id = $1", member.guild.id)
        if not role in member.roles: return
        try: await member.remove_roles(role, reason="member removed a good 0001 discriminator name") 
        except: pass   
   
   async def chat(self, prompt: str) -> str:
    headers = {"Content-Type": "application/json",  "Authorization": f"Bearer {self.chatgpt_api}"}
    data = {"prompt": prompt, "max_tokens": 1024, "temperature": 0.7,  "stop": None}
    url = "https://api.openai.com/v1/engines/text-davinci-002/completions"
    response_json = await self.bot.session.post_json(url, json=data, headers=headers)
    try: return response_json["choices"][0]["text"].strip()
    except: return None

   @commands.Cog.listener()
   async def on_member_update(self, before: discord.Member, after: discord.Member): 
    if before.name + "#" + before.discriminator == after.name + "#" + after.discriminator: return 
    if before.discriminator != after.discriminator: 
      if after.discriminator == "0001" and checktag(after.name) is True: return await self.assign_0001(after)
      elif before.discriminator == "0001": return await self.remove_0001(before)
    else: 
     if before.discriminator == "0001": 
      if not checktag(before.name) and checktag(after.name) is True: return await self.assign_0001(after)
      if checktag(before.name) is True and not checktag(after.name): return await self.remove_0001(before)    

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
       if len(webhooks) == 0: webhook = await message.channel.create_webhook(name="pretend - uwulock", reason="for uwulock")
       else: webhook = webhooks[0] 
       await webhook.send(content=uwumsg, username=message.author.name, avatar_url=message.author.display_avatar.url)
     except: pass 

   @commands.command(aliases=["ask", "chat"], description="ask chatgpt a question", help="utility", usage="[message]")
   @premium()
   async def chatgpt(self, ctx: commands.Context, *, message: str):
     await ctx.typing()
     mes = await self.chat(message)
     if not mes: return await ctx.send_warning("Chat GPT couldn't return a response")
     return await ctx.reply(mes) 
     
   @commands.command(description="revoke the hardban from an user", help="donor", usage="[user]", brief="ban_members")
   @Perms.get_perms("ban_members")
   @premium()
   async def hardunban(self, ctx: commands.Context, *, member: discord.User):     
      che = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = {} AND banned = {}".format(ctx.guild.id, member.id))      
      if che is None: return await ctx.send_warning(f"{member} is **not** hardbanned") 
      await self.bot.db.execute("DELETE FROM hardban WHERE guild_id = {} AND banned = {}".format(ctx.guild.id, member.id))
      await ctx.guild.unban(member, reason="unhardbanned by {}".format(ctx.author.mention)) 
      await ctx.message.add_reaction("<:catthumbsup:974982144021626890>")   
   
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
      if member.id == self.bot.user.id: return await ctx.reply("leave me alone <:angry:1037460375223939112>")
      if await Mod.check_hieracy(ctx, member):   
       che = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = {} AND banned = {}".format(ctx.guild.id, member.id))
       if che is not None: return await ctx.send_warning(f"**{member}** has been hardbanned by **{await self.bot.fetch_user(che['author'])}**")
       await ctx.guild.ban(member, reason="hardbanned by {}".format(ctx.author))
       await self.bot.db.execute("INSERT INTO hardban VALUES ($1,$2,$3)", ctx.guild.id, member.id, ctx.author.id)
       await ctx.message.add_reaction("<:catthumbsup:974982144021626890>")
  
   @commands.command(description="uwuify a person's messages", help="donor", usage="[member]", brief="administrator")
   @Perms.get_perms("administrator")
   @premium()
   async def uwulock(self, ctx: commands.Context, *, member: NoStaff): 
     if member.bot: return await ctx.send_warning("You can't **uwulock** a bot")
     check = await self.bot.db.fetchrow("SELECT user_id FROM uwulock WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))    
     if check is None: await self.bot.db.execute("INSERT INTO uwulock VALUES ($1,$2)", ctx.guild.id, member.id)
     else: await self.bot.db.execute("DELETE FROM uwulock WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))    
     return await ctx.message.add_reaction("<:catthumbsup:974982144021626890>")    

   @commands.command(description="force nicknames an user", help="donor", usage="[member] [nickname]\nif none is passed as nickname, the force nickname gets removed", aliases=["locknick"], brief="manage nicknames")
   @Perms.get_perms("manage_nicknames")
   @premium()
   async def forcenick(self, ctx: commands.Context, member: NoStaff, *, nick: str): 
             if nick.lower() == "none": 
               check = await self.bot.db.fetchrow("SELECT * FROM forcenick WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))
               if check is None: return await ctx.send_warning(f"**No** forcenick found for {member}")
               await self.bot.db.execute("DELETE FROM forcenick WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))              
               await member.edit(nick=None)
               await ctx.message.add_reaction("<:catthumbsup:974982144021626890>")
             else: 
               check = await self.bot.db.fetchrow("SELECT * FROM forcenick WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))               
               if check is None: await self.bot.db.execute("INSERT INTO forcenick VALUES ($1,$2,$3)", ctx.guild.id, member.id, nick)
               else: await self.bot.db.execute("UPDATE forcenick SET nickname = '{}' WHERE user_id = {} AND guild_id = {}".format(nick, member.id, ctx.guild.id))  
               await member.edit(nick=nick)
               await ctx.message.add_reaction("<:catthumbsup:974982144021626890>")  

   @commands.command(description="find names with certain discriminators" ,help="donor", usage="[discriminator]", aliases=["tags"])
   @premium()
   async def lookup(self, ctx, tag: str="0001"):
                try: 
                  t = int(tag) 
                  type = "int"
                except : 
                  t = str(tag) 
                  type = "str"

                data = await get_tags(self.bot, type, tag)
                i=0
                k=1
                l=0
                number = []
                messages = []
                num = 0
                auto = ""  
                if data:
                    for table in data:                                          
                        username = table[0]
                        if checktag(username) is False: continue
                        discrim = table[1]
                        num += 1
                        auto += f"\n`{num}` {username}#{discrim}: <t:{int(table[2])}:R> "
                        k+=1
                        l+=1
                        if l == 10:
                          messages.append(auto)
                          number.append(discord.Embed(color=self.bot.color, title="Searches by tag" if type == "int" else "Searches by name", description=auto).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar))
                          i+=1
                          auto = ""
                          l=0
                    messages.append(auto)
                    embed = discord.Embed(color=self.bot.color, title="Searches by tag" if type == "int" else "Searches by name", description=auto).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                    number.append(embed)
                    await ctx.paginator(number) 
                else: return await ctx.send_warning(f"no **{tag}** tags available") 

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
      embed = discord.Embed(color=self.bot.color, title="donator perks", description="Perks for the donators. Boost **1** time or donate **5$** to have access to these perks")
      embed.add_field(name="commands", value="**embed steal** - steal member's lastfm custom embeds\n" + '\n'.join([f"**{command.name}** - {command.description}" for command in set(ctx.cog.walk_commands()) if not command.name in [ctx.command.name, 'donate'] and not "discrim" in command.name]), inline=False) 
      return await ctx.reply(embed=embed) 
 
   @commands.command(description="see how can you become a donator", help="donor", aliases=["payment"])
   async def donate(self, ctx: commands.Context): 
    embed = discord.Embed(color=self.bot.color, title="donation methods", description=f"<:paypal:1055055000490999890> - [`sentontop`](https://paypal.me/sentontop)\n<:boosts:978686077365800970> - [`/pretend`](https://discord.gg/pretend)\n<a:cashapp:1093815946726084618> - [`$Kabranch04`](https://cash.app/$Kabranch04)\n<:bitcoin:1060948162178732052> - `bc1qmlrv4c3g5aucmjqka8h86rflfgp2skqnh5jjv8`\n<:eth:1060948163961290902> - `0xf85357CA8eCB7B2BAee0d55DD527692d36e3184d`\nBoosting will only get you access to premium perks. If you want a server authorization, please use the other payment methods. Once sent, include your discord tag and id in the payment note (ex: sent#0001 {self.bot.owner_ids[0]})")
    paypal = discord.ui.Button(emoji="<:paypal:1055055000490999890>")
    boost = discord.ui.Button(emoji="<:boosts:978686077365800970>")
    cashapp = discord.ui.Button(emoji="<a:cashapp:1093815946726084618>")
    btc = discord.ui.Button(emoji="<:bitcoin:1060948162178732052>")
    eth = discord.ui.Button(emoji="<:eth:1060948163961290902>")
    view = discord.ui.View(timeout=None)
    
    async def paypal_callback(interaction: discord.Interaction): 
      await interaction.response.send_message("https://paypal.me/sentontop", ephemeral=True)

    async def boost_callback(interaction: discord.Interaction): 
      await interaction.response.send_message("boost https://discord.gg/pretend for perks", ephemeral=True)

    async def cashapp_callback(interaction: discord.Interaction): 
      await interaction.response.send_message("https://cash.app/$Kabranch04", ephemeral=True)

    async def btc_callback(interaction: discord.Interaction): 
      await interaction.response.send_message("`bc1qmlrv4c3g5aucmjqka8h86rflfgp2skqnh5jjv8`", ephemeral=True)  

    async def eth_callback(interaction: discord.Interaction): 
      await interaction.response.send_message("`0xf85357CA8eCB7B2BAee0d55DD527692d36e3184d`", ephemeral=True)       
    
    paypal.callback = paypal_callback
    boost.callback = boost_callback
    cashapp.callback = cashapp_callback
    btc.callback = btc_callback
    eth.callback = eth_callback 
    
    view.add_item(paypal)
    view.add_item(boost)
    view.add_item(cashapp)
    view.add_item(btc)
    view.add_item(eth)
    await ctx.reply(embed=embed, view=view, mention_author=False)
   
   @commands.group(invoke_without_command=True, aliases=["discriminator"], description="role users that have a 'clean' 0001 discriminator")
   async def discrim(self, ctx): 
    return await ctx.create_pages()
   
   @discrim.command(name="refresh", help="donor", description="add the discrim role to any eligible member if any", brief="manage guild") 
   @Perms.get_perms("manage_guild")
   async def discrim_refresh(self, ctx: commands.Context): 
    check = await self.bot.db.fetchrow("SELECT * FROM discrim WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.send_warning("Discrim role not found")
    role = ctx.guild.get_role(int(check['role_id']))
    if not role: return await ctx.send_error("Role not found")
    mes = await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"Adding {role.mention} to all eligible members...."))
    for member in role.members: 
      if member.discriminator != "0001": 
        try: await member.remove_roles(role, reason="member doesn't have a good 0001 discriminator name anymore")   
        except: continue  
    for member in [m for m in ctx.guild.members if m.discriminator == "0001"]:
     if checktag(member.name) is True:  
      try: await member.add_roles(role, reason="member has a good 0001 discriminator name") 
      except: continue
    await mes.edit(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: Added the role to all eligible members"))  

   @discrim.command(name="add", help="donor", usage="[role]", description="add a role that will get assigned to members with a 0001 discriminator", brief="manage guild")
   @Perms.get_perms("manage_guild")
   async def discrim_add(self, ctx: commands.Context, *, role: GoodRole): 
     check = await self.bot.db.fetchrow("SELECT * FROM discrim WHERE guild_id = $1", ctx.guild.id)
     if check: await self.bot.db.execute("UPDATE discrim set role_id = $1 WHERE guild_id = $2", role.id, ctx.guild.id) 
     else: await self.bot.db.execute("INSERT INTO discrim VALUES ($1,$2)", ctx.guild.id, role.id)
     await ctx.send_success(f"{role.mention} will be assigned to anyone with a 0001 discriminator from now")

   @discrim.command(name="remove", help="donor", description="remove the discrim role", brief="manage guild")
   @Perms.get_perms("manage_guild")   
   async def discrim_remove(self, ctx: commands.Context): 
    check = await self.bot.db.fetchrow("SELECT * FROM discrim WHERE guild_id = $1", ctx.guild.id)
    if not check: return await ctx.send_warning("Discrim role not found")
    await self.bot.db.execute("DELETE FROM discrim WHERE guild_id = $1", ctx.guild.id)
    await ctx.send_success("Removed discrim feature") 

   @discrim.command(name="role", help="donor", description="returns the discrim role", brief="manage guild")
   async def discrim_role(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM discrim WHERE guild_id = $1", ctx.guild.id)
     if not check: return await ctx.send_warning("Discrim role not found")
     role = ctx.guild.get_role(int(check['role_id']))
     if not role: 
       await ctx.send_warning("Discrim role not found")
       return await self.bot.db.execute("DELETE FROM discrim WHERE guild_id = $1", ctx.guild.id)
     embed = discord.Embed(color=self.bot.color, description=f"Discrim role -> {role.mention}")
     return await ctx.reply(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Premium(bot))               
