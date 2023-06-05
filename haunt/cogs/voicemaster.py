import discord 
from discord.ext import commands
from utils.classes import Colors, Emojis
from discord.ui import Modal
from cogs.events import blacklist, commandhelp, noperms

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

    @discord.ui.button(label="", emoji="<:icons_lock:1067625900851613727>", style=discord.ButtonStyle.gray, custom_id="persistent_view:lock")    
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
              await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=False)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: locked <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)      

    @discord.ui.button(label="", emoji="<:icons_unlock:1067625896585990264>", style=discord.ButtonStyle.gray, custom_id="persistent_view:unlock")
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
              await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=True)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: unlocked <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

    @discord.ui.button(label="", emoji="<:reveal:1067625891452162089>", style=discord.ButtonStyle.gray, custom_id="persistent_view:reveal")
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
              await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, view_channel=True)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: revealed <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
      
    @discord.ui.button(label="", emoji="<:hide:1067625888654573669> ", style=discord.ButtonStyle.gray, custom_id="persistent_view:hide")
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
              await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, view_channel=False)
              emb = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: hidden <#{interaction.user.voice.channel.id}>")
              await interaction.response.send_message(embed=emb, view=None, ephemeral=True)   

    @discord.ui.button(label="", emoji="<:rename:1067625914407596052>", style=discord.ButtonStyle.gray, custom_id="persistent_view:rename")
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
    
    @discord.ui.button(label="", emoji="<:increase:1067625931205771355>", style=discord.ButtonStyle.gray, custom_id="persistent_view:increase")
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

    @discord.ui.button(label="", emoji="<:decrease:1067625923920265247>", style=discord.ButtonStyle.gray, custom_id="persistent_view:decrease")
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
                embe = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {interaction.user.mention}: You don't own this voice channel")
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
    
    @discord.ui.button(label="", emoji="<:claim:1067625919155544128>", style=discord.ButtonStyle.gray, custom_id="persistent_view:claim")
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

             await cursor.execute("SELECT * FROM vcs WHERE voice = {}".format(interaction.user.voice.channel.id))
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
    
    @discord.ui.button(label="", emoji="<:info:1067625909902917734>", style=discord.ButtonStyle.gray, custom_id="persistent_view:info")
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
                embed = discord.Embed(color=Colors.default, title=interaction.user.voice.channel.name, description=f"owner: **{member}** (`{member.id}`)\ncreated: <t:{int(interaction.user.voice.channel.created_at.timestamp())}:R>\nbitrate: **{interaction.user.voice.channel.bitrate/1000}kbps**\nconnected: **{len(interaction.user.voice.channel.members)}**")    
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
                embed.set_thumbnail(url=member.display_avatar)
                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)  
    
    @discord.ui.button(label="", emoji="<:delete:1067625906174173265>", style=discord.ButtonStyle.gray, custom_id="persistent_view:delete")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
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
              await cursor.execute("DELETE FROM vcs WHERE voice = {}".format(interaction.user.voice.channel.id))
              await interaction.client.db.commit()               
              await interaction.user.voice.channel.delete() 
              embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {interaction.user.mention}: deleted the channel")
              await interaction.response.send_message(embed=embed, view=None, ephemeral=True)        
                
class VoiceMaster(commands.Cog): 
   def __init__(self, bot: commands.AutoShardedBot): 
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
           if before.channel.id == after.channel.id: return  
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
             if before.channel.id == after.channel.id: return    
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
   @blacklist()
   async def voicemaster(self, ctx: commands.Context, option=None):
    if (not ctx.author.guild_permissions.administrator):
     await noperms(self, ctx, "administrator")
     return
 
    if option == None:
        await commandhelp(self, ctx, ctx.command.name) 
        return  
    elif option == "set":
     async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
      check = await cursor.fetchone() 
      if check is not None:
            em = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: voice master is already set")
            await ctx.reply(embed=em, mention_author=False)
            return
      elif check is None:                   
        category = await ctx.guild.create_category("voice channels")
        overwrite = {ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False)}  
        em = discord.Embed(color=Colors.default, title="VoiceMaster", description="click the buttons below to control the voice channel")
        em.set_thumbnail(url=self.bot.user.avatar.url)
        em.add_field(name="Button Usage", value="<:icons_lock:1067625900851613727> - [`lock`](https://discord.gg/hGkwSc6vzK) the voice channel\n<:icons_unlock:1067625896585990264> - [`unlock`](https://discord.gg/hGkwSc6vzK) the voice channel\n<:reveal:1067625891452162089> - [`reveal`](https://discord.gg/hGkwSc6vzK) the voice channel\n<:hide:1067625888654573669> - [`hide`](https://discord.gg/hGkwSc6vzK) the voice channel\n<:rename:1067625914407596052> - [`rename`](https://discord.gg/hGkwSc6vzK) the voice channel\n<:increase:1067625931205771355> - [`increase`](https://discord.gg/hGkwSc6vzK) the user limit\n<:decrease:1067625923920265247> - [`decrease`](https://discord.gg/hGkwSc6vzK) the user limit\n<:claim:1067625919155544128> - [`claim`](https://discord.gg/hGkwSc6vzK) the voice channel\n<:info:1067625909902917734> - [`info`](https://discord.gg/hGkwSc6vzK) of the voice channel\n<:delete:1067625906174173265> - [`delete`](https://discord.gg/hGkwSc6vzK) a voice channel")    
        text = await ctx.guild.create_text_channel("interface", category=category, overwrites=overwrite)
        vc = await ctx.guild.create_voice_channel("Join to create", category=category)
        await text.send(embed=em, view=vmbuttons())
        await cursor.execute("INSERT INTO voicemaster VALUES (?,?,?)", (ctx.guild.id, vc.id, text.id))
        await self.bot.db.commit()
        e = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: configured the voice master interface")
        await ctx.reply(embed=e, mention_author=False)               
    elif option == "unset":
      async with self.bot.db.cursor() as cursor: 
         await cursor.execute("SELECT * FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
         check = await cursor.fetchone() 
         if check is None:
            em = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: voice master module isn't set")
            await ctx.reply(embed=em, mention_author=False)
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
             await ctx.reply(embed=embed, mention_author=False) 
             return
            except:
             
             await cursor.execute("DELETE FROM voicemaster WHERE guild_id = {}".format(ctx.guild.id))
             await self.bot.db.commit()
             embed = discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: voice master module has been disabled")
             await ctx.reply(embed=embed, mention_author=False)  
    else:
        await commandhelp(self, ctx, ctx.command.name) 
        return         
        
async def setup(bot):
    await bot.add_cog(VoiceMaster(bot))        