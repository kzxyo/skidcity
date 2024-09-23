from discord.ext.commands import Context, Bot as Bot, group
from discord.ext import commands
from discord import Embed, TextChannel, PartialEmoji
from patches.permissions import Permissions
from typing import Union
import discord

class skull(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot 

    @group(invoke_without_command=True)
    async def skull(self, ctx): 
        await ctx.create_pages()

    @skull.command(description="modify the skullboard count", brief="manage guild", usage="[count]", aliases=["amount"])
    @Permissions.has_permission(manage_guild=True)
    async def count(self, ctx: Context, count: int): 
      if count < 1: return await ctx.warning("Count can't be **less** than 1")
      check = await self.bot.db.fetchrow("SELECT * FROM skullboard WHERE guild_id = $1", ctx.guild.id)
      if check is None: await self.bot.db.execute("INSERT INTO skullboard (guild_id, count) VALUES ($1, $2)", ctx.guild.id, count)
      else: await self.bot.db.execute("UPDATE skullboard SET count = $1 WHERE guild_id = $2", count, ctx.guild.id)
      await ctx.success(f"Skull **count** set to **{count}**")  

    @skull.command(name="channel", description="configure the skullboard channel", brief="manage guild", usage="[channel]")
    @Permissions.has_permission(manage_guild=True)
    async def skull_channel(self, ctx: Context, *, channel: TextChannel): 
      check = await self.bot.db.fetchrow("SELECT * FROM skullboard WHERE guild_id = $1", ctx.guild.id)
      if check is None: await self.bot.db.execute("INSERT INTO skullboard (guild_id, channel_id) VALUES ($1, $2)", ctx.guild.id, channel.id)
      else: await self.bot.db.execute("UPDATE skullboard SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
      await ctx.success(f"skullboard **channel** set to {channel.mention}")

    @skull.command(name="remove", description="remove skullboard", brief="manage guild", aliases=["disable"])
    @Permissions.has_permission(manage_guild=True)
    async def skull_remove(self, ctx: Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM skullboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.warning("skullboard is not **enabled**") 
     await self.bot.db.execute("DELETE FROM skullboard WHERE guild_id = $1", ctx.guild.id)
     await self.bot.db.execute("DELETE FROM skullboardmes WHERE guild_id = $1", ctx.guild.id)
     await ctx.success("Disabled skullboard **succesfully**")

    @skull.command(name='stats', description="check skullboard stats", aliases=["settings", "status"])
    @Permissions.has_permission(manage_guild=True)
    async def skull_stats(self, ctx: Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM skullboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.warning("skullboard is not **enabled**") 
     embed = Embed(color=self.bot.color, title="skullboard settings")
     if ctx.guild.get_channel(int(check["channel_id"])): embed.add_field(name="channel", value=ctx.guild.get_channel(int(check["channel_id"])).mention)
     if check["count"]: embed.add_field(name="amount", value=check["count"])
     if check["emoji_text"]: embed.add_field(name="emoji", value=check["emoji_text"])
     await ctx.reply(embed=embed)

    @skull.command(name="emoji", description="configure the skullboard emoji", brief="manage guild", usage="[emoji]")
    async def skull_emoji(self, ctx: Context, emoji: Union[PartialEmoji, str]): 
     check = await self.bot.db.fetchrow("SELECT * FROM skullboard WHERE guild_id = $1", ctx.guild.id)
     emoji_id = emoji.id if isinstance(emoji, PartialEmoji) else ord(str(emoji)) 
     if check is None: await self.bot.db.execute("INSERT INTO skullboard (guild_id, emoji_id, emoji_text) VALUES ($1,$2,$3)", ctx.guild.id, emoji_id, str(emoji)) 
     else: 
      await self.bot.db.execute("UPDATE skullboard SET emoji_id = $1 WHERE guild_id = $2", emoji_id, ctx.guild.id)
      await self.bot.db.execute("UPDATE skullboard SET emoji_text = $1 WHERE guild_id = $2", str(emoji), ctx.guild.id) 
     await ctx.success(f"Skullboard **emoji** set to {emoji}") 

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
     try:   
       check = await self.bot.db.fetchrow("SELECT * FROM skullboard WHERE guild_id = {}".format(payload.guild_id))
       if check: 
         if payload.emoji.is_unicode_emoji(): 
          if ord(str(payload.emoji)) != int(check["emoji_id"]): return  
         elif payload.emoji.is_custom_emoji(): 
          if payload.emoji.id != int(check["emoji_id"]): return
         message = await payload.member.guild.get_channel(payload.channel_id).fetch_message(payload.message_id) 
         chec = await self.bot.db.fetchrow(f"SELECT * FROM skullboardmes WHERE guild_id = {payload.guild_id} AND channel_message_id = {payload.channel_id} AND message_id = {payload.message_id}") 
         if chec is not None: 
            messa = await payload.member.guild.get_channel(int(chec['channel_skullboard_id'])).fetch_message(int(chec['message_skullboard_id']))
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
                  await self.bot.db.execute("INSERT INTO skullboardmes VALUES ($1,$2,$3,$4,$5)", payload.guild_id, channel.id, payload.channel_id, mes.id, payload.message_id)
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

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
     try: 
         check = await self.bot.db.fetchrow("SELECT * FROM skullboard WHERE guild_id = {}".format(payload.guild_id))
         if check is not None:  
          if payload.emoji.is_unicode_emoji():
           if ord(str(payload.emoji)) != int(check['emoji_id']): return
          elif payload.emoji.is_custom_emoji(): 
            if payload.emoji.id != int(check["emoji_id"]): return   
          message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id) 
          chec = await self.bot.db.fetchrow(f"SELECT * FROM skullboardmes WHERE guild_id = {payload.guild_id} AND channel_message_id = {payload.channel_id} AND message_id = {payload.message_id}") 
          if chec is not None: 
            messa = await self.bot.get_channel(int(chec['channel_skullboard_id'])).fetch_message(int(chec['message_skullboard_id']))
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

async def setup(bot):
    await bot.add_cog(skull(bot))  