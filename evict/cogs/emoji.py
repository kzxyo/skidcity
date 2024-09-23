import discord, asyncio, io, re, aiohttp
from discord.ext import commands
from typing import Union, Optional, List
from io import BytesIO
from patches.permissions import Permissions
from itertools import zip_longest
from dataclasses import dataclass

IMAGE_TYPES = (".png", ".jpg", ".jpeg", ".gif", ".webp")
STICKER_KB = 512
STICKER_DIM = 320
STICKER_EMOJI = "😶"
MISSING_EMOJIS = "cant find emojis or stickers in that message."
MISSING_REFERENCE = "reply to a message with this command to steal an emoji."
MESSAGE_FAIL = "i couldn't grab that message."
UPLOADED_BY = "uploaded by"
STICKER_DESC = "stolen sticker"
STICKER_FAIL = "failed to upload sticker"
STICKER_SUCCESS = "uploaded sticker"
EMOJI_SUCCESS = "uploaded emoji"
STICKER_SLOTS = "this server doesn't have any more space for stickers."
EMOJI_FAIL = "failed to upload"
EMOJI_SLOTS = "this server doesn't have any more space for emojis."
INVALID_EMOJI = "invalid emoji or emoji ID."
STICKER_TOO_BIG = f"stickers may only be up to {STICKER_KB} KB and {STICKER_DIM}x{STICKER_DIM} pixels."
STICKER_ATTACHMENT = ""


@dataclass(init=True, order=True, frozen=True)
class StolenEmoji:
    animated: bool
    name: str
    id: int

    @property
    def url(self):
        return f"https://cdn.discordapp.com/emojis/{self.id}.{'gif' if self.animated else 'png'}"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, StolenEmoji) and self.id == other.id

class emoji(commands.Cog):
   def __init__(self, bot: commands.Bot):
      self.bot = bot

   @staticmethod
   def get_emojis(content: str) -> Optional[List[StolenEmoji]]:
      results = re.findall(r"<(a?):(\w+):(\d{10,20})>", content)
      return [StolenEmoji(*result) for result in results]
    
   @staticmethod
   def available_emoji_slots(guild: discord.Guild, animated: bool):
        current_emojis = len([em for em in guild.emojis if em.animated == animated])
        return guild.emoji_limit - current_emojis

   async def steal_ctx(self, ctx: commands.Context) -> Optional[List[Union[StolenEmoji, discord.StickerItem]]]:
        reference = ctx.message.reference
        if not reference:
            await ctx.warning("Reply to a message with this command to steal an emoji, or run ``addemoji``.")
            return None
        message = await ctx.channel.fetch_message(reference.message_id)
        if not message:
            await ctx.warning("I couldn't fetch that message.")
            return None
        if message.stickers:
            return message.stickers
        if not (emojis := self.get_emojis(message.content)):
            await ctx.warning("Can't find emojis or stickers in that message.")
            return None
        return emojis

   @commands.command(description="delete an emoji", usage="[emoji]", brief="manage emojis", aliases=["delemoji"])
   @Permissions.has_permission(manage_expressions=True) 
   async def deleteemoji(self, ctx: commands.Context, emoji: discord.Emoji): 
    
    await emoji.delete()
    await ctx.success(f"deleted the emoji {emoji.name}.")  

   @commands.command(description="add an emoji", usage="[emoji] <name>", brief="manage emojis")
   @Permissions.has_permission(manage_expressions=True) 
   async def addemoji(self, ctx: commands.Context, emoji: Union[discord.Emoji, discord.PartialEmoji], *, name: str=None):
    
    if not name: name = emoji.name 
    try:
     
     emoji = await ctx.guild.create_custom_emoji(image=await emoji.read(), name=name)
     await ctx.success(f"added emoji `{name}` | {emoji}".capitalize())
    
    except discord.HTTPException as e: return await ctx.error(ctx, f"Unable to add the emoji | {e}")

   @commands.command(description="add multiple emojis", usage="[emojis]", aliases=["am"], brief="manage emojis")
   @Permissions.has_permission(manage_expressions=True) 
   async def addmultiple(self, ctx: commands.Context, *emoji: Union[discord.Emoji, discord.PartialEmoji]): 
    
    if len(emoji) == 0: return await ctx.warning("Please provide some emojis to add")       
    emojis = []
    await ctx.channel.typing()
    
    for emo in emoji:
       try:
         emoj = await ctx.guild.create_custom_emoji(image=await emo.read(), name=emo.name)
         emojis.append(f"{emoj}")
         await asyncio.sleep(.5)
       
       except discord.HTTPException as e: return await ctx.error(ctx, f"Unable to add the emoji | {e}")

    embed = discord.Embed(color=self.bot.color, title=f"added {len(emoji)} emojis") 
    embed.description = "".join(map(str, emojis))    
    return await ctx.reply(embed=embed)
   
   @commands.group(invoke_without_command=True, description="manage server's stickers")
   async def sticker(self, ctx: commands.Context): 
    return await ctx.create_pages()

   @sticker.command(name="steal", description="add a sticker", aliases=['add'], usage="[attach sticker]", brief="manage emojis")
   @Permissions.has_permission(manage_expressions=True) 
   async def sticker_steal(self, ctx: commands.Context): 
    return await ctx.invoke(self.bot.get_command('stealsticker'))  
   
   @sticker.command(name="enlarge", aliases=['e', 'jumbo'], description="returns a sticker as a file", usage="[attach sticker]")
   async def sticker_enlarge(self, ctx: commands.Context): 
    
    if ctx.message.stickers: stick = ctx.message.stickers[0]
    
    else: 
     
     messages = [m async for m in ctx.channel.history(limit=20) if m.stickers]  
     if len(messages) == 0: return await ctx.warning("No sticker found")
     stick = messages[0].stickers[0]
    
    return await ctx.reply(file=await stick.to_file(filename=f"{stick.name}.png"))

   @Permissions.has_permission(manage_expressions=True) 
   @sticker.command(name="tag", aliases=['t'], brief="manage expressions", description="puts your vanity code in the stickers")
   async def sticker_tag(self, ctx: commands.Context): 
       
    if ctx.guild.vanity_url_code == None: return await ctx.warning("You **must** have a vanity set to run this command.")
    
    if len(ctx.guild.stickers) == 0:
            return await ctx.warning("There are **no** stickers in this server.")
    
    embed = discord.Embed(color=self.bot.color, description=f"{ctx.author.mention}: I have started **tagging** all the servers stickers.")
    message = await ctx.reply(embed=embed)
        
    for s in ctx.guild.stickers:
            v = ctx.guild.vanity_url_code
            await s.edit(name=f"/{v}")
            
    await message.edit(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: I have **tagged** all the guilds stickers."))
    
   @sticker.command(name='list', description="returns a list of server's stickers", aliases=["l"])
   async def sticker_list(self, ctx: commands.Context):
       
        if len(ctx.guild.stickers) == 0:
            return await ctx.warning("There are **no** stickers in this server.")
            
        sticker_list = [f"[**{sticker.name}**]({sticker.url}) (``{sticker.id}``)"
                     for sticker in ctx.guild.stickers]

        await ctx.paginate(sticker_list, f"server stickers [{len(ctx.guild.stickers)}]") 

   @sticker.command(name="delete", description="delete a sticker", usage="[attach sticker]", brief="manage emojis")
   @Permissions.has_permission(manage_expressions=True) 
   async def sticker_delete(self, ctx: commands.Context): 
    
    if ctx.message.stickers: 
     sticker = ctx.message.stickers[0]
     sticker = await sticker.fetch() 
     
     if sticker.guild.id != ctx.guild.id: return await ctx.warning("This sticker is not from this server")
     await sticker.delete(reason=f"sticker deleted by {ctx.author}") 
     return await ctx.success("Deleted the sticker")
    
    async for message in ctx.channel.history(limit=10): 
      
      if message.stickers: 
        sticker = message.stickers[0]
        s = await sticker.fetch()
        
        if s.guild_id == ctx.guild.id: 
         
         embed = discord.Embed(color=self.bot.color, description=f"Are you sure you want to delete `{s.name}`?").set_image(url=s.url)
         button1 = discord.ui.Button(emoji="<:check:1208233844751474708>")
         button2 = discord.ui.Button(emoji="<:stop:1208240063691886642>")
         
         async def button1_callback(interaction: discord.Interaction): 
          if ctx.author.id != interaction.user.id: return await self.bot.ext.warning(interaction, "You are not the author of this embed")
          await s.delete()
          return await interaction.response.edit_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {interaction.user.mention}: Deleted sticker"), view=None)   
         
         async def button2_callback(interaction: discord.Interaction): 
           if ctx.author.id != interaction.user.id: return await self.bot.ext.warning(interaction, "You are not the author of this embed")
           return await interaction.response.edit_message(embed=discord.Embed(color=self.bot.color, description=f"{interaction.user.mention}"))
         
         button1.callback = button1_callback
         button2.callback = button2_callback 
         
         view = discord.ui.View()
         view.add_item(button1)
         view.add_item(button2)
         
         return await ctx.reply(embed=embed, view=view)
         
   @commands.command(description="add a sticker", usage="[attach sticker]", brief="manage expressions", aliases=["stickersteal", "addsticker", "stickeradd"])
   @Permissions.has_permission(manage_expressions=True) 
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
       embed = discord.Embed(color=self.bot.color, title="sticker added")
       embed.set_thumbnail(url=url)
       embed.add_field(name="values", value=f"name: `{name}`\nid: `{sticker.id}`\nformat: `{form}`\nlink: [url]({url})")
       
       return await ctx.reply(embed=embed)
      
      except Exception as error: return await ctx.error(ctx, f"Unable to add this sticker - {error}")
     
     elif not ctx.message.stickers:
      async for message in ctx.channel.history(limit=10):
       
       if message.stickers:
        
        e = discord.Embed(color=self.bot.color, title=message.stickers[0].name).set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        e.set_image(url=message.stickers[0].url)
        e.set_footer(text="react below to steal")
        
        button1 = discord.ui.Button(label="", style=discord.ButtonStyle.gray, emoji="<:check:1208233844751474708>")
        button2 = discord.ui.Button(label="", style=discord.ButtonStyle.gray, emoji="<:stop:1208240063691886642>")
        
        async def button1_callback(interaction: discord.Interaction): 
          
          if interaction.user != ctx.author: return await self.bot.ext.warning(interaction, "you cant use this button", ephemeral=True)
          
          try:
           
           url = message.stickers[0].url
           name = message.stickers[0].name
           img_data = await self.bot.session.read(url)
           tobytess = BytesIO(img_data)
           file = discord.File(fp=tobytess)
           sticker = await ctx.guild.create_sticker(name=name, description=name, emoji="skull", file=file, reason=f"sticker created by {ctx.author}")
           format = str(sticker.format) 
           form = format.replace("StickerFormatType.", "")
           
           embed = discord.Embed(color=self.bot.color, title="sticker added")
           embed.set_thumbnail(url=url)
           embed.add_field(name="values", value=f"name: `{name}`\nid: `{sticker.id}`\nformat: `{form}`\nlink: [url]({url})")
           
           return await interaction.response.edit_message(embed=embed, view=None)
          
          except:
           embed = discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.author.mention}: unable to add this sticker")
           return await interaction.response.edit_message(embed=embed, view=None)

        button1.callback = button1_callback 

        async def button2_callback(interaction: discord.Interaction): 
          if interaction.user != ctx.author: return await self.bot.ext.warning(interaction, "You can't use this button", ephemeral=True)            
          return await interaction.response.edit_message(embed=discord.Embed(color=self.bot.color, description=f"{interaction.user.mention}: Cancelled sticker steal"), view=None)

        button2.callback = button2_callback 

        view = discord.ui.View()
        view.add_item(button1)
        view.add_item(button2)
        
        return await ctx.reply(embed=e, view=view)      
       
     return await ctx.error("No sticker found")
            
   @commands.command(name='emojilist', description="returns a list of server's emojis", aliases=["emojis"])
   async def emojilist(self, ctx: commands.Context):
       
        if len(ctx.guild.emojis) == 0:
            return await ctx.warning("There are **no** emojis in this server.")
            
        emoji_list = [f"{emoji} - [**{emoji.name}**]({emoji.url}) (``{emoji.id}``)"
                     for emoji in ctx.guild.emojis]

        await ctx.paginate(emoji_list, f"server emojis [{len(ctx.guild.emojis)}]")  

   @commands.command(aliases=["downloademoji", "e", 'jumbo'], description="gets an image version of your emoji", usage="[emoji]")
   async def enlarge(self, ctx: commands.Context, emoj: Union[discord.PartialEmoji, str]): 
    if isinstance(emoj, discord.PartialEmoji): return await ctx.reply(file=await emoj.to_file(filename=f"{emoj.name}{'.gif' if emoj.animated else '.png'}"))
    elif isinstance(emoj, str): return await ctx.reply(file=discord.File(fp=await self.bot.getbyte(f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{ord(emoj):x}.png"), filename="emoji.png"))
   
   @commands.command(aliases=['ei'], description="show emoji info", usage="[emoji]")
   async def emojiinfo(self, ctx: commands.Context, *, emoji: Union[discord.Emoji, discord.PartialEmoji]): 
    
    embed = discord.Embed(color=self.bot.color, title=emoji.name, timestamp=emoji.created_at).set_footer(text=f"id: {emoji.id}")
    embed.set_thumbnail(url=emoji.url)
    embed.add_field(name="animated", value=emoji.animated)
    embed.add_field(name="link", value=f"[emoji]({emoji.url})")
    
    if isinstance(emoji, discord.Emoji): 
     embed.add_field(name="guild", value=emoji.guild.name) 
     embed.add_field(name="usable", value=emoji.is_usable())
     embed.add_field(name="available", value=emoji.available) 
     
     emo = await emoji.guild.fetch_emoji(emoji.id)
     
     embed.add_field(name="created by", value=str(emo.user))
    
    return await ctx.reply(embed=embed) 
   
   @commands.command(name='steal', description="reply to a message to steal an emoji or sticker", usage="[emojis]", brief="manage expressions")
   @commands.has_permissions(manage_expressions=True)
   async def steal(self, ctx: commands.Context, *names: str):
        
        if not (emojis := await self.steal_ctx(ctx)):
            return
        
        if isinstance(emojis[0], discord.StickerItem):
            if len(ctx.guild.stickers) >= ctx.guild.sticker_limit:
                return await ctx.warning('there are no more sticker slots.')
            
            sticker = emojis[0]
            fp = io.BytesIO()
            
            try:
                await sticker.save(fp)
                await ctx.guild.create_sticker(name=sticker.name, description=STICKER_DESC, emoji=STICKER_EMOJI, file=discord.File(fp), reason=f'uploaded by {ctx.author}')
            
            except Exception as error:
                return await ctx.warning(f"{STICKER_FAIL}, {type(error).__name__}: {error}")
            return await ctx.success(f"{STICKER_SUCCESS}: {sticker.name}")
        
        names = [''.join(re.findall(r"\w+", name)) for name in names]
        names = [name if len(name) >= 2 else None for name in names]
        emojis = list(dict.fromkeys(emojis))

        async with aiohttp.ClientSession() as session:
            for emoji, name in zip_longest(emojis, names):
                if not self.available_emoji_slots(ctx.guild, emoji.animated):
                    return await ctx.warning(EMOJI_SLOTS)
                if not emoji:
                    break
                try:
                    async with session.get(emoji.url) as resp:
                        image = io.BytesIO(await resp.read()).read()
                    added = await ctx.guild.create_custom_emoji(name=name or emoji.name, image=image, reason=f'uploaded by {ctx.author}')
                except Exception as error:
                    return await ctx.warning(f"{EMOJI_FAIL} {emoji.name}, {type(error).__name__}: {error}")
                try:
                    await ctx.message.add_reaction(added)
                except:
                    pass
                
   # @commands.cooldown(rate=1, per=15)
   @commands.command(name="fromimage", description="add an emoji from an image", brief="manage expressions")
   @commands.has_permissions(manage_expressions=True)
   async def _add_from_image(self, ctx: commands.Context, name: str = None):

        async with ctx.typing():
            if len(ctx.message.attachments) > 1:
                return await ctx.warning("only attach 1 file.")

            if not ctx.message.attachments[0].filename.endswith((".png", ".jpg", ".gif")):
                return await ctx.warning("Please make sure the uploaded image is a `.png`, `.jpg`, or `.gif` file.")

            image = await ctx.message.attachments[0].read()

            try:
                new = await asyncio.wait_for(
                    ctx.guild.create_custom_emoji(
                        name=name or ctx.message.attachments[0].filename[:-4],
                        image=image,
                        reason=f"emoji added by {ctx.author.name}",
                    ),
                    timeout=10,
                )
            except asyncio.TimeoutError:
                return await ctx.warning("your request has **timed out**.")
            except discord.HTTPException:
                return await ctx.warning("something went wrong while adding emojis.")

        return await ctx.success(f"{new} has been added to the server.")

async def setup(bot) -> None:
    await bot.add_cog(emoji(bot))   
