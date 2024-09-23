from discord.ext import commands 
import discord

class reacts(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
   self.bot = bot 
  
  @commands.Cog.listener('on_raw_reaction_add')
  async def starboard_add(self, payload: discord.RawReactionActionEvent):
     try:   
       check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = {}".format(payload.guild_id))
       if check: 
         if payload.emoji.is_unicode_emoji(): 
          if ord(str(payload.emoji)) != int(check["emoji_id"]): return  
         elif payload.emoji.is_custom_emoji(): 
          if payload.emoji.id != int(check["emoji_id"]): return
         message = await payload.member.guild.get_channel(payload.channel_id).fetch_message(payload.message_id) 
         chec = await self.bot.db.fetchrow(f"SELECT * FROM starboardmes WHERE guild_id = {payload.guild_id} AND channel_message_id = {payload.channel_id} AND message_id = {payload.message_id}") 
         if chec is not None: 
            messa = await payload.member.guild.get_channel(int(chec['channel_starboard_id'])).fetch_message(int(chec['message_starboard_id']))
            try: return await messa.edit(content=f"{payload.emoji} **#{sum(r.count for r in message.reactions if str(r.emoji) == str(payload.emoji))}** <#{payload.channel_id}>")              
            except: pass                                   
         elif chec is None:
            channel = payload.member.guild.get_channel(check['channel_id'])
            if not message.embeds: embed = discord.Embed(color=self.bot.color, description=message.content, timestamp=message.created_at.now())
            else: 
              embed = discord.Embed(color=message.embeds[0].color, title=message.embeds[0].title, description=message.embeds[0].description, timestamp=message.created_at.now()) 
              embed.set_image(url=message.embeds[0].image.url)
              embed.set_footer(text=message.embeds[0].footer.text, icon_url=message.embeds[0].footer.icon_url) 
            embed.set_author(name=message.author, icon_url=message.author.display_avatar)
            file = ""
            if message.attachments:
                if ".mp4" in message.attachments[0].url or ".mov" in message.attachments[0].url:  
                  url = message.attachments[0].url
                  bytes_io = await self.bot.ext.getbyte(url)
                  file = discord.File(fp=bytes_io, filename=message.attachments[0].filename)
                else: embed.set_image(url=message.attachments[0].url)
            button = discord.ui.Button(label="message", style=discord.ButtonStyle.link, url=message.jump_url)
            view = discord.ui.View()
            view.add_item(button)
            async def idk(): 
                  if isinstance(file, discord.File):
                   mes = await channel.send(content=f"{payload.emoji} **#{reaction.count}** <#{payload.channel_id}>", file=file, embed=embed, view=view)
                  else: 
                     mes = await channel.send(content=f"{payload.emoji} **#{reaction.count}** <#{payload.channel_id}>", embed=embed, view=view)
                  await self.bot.db.execute("INSERT INTO starboardmes VALUES ($1,$2,$3,$4,$5)", payload.guild_id, channel.id, payload.channel_id, mes.id, payload.message_id)
            for reaction in message.reactions: 
                if isinstance(reaction.emoji, str): 
                 try: 
                  if ord(str(reaction.emoji)) == int(check["emoji_id"]): 
                    if reaction.count == int(check["count"]): await idk()
                 except: pass 
                else: 
                 if reaction.emoji.id == int(check["emoji_id"]):
                  if reaction.count == int(check["count"]): await idk()
         
     except Exception as er:
        print(er)

  @commands.Cog.listener('on_raw_reaction_remove')
  async def starboard_remove(self, payload: discord.RawReactionActionEvent):
     try: 
         check = await self.bot.db.fetchrow("SELECT * FROM starboard WHERE guild_id = {}".format(payload.guild_id))
         if check is not None:  
          if payload.emoji.is_unicode_emoji():
           if ord(str(payload.emoji)) != int(check['emoji_id']): return
          elif payload.emoji.is_custom_emoji(): 
            if payload.emoji.id != int(check["emoji_id"]): return   
          message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id) 
          chec = await self.bot.db.fetchrow(f"SELECT * FROM starboardmes WHERE guild_id = {payload.guild_id} AND channel_message_id = {payload.channel_id} AND message_id = {payload.message_id}") 
          if chec is not None: 
            messa = await self.bot.get_channel(int(chec['channel_starboard_id'])).fetch_message(int(chec['message_starboard_id']))
            for reaction in message.reactions: 
             if isinstance(reaction.emoji, str):
              if ord(str(reaction.emoji)) == int(check['emoji_id']):  
               try: 
                await messa.edit(content=f"{reaction.emoji} **#{reaction.count}** <#{payload.channel_id}>")
               except:
                  pass  
             else: 
              if reaction.emoji.id == int(check["emoji_id"]): 
                try: await messa.edit(content=f"{reaction.emoji} **#{reaction.count}** <#{payload.channel_id}>")
                except: pass                  
     except Exception as er:
        print(er) 

async def setup(bot: commands.Bot) -> None: 
  await bot.add_cog(reacts(bot))  