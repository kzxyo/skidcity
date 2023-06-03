import discord
from discord.ext import commands
from classes import Colors, Emojis
from discord.ui import Modal, Select, View

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
           e = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: voice channel renamed to **{name}**")
           await interaction.response.send_message(embed=e, ephemeral=True)
        except Exception as er:
            em = discord.Embed(color=Colors.red, description=f"{Emojis.wrong} {interaction.user.mention}: an error occured {er}")
            await interaction.response.send_message(embed=em, ephemeral=True)  

class vmbuttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="", emoji="<:icons_locked:986219156821131304>", style=discord.ButtonStyle.gray, custom_id="persistent_view:lock")    
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
         async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: you don't own this voice channel")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(connect=False)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: locked <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)      

    @discord.ui.button(label="", emoji="<:icons_unlock:986219160369508393>", style=discord.ButtonStyle.gray, custom_id="persistent_view:unlock")
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):   
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: you don't own this voice channel")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(connect=True)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: unlocked <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:icons_on:986220176829726780>", style=discord.ButtonStyle.gray, custom_id="persistent_view:reveal")
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: you don't own this voice channel")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: revealed <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
      
    @discord.ui.button(label="", emoji="<:icons_off:986220179983831061>", style=discord.ButtonStyle.gray, custom_id="persistent_view:hide")
    async def hide(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: you don't own this voice channel")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: hidded <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)   

    @discord.ui.button(label="", emoji="<:icons_richpresence:986220183519657985>", style=discord.ButtonStyle.gray, custom_id="persistent_view:rename")
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button): 
       async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: you don't own this voice channel")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
                rename = vcModal()
                await interaction.response.send_modal(rename)
    
    @discord.ui.button(label="", emoji="<:icons_increase:1021037401059119156>", style=discord.ButtonStyle.gray, custom_id="persistent_view:increase")
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: you don't own this voice channel")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 99:
                emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: I can't increase the limit for <#{interaction.user.voice.channel.id}>")
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                return
              
              res = limit + 1
              await interaction.user.voice.channel.edit(user_limit=res)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention} increased <#{interaction.user.voice.channel.id}> limit to **{res}** members")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:icons_decrease:1021037305311535196>", style=discord.ButtonStyle.gray, custom_id="persistent_view:decrease")
    async def decrease(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: you don't own this voice channel")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 0:
                emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention} i can't decrease the limit for <#{interaction.user.voice.channel.id}>")
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                return
              
              res = limit - 1
              await interaction.user.voice.channel.edit(user_limit=res)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: decreased <#{interaction.user.voice.channel.id}> limit to **{res}** members")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)          
    
    @discord.ui.button(label="", emoji="<:icons_owner:986220186988326933>", style=discord.ButtonStyle.gray, custom_id="persistent_view:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
         async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is not None:
                memberid = che[0]   
                member = interaction.guild.get_member(memberid)
                if member in interaction.user.voice.channel.members:
                    embed = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: the owner is still in the voice channel")
                    await interaction.response.send_message(embed=embed, ephemeral=True, view=None)
                else:
                    await cursor.execute(f"UPDATE vcs SET user_id = {interaction.user.id} WHERE voice = {interaction.user.voice.channel.id}")
                    await interaction.client.db.commit()
                    embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: you own {interaction.user.voice.channel.mention}")
                    await interaction.response.send_message(embed=embed, view=None, ephemeral=True)        
    
    @discord.ui.button(label="", emoji="<:icons_todolist:986252960570961943>", style=discord.ButtonStyle.gray, custom_id="persistent_view:info")
    async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in a voice channel created by the bot")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {}".format(interaction.user.voice.channel.id))
             che = await cursor.fetchone()
             if che is not None:
                memberid = che[0]   
                member = interaction.guild.get_member(memberid)
                embed = discord.Embed(color=0xffffff, title=interaction.user.voice.channel.name, description=f"owner: **{member}** (`{member.id}`)\ncreated: <t:{int(interaction.user.voice.channel.created_at.timestamp())}:R>\nbitrate: **{interaction.user.voice.channel.bitrate/1000}kbps**\nconnected: **{len(interaction.user.voice.channel.members)}**")    
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
                embed.set_thumbnail(url=member.display_avatar)
                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)            
    
    @discord.ui.button(label="", emoji="<:icons_activity:1021037240861868112>", style=discord.ButtonStyle.gray, custom_id="persistent_view:activity")
    async def activity(self, interaction: discord.Interaction, button: discord.ui.Button):
         async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
           channeid = check[1]
           voicechannel = interaction.guild.get_channel(channeid)
           category = voicechannel.category 
           if interaction.user.voice is None:
              e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You are not in your voice channel")
              await interaction.response.send_message(embed=e, view=None, ephemeral=True)
              return
           elif interaction.user.voice is not None:
            if interaction.user.voice.channel.category != category:
               emb = discord.Embed(color=Colors.yellow, description=f"{Emojis.wrong} {interaction.user.mention} you are not in a voice channel created by the bot")
               await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
               return
         

            activity_types = {'watch_together': '880218394199220334','poker_night': '755827207812677713', 'betrayal': '773336526917861400','fishing': '814288819477020702', 'chess_in_the_park': '832012774040141894','letter-tile': '879863686565621790','word_snacks': '879863976006127627','doodle-crew': '878067389634314250', 'spellcast': '852509694341283871', 'awkword': '879863881349087252','checkers': '832013003968348200'}  
            em = discord.Embed(color=0xffffff, description="select an activity from the **dropdown menu** to start")
            select = Select(placeholder="choose an activity...", 
               options=[
                discord.SelectOption(
                    label="watch together",
                    value="watch_together",
                    emoji="<:youtube:1025433260978880583>"
                ),
                discord.SelectOption(
                    label="poker night",
                    value="poker_night",
                    emoji="🃏"
                ),
                discord.SelectOption(
                    label="chess in the park",
                    value="chess_in_the_park",
                    emoji="♟️"
                ),
                discord.SelectOption(
                    label="word snacks",
                    value="word_snacks",
                    emoji="🍬"
                ),
                discord.SelectOption(
                    label="betrayal",
                    value="betrayal",
                    emoji="🔫"
                ),
                discord.SelectOption(
                    label="fishington",
                    value="fishing",
                    emoji="🎣"
                ),
                discord.SelectOption(
                  label="letter tile",
                  value="letter_tile",
                  emoji="🅰️"
                ),
                discord.SelectOption(
                  label="doodle crew",
                  value="doodle-crew",
                  emoji="🖌️"
                ),
                discord.SelectOption(
                  label="spell cast",
                  value="spellcast",
                  emoji="🪄"
                ),
                 discord.SelectOption(
                  label="awkword",
                  emoji="🔤"
                 ),
                 discord.SelectOption(
                  label="checkers",
                  emoji="🎲"
                 )
               ])
            async def my_callback(inter: discord.Interaction):      
                invite = await inter.user.voice.channel.create_invite(max_age=0, max_uses=0, target_application_id=activity_types.get(select.values[0]),target_type=discord.InviteTarget.embedded_application)
                e = discord.Embed(color=0xffffff, description=f"{inter.user.mention}: [**click here**]({invite}) to join the activity")
                await inter.response.send_message(embed=e, ephemeral=True)
            select.callback = my_callback

            sel = View()
            sel.add_item(select)
            await interaction.response.send_message(embed=em, ephemeral=True, view=sel)

class voicemaster(commands.Cog):
   def __init__(self, bot):
        self.bot = bot
   
   @commands.Cog.listener()
   async def on_ready(self): 
    async with self.bot.db.cursor() as cursor: 
      await cursor.execute("CREATE TABLE IF NOT EXISTS voicemaster (guild_id INTEGER, vc INTEGER, interface INTEGER)")
      await cursor.execute("CREATE TABLE IF NOT EXISTS vcs (user_id INTEGER, voice INTEGER)") 
    await self.bot.db.commit()   

   @commands.Cog.listener() 
   async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
     async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(member.guild.id))
      check = await cursor.fetchone()
      if check is not None:
       chan = check[1]
       if (after.channel is not None and before.channel is None) or (after.channel is not None and before.channel is not None):
        if after.channel.id == int(chan) and before.channel is None:     
          channel = await member.guild.create_voice_channel(f"{member.name}'s channel", category=after.channel.category)
          await member.move_to(channel)
          await cursor.execute("INSERT INTO vcs VALUES (?,?)", (member.id, after.channel.id))
          await self.bot.db.commit()
        elif before.channel is not None and after.channel is not None:
         await cursor.execute("SELECT * FROM vcs WHERE voice = {}".format(before.channel.id))
         chek = await cursor.fetchone()
         if (chek is not None) and (before.channel is not None and after.channel.id == int(chan)):
          if before.channel.category == after.channel.category: 
           await before.channel.delete()
           await cursor.execute("DELETE FROM vcs WHERE voice = {}".format(before.channel.id))
           await self.bot.db.commit() 
           await member.move_to(channel=None)
          else: 
            chane = await member.guild.create_voice_channel(f"{member.name}'s channel", category=after.channel.category)
            await member.move_to(chane)
            await cursor.execute("INSERT INTO vcs VALUES (?,?)", (member.id, chane.id))
            await self.bot.db.commit()   
         elif (chek is not None) and (before.channel is not None and after.channel.id != int(chan)):
            if before.channel.category == after.channel.category: 
             await before.channel.delete()
             await cursor.execute("DELETE FROM vcs WHERE voice = {}".format(before.channel.id))
             await self.bot.db.commit() 
            elif after.channel.category != before.channel.category: 
                 if before.channel.id == int(chan): return
                 channel = before.channel  
                 members = channel.members
                 if len(members) == 0:
                  await cursor.execute("DELETE FROM vcs WHERE voice = {}".format(before.channel.id))
                  await self.bot.db.commit()
                  await channel.delete() 
                  
       elif before.channel is not None and after.channel is None: 
         async with self.bot.db.cursor() as curs: 
            await curs.execute("SELECT * FROM vcs WHERE voice = {}".format(before.channel.id))
            cheki = await curs.fetchone() 
            if cheki is not None:  
               channel = before.channel  
               members = channel.members
               if len(members) == 0:
                await curs.execute("DELETE FROM vcs WHERE voice = {}".format(before.channel.id))
                await self.bot.db.commit()
                await channel.delete()   

   @commands.command(aliases=["vm"], help="sets voicemaster module for your server", description="config", usage="[subcommand]", brief="voicemaster set - sets voicemaster\nvoicemaster unset - unsets voice master")
   @commands.cooldown(1, 5, commands.BucketType.guild)
   async def voicemaster(self, ctx: commands.Context, option=None):
    if (not ctx.author.guild_permissions.administrator):
     await(self, ctx, "administrator")
     return
 
    if option == None:
        await(self, ctx, ctx.command.name) 
        return
    elif option == "set":
     async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
      check = await cursor.fetchone() 
      if check is not None:
            em = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: voice master is already set")
            await(self, ctx, None, em, None, None, None)
            return
      elif check is None:                   
        category = await ctx.guild.create_category("voice channels")
        overwrite = {ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)}  
        em = discord.Embed(color=0xffffff, title="VoiceMaster Interface", description="click the buttons below to control the voice channel")
        em.set_thumbnail(url=self.bot.user.avatar.url)
        try:
          em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        except:
            em.set_author(name=ctx.guild.name)

        em.add_field(name="Button Usage", value="<:icons_locked:986219156821131304> - [`lock`](https://discord.gg/mJzM4Bzf8Y) the voice channel\n<:icons_unlock:986219160369508393> - [`unlock`](https://discord.gg/mJzM4Bzf8Y) the voice channel\n<:icons_on:986220176829726780> - [`reveal`](https://discord.gg/mJzM4Bzf8Y) the voice channel\n<:icons_off:986220179983831061> - [`hide`](https://discord.gg/mJzM4Bzf8Y) the voice channel\n<:icons_richpresence:986220183519657985> - [`rename`](https://discord.gg/mJzM4Bzf8Y) the voice channel\n<:icons_increase:1021037401059119156> - [`increase`](https://discord.gg/mJzM4Bzf8Y) the user limit\n<:icons_decrease:1021037305311535196> - [`decrease`](https://discord.gg/mJzM4Bzf8Y) the user limit\n<:icons_owner:986220186988326933> - [`claim`](https://discord.gg/mJzM4Bzf8Y) the voice channel\n<:icons_todolist:986252960570961943> - [`info`](https://discord.gg/mJzM4Bzf8Y) of the voice channel\n<:icons_activity:1021037240861868112> - [`play`](https://discord.gg/mJzM4Bzf8Y) a game in voice channel")    
        text = await ctx.guild.create_text_channel("interface", category=category, overwrites=overwrite)
        vc = await ctx.guild.create_voice_channel("Join to create", category=category)
        await text.send(embed=em, view=vmbuttons())
        await cursor.execute("INSERT INTO voicemaster VALUES (?,?,?)", (ctx.guild.id, vc.id, text.id))
        await self.bot.db.commit()
        e = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: configured the voice master interface")
        await(self, ctx, None, e, None, None, None)            
    elif option == "unset":
     async with self.bot.db.cursor() as cursor: 
         await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
         check = await cursor.fetchone() 
         if check is None:
            em = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: voice master module isn't set")
            await(self, ctx, None, em, None, None, None)
            return
         elif check is not None:
            try:
             channelid = check[1]
             interfaceid = check[2]
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
             await cursor.execute("DELETE FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
             await self.bot.db.commit()
             embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: voice master module has been disabled")
             await(self, ctx, None, embed, None, None, None)
             return
            except:
             await cursor.execute("DELETE FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
             await self.bot.db.commit()
             embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: voice master module has been disabled")
             await(self, ctx, None, embed, None, None, None)
    else:
        await(self, ctx, ctx.command.name) 
        return       

async def setup(bot) -> None:
    await bot.add_cog(voicemaster(bot))       