import discord, asyncio
from discord.ext import commands
from typing import Union
from tools.utils.checks import Perms

class Emoji(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.command(description="add an emoji to your server", help="emoji", usage="[emoji] <name>")
    @Perms.get_perms("manage_emojis")
    async def addemoji(self, ctx: commands.Context, emoji: Union[discord.Emoji, discord.PartialEmoji], *, name: str=None):
      if not name: name = emoji.name
      try:
        emoji = await ctx.guild.create_custom_emoji(image= await emoji.read(), name=name)
        return await ctx.send_success(f"added {emoji} as `{name}`")
      except discord.HTTPException as e: await ctx.send_error(f"Unable to add emoji - {e}")
    
    @commands.command(description="add multiple emojis", help="emoji", usage="[emojis]", aliases=["am"], brief="manage emojis")
    @Perms.get_perms("manage_emojis")
    async def addmultiple(self, ctx: commands.Context, *emoji: Union[discord.Emoji, discord.PartialEmoji]): 
      if len(emoji) == 0: return await ctx.send_warning("Please provide the emojis you want to add")       
      emojis = []
      await ctx.channel.typing()
      for emo in emoji:
       try:
         emoj = await ctx.guild.create_custom_emoji(image=await emo.read(), name=emo.name)
         emojis.append(f"{emoj}")
         await asyncio.sleep(.5)
       except discord.HTTPException as e: return await ctx.send_error(f"Unable to add the emoji -> {e}")

      embed = discord.Embed(color=self.bot.color, title=f"added {len(emoji)} emojis") 
      embed.description = "".join(map(str, emojis))    
      return await ctx.reply(embed=embed)
    
    @commands.command(description="see a list of the server emojis", help="emoji")
    async def emojilist(self, ctx):
        i=0
        k=1
        l=0
        mes = ""
        number = []
        messages = []
        if not ctx.guild.emojis: return await ctx.send_error("This server has no emojis")
        for emoji in ctx.guild.emojis:
          mes = f"{mes}`{k}` {emoji} - {emoji.name}\n"
          k+=1
          l+=1
          if l == 10:
           messages.append(mes)
           number.append(discord.Embed(color=self.bot.color, title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]", description=messages[i]))
           i+=1
           mes = ""
           l=0
        
        messages.append(mes)
        number.append(discord.Embed(color=self.bot.color, title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]", description=messages[i]))
        await ctx.paginator(number)
    
    @commands.command(aliases=["downloademoji", "e"], description="gets an image version of your emoji", help="emoji", usage="[emoji]")
    async def enlarge(self, ctx: commands.Context, emoj: Union[discord.PartialEmoji, str]): 
      if isinstance(emoj, discord.PartialEmoji): return await ctx.reply(file=await emoj.to_file(filename=f"{emoj.name}{'.gif' if emoj.animated else '.png'}"))
      elif isinstance(emoj, str): return await ctx.reply(file=discord.File(fp=await self.bot.getbyte(f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{ord(emoj):x}.png"), filename="emoji.png"))
    
async def setup(bot):
    await bot.add_cog(Emoji(bot))