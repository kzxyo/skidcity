import discord
from discord.ext import commands
from discord.ui import Modal, Select, View

class vcModal(Modal, title="Rename your voice channel"):
       name = discord.ui.TextInput(
        label="Channel name",
        placeholder="Rename your channel",
        required=True,
        style=discord.TextStyle.short
       )

       async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        try: 
           await interaction.user.voice.channel.edit(name=name)   
           e = discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146> {interaction.user.mention}: Successfully renamed your **voice channel** to **{name}**")
           await interaction.response.send_message(embed=e, ephemeral=True)
        except Exception as er:
            em = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: Something went wrong:\n```{er}```")
            await interaction.response.send_message(embed=em, ephemeral=True)  

class vmbuttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="", emoji="<:lock:1049009455884415046>", style=discord.ButtonStyle.grey, custom_id="persistent_view:lock")    
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
         async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You don't **own** this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(connect=False)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146> {interaction.user.mention}: Successfully locked <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)      

    @discord.ui.button(label="", emoji="<:unlock:1049009465774575647> ", style=discord.ButtonStyle.grey, custom_id="persistent_view:unlock")
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):   
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You don't **own** this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(connect=True)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146> {interaction.user.mention}: Successfully unlocked <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:reveal:1049009464080084992> ", style=discord.ButtonStyle.grey, custom_id="persistent_view:reveal")
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You don't **own** this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146>  {interaction.user.mention}: Your **voice channel** is no longer **hidden**")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
      
    @discord.ui.button(label="", emoji="<:hide:1049009451769790536>", style=discord.ButtonStyle.grey, custom_id="persistent_view:hide")
    async def hide(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You don't **own** this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              overwrite = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
              await interaction.user.voice.channel.edit(overwrites=overwrite)
              emb = discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146> {interaction.user.mention}: Your **voice channel** is now **hidden**")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)   

    @discord.ui.button(label="", emoji="<:rename:1049009462230388866>", style=discord.ButtonStyle.grey, custom_id="persistent_view:rename")
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button): 
       async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You don't **own** this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
                rename = vcModal()
                await interaction.response.send_modal(rename)
    
    @discord.ui.button(label="", emoji="<:plus:1049009459109822474>", style=discord.ButtonStyle.grey, custom_id="persistent_view:increase")
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You don't **own** this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 99:
                emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: I can't **increase the limit** for that **voice channel**")
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                return
              
              res = limit + 1
              await interaction.user.voice.channel.edit(user_limit=res)
              emb = discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146> {interaction.user.mention} Successfully **increased** the member limit to `{res}`")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:minus:1049009457545367582> ", style=discord.ButtonStyle.grey, custom_id="persistent_view:decrease")
    async def decrease(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You don't **own** this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             elif che is not None:
              limit = interaction.user.voice.channel.user_limit
              if limit == 0:
                emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention} I can't **decrease the limit** for that **voice channel**")
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
                return
              
              res = limit - 1
              await interaction.user.voice.channel.edit(user_limit=res)
              emb = discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146> {interaction.user.mention}: Successfully **decreased** the member limit to `{res}`")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)          
    
    @discord.ui.button(label="", emoji="<:claim:1049009448640860170> ", style=discord.ButtonStyle.grey, custom_id="persistent_view:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
         async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is not None:
                memberid = che[0]   
                member = interaction.guild.get_member(memberid)
                if member in interaction.user.voice.channel.members:
                    embed = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: The owner of this **voice channel** is still **connected**")
                    await interaction.response.send_message(embed=embed, ephemeral=True, view=None)
                else:
                    await cursor.execute(f"UPDATE vcs SET user_id = {interaction.user.id} WHERE voice = {interaction.user.voice.channel.id}")
                    await interaction.client.db.commit()
                    embed = discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146> {interaction.user.mention}: Successfully **claimed** {interaction.user.voice.channel.mention} as your **voice channel**")
                    await interaction.response.send_message(embed=embed, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:info:1049009454085046302>", style=discord.ButtonStyle.grey, custom_id="persistent_view:info")
    async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return

             await cursor.execute("SELECT * FROM vcs WHERE voice = {}".format(interaction.user.voice.channel.id))
             che = await cursor.fetchone()
             if che is not None:
                memberid = che[0]   
                member = interaction.guild.get_member(memberid)
                embed = discord.Embed(color=0x2f3136, title=interaction.user.voice.channel.name, description=f"""**Owner:** {member} (`{member.id}`)
**Created:** <t:{int(interaction.user.voice.channel.created_at.timestamp())}:R>
**Bitrate:** {interaction.user.voice.channel.bitrate/1000} kbps
**Members:** {len(interaction.user.voice.channel.members)}""")    
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
                embed.set_thumbnail(url=member.display_avatar)
                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:delete:1049009450368897054>", style=discord.ButtonStyle.grey)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
         async with interaction.client.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(interaction.guild.id)) 
          check = await cursor.fetchone()
          if check is not None:     
             channeid = check[1]
             voicechannel = interaction.guild.get_channel(channeid)
             category = voicechannel.category 
             if interaction.user.voice is None:
                e = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voice channel**")
                await interaction.response.send_message(embed=e, view=None, ephemeral=True)
                return
             elif interaction.user.voice is not None:
                if interaction.user.voice.channel.category != category:
                    emb = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You aren't connected to a **voicemaster channel**")
                    await interaction.response.send_message(embed=emb, view=None, ephemeral=True) 
                    return
             await cursor.execute("SELECT * FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             che = await cursor.fetchone()
             if che is None:
                embe = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {interaction.user.mention}: You don't **own** this **voice channel**")
                await interaction.response.send_message(embed=embe, view=None, ephemeral=True)
                return
             await cursor.execute("DELETE FROM vcs WHERE voice = {} AND user_id = {}".format(interaction.user.voice.channel.id, interaction.user.id))
             await interaction.user.voice.channel.delete()
             embed= discord.Embed(color=0x2f3136, description=f"<:success:1034500520926253146> Successfully **deleted** your **voice channel**")
             await interaction.response.send_message(embed=embed, view=None, ephemeral=True)


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

   @commands.command(aliases=["vm", 'vc'], help="sets voicemaster module for your server", description="config", usage="[subcommand]", brief="voicemaster set - sets voicemaster\nvoicemaster unset - unsets voice master")
   @commands.cooldown(1, 5, commands.BucketType.guild)
   @commands.has_permissions(administrator = True)
   async def voicemaster(self, ctx: commands.Context, option=None):
        if option == None:
            dev = self.bot.get_user(565627105552105507)
            return await ctx.reply(f"{ctx.author.mention}: view the commands @ https://skidward.ml, for support contact **{dev.name}#{dev.discriminator}**")
        elif option == "set":
            async with self.bot.db.cursor() as cursor: 
                await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
                check = await cursor.fetchone() 
                if check is not None:
                    embed = discord.Embed(color=0x2f3136, description=f"{ctx.author.mention}: **Voicemaster module** has already been set up")
                    await ctx.reply(embed=embed)
                    return
                elif check is None:                   
                  category = await ctx.guild.create_category("voice channels")
                  overwrite = {ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)}  
                  em = discord.Embed(color=0xFEA127, title="**Voicemaster Interface**",description="""Control your **voice channel** using the buttons below""")
                  em.set_thumbnail(url=self.bot.user.avatar.url)
                  try:
                     em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
                  except:
                     em.set_author(name=ctx.guild.name)

                  em.add_field(name="Button Usage", value="""<:lock:1049009455884415046> — **Lock** the **voice channel**
<:unlock:1049009465774575647>  — **Unlock** the **voice channel**
<:reveal:1049009464080084992>  — **Reveal** the **voice channel**
<:hide:1049009451769790536> — **Hide** the **voice channel**
<:rename:1049009462230388866> — **Rename** the **voice channel**
<:plus:1049009459109822474> — **Increase** the **member limit**
<:minus:1049009457545367582>  — **Decrease** the **member limit**
<:claim:1049009448640860170> — **Claim** the **voice channel**
<:info:1049009454085046302> — **Info** about the **voice channel**
<:delete:1049009450368897054> — **Delete** the **voice channel**""")  
                  text = await ctx.guild.create_text_channel("control panel", category=category, overwrites=overwrite)
                  vc = await ctx.guild.create_voice_channel("j2c", category=category)
                  await text.send(embed=em, view=vmbuttons())
                  await cursor.execute("INSERT INTO voicemaster VALUES (?,?,?)", (ctx.guild.id, vc.id, text.id))
                  await self.bot.db.commit()
                  e = discord.Embed(color=0x2f3136, description=f"{ctx.author.mention}: Successfully set up **voicemaster interface**")
                  await ctx.reply(embed=e)         
        elif option == "unset":
            async with self.bot.db.cursor() as cursor: 
                await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
                check = await cursor.fetchone() 
                if check is None:
                    embed = discord.Embed(color=0x2f3136, description=f"<:fail:1034500518782980119> {ctx.author.mention}: **Voicemaster module** hasn't been set up")
                    await ctx.reply(embed=embed)
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
                        embed = discord.Embed(color=0x2f3136, description=f"{ctx.author.mention}: Successfully disabled **voicemaster module**")
                        await ctx.reply(embed=embed)
                        return
                    except:
                        await cursor.execute("DELETE FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
                        await self.bot.db.commit()
                        embed = discord.Embed(color=0x2f3136, description=f"{ctx.author.mention}: Successfully disabled **voicemaster module**")
                        await ctx.reply(embed=embed)
                else:
                    pass

async def setup(bot):
    await bot.add_cog(voicemaster(bot))  