import discord, aiohttp, button_paginator as pg
from cogs.events import noperms, commandhelp, sendmsg
from core.utils.classes import Colors, Emojis
from discord.ext import commands
from typing import Union
from io import BytesIO

class emoji(commands.Cog):
   def __init__(self, bot):
      self.bot = bot
    
   @commands.command(help="add an emoji", description="utility", usage="[emoji] <name>")
   @commands.cooldown(1, 4, commands.BucketType.user)
   async def addemoji(self, ctx, emoji: Union[discord.Emoji, discord.PartialEmoji]=None, *, name=None):
    if (not ctx.author.guild_permissions.manage_emojis_and_stickers):
     await noperms(self, ctx, "manage_emojis_and_stickers")
     return
    if emoji is None: return await commandhelp(self, ctx, ctx.command.name) 
    if name == None:
        name = emoji.name

    url = emoji.url
    async with aiohttp.ClientSession() as ses: 
     async with ses.get(url) as r:
        try:
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                emoji = await ctx.guild.create_custom_emoji(image=bytes, name=name)
                await sendmsg(self, ctx, f"i add `{name}` | {emoji}", None, None, None, None)
        except discord.HTTPException as re:
          pass

   @commands.command(help="add multiple emojis", description="utility", usage="[emojis]", aliases=["am"])
   @commands.cooldown(1, 6, commands.BucketType.guild)
   async def addmultiple(self, ctx: commands.Context, *emoji: Union[discord.Emoji, discord.PartialEmoji]):
    if (not ctx.author.guild_permissions.manage_emojis_and_stickers):
     await noperms(self, ctx, "manage_emojis_and_stickers")
     return
    if len(emoji) == 0: return await commandhelp(self, ctx, ctx.command.name) 
    if len(emoji) > 30: return await ctx.reply("you can only add up to 30 emojis at once")
    emojis = []
    await ctx.channel.typing()
    for emo in emoji:
        url = emo.url
        async with aiohttp.ClientSession() as ses: 
          async with ses.get(url) as r:
             try:
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                emoj = await ctx.guild.create_custom_emoji(image=bytes, name=emo.name)
                emojis.append(f"{emoj}")
             except discord.HTTPException as re:
               pass

    embed = discord.Embed(color=Colors.green, title=f"I add {len(emoji)} emojis") 
    embed.description = "".join(map(str, emojis))    
    await sendmsg(self, ctx, None, embed, None, None, None)

   @commands.command(help="returns a list of server's emojis", description="utility")
   @commands.cooldown(1, 3, commands.BucketType.user)
   async def emojilist(self, ctx: commands.Context):
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for emoji in ctx.guild.emojis:
              mes = f"{mes}`{k}` {emoji} - {emoji.name}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=Colors.green, title=f"There are {len(ctx.guild.emojis)} emojis in {ctx.guild.name}", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            number.append(discord.Embed(color=Colors.green, title=f"emojis in {ctx.guild.name} {len(ctx.guild.emojis)}", description=messages[i]))
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
            paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
            paginator.add_button('next', emoji="<:right:1018156484170883154>")
            await paginator.start()        

   @commands.command(aliases=["downloademoji", "e"], help="gets an image version of your emoji", description="utility", usage="[emoji]")
   @commands.cooldown(1, 4, commands.BucketType.user)
   async def enlarge(self, ctx, emoji: Union[discord.PartialEmoji, str]=None):
    if emoji is None:
     await commandhelp(self, ctx, ctx.command.name)
     return  
    elif isinstance(emoji, discord.PartialEmoji): 
      await sendmsg(self, ctx, emoji.url, None, None, None, None)
      return
    elif isinstance(emoji, str):
      ordinal = ord(emoji)
      await sendmsg(self, ctx, f"https://twemoji.maxcdn.com/v/latest/72x72/{ordinal:x}.png", None, None, None, None)
    else:
       e = discord.Embed(color=Colors.green, description=f"{Emojis.Emojis.warninging} {ctx.author.mention}: emoji not found")
       await sendmsg(self, ctx, None, e, None, None, None)

async def setup(bot) -> None:
    await bot.add_cog(emoji(bot))   
