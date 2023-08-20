import discord
from discord.ext import commands
from tools.utils.checks import Perms
from discord.ui import Modal, Select, Button, View

lockemoji = "<:lock:1128623706470625300>"
unlockemoji = "<:unlock:1128623793988972544>"
ghostemoji = "<:ghost:1128310312731422850>"
unghostemoji = "<:unghost:1128310281253163020>"
channelemoji = "<:channel:1128623627638673408>"
plusemoji = "<:plus:1128623746635276370>"
minusemoji = "<:minus:1128623727731552266>"
claimemoji = "<:claim:1128623604075073626>"
manemoji = "<:man:1128623680348491817>"
hammeremoji = "<:gryhammer:1128623651604926504>"

async def check_owner(ctx: commands.Context):
            if ctx.author.voice is None:
               await ctx.bot.ext.send_warning(ctx, "You are not in a voice channel")
            check = await ctx.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", ctx.author.voice.channel.id, ctx.author.id)
            if check is None: 
             await ctx.bot.ext.send_warning(ctx, "You are not the owner of this voice channel")
             return True                

async def check_voice(ctx: commands.Context):
          check = await ctx.bot.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", ctx.guild.id) 
          if check is not None:     
             channeid = check[1]
             voicechannel = ctx.guild.get_channel(channeid)
             category = voicechannel.category 
             if ctx.author.voice is None:
                await ctx.bot.ext.send_warning(ctx, "You are not in a voice channel")
                return True
             elif ctx.author.voice is not None:
                if ctx.author.voice.channel.category != category:
                    await ctx.bot.ext.send_warning(ctx, "You are not in a voice channel created by the bot")
                    return True

async def check_vc(interaction: discord.Interaction, category: discord.CategoryChannel): 
  if interaction.user.voice is None:
    await interaction.client.ext.send_warning(interaction, "You are not in a voice channel", ephemeral=True)
    return False
  elif interaction.user.voice is not None:
      if interaction.user.voice.channel.category != category:
         await interaction.client.ext.send_warning(interaction, "You are not in a voice channel created by the bot", ephemeral=True)
         return False
      return True   

def check_vc_owner(): 
   async def predicate(ctx: commands.Context): 
     voice = await check_voice(ctx)
     owner = await check_owner(ctx)
     if voice is True or owner is True: return False 
     return True 
   return commands.check(predicate)

class vcModal(Modal, title="rename your voice channel"):
       name = discord.ui.TextInput(
        label = "voice channel name",
        placeholder = "give your voice channel a better name",
        style = discord.TextStyle.short,
        required = True
       )
        
       async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        try:
            await interaction.user.voice.channel.edit(name=name)
            await interaction.client.ext.send_success(interaction, f"voice channel renamed to **{name}**", ephemeral=True)
        except Exception as e: await interaction.client.ext.send_error(interaction, f"an error occured - {e}", ephemeral=True)

class vmbuttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="", emoji=lockemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:lock")
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id)
        if not check: return await interaction.client.ext.send_warning(interaction, "VoiceMaster is **not** configured", ephemeral=True)
        elif check:
            channelid = check["channel_id"]
            voicechannel = interaction.guild.get_channel(channelid)
            category = voicechannel.category
            if await check_vc(interaction, category) is False: return
            che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
            if not che: return await interaction.client.ext.send_warning(interaction, "You don't own this voice channel", ephemeral=True)
            elif check:
                await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=False)
                await interaction.client.ext.send_success(interaction, f"locked <#{interaction.user.voice.channel.id}>", ephemeral=True)
    
    @discord.ui.button(label="", emoji=unlockemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:unlock")
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id)
        if not check: return await interaction.client.ext.send_warning(interaction, "VoiceMaster is **not** configured", ephemeral=True)
        elif check:
            channelid = check["channel_id"]
            voicechannel = interaction.guild.get_channel(channelid)
            category = voicechannel.category
            if await check_vc(interaction, category) is False: return
            che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
            if not che: return await interaction.client.ext.send_warning(interaction, "You don't own this voice channel", ephemeral=True)
            elif check:
                await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=True)
                await interaction.client.ext.send_success(interaction, f"unlocked <#{interaction.user.voice.channel.id}>", ephemeral=True)
    
    @discord.ui.button(label="", emoji=ghostemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:hide")
    async def hide(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id)
        if not check: return await interaction.client.ext.send_warning(interaction, "VoiceMaster is **not** configured", ephemeral=True)
        elif check:
            channelid = check["channel_id"]
            voicechannel = interaction.guild.get_channel(channelid)
            category = voicechannel.category
            if await check_vc(interaction, category) is False: return
            che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
            if not che: return await interaction.client.ext.send_warning(interaction, "You don't own this voice channel", ephemeral=True)
            elif check:
                await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, view_channel=False)
                await interaction.client.ext.send_success(interaction, f"hidden <#{interaction.user.voice.channel.id}>", ephemeral=True)
    
    @discord.ui.button(label="", emoji=unghostemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:reveal")
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id)
        if not check: return await interaction.client.ext.send_warning(interaction, "VoiceMaster is **not** configured", ephemeral=True)
        elif check:
            channelid = check["channel_id"]
            voicechannel = interaction.guild.get_channel(channelid)
            category = voicechannel.category
            if await check_vc(interaction, category) is False: return
            che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
            if not che: return await interaction.client.ext.send_warning(interaction, "You don't own this voice channel", ephemeral=True)
            elif check:
                await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, view_channel=True)
                await interaction.client.ext.send_success(interaction, f"revealed <#{interaction.user.voice.channel.id}>", ephemeral=True)
    
    @discord.ui.button(label="", emoji=channelemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:rename")
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id)
        if not check: return await interaction.client.ext.send_warning(interaction, "VoiceMaster is **not** configured", ephemeral=True)
        elif check:
            channelid = check["channel_id"]
            voicechannel = interaction.guild.get_channel(channelid)
            category = voicechannel.category
            if await check_vc(interaction, category) is False: return
            che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
            if not che: return await interaction.client.ext.send_warning(interaction, "You don't own this voice channel", ephemeral=True)
            elif check:
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
                return await interaction.client.ext.send_warning(interaction, "you don't own this voice channel".capitalize(), ephemeral=True)
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 99: return await interaction.client.ext.send_warning(interaction, f"I can't increase the limit for <#{interaction.user.voice.channel.id}>", ephemeral=True)              
              res = limit + 1
              await interaction.user.voice.channel.edit(user_limit=res)
              await interaction.client.ext.send_success(interaction, f"increased <#{interaction.user.voice.channel.id}> limit to **{res}** members", ephemeral=True)

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
                return await interaction.client.ext.send_warning(interaction, "you don't own this voice channel".capitalize(), ephemeral=True)
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 0: return await interaction.client.ext.send_warning(interaction, f"I can't decrease the limit for <#{interaction.user.voice.channel.id}>", ephemeral=True)              
              res = limit - 1
              await interaction.user.voice.channel.edit(user_limit=res)
              await interaction.client.ext.send_success(interaction, f"decreased <#{interaction.user.voice.channel.id}> limit to **{res}** members", ephemeral=True)
    
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
             if member.id == interaction.user.id: return await interaction.client.ext.send_warning(interaction, "You are already the owner of this voice channel", ephemeral=True)
             if member in interaction.user.voice.channel.members: return await interaction.client.ext.send_warning(interaction, "The owner of the voice channel is still here", ephemeral=True)
             else:
                    await interaction.client.db.execute(f"UPDATE vcs SET user_id = $1 WHERE voice = $2", interaction.user.id, interaction.user.voice.channel.id)
                    return await interaction.client.ext.send_success(interaction, "You are the new owner of this voice channel", ephemeral=True)     
    
    @discord.ui.button(label="", emoji=manemoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:info")
    async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
         check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
         if not interaction.user.voice: return await interaction.client.ext.send_warning(interaction, "You are not in a voice channel", ephemeral=True)
         if check is not None:     
             che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", interaction.user.voice.channel.id)
             if che is not None:
                memberid = che["user_id"]   
                member = interaction.guild.get_member(memberid)
                embed = discord.Embed(color=interaction.client.color, title=interaction.user.voice.channel.name, description=f"owner: **{member}** (`{member.id}`)\ncreated: **{discord.utils.format_dt(interaction.user.voice.channel.created_at, style='R')}**\nbitrate: **{interaction.user.voice.channel.bitrate/1000}kbps**\nconnected: **{len(interaction.user.voice.channel.members)} member{'s' if len(interaction.user.voice.channel.members) > 1 else ''}**")    
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
                embed.set_thumbnail(url=member.display_avatar)
                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)                     
    @discord.ui.button(label="", emoji=hammeremoji, style=discord.ButtonStyle.gray, custom_id="persistent_view:manage")
    async def manage(self, interaction: discord.Interaction, button: discord.ui.Button):
         check = await interaction.client.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", interaction.guild.id) 
         if check is not None:     
            channeid = check["channel_id"]
            voicechannel = interaction.guild.get_channel(channeid)
            category = voicechannel.category 
            if await check_vc(interaction, category) is False: return 
            che = await interaction.client.db.fetchrow("SELECT * FROM vcs WHERE voice = $1 AND user_id = $2", interaction.user.voice.channel.id, interaction.user.id)
            if che is None: return await interaction.client.ext.send_warning(interaction, "you don't own this voice channel".capitalize(), ephemeral=True)
            if len(interaction.user.voice.channel.members) == 1: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.warning} {interaction.user.mention}: You are the only person in the voice channel"), ephemeral=True)
            em = discord.Embed(color=interaction.client.color, title="VoiceMaster Moderation Menu", description="Moderate your voice channel using the options below")
            options = [ 
               discord.SelectOption(
                  label="mute",
                  description="mute member in the voice channel",
                  emoji="<:muted:1130421571778007082>"
               ),
               discord.SelectOption(
                  label="unmute",
                  description="unmute members in the voice channel",
                  emoji="<:unmuted:1130421375081910402>"
               ),
               discord.SelectOption(
                  label="deafen",
                  description="deafen members in your voice channel",
                  emoji="<:deafened:1130421608977289299>"
               ),
               discord.SelectOption(
                  label="undeafen",
                  emoji="<:undeafened:1130421530170499093>",
                  description="undeafen members in your voice channel"
               ),
               discord.SelectOption(
                  label="kick",
                  description="kick members from your voice channel",
                  emoji="<:gryhammer:1128623651604926504>"
               )
            ]
            select = discord.ui.Select(options=options, placeholder="select category...")
            members = []
            for member in interaction.user.voice.channel.members:
               if member.id == interaction.user.id: continue
               members.append(discord.SelectOption(label=member.name + "#" + member.discriminator, value=member.id))

            async def select_callback(interactio: discord.Interaction):
               if select.values[0] == "mute":
                  e = discord.Embed(color=interaction.client.color, title="VoiceMaster Moderation | Mute Members", description="mute members in your voice channel")
                  sel = Select(options=members, placeholder="select members...", min_values=1, max_values=len(members))
                  async def sel_callback(interacti: discord.Interaction):
                    for s in sel.values: 
                     await interacti.guild.get_member(int(s)).edit(mute=True, reason=f"muted by {interacti.user}")

                    embede = discord.Embed(color=interaction.client.color, description="{} {}: Muted all members".format(interaction.client.yes, interacti.user.mention))   
                    await interacti.response.edit_message(embed=embede, view=None)

                  sel.callback = sel_callback 
                  
                  vi = View()
                  vi.add_item(sel)
                  await interactio.response.send_message(embed=e, view=vi, ephemeral=True) 

               elif select.values[0] == "unmute":
                  e = discord.Embed(color=interaction.client.color, title="VoiceMaster Moderation | Unmute Members", description="unmute members in your voice channel")
                  sel = Select(options=members, placeholder="select members...", min_values=1, max_values=len(members))
                  async def sel_callback(interacti: discord.Interaction):
                    for s in sel.values: 
                     await interacti.guild.get_member(int(s)).edit(mute=False, reason=f"unmuted by {interacti.user}")

                    embede = discord.Embed(color=interaction.client.color, description="{} {}: Unuted all members".format(interaction.client.yes, interacti.user.mention))   
                    await interacti.response.edit_message(embed=embede, view=None)

                  sel.callback = sel_callback 
                  
                  vi = View()
                  vi.add_item(sel)
                  await interactio.response.send_message(embed=e, view=vi, ephemeral=True)    

               if select.values[0] == "deafen":
                  e = discord.Embed(color=interaction.client.color, title="VoiceMaster Moderation | Deafen Members", description="deafen members in your voice channel")
                  sel = Select(options=members, placeholder="select members...", min_values=1, max_values=len(members))
                  async def sel_callback(interacti: discord.Interaction):
                    for s in sel.values: 
                     await interacti.guild.get_member(int(s)).edit(deafen=True, reason=f"deafened by {interacti.user}")

                    embede = discord.Embed(color=interaction.client.color, description="{} {}: Deafened all members".format(interaction.client.yes, interacti.user.mention))   
                    await interacti.response.edit_message(embed=embede, view=None)

                  sel.callback = sel_callback 
                  
                  vi = View()
                  vi.add_item(sel)
                  await interactio.response.send_message(embed=e, view=vi, ephemeral=True) 

               elif select.values[0] == "undeafen":
                  e = discord.Embed(color=interaction.client.color, title="VoiceMaster Moderation | Undeafen Members", description="undeafen members in your voice channel")
                  sel = Select(options=members, placeholder="select members...", min_values=1, max_values=len(members))
                  async def sel_callback(interacti: discord.Interaction):
                    for s in sel.values: 
                     await interacti.guild.get_member(int(s)).edit(deafen=False, reason=f"undeafened by {interacti.user}")

                    embede = discord.Embed(color=interaction.client.color, description="{} {}: Undeafened all members".format(interaction.client.yes, interacti.user.mention))   
                    await interacti.response.edit_message(embed=embede, view=None)

                  sel.callback = sel_callback 
                  
                  vi = View()
                  vi.add_item(sel)
                  await interactio.response.send_message(embed=e, view=vi, ephemeral=True)    
               
               elif select.values[0] == "kick":
                  e = discord.Embed(color=interaction.client.color, title="VoiceMaster Moderation | Kick Members", description="kick members from your voice channel")
                  sel = Select(options=members, placeholder="select members...", min_values=1, max_values=len(members))
                  async def sel_callback(interacti: discord.Interaction):
                    for s in sel.values: 
                     await interacti.guild.get_member(int(s)).move_to(channel=None, reason="kicked by {}".format(interacti.user))

                    embede = discord.Embed(color=interaction.client.color, description="{} {}: Kicked all members".format(interaction.client.yes, interacti.user.mention))   
                    await interacti.response.edit_message(embed=embede, view=None)

                  sel.callback = sel_callback 
                  
                  vi = View()
                  vi.add_item(sel)
                  await interactio.response.send_message(embed=e, view=vi, ephemeral=True) 

            select.callback = select_callback
            
            view = View()
            view.add_item(select)
            await interaction.response.send_message(embed=em, view=view, ephemeral=True)
    
class VoiceMaster(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
       self.bot = bot

   def create_interface(self, ctx: commands.Context) -> discord.Embed: 
     em = discord.Embed(color=self.bot.color, title="VoiceMaster Interface", description="use the buttons below to control the voice channel")    
     em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
     em.add_field(name="Manage", value=f"{lockemoji} - [`lock`](https://discord.gg/kQcYeuDjvN) the voice channel\n{unlockemoji} - [`unlock`](https://discord.gg/kQcYeuDjvN) the voice channel\n{ghostemoji} - [`hide`](https://discord.gg/kQcYeuDjvN) the voice channel\n{unghostemoji} - [`reveal`](https://discord.gg/kQcYeuDjvN) the voice channel\n{channelemoji} - [`rename`](https://discord.gg/kQcYeuDjvN) the voice channel")
     em.add_field(name="Misc", value=f"{plusemoji} - [`increase`](https://discord.gg/kQcYeuDjvN) the user limit\n{minusemoji} - [`decrease`](https://discord.gg/kQcYeuDjvN) the user limit\n{claimemoji} - [`claim`](https://discord.gg/kQcYeuDjvN) the voice channel\n{manemoji} - [`info`](https://discord.gg/kQcYeuDjvN) of the channel\n{hammeremoji} - [`manage`](https://discord.gg/kQcYeuDjvN) the voice channel")
     return em

   async def get_channel_categories(self, channel: discord.VoiceChannel, member: discord.Member) -> bool: 
     if len(channel.category.channels) == 50: 
      await member.move_to(channel=None)
      try: 
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"sent from {member.guild.name}", disabled=True)) 
        await member.send("I couldn't make a new voice channel", view=view)
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
         try: return await member.move_to(channel=None, reason="member not allowed to join this voice channel")
         except: pass

   @commands.Cog.listener() 
   async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
     check = await self.bot.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", member.guild.id)
     if check:
      jtc = int(check["channel_id"])
      if not before.channel and after.channel: 
       if after.channel.id == jtc: 
        if await self.get_channel_categories(after.channel, member) is True: return
        channel = await member.guild.create_voice_channel(name=f"{member.name}'s channel", category=after.channel.category)#, reason="creating temporary voice channel")
        await channel.set_permissions(member.guild.default_role, connect=True)
        await member.move_to(channel=channel)
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
         cha = await member.guild.create_voice_channel(name=f"{member.name}'s channel", category=after.channel.category)#, reason="creating temporary voice channel")
         await cha.set_permissions(member.guild.default_role, connect=True)
         await member.move_to(channel=cha)
         return await self.bot.db.execute("INSERT INTO vcs VALUES ($1,$2)", member.id, cha.id)  
        elif before.channel.id != after.channel.id: 
         await self.get_channel_overwrites(after.channel, member)
         che = await self.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", before.channel.id)
         if che: 
           if len(before.channel.members) == 0:
            await self.bot.db.execute("DELETE FROM vcs WHERE voice = $1", before.channel.id)
            await before.channel.delete()#reason="no one in the temporary voice channel")                
       else: 
        if after.channel.id == jtc: 
         if await self.get_channel_categories(after.channel, member) is True: return
         cha = await member.guild.create_voice_channel(name=f"{member.name}'s channel", category=after.channel.category)#, reason="creating temporary voice channel")
         await cha.set_permissions(member.guild.default_role, connect=True)
         await member.move_to(channel=cha)
         return await self.bot.db.execute("INSERT INTO vcs VALUES ($1,$2)", member.id, cha.id)
        else:
          await self.get_channel_overwrites(after.channel, member)
          result = await self.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", before.channel.id)
          if result: 
            if len(before.channel.members) == 0:
             await self.bot.db.execute("DELETE FROM vcs WHERE voice = $1", before.channel.id)
             return await before.channel.delete()#reason="no one in the temporary voice channel")        
      elif before.channel and not after.channel: 
       if before.channel.id == jtc: return
       che = await self.bot.db.fetchrow("SELECT * FROM vcs WHERE voice = $1", before.channel.id)
       if che: 
           if len(before.channel.members) == 0:
            await self.bot.db.execute("DELETE FROM vcs WHERE voice = $1", before.channel.id)
            await before.channel.delete()#reason="no one in the temporary voice channel")    
   
   @commands.group(aliases=["vc"], invoke_without_command=True)
   async def voice(self, ctx):
    await ctx.create_pages()
   
   @voice.command(description="lock the voice channel", help="config")
   @check_vc_owner()
   async def lock(self, ctx: commands.Context): 
      await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, connect=False)
      return await ctx.send_success( f"locked <#{ctx.author.voice.channel.id}>")

   @voice.command(description="unlock the voice channel", help="config")
   @check_vc_owner()
   async def unlock(self, ctx: commands.Context):  
      await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, connect=True)
      return await ctx.send_success( f"unlocked <#{ctx.author.voice.channel.id}>")
   
   @voice.command(description="rename the voice channel", help="config", usage="[name]")
   @check_vc_owner()
   async def rename(self, ctx: commands.Context, *, name: str): 
      await ctx.author.voice.channel.edit(name=name)
      return await ctx.send_success( f"voice channel renamed to **{name}**")
   
   @voice.command(description="hide the voice channel", help="config")
   @check_vc_owner()
   async def hide(self, ctx: commands.Context): 
      await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, view_channel=False)
      return await ctx.send_success( f"hidden <#{ctx.author.voice.channel.id}>")   

   @voice.command(description="reveal the voice channel", help="config")
   @check_vc_owner()
   async def reveal(self, ctx: commands.Context): 
      await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, view_channel=True)
      return await ctx.send_success( f"revealed <#{ctx.author.voice.channel.id}>")
   
   @commands.command(description="get an updated version of the voice master interface", help="config")
   @Perms.get_perms("administrator")
   async def interface(self, ctx):
      check = await self.bot.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", ctx.guild.id)
      if not check: return await ctx.send_warning("VoiceMaster is **not** configured")
      await ctx.send(embed=self.create_interface(ctx), view=vmbuttons())
      await ctx.message.delete()
   
   @commands.group(invoke_without_command=True, aliases=["vm"])
   async def voicemaster(self, ctx):
    await ctx.create_pages()
   
   @voicemaster.command(description="configure voicemaster module for your server", help="config")
   @Perms.get_perms("administrator")
   async def setup(self, ctx: commands.Context):
      check = await self.bot.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", ctx.guild.id)
      if check: return await ctx.send_warning("VoiceMaster is **already** configured")
      elif not check:
        category = await ctx.guild.create_category("voice channels")
        overwrite = {ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)}
        text = await ctx.guild.create_text_channel("interface", overwrites=overwrite, category=category)
        vc = await ctx.guild.create_voice_channel("Join to Create", category=category)
        await text.send(embed=self.create_interface(ctx), view=vmbuttons())
        await self.bot.db.execute("INSERT INTO voicemaster VALUES ($1,$2,$3)", ctx.guild.id, vc.id, text.id)
        return await ctx.send_success("VoiceMaster has been configured")
   
   @voicemaster.command(description="remove voicemaster module from your server", help="config")
   @Perms.get_perms("administrator")
   async def remove(self, ctx):
      check = await self.bot.db.fetchrow("SELECT * FROM voicemaster WHERE guild_id = $1", ctx.guild.id)
      if not check: return await ctx.send_warning("VoiceMaster is **not** configured")
      elif check:
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
            await ctx.send_success("VoiceMaster has been deleted")
        except:
            await self.bot.db.execute("DELETE FROM voicemaster WHERE guild_id = $1", ctx.guild.id)
            await ctx.send_success("VoiceMaster has been deleted")
   
   voicemaster.command()
   @commands.is_owner()
   async def view(self, ctx):
        await ctx.send(embed=self.create_interface(ctx), view=vmbuttons())
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(VoiceMaster(bot))