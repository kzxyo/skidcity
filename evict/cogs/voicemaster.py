import discord
from discord.ext import commands
from discord.ui import Modal, Select, View
from patches.permissions import Permissions

unlockemoji = "<:unlock:1263730907680870435>"
lockemoji = "<:lock:1263727069095919698>"
plusemoji = "<:increase:1263731093845315654>"
minusemoji = "<:decrease:1263731510239035442>"
channelemoji = "<:rename:1263727430561169560>"
unghostemoji = "<:reveal:1263731670121709568>"
ghostemoji = "<:hide:1263731781157392396>"
claimemoji = "<:claim:1263731873167708232>"
hammeremoji = "<:moderate:1263727075198763101>"
manemoji = "<:information:1263727043967717428>" 
trashemoji = "<:trash:1263727144832602164>"

async def check_owner(ctx: commands.Context):
            check = await ctx.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", ctx.author.voice.channel.id, ctx.author.id)
            if check is None: 
             await ctx.bot.ext.warning(ctx, "You are not the owner of this voice channel")
             return True                

async def check_voice(ctx: commands.Context):
          check = await ctx.bot.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", ctx.guild.id) 
          if check is not None:     
             channeid = check[1]
             voicechannel = ctx.guild.get_channel(channeid)
             category = voicechannel.category 
             if ctx.author.voice is None:
                await ctx.bot.ext.warning(ctx, "You are not in a voice channel")
                return True
             elif ctx.author.voice is not None:
                if ctx.author.voice.channel.category != category:
                    await ctx.bot.ext.warning(ctx, "You are not in a voice channel created by the bot")
                    return True

async def check_vc(interaction: discord.Interaction, category: discord.CategoryChannel): 
  if interaction.user.voice is None:
    await interaction.client.ext.warning(interaction, "You are not in a voice channel", ephemeral=True)
    return False
  elif interaction.user.voice is not None:
      if interaction.user.voice.channel.category != category:
         await interaction.client.ext.warning(interaction, "You are not in a voice channel created by the bot", ephemeral=True)
         return False
      return True   

def check_vc_owner(): 
   async def predicate(ctx: commands.Context): 
     voice = await check_voice(ctx)
     owner = await check_owner(ctx)
     if voice is True or owner is True: return False 
     return True 
   return commands.check(predicate)       

class vcModal(Modal, title="Rename your voice channel"):
       name = discord.ui.TextInput(
        label="Voice Channel Name",
        placeholder="Give your channel a better name",
        required=True,
        style=discord.TextStyle.short
       )

       async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        try: 
           await interaction.user.voice.channel.edit(name=name)   
           await interaction.client.ext.success(interaction, f"I **renamed** the voice channel to **{name}**.", ephemeral=True)
        except Exception as er: await interaction.client.error(interaction, f"An **error** has occured.\n {er}", ephemeral=True)

class vmbuttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="", emoji=lockemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:lock")    
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
          check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
          if check is not None:     
             channeid = check["channel_id"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if await check_vc(interaction, category) is False: return 
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
             if che is None:
                return await interaction.client.ext.warning(interaction, "You **don't** own this voice channel.", ephemeral=True)
             elif che is not None:
              await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=False)
              await interaction.client.ext.success(interaction, f"I **locked** <#{interaction.user.voice.channel.id}>.", ephemeral=True)   

    @discord.ui.button(label="", emoji=unlockemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:unlock")
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):   
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
        if check is not None:     
             channeid = check["channel_id"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if await check_vc(interaction, category) is False: return 
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
             if che is None:
                return await interaction.client.ext.warning(interaction, "You **don't** own this voice channel.", ephemeral=True)
             elif che is not None:
              await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=True)
              await interaction.client.ext.success(interaction, f"I **unlocked** <#{interaction.user.voice.channel.id}>.", ephemeral=True)

    @discord.ui.button(label="", emoji=unghostemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:reveal")
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
        if check is not None:     
             channeid = check["channel_id"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if await check_vc(interaction, category) is False: return 
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
             if che is None:
                return await interaction.client.ext.warning(interaction, "You **don't** own this voice channel.", ephemeral=True)
             elif che is not None:
              await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, view_channel=True)
              await interaction.client.ext.success(interaction, f"I **revealed** <#{interaction.user.voice.channel.id}>.", ephemeral=True)
      
    @discord.ui.button(label="", emoji=ghostemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:hide")
    async def hide(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
        if check is not None:     
             channeid = check["channel_id"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if await check_vc(interaction, category) is False: return 
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
             if che is None:
                return await interaction.client.ext.warning(interaction, "You **don't** own this voice channel.", ephemeral=True)
             elif che is not None:
              await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, view_channel=False)
              await interaction.client.ext.success(interaction, f"I **hid** <#{interaction.user.voice.channel.id}>.", ephemeral=True)  

    @discord.ui.button(label="", emoji=channelemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:rename")
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button): 
       check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
       if check is not None:     
             channeid = check["channel_id"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if await check_vc(interaction, category) is False: return 
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
             if che is None:
                return await interaction.client.ext.warning(interaction, "You **don't** own this voice channel.", ephemeral=True)
             elif che is not None:
                rename = vcModal()
                await interaction.response.send_modal(rename)
    
    @discord.ui.button(label="", emoji=plusemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:increase")
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
        if check is not None:     
             channeid = check["channel_id"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if await check_vc(interaction, category) is False: return 
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
             if che is None:
                return await interaction.client.ext.warning(interaction, "You **don't** own this voice channel.", ephemeral=True)
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 99: return await interaction.client.ext.warning(interaction, f"I can't increase the limit for <#{interaction.user.voice.channel.id}>", ephemeral=True)              
              res = limit + 1
              await interaction.user.voice.channel.edit(user_limit=res)
              await interaction.client.ext.success(interaction, f"I **increased** <#{interaction.user.voice.channel.id}> limit to **{res}** members.", ephemeral=True)

    @discord.ui.button(label="", emoji=minusemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:decrease")
    async def decrease(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
        if check is not None:     
             channeid = check["channel_id"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if await check_vc(interaction, category) is False: return 
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
             if che is None:
                return await interaction.client.ext.warning(interaction, "You **don't** own this voice channel.", ephemeral=True)
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 0: return await interaction.client.ext.warning(interaction, f"I can't **decrease** the limit for <#{interaction.user.voice.channel.id}>.", ephemeral=True)              
              res = limit - 1
              await interaction.user.voice.channel.edit(user_limit=res)
              await interaction.client.ext.success(interaction, f" I **decreased** <#{interaction.user.voice.channel.id}> limit to **{res}** members.", ephemeral=True)
    
    @discord.ui.button(label="", emoji=claimemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
         check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
         if check is not None:     
             channeid = check["channel_id"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if await check_vc(interaction, category) is False: return 
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", interaction.user.voice.channel.id)             
             memberid = che["user_id"]   
             member = interaction.guild.get_member(memberid)
             if member.id == interaction.user.id: return await interaction.client.ext.warning(interaction, "You are **already** the owner of this voice channel.", ephemeral=True)
             if member in interaction.user.voice.channel.members: return await interaction.client.ext.warning(interaction, "The owner is **still** in the voice channel.", ephemeral=True)
             else:
                    await interaction.client.db.execute(f"UPDATE vcs SET user_id = $1 WHERE voice = $2", interaction.user.id, interaction.user.voice.channel.id)
                    return await interaction.client.ext.success(interaction, "you are the new owner of this voice channel", ephemeral=True)     
    
    @discord.ui.button(label="", emoji=manemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:info")
    async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
         check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
         if not interaction.user.voice: return await interaction.client.ext.warning(interaction, "You are **not** in a voice channel.", ephemeral=True)
         if check is not None:     
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", interaction.user.voice.channel.id)
             if che is not None:
                memberid = che["user_id"]   
                member = interaction.guild.get_member(memberid)
                embed = discord.Embed(color=interaction.client.color, title=interaction.user.voice.channel.name, description=f"owner: **{member}** (`{member.id}`)\ncreated: **{discord.utils.format_dt(interaction.user.voice.channel.created_at, style='R')}**\nbitrate: **{interaction.user.voice.channel.bitrate/1000}kbps**\nconnected: **{len(interaction.user.voice.channel.members)} member{'s' if len(interaction.user.voice.channel.members) > 1 else ''}**")    
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
                embed.set_thumbnail(url=member.display_avatar)
                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)
                
    @discord.ui.button(label="", emoji=trashemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:trash")
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
         check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
         if not interaction.user.voice: return await interaction.client.ext.warning(interaction, "You are **not** in a voice channel.", ephemeral=True)
         che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
         if che is None: return await interaction.client.ext.warning(interaction, "You **don't** own this voice channel.", ephemeral=True)
         if check is not None: await interaction.user.voice.channel.delete()

class voicemaster(commands.Cog):
   def __init__(self, bot: commands.Bot):
        self.bot = bot
   
   def create_interface(self, ctx: commands.Context) -> discord.Embed: 
     em = discord.Embed(color=self.bot.color, title="VoiceMaster Interface", description="Click the buttons below to control the voice channel")    
     em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
     em.set_thumbnail(url=ctx.guild.icon)
     em.add_field(name="Button Usage", value=f"{lockemoji} — Lock the voice channel\n{unlockemoji} — Unlock the voice channel\n{ghostemoji} — Hide the voice channel\n{unghostemoji} — Reveal the voice channel\n{channelemoji} — Rename the voice channel\n{plusemoji} — Increase the user limit\n{minusemoji} — Decrease the user limit\n{claimemoji} — Claim the voice channel\n{manemoji} — Info of the channel\n{trashemoji} — Delete the voice channel")
     return em

   async def get_channel_categories(self, channel: discord.VoiceChannel, member: discord.Member) -> bool: 
     if len(channel.category.channels) == 50: 
      await member.move_to(channel=None)
      try: 
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"sent from {member.guild.name}", disabled=True)) 
        await member.send("I **couldn't** make a new voice channel as the category is full of channels.", view=view)
      except: pass 
     return len(channel.category.channels) == 50   
   
   async def get_channel_overwrites(self, channel: discord.VoiceChannel, member: discord.Member) -> bool:  
    if member.bot: return
    che = await self.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", channel.id)
    if che: 
     if che['user_id'] == member.id: return
     if channel.overwrites_for(channel.guild.default_role).connect == False: 
      if member not in channel.overwrites and member.id != member.guild.owner_id:
        if not channel.overwrites_for(member).connect == True:
         try: return await member.move_to(channel=None, reason="not allowed to join this voice channel")
         except: pass

   @commands.Cog.listener()
   async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
     
     naughty = await self.bot.db.fetchrow("SELECT * FROM naughtycorner_members WHERE guild_id = $1 AND user_id = $2", member.guild.id, member.id)
     if naughty: return
     check = await self.bot.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", member.guild.id)
     
     if check:
      jtc = int(check["channel_id"])
      
      if not before.channel and after.channel: 
       
       if after.channel.id == jtc: 
        if await self.get_channel_categories(after.channel, member) is True: return
        
        channel = await member.guild.create_voice_channel(name=f"{member.name}'s channel", category=after.channel.category, reason="creating temporary voice channel")
        
        try:
       
             await channel.set_permissions(member.guild.default_role, connect=True)
             await member.move_to(channel=channel)
        
        except: await channel.delete() 
        
        return await self.bot.db.execute("INSERT INTO vcs VALUES ($1,$2)", member.id, channel.id)
       
       else: return await self.get_channel_overwrites(after.channel, member)          
      
      elif before.channel and after.channel: 
       
       if before.channel.id == jtc: return 
       if before.channel.category == after.channel.category: 
        if after.channel.id == jtc: 
         
         che = await self.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", before.channel.id)
         
         if che: 
           if len(before.channel.members) == 0: return await member.move_to(channel=before.channel) 
         if await self.get_channel_categories(after.channel, member) is True: return
         
         cha = await member.guild.create_voice_channel(name=f"{member.name}'s channel", category=after.channel.category, reason="creating temporary voice channel")
         await self.bot.db.execute("INSERT INTO vcs VALUES ($1,$2)", member.id, channel.id)
         
         try:
             await cha.set_permissions(member.guild.default_role, connect=True)
             await member.move_to(channel=cha)
         except: await cha.delete() 
        
        elif before.channel.id != after.channel.id: 
         await self.get_channel_overwrites(after.channel, member)
         
         che = await self.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", before.channel.id)
         if che: 
           
           if len(before.channel.members) == 0:
            await self.bot.db.execute("DELETE FROM vcs WHERE voice = $1", before.channel.id)
            await before.channel.delete(reason="no one in the temporary voice channel")                
       else: 
        
        if after.channel.id == jtc: 
         if await self.get_channel_categories(after.channel, member) is True: return
         cha = await member.guild.create_voice_channel(name=f"{member.name}'s Channel", category=after.channel.category, reason="creating temporary voice channel")
         
         try:
             await self.bot.db.execute("INSERT INTO vcs VALUES ($1,$2)", member.id, channel.id)
             await cha.set_permissions(member.guild.default_role, connect=True)
             await member.move_to(channel=cha)
         except: await cha.delete()
        
        else:
          
          await self.get_channel_overwrites(after.channel, member)
          result = await self.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", before.channel.id)
          if result: 
            
            if len(before.channel.members) == 0:
             
             await self.bot.db.execute("DELETE FROM vcs WHERE voice = $1", before.channel.id)
             return await before.channel.delete(reason="no one in the temporary voice channel")        
      
      elif before.channel and not after.channel: 
       if before.channel.id == jtc: return
       
       che = await self.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", before.channel.id)
       if che: 
           
           if len(before.channel.members) == 0:
            
            await self.bot.db.execute("DELETE FROM vcs WHERE voice = $1", before.channel.id)
            await before.channel.delete(reason="no one in the temporary voice channel")    

   @commands.group(aliases=["vc"], invoke_without_command=True)
   async def voice(self, ctx): 
      await ctx.create_pages()

   @voice.command(description="lock the voice channel", brief="vc owner")
   @check_vc_owner()
   async def lock(self, ctx: commands.Context):  
      await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, connect=False)
      return await ctx.success( f"I have **locked** <#{ctx.author.voice.channel.id}>")

   @voice.command(description="unlock the voice channel", brief="vc owner")
   @check_vc_owner()
   async def unlock(self, ctx: commands.Context):  
      await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, connect=True)
      return await ctx.success( f"I have **unlocked** <#{ctx.author.voice.channel.id}>")
   
   @voice.command(description="rename the voice channel", usage="[name]", brief="vc owner")
   @check_vc_owner()
   async def rename(self, ctx: commands.Context, *, name: str): 
      await ctx.author.voice.channel.edit(name=name)
      return await ctx.success( f"I have **renamed** voice channel to **{name}**")

   @voice.command(description="hide the voice channel", brief="vc owner")
   @check_vc_owner()
   async def hide(self, ctx: commands.Context): 
      await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, view_channel=False)
      return await ctx.success( f"I have **hid** {ctx.author.voice.channel.mention}.")   

   @voice.command(description="reveal the voice channel", brief="vc owner")
   @check_vc_owner()
   async def reveal(self, ctx: commands.Context): 
      await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, view_channel=True)
      return await ctx.success( f"I have **revealed** {ctx.author.voice.channel.mention}.")

   @voice.command(description="let someone join your locked voice channel", usage="[member]", brief="vc owner")
   @check_vc_owner()
   async def permit(self, ctx: commands.Context, *, member: discord.Member): 
      await ctx.author.voice.channel.set_permissions(member, connect=True)
      return await ctx.success( f"**{member}** is allowed to join {ctx.author.voice.channel.mention}.")
   
   @voice.command(description="restrict someone from joining your voice channel", usage="[member]", brief="vc owner")
   @check_vc_owner()
   async def reject(self, ctx: commands.Context, *, member: discord.Member):  
      if member.id == ctx.author.id: return await ctx.reply("You **cannot** kick yourself.")  
      if member in ctx.author.voice.channel.members: await member.move_to(channel=None)
      await ctx.author.voice.channel.set_permissions(member, connect=False)
      return await ctx.success( f"**{member}** not is allowed to join {ctx.author.voice.channel.mention} anymore.")
   
   @voice.command(name="kick", description="kick a member from your voice channel", usasge="[member]", brief="vc owner")
   @check_vc_owner()
   async def vc_kick(self, ctx: commands.Context, *, member: discord.Member): 
     if member.id == ctx.author.id: return await ctx.reply("you **cannot** kick yourself")  
     if not member in ctx.author.voice.channel.members: return await ctx.error(f"**{member}** isn't in **your** voice channel") 
     await member.move_to(channel=None, reason=f"{ctx.member} is **not** allowed to join this voice channel.")
     return await ctx.success( f"**{member}** got kicked from {ctx.author.voice.channel.mention}.")
   
   @voice.command(description="claim the voice channel ownership")
   async def claim(self, ctx: commands.Context): 
    if not ctx.author.voice: return await ctx.warning("You are **not** in a voice channel")  
    check = await self.bot.db.fetchrow("SELECT user_id FROM vcs WHERE voice = $1", ctx.author.voice.channel.id) 
    if not check: return await ctx.warning("You are **not** in a voice channel made by the bot.")
    if ctx.author.id == check[0]: return await ctx.warning("You are now the **owner** of this voice channel.")
    if check[0] in [m.id for m in ctx.author.voice.channel.members]: return await ctx.warning("The owner is **still** in the voice channel.")
    await self.bot.db.execute("UPDATE vcs SET user_id = $1 WHERE voice = $2", ctx.author.voice.channel.id, ctx.author.voice.channel.id) 
    return await ctx.success("**You** are the new owner of this voice channel.") 

   @voice.command(description="transfer the voice channel ownership to another member", usage="[member]", brief="vc owner")
   @check_vc_owner()
   async def transfer(self, ctx: commands.Context, *, member: discord.Member): 
     if not member in ctx.author.voice.channel.members: return await ctx.warning(f"**{member}** is not in your voice channel")
     if member == ctx.author: return await ctx.warning("You are already the **owner** of this **voice channel**.")
     await self.bot.db.execute("UPDATE vcs SET user_id = $1 WHERE voice = $2", member.id, ctx.author.voice.channel.id) 
     return await ctx.success(f"I have **transfered** the voice ownership to **{member}**.")

   @commands.command(description="sends an updated interface of voicemaster", brief="administrator")
   @Permissions.has_permission(administrator=True)
   async def interface(self, ctx: commands.Context): 
      check = await self.bot.db.execute("SELECT * FROM voicemaster WHERE guild_id = $1", ctx.guild.id)
      if check is None: return await ctx.warning("The voicemaster **isn't*** configured.")      
      await ctx.send(embed=self.create_interface(ctx), view=vmbuttons())
      await ctx.message.delete()
   
   @commands.group(invoke_without_command=True, aliases=["vm", "jtc"])
   async def voicemaster(self, ctx): 
      await ctx.create_pages()   

   @voicemaster.command(description="sets voicemaster module for your server", brief="administrator")
   @Permissions.has_permission(administrator=True)
   async def setup(self, ctx: commands.Context):
      check = await self.bot.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", ctx.guild.id)
      if check is not None: return await ctx.warning("The voicemaster is **already** configured.") 
      elif check is None:                   
        category = await ctx.guild.create_category("voice channels")
        overwrite = {ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)}          
        text = await ctx.guild.create_text_channel("interface", category=category, overwrites=overwrite)
        vc = await ctx.guild.create_voice_channel("Join to Create", category=category)
        await text.send(embed=self.create_interface(ctx), view=vmbuttons())
        await self.bot.db.execute("INSERT INTO voicemaster VALUES ($1,$2,$3)", ctx.guild.id, vc.id, text.id)
        return await ctx.success("I have configured the voicemaster interface.")    

   @voicemaster.command(description="remove voicemaster module from your server", aliases=["unset"], brief="administrator")
   @Permissions.has_permission(administrator=True)
   async def remove(self, ctx: commands.Context):
         check = await self.bot.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", ctx.guild.id)
         if check is None: return await ctx.warning("The voicemaster is not configured.") 
         elif check is not None:
            try:
             channelid = check["channel_id"]
             interfaceid = check["interface"]
             channel2 = ctx.guild.get_channel(interfaceid)
             channel = ctx.guild.get_channel(channelid)
             category = channel.category
             channels = category.channels
             for chan in channels:
                try: await chan.delete()
                except: continue

             await category.delete()    
             await channel2.delete()      
             await self.bot.db.execute("DELETE FROM voicemaster WHERE guild_id = $1", ctx.guild.id)
             await ctx.success("The voicemaster module has been disabled.")
            except:
             await self.bot.db.execute("DELETE FROM voicemaster WHERE guild_id = $1", ctx.guild.id)
             await ctx.success("The voicemaster module has been disabled.")  

async def setup(bot) -> None:
    await bot.add_cog(voicemaster(bot))       