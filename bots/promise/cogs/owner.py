from cogs.events import commandhelp
import discord, button_paginator as pg
from discord.ext import commands
from core.utils.classes import Colors, Emojis
from cogs.events import sendmsg

class owner(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
       self.bot = bot           

   @commands.command(aliases=["guilds"])
   async def servers(self, ctx):
            if not ctx.author.id in self.bot.owner_ids: return 
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for guild in self.bot.guilds:
              mes = f"{mes}`{k}` {guild.name} ({guild.id}) - ({guild.member_count})\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=Colors.green, title=f"servers :  {len(self.bot.guilds)}", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            number.append(discord.Embed(color=Colors.green, title=f"servers :  {len(self.bot.guilds)}", description=messages[i]))
            paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
            paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
            paginator.add_button('next', emoji="<:right:1018156484170883154>")
            await paginator.start()    

   @commands.command()
   async def portal(self, ctx, id: int=None):
     if not ctx.author.id in self.bot.owner_ids: 
       return 

     if id == None:
        await ctx.send("you didnt specifiy a guild id", delete_after=1)
        await ctx.message.delete()
     else: 
      await ctx.message.delete()      
      guild = self.bot.get_guild(id)
      for c in guild.text_channels:
        if c.permissions_for(guild.me).create_instant_invite: 
            invite = await c.create_invite()
            await ctx.author.send(f"{guild.name} invite link - {invite}")
            break
            
async def setup(bot) -> None:
    await bot.add_cog(owner(bot))      
