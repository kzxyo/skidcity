import discord, aiohttp, button_paginator as pg
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote

class emoji(commands.Cog):
   def __init__(self, bot):
      self.bot = bot
      
# Add Emojis Command
    
   @commands.command(aliases=['addemote', 'add', 'ae'])
   @commands.cooldown(1, 3, commands.BucketType.user)
   async def addemoji(self, ctx, emoji: Union[discord.Emoji, discord.PartialEmoji] = None, *, name = None):
    if (not ctx.author.guild_permissions.manage_emojis_and_stickers):
        embed = discord.Embed(colour=hex.normal, description=f"**{emote.warning} {ctx.author.mention} You are missing: `Manage emojis & Stickers` **")
        await ctx.reply(embed=embed)
        return
    e = discord.Embed(colour=hex.warning, description=f"**{emote.warning} {ctx.author.mention}: Usage: `,addemoji [emote]`**")
    if emoji is None: return await ctx.reply(embed=e)
    await ctx.channel.typing()
    if name == None:
        name = emoji.name
    emoteurl = emoji.url
    async with aiohttp.ClientSession() as ses: 
     async with ses.get(emoteurl) as r:
        try:
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                emoji = await ctx.guild.create_custom_emoji(image=bytes, name=name)
                e = discord.Embed(colour=hex.normal, description=f"{ctx.author.mention} **added {emoji} as {name}**")
                await ctx.reply(embed=e)
        except discord.HTTPException as re:
          pass
       
# Add Multiple Emotes

   @commands.command(aliases=['addmulti', 'am', 'addmore'])
   @commands.cooldown(1, 6, commands.BucketType.guild)
   async def addmultiple(self, ctx: commands.Context, *emoji: Union[discord.Emoji, discord.PartialEmoji]):
    if (not ctx.author.guild_permissions.manage_emojis_and_stickers):
     embed = discord.Embed(colour=hex.warning, description=f"{emote.warning} {ctx.author.mention}**: You do not have the `manage_emojis_and_stickers` permission.**")
     await ctx.reply(embed=embed)
     return
    if len(emoji) > 20: return await ctx.reply("you can only add up to 20 emojis at once")
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
    embed = discord.Embed(color=hex.normal, title=f"Rockstar has added {len(emoji)} emojis") 
    embed.description = "".join(map(str, emojis))    
    await ctx.reply(embed=embed)
    
# Server Emote List

   @commands.command(aliases=['emojis', 'emotes'])
   @commands.cooldown(1, 3, commands.BucketType.user)
   async def emojilist(self, ctx: commands.Context):
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for emoji in ctx.guild.emojis:
              mes = f"{mes}`{k}` {emoji} - `{emoji.name}`\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=hex.normal, title=f"emojis in {ctx.guild.name} ({len(ctx.guild.emojis)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
            messages.append(mes)
            number.append(discord.Embed(color=hex.normal, title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]", description=messages[i]))
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
            paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
            paginator.add_button('next', emoji="<:right:1018156484170883154>")
            await paginator.start()

async def setup(bot) -> None:
    await bot.add_cog(emoji(bot))   
