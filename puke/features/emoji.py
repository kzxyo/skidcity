import discord, asyncio
from discord.ext import commands
from typing import Union
from io import BytesIO
from tools.checks import Perms as utils

class Emoji(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
      self.bot = bot

   @commands.command(description="delete an emoji", usage="[emoji]", brief="manage emojis", aliases=["delemoji"])
   @utils.get_perms("manage_emojis")
   async def deleteemoji(self, ctx: commands.Context, emoji: discord.Emoji): 
    await emoji.delete()
    await ctx.approve("Deleted the emoji")  

   @commands.command(description="add an emoji", usage="[emoji] <name>", brief="manage emojis", aliases=['steal'])
   @utils.get_perms("manage_emojis")
   async def addemoji(self, ctx: commands.Context, emoji: Union[discord.Emoji, discord.PartialEmoji], *, name: str=None):
    if not name: name = emoji.name 
    try:
     emoji = await ctx.guild.create_custom_emoji(image=await emoji.read(), name=name)
     await ctx.approve(f"added emoji `{name}` | {emoji}".capitalize())
    except discord.HTTPException as e: return await ctx.warn(ctx, f"Unable to add the emoji | {e}")

   @commands.command(description="add multiple emojis", help="emoji", usage="[emojis]", aliases=["am"], brief="manage emojis")
   @utils.get_perms("manage_emojis")
   async def addmultiple(self, ctx: commands.Context, *emoji: Union[discord.Emoji, discord.PartialEmoji]): 
    if len(emoji) == 0: return await ctx.warn("Please provide some emojis to add")       
    emojis = []
    await ctx.channel.typing()
    for emo in emoji:
       try:
         emoj = await ctx.guild.create_custom_emoji(image=await emo.read(), name=emo.name)
         emojis.append(f"{emoj}")
         await asyncio.sleep(5)
       except discord.HTTPException as e: return await ctx.warn(ctx, f"Unable to add the emoji | {e}")

    embed = discord.Embed(title=f"added {len(emoji)} emojis") 
    embed.description = "".join(map(str, emojis))    
    return await ctx.reply(embed=embed)
   
   @commands.group(invoke_without_command=True, help="emoji", description="manage server's stickers")
   async def sticker(self, ctx: commands.Context): 
    return await ctx.create_pages()

   @sticker.command(name="steal", description="add a sticker", aliases=['add'], usage="[attach sticker]", brief="manage emojis")
   @utils.get_perms("manage_emojis")
   async def sticker_steal(self, ctx: commands.Context): 
    return await ctx.invoke(self.bot.get_command('stealsticker'))  
   
   @sticker.command(name="enlarge", aliases=['e', 'jumbo'], help="emoji", description="returns a sticker as a file", usage="[attach sticker]")
   async def sticker_enlarge(self, ctx: commands.Context): 
    if ctx.message.stickers: stick = ctx.message.stickers[0]
    else: 
     messages = [m async for m in ctx.channel.history(limit=20) if m.stickers]  
     if len(messages) == 0: return await ctx.warn("No sticker found")
     stick = messages[0].stickers[0]
    return await ctx.reply(file=await stick.to_file(filename=f"{stick.name}.png"))

   @sticker.command(name="delete", help="emoji", description="delete a sticker", usage="[attach sticker]", brief="manage emojis")
   @utils.get_perms("manage_emojis")
   async def sticker_delete(self, ctx: commands.Context): 
    if ctx.message.stickers: 
     sticker = ctx.message.stickers[0]
     sticker = await sticker.fetch() 
     if sticker.guild.id != ctx.guild.id: return await ctx.warn("This sticker is not from this server")
     await sticker.delete(reason=f"sticker deleted by {ctx.author}") 
     return await ctx.approve("Deleted the sticker")
    async for message in ctx.channel.history(limit=10): 
      if message.stickers: 
        sticker = message.stickers[0]
        s = await sticker.fetch()
        if s.guild_id == ctx.guild.id: 
         embed = discord.Embed(description=f"Are you sure you want to delete `{s.name}`?").set_image(url=s.url)
         button1 = discord.ui.Button(emoji="<:approve:1203608161513373718>")
         button2 = discord.ui.Button(emoji="<:deny:1203608169528565780>")
         async def button1_callback(interaction: discord.Interaction): 
          if ctx.author.id != interaction.user.id: return await self.bot.ext.warn(interaction, "You are not the author of this embed")
          await s.delete()
          return await interaction.response.edit_message(embed=discord.Embed(description=f"{interaction.user.mention}: Deleted sticker"), view=None)   
         
         async def button2_callback(interaction: discord.Interaction): 
           if ctx.author.id != interaction.user.id: return await self.bot.ext.warn(interaction, "You are not the author of this embed")
           return await interaction.response.edit_message(embed=discord.Embed(description=f"{interaction.user.mention}"))
         
         button1.callback = button1_callback
         button2.callback = button2_callback 
         view = discord.ui.View()
         view.add_item(button1)
         view.add_item(button2)
         return await ctx.reply(embed=embed, view=view)
         
   @commands.command(description="add a sticker", help="emoji", usage="[attach sticker]", brief="manage emojis", aliases=["stickersteal", "addsticker", "stickeradd"])
   @utils.get_perms("manage_emojis")
   async def stealsticker(self, ctx: commands.Context):
     if ctx.message.stickers:
      try:
       url = ctx.message.stickers[0].url
       name = ctx.message.stickers[0].name
       img_data = await self.bot.session.read(url)
       tobytess = BytesIO(img_data)
       file = discord.File(fp=tobytess)
       sticker = await ctx.guild.create_sticker(name=name, description=name, emoji="skull", file=file, reason=f"sticker created by {ctx.author}")
       format = str(sticker.format) 
       form = format.replace("StickerFormatType.", "")
       embed = discord.Embed(title="sticker added")
       embed.set_thumbnail(url=url)
       embed.add_field(name="values", value=f"name: `{name}`\nid: `{sticker.id}`\nformat: `{form}`\nlink: [url]({url})")
       return await ctx.reply(embed=embed)
      except Exception as error: return await ctx.approve(ctx, f"Unable to add this sticker - {error}")
     elif not ctx.message.stickers:
      async for message in ctx.channel.history(limit=10):
       if message.stickers:
        e = discord.Embed(title=message.stickers[0].name).set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        e.set_image(url=message.stickers[0].url)
        e.set_footer(text="react below to steal")
        button1 = discord.ui.Button(label="", style=discord.ButtonStyle.gray, emoji="<:check:1198054589136646164>")
        button2 = discord.ui.Button(label="", style=discord.ButtonStyle.gray, emoji="<:deny:1198055643186221068>")
        
        async def button1_callback(interaction: discord.Interaction): 
          if interaction.user != ctx.author: return await self.bot.ext.warn(interaction, "You can't use this button", ephemeral=True)
          try:
           url = message.stickers[0].url
           name = message.stickers[0].name
           img_data = await self.bot.session.read(url)
           tobytess = BytesIO(img_data)
           file = discord.File(fp=tobytess)
           sticker = await ctx.guild.create_sticker(name=name, description=name, emoji="skull", file=file, reason=f"sticker created by {ctx.author}")
           format = str(sticker.format) 
           form = format.replace("StickerFormatType.", "")
           embed = discord.Embed(title="sticker added")
           embed.set_thumbnail(url=url)
           embed.add_field(name="values", value=f"name: `{name}`\nid: `{sticker.id}`\nformat: `{form}`\nlink: [url]({url})")
           return await interaction.response.edit_message(embed=embed, view=None)
          except:
           embed = discord.Embed(description=f"{ctx.author.mention}: Unable to add this sticker")
           return await interaction.response.edit_message(embed=embed, view=None)

        button1.callback = button1_callback 

        async def button2_callback(interaction: discord.Interaction): 
          if interaction.user != ctx.author: return await self.bot.ext.warn(interaction, "You can't use this button", ephemeral=True)            
          return await interaction.response.edit_message(embed=discord.Embed(cdescription=f"{interaction.user.mention}: Cancelled sticker steal"), view=None)

        button2.callback = button2_callback 

        view = discord.ui.View()
        view.add_item(button1)
        view.add_item(button2)
        return await ctx.reply(embed=e, view=view)      
       
     return await ctx.warn(ctx, "No sticker found")

   @commands.command(description="returns a list of server's emojis", help="emoji", aliases=["emojis"])
   async def emojilist(self, ctx: commands.Context):
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for emoji in ctx.guild.emojis:
              mes = f"{mes}`{k}` {emoji} - ({emoji.name})\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            number.append(discord.Embed( title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]", description=messages[i]))
            await ctx.paginator(number)       

   @commands.command(aliases=["downloademoji", "e", 'jumbo'], description="gets an image version of your emoji", help="emoji", usage="[emoji]")
   async def enlarge(self, ctx: commands.Context, emoj: Union[discord.PartialEmoji, str]): 
    if isinstance(emoj, discord.PartialEmoji): return await ctx.reply(file=await emoj.to_file(filename=f"{emoj.name}{'.gif' if emoj.animated else '.png'}"))
    elif isinstance(emoj, str): return await ctx.reply(file=discord.File(fp=await self.bot.getbyte(f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{ord(emoj):x}.png"), filename="emoji.png"))
   
   @commands.command(aliases=['ei'], description="show emoji info", help="emoji", usage="[emoji]")
   async def emojiinfo(self, ctx: commands.Context, *, emoji: Union[discord.Emoji, discord.PartialEmoji]): 
    embed = discord.Embed(title=emoji.name, timestamp=emoji.created_at).set_footer(text=f"id: {emoji.id}")
    embed.set_thumbnail(url=emoji.url)
    embed.add_field(name="Animated", value=emoji.animated)
    embed.add_field(name="Link", value=f"[emoji]({emoji.url})")
    if isinstance(emoji, discord.Emoji): 
     embed.add_field(name="Guild", value=emoji.guild.name) 
     embed.add_field(name="Usable", value=emoji.is_usable())
     embed.add_field(name="Available", value=emoji.available) 
     emo = await emoji.guild.fetch_emoji(emoji.id)
     embed.add_field(name="Created by", value=str(emo.user))
    return await ctx.reply(embed=embed) 
  
async def setup(bot) -> None:
    await bot.add_cog(Emoji(bot))   
