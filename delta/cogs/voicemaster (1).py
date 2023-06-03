import discord, json
from discord.ext import commands
from discord.ui import Modal, Select, View
from pymongo import MongoClient 

with open("./config.json") as f:
    data = json.load(f)
    mongo = data["mongo"]

cluster = MongoClient(mongo)
db = cluster["noob"]

class vcModal(Modal, title="rename your voice channel"):
       name = discord.ui.TextInput(
        label="voice channel name",
        placeholder="give your channel a better name",
        required=True,
        style=discord.TextStyle.short
       )

       async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        try: 
           await interaction.user.voice.channel.edit(name=name)   
           e = discord.Embed(color=0x2f3136, description=f"{interaction.user.mention} voice channel renamed to **{name}**")
           await interaction.response.send_message(embed=e, ephemeral=True)
        except:
            em = discord.Embed(color=discord.Color.red(), description=f"{interaction.user.mention} an error occured")
            await interaction.response.send_message(embed=em, ephemeral=True)  

class vmbuttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="", emoji="<:icons_lock:1049009150140616784>", style=discord.ButtonStyle.gray, custom_id="persistent_view:lock")    
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
             collection = db["voicemaster"]
             check = collection.find_one({"_id": interaction.guild.id}) 
             channeid = check["channel"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel__")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel created by the bot__")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             col = db["owners"]
             che = col.find_one({"_id": interaction.user.voice.channel.id, "member": interaction.user.id})
             if che is None:
                embe = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you don't **own** this __voice channel__")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(connect=False)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=0x2f3136, description=f"> {interaction.user.mention} locked __ <#{interaction.user.voice.channel.id}> __")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:icons_unlock:1049009041919197284>", style=discord.ButtonStyle.gray, custom_id="persistent_view:unlock")
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):   
             collection = db["voicemaster"]
             check = collection.find_one({"_id": interaction.guild.id}) 
             channeid = check["channel"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel__")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel__ created by the **bot**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             col = db["owners"]
             che = col.find_one({"_id": interaction.user.voice.channel.id, "member": interaction.user.id})
             if che is None:
                embe = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you don't **own** this __voice channel__")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(connect=True)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=0x2f3136, description=f"> {interaction.user.mention} unlocked __ <#{interaction.user.voice.channel.id}> __")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:icons__on:1049012483312062544>", style=discord.ButtonStyle.gray, custom_id="persistent_view:reveal")
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
             collection = db["voicemaster"]
             check = collection.find_one({"_id": interaction.guild.id}) 
             channeid = check["channel"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel__")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel__ created by the **bot**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             col = db["owners"]
             che = col.find_one({"_id": interaction.user.voice.channel.id, "member": interaction.user.id})
             if che is None:
                embe = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you don't __own__ this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=0x2f3136, description=f"> {interaction.user.mention} unlocked __ <#{interaction.user.voice.channel.id}> __")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
      
    @discord.ui.button(label="", emoji="<:icons_off:1049012436382003210>", style=discord.ButtonStyle.gray, custom_id="persistent_view:hide")
    async def hide(self, interaction: discord.Interaction, button: discord.ui.Button):
             collection = db["voicemaster"]
             check = collection.find_one({"_id": interaction.guild.id}) 
             channeid = check["channel"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel__ created by the **bot**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             col = db["owners"]
             che = col.find_one({"_id": interaction.user.voice.channel.id, "member": interaction.user.id})
             if che is None:
                embe = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you don't _own_ this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=0x2f3136, description=f"> {interaction.user.mention} unlocked __ <#{interaction.user.voice.channel.id}> __")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)   

    @discord.ui.button(label="", emoji="<:icons_richpresence:1049046415722156183>", style=discord.ButtonStyle.gray, custom_id="persistent_view:rename")
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button): 
            collection = db["voicemaster"]
            check = collection.find_one({"_id": interaction.guild.id}) 
            channeid = check["channel"]
            voicechannel = interaction.guild.get_channel(channeid)
            category = voicechannel.category 
            if interaction.user.voice is None:
                e = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel__")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
            elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel created by the bot__")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

            col = db["owners"]
            che = col.find_one({"_id": interaction.user.voice.channel.id, "member": interaction.user.id})
            if che is None:
                embe = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} __you don't own this voice channel__")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
            elif che is not None:
                rename = vcModal()
                await interaction.response.send_modal(rename)
    
    @discord.ui.button(label="", emoji="<:icons_plus:1049047366084345988>", style=discord.ButtonStyle.gray, custom_id="persistent_view:increase")
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
             collection = db["voicemaster"]
             check = collection.find_one({"_id": interaction.guild.id}) 
             channeid = check["channel"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __**voice channel**__")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel__ created by the **bot**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             col = db["owners"]
             che = col.find_one({"_id": interaction.user.voice.channel.id, "member": interaction.user.id})
             if che is None:
                embe = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you don't __own__ this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 99:
                emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} i can't increase the limit for __ <#{interaction.user.voice.channel.id}> __")
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                return
              
              res = limit + 1
              await interaction.user.voice.channel.edit(user_limit=res)
              emb = discord.Embed(color=0x2f3136, description=f"> {interaction.user.mention} increased __ <#{interaction.user.voice.channel.id}> __ limit to **{res}** members")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:icons_minus:1049048527701032963>", style=discord.ButtonStyle.gray, custom_id="persistent_view:decrease")
    async def decrease(self, interaction: discord.Interaction, button: discord.ui.Button):
             collection = db["voicemaster"]
             check = collection.find_one({"_id": interaction.guild.id}) 
             channeid = check["channel"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> **{interaction.user.mention}** you are not in a __voice channel__")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a __voice channel__ created by the **bot**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             col = db["owners"]
             che = col.find_one({"_id": interaction.user.voice.channel.id, "member": interaction.user.id})
             if che is None:
                embe = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> **{interaction.user.mention}** you don't own this __voice channel__")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 0:
                emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> **{interaction.user.mention}** i can't decrease the limit for __ <#{interaction.user.voice.channel.id}>__")
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                return
              
              res = limit - 1
              await interaction.user.voice.channel.edit(user_limit=res)
              emb = discord.Embed(color=0x2f3136, description=f"> **{interaction.user.mention}** decreased __ <#{interaction.user.voice.channel.id}> __ limit to **{res}** members")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)          
    
    @discord.ui.button(label="", emoji="<:icons_owner:1049049388766470234>", style=discord.ButtonStyle.gray, custom_id="persistent_view:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
             collection = db["voicemaster"]
             check = collection.find_one({"_id": interaction.guild.id}) 
             channeid = check["channel"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> __{interaction.user.mention}__ you are not in a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0xffff00, description=f"> <:emoji_7:1048996990706524322> __{interaction.user.mention}__ you are not in a _voice channel_ created by the **bot**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return
             col = db["owners"]
             che = col.find_one({"_id": interaction.user.voice.channel.id})
             if che is not None:
                memberid = che["member"]   
                member = interaction.guild.get_member(memberid)
                if member in interaction.user.voice.channel.members:
                    embed = discord.Embed(color=0xffff00, description=f"<:emoji_7:1048996990706524322> {interaction.user.mention} the owner is still in the voice channel")
                    await interaction.response.send_message(embed=embed, ephemeral=True, view=None)
                else:
                    col.update_one({"_id": interaction.user.voice.channel.id}, {'$set': {"member": interaction.user.id}})
                    embed = discord.Embed(color=0x2f3136, description=f"{interaction.user.mention} you now own {interaction.user.voice.channel.mention}")
                    await interaction.response.send_message(embed=embed, view=None, ephemeral=True)        
    
    @discord.ui.button(label="", emoji="<:icons_todolist:1049050116281090079>", style=discord.ButtonStyle.gray, custom_id="persistent_view:info")
    async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
             collection = db["voicemaster"]
             check = collection.find_one({"_id": interaction.guild.id}) 
             channeid = check["channel"]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0xffff00, description=f"<:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0xffff00, description=f"<:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return
             col = db["owners"]
             che = col.find_one({"_id": interaction.user.voice.channel.id})
             if che is not None:
                memberid = che["member"]   
                member = interaction.guild.get_member(memberid)
                embed = discord.Embed(color=0x2f3136, title=interaction.user.voice.channel.name, description=f"owner: **{member}** (`{member.id}`)\ncreated: <t:{int(interaction.user.voice.channel.created_at.timestamp())}:R>\nbitrate: **{interaction.user.voice.channel.bitrate/1000}kbps**\nconnected: **{len(interaction.user.voice.channel.members)}**")    
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
                embed.set_thumbnail(url=member.display_avatar)
                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)  
    
    #@discord.ui.button(label="", emoji="<:icons_activities:1049051379441881159>", style=discord.ButtonStyle.gray, custom_id="persistent_view:activity")
    #async def activity(self, interaction: discord.Interaction, button: discord.ui.Button):
            #collection = db["voicemaster"]
            #check = collection.find_one({"_id": interaction.guild.id}) 
            #channeid = check["channel"]
            #voicechannel = interaction.guild.get_channel(channeid)
            #category = voicechannel.category  
            #if interaction.user.voice is None:
                #e = discord.Embed(color=0xffff00, description=f"<:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a voice channel")
                #await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                #return
            #elif interaction.user.voice is not None:
                #if interaction.user.voice.channel.category != category:
                    #emb = discord.Embed(color=0xffff00, description=f"<:emoji_7:1048996990706524322> {interaction.user.mention} you are not in a voice channel created by the bot")
                    #await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    #return
            #colle = db["premium_guild"]
            #checke = colle.find_one({"_id": interaction.guild.id})
            #if checke is None:
              #prem = db["pretend+"]   
              #cheprem = prem.find_one({"_id": interaction.user.id})
              #if cheprem is None:
                    #embe = discord.Embed(color=0xffff00, description=f"<:emoji_7:1048996990706524322> {interaction.user.mention} using activities via VoiceMaster is a premium feature. Join [here](https://discord.gg/MSVCm2FEKQ) for more")
                    #await interaction.response.send_message(embed=embe, view=None, ephemeral=True) 
                    #return
              #elif cheprem is not None:
                #pass
            #elif checke is not None:
                #pass    

            #activity_types = {'watch_together': '880218394199220334','poker_night': '755827207812677713', 'betrayal': '773336526917861400','fishing': '814288819477020702', 'chess_in_the_park': '832012774040141894','letter-tile': '879863686565621790','word_snacks': '879863976006127627','doodle-crew': '878067389634314250', 'spellcast': '852509694341283871', 'awkword': '879863881349087252','checkers': '832013003968348200'}  
            #em = discord.Embed(color=0x2f3136, description="select an activity from the **dropdown menu** to start")
            #select = Select(placeholder="choose an activity...", 
               #options=[
                #discord.SelectOption(
                    #label="watch together",
                    #value="watch_together",
                    #emoji="<:youtube:995275073277657198>"
                #),
                #discord.SelectOption(
                    #label="poker night",
                    #value="poker_night",
                    #emoji="🃏"
                #),
                #discord.SelectOption(
                    #label="chess in the park",
                    #value="chess_in_the_park",
                    #emoji="♟️"
                #),
                #discord.SelectOption(
                    #label="word snacks",
                    #value="word_snacks",
                    #emoji="🍬"
                #),
                #discord.SelectOption(
                    #label="betrayal",
                    #value="betrayal",
                    #emoji="🔫"
                #),
                #discord.SelectOption(
                    #label="fishington",
                    #value="fishing",
                    #emoji="🎣"
                #),
                #discord.SelectOption(
                  #label="letter tile",
                  #value="letter_tile",
                  #emoji="🅰️"
                #),
                #discord.SelectOption(
                  #label="doodle crew",
                  #value="doodle-crew",
                  #emoji="🖌️"
                #),
                #discord.SelectOption(
                  #label="spell cast",
                  #value="spellcast",
                  #emoji="🪄"
                #),
                 #discord.SelectOption(
                  #label="awkword",
                  #emoji="🔤"
                 #),
                 #discord.SelectOption(
                  #label="checkers",
                  #emoji="🎲"
                 #)
               #])
            #async def my_callback(inter: discord.Interaction):      
                #invite = await inter.user.voice.channel.create_invite(max_age=0, max_uses=0, target_application_id=activity_types.get(select.values[0]),target_type=discord.InviteTarget.embedded_application)
                #e = discord.Embed(color=0x2f3136, description=f"{inter.user.mention}: [**click here**]({invite} to join the activity")
                #await inter.response.send_message(embed=e, ephemeral=True)
            #select.callback = my_callback

            #sel = View()
            #sel.add_item(select)
            #await interaction.response.send_message(embed=em, ephemeral=True, view=sel)

class voicemaster(commands.Cog):
   def __init__(self, bot):
        self.bot = bot

   @commands.Cog.listener() 
   async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
     collection = db["voicemaster"]
     check = collection.find_one({"_id": member.guild.id})
     if check is None:
        pass
     elif check is not None:
      chan = check["channel"]
      if (after.channel is not None and before.channel is None) or (after.channel is not None and before.channel is not None):
       if after.channel.id == int(chan):
          col = db["owners"]      
          channel = await member.guild.create_voice_channel(f"{member.name}'s channel", category=after.channel.category)
          await member.move_to(channel)
          insert = {"_id": channel.id, "member": member.id}
          col.insert_one(insert)
       if before.channel is not None and after.channel is not None:
        cole = db["owners"]
        chek = cole.find_one({"_id": before.channel.id})
        if chek is not None and after.channel.id == int(chan):
         await member.move_to(channel=None)   
        elif chek is not None and after.channel.category != before.channel.category:
                coli = db["owners"]
                cheki = coli.find_one({"_id": before.channel.id}) 
                if cheki is None:
                 pass
                elif cheki is not None:  
                 channel = before.channel  
                 members = channel.members
                 k=0
                 for me in members:
                  k+=1

                 if k == 0:
                  coli.delete_one({"_id": before.channel.id})
                  await channel.delete() 
                  
      elif before.channel is not None and after.channel is None: 
            coli = db["owners"]
            cheki = coli.find_one({"_id": before.channel.id}) 
            if cheki is None:
              pass
            elif cheki is not None:  
              channel = before.channel  
              members = channel.members
              k=0
              for me in members:
               k+=1

              if k == 0:
               coli.delete_one({"_id": before.channel.id})
               await channel.delete()                              

   @commands.command(aliases=["vm"])
   async def voicemaster(self, ctx: commands.Context, option=None):
    if (not ctx.author.guild_permissions.administrator):
     emb = discord.Embed(color=discord.Color.yellow(), description=f"> {ctx.author.mention} you are missing __permissions__ `administrator`")
     await ctx.reply(embed=emb, mention_author=False)
     return
 
    if option == None:
        emb = discord.Embed(color=0x2f3136, title="voicemaster", description="> sets join to create module for your server")
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        emb.add_field(name="**category**", value="> __config__")
        emb.add_field(name="**permissions**", value="> __administrator__")
        emb.add_field(name="**usage**", value="`voicemaster set\nvoicemaster unset`", inline=False)
        emb.add_field(name="**aliases**", value="> __vm__")
        await ctx.reply(embed=emb, mention_author=False)  
        return
    elif option == "set":
     collection = db["voicemaster"]
     check = collection.find_one({"_id": ctx.guild.id})
     if check is not None:
            em = discord.Embed(color=discord.Color.red(), description=f"> {ctx.author.mention} voice master is already **set**")
            await ctx.reply(embed=em, mention_author=False)
            return
     elif check is None:                   
        category = await ctx.guild.create_category("voice channels")
        overwrite = {ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False)}  
        em = discord.Embed(color=0x2f3136, title="VoiceMaster Interface", description="> click the buttons below to control the __voice channel__")
        em.set_thumbnail(url=self.bot.user.avatar.url)
        try:
          em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        except:
            em.set_author(name=ctx.guild.name)

        em.add_field(name="Button Usage", value="<:icons_lock:1049009150140616784> - [`lock`](https://discord.gg/MSVCm2FEKQ) the voice channel\n<:icons_unlock:1049009041919197284> - [`unlock`](https://discord.gg/MSVCm2FEKQ) the voice channel\n<:icons__on:1049012483312062544> - [`reveal`](https://discord.gg/MSVCm2FEKQ) the voice channel\n<:icons_off:1049012436382003210> - [`hide`](https://discord.gg/MSVCm2FEKQ) the voice channel\n<:icons_richpresence:1049046415722156183> - [`rename`](https://discord.gg/MSVCm2FEKQ) the voice channel\n<:icons_plus:1049047366084345988> - [`increase`](https://discord.gg/MSVCm2FEKQ) the user limit\n<:icons_minus:1049048527701032963> - [`decrease`](https://discord.gg/MSVCm2FEKQ) the user limit\n<:icons_owner:1049049388766470234> - [`claim`](https://discord.gg/MSVCm2FEKQ) the voice channel\n<:icons_todolist:1049050116281090079> - [`info`](https://discord.gg/MSVCm2FEKQ) of the voice channe")    
        text = await ctx.guild.create_text_channel("interface", category=category, overwrites=overwrite)
        vc = await ctx.guild.create_voice_channel("Join to create", category=category)
        await text.send(embed=em, view=vmbuttons())
        insert = {"_id": ctx.guild.id, "channel": vc.id, "interface": text.id}
        collection.insert_one(insert)
        e = discord.Embed(color=0x2f3135, description=f"> {ctx.author.mention} configured the ** voice master** **interface**")
        await ctx.reply(embed=e, mention_author=False)               
    elif option == "unset":
         collection = db["voicemaster"]
         check = collection.find_one({"_id": ctx.guild.id})
         if check is None:
            em = discord.Embed(color=discord.Color.red(), description=f"> {ctx.author.mention} __voice master module__ isn't **set**")
            await ctx.reply(embed=em, mention_author=False)
            return
         elif check is not None:
            try:
             channelid = check["channel"]
             interfaceid = check["interface"]
             channel2 = ctx.guild.get_channel(interfaceid)
             channel = ctx.guild.get_channel(channelid)
             category = channel.category
             channels = category.channels
             for chan in channels:
                try:
                    await chan.delete()
                except:
                   continue

             await category.delete()    
             await channel2.delete()      
             collection.delete_one({"_id": ctx.guild.id})
             embed = discord.Embed(color=0x2f3136, description=f"> {ctx.author.mention} __voice master module__ has been **disabled**")
             await ctx.reply(embed=embed, mention_author=False) 
             return
            except:
             collection.delete_one({"_id": ctx.guild.id})
             embed = discord.Embed(color=0x2f3136, description=f"> {ctx.author.mention} __voice master module__ has been **disabled**")
             await ctx.reply(embed=embed, mention_author=False)  
    else:
        emb = discord.Embed(color=0x2f3136, title="voicemaster", description="> **sets join to create module for your server**")
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        emb.add_field(name="**category**", value="> __config__")
        emb.add_field(name="**permissions**", value="> __administrator__")
        emb.add_field(name="**usage**", value="> `voicemaster [subcommand]`", inline=False)
        emb.add_field(name="**commands**", value="> jointocreate set\n> jointocreate unset", inline=False)
        emb.add_field(name="**aliases**", value="> __vm__")
        await ctx.reply(embed=emb, mention_author=False)  
        return       

async def setup(bot) -> None:
    await bot.add_cog(voicemaster(bot))       