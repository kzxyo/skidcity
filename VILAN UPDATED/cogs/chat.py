import discord, json
from discord.ext import commands
from tools.utils.checks import Perms, Messages
from typing import Union
from tools.utils.utils import EmbedBuilder

class Chat(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(3, 6, commands.BucketType.guild) 

    def get_ratelimit(self, message):
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()
  
    @commands.Cog.listener('on_message')
    async def on_autoresponder(self, message: discord.Message): 
     if Messages.good_message(message): 
      res = await self.bot.db.fetchrow("SELECT response FROM autoresponder WHERE guild_id = $1 AND trigger = $2", message.guild.id, message.content)
      if res:
       retry_after = self.get_ratelimit(message)
       if retry_after: return
       reply = res['response']
       try: 
        x=await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(message.author, reply))
        await message.channel.send(content=x[0],embed=x[1], view=x[2])
       except: await message.channel.send(EmbedBuilder.embed_replacement(message.author, reply))      
    
    @commands.Cog.listener('on_message')
    async def on_autoreact(self, message: discord.Message): 
     if Messages.good_message(message): 
      check = await self.bot.db.fetchrow("SELECT emojis FROM autoreact WHERE guild_id = $1 AND trigger = $2", message.guild.id, message.content)
      if check: 
       retry_after = self.get_ratelimit(message)
       if retry_after: return
       emojis = json.loads(check['emojis'])   
       for emoji in emojis: 
         try: await message.add_reaction(emoji)
         except: continue
    
    @commands.group(aliases=["ar"], invoke_without_command=True)
    async def autoresponder(self, ctx): 
      await ctx.create_pages()

    @autoresponder.command(name="add", help="config", description="add an autoresponder", usage="[trigger], [response]") 
    @Perms.get_perms("manage_guild")
    async def ar_add(self, ctx: commands.Context, *, arg: str): 
     arg = arg.split(', ')
     trigger = arg[0]
     try: response = arg[1]
     except: return await ctx.send_warning("No response has been found")
     check = await self.bot.db.fetchrow("SELECT * FROM autoresponder WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, trigger)
     if check: 
      await self.bot.db.execute("UPDATE autoresponder SET response = $1 WHERE guild_id = $2 AND trigger = $3", response, ctx.guild.id, trigger)
      return await ctx.send_success("Set response `{}` for the trigger `{}`".format(response, trigger))
     else: 
      await self.bot.db.execute("INSERT INTO autoresponder VALUES ($1,$2,$3)", ctx.guild.id, trigger, response)
      return await ctx.send_success("Added autoresponder with trigger `{}` and response `{}`".format(trigger, response)) 

    @autoresponder.command(name="remove", help="config", description="remove an autoresponder", usage="[trigger], [response]")
    @Perms.get_perms("manage_guild")
    async def ar_remove(self, ctx: commands.Context, *, trigger: str): 
      check = await self.bot.db.fetchrow("SELECT * FROM autoresponder WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, trigger)
      if not check: return await ctx.send_warning(f"Cannot find an autoresponse with the trigger `{trigger}`") 
      await self.bot.db.execute('DELETE FROM autoresponder WHERE guild_id = $1 AND trigger = $2', ctx.guild.id, trigger)
      await ctx.send_success(f"Deleted autoresponder for the trigger `{trigger}`")
    
    @autoresponder.command(name="variables", help="config", description="returns variables for autoresponder")
    async def ar_variables(self, ctx: commands.Context): 
      await ctx.invoke(self.bot.get_command('embed variables'))
    
    @autoresponder.command(name="list", help="config", description="returns a list of all autoresponders")
    async def ar_list(self, ctx: commands.Context): 
     results = await self.bot.db.fetch("SELECT * FROM autoresponder WHERE guild_id = $1", ctx.guild.id)
     if len(results) == 0: return await ctx.send_warning("There are no **autoresponders**") 
     l=0
     k=0
     mes=""
     embeds = [] 
     for result in results: 
      k+=1 
      l+=1 
      mes=mes+f"`{k}` {result['trigger']} - {result['response']}\n"
      if l == 10: 
        embeds.append(discord.Embed(color=self.bot.color, title=f"autoresponders ({len(results)})", description=mes))
        l=0
     embeds.append(discord.Embed(color=self.bot.color, title=f"autoresponders ({len(results)})", description=mes)) 
     await ctx.paginator(embeds)
    
    @commands.group(invoke_without_command=True)
    async def autoreact(self, ctx): 
      await ctx.create_pages()

    @autoreact.command(name="add", help="config", description="make the bot react with emojis on your message", brief="manage guild", usage="[content], [emojis]")     
    @Perms.get_perms("manage_guild")
    async def autoreact_add(self, ctx: commands.Context, *, content: str):
     con = content.split(",")
     if len(con) == 1: return await self.bot.help_command.send_command_help(ctx.command)
     emojis = [e for e in con[1].split(" ") if e != " "] 
     if len(emojis) == 0: return await self.bot.help_command.send_command_help(ctx.command)
     sql_as_text = json.dumps(emojis)  
     check = await self.bot.db.fetchrow("SELECT * FROM autoreact WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, con[0])
     if check: await self.bot.db.execute("UPDATE autoreact SET emojis = $1 WHERE guild_id = $2 AND trigger = $3", sql_as_text, ctx.guild.id, con[0])   
     else: await self.bot.db.execute("INSERT INTO autoreact VALUES ($1,$2,$3)", ctx.guild.id, con[0], sql_as_text)
     await ctx.send_success(f"Added autoreact for trigger **{con[0]}** - {''.join([e for e in emojis])}")
  
    @autoreact.command(name="remove", help="config", description="remove auto reactions from a content", brief="manage guild", usage='[content]')
    @Perms.get_perms("manage_guild")
    async def autoreact_remove(self, ctx: commands.Context, *, content: str): 
     check = await self.bot.db.fetchrow("SELECT * FROM autoreact WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, content)
     if not check: return await ctx.send_warning(f"No autoreact found for the trigger **{content}**")
     await self.bot.db.execute("DELETE FROM autoreact WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, content)
     return await ctx.send_success(f"Autoreact deleted for **{content}**")

    @autoreact.command(name="list", help="config", description="return a list of autoreactions in this server")
    async def autoreact_list(self, ctx: commands.Context): 
      check = await self.bot.db.fetch("SELECT * FROM autoreact WHERE guild_id = $1", ctx.guild.id)  
      if len(check) == 0: return await ctx.send_warning("this server has no **autoreactions**".capitalize())
      i=0
      k=1
      l=0
      mes = ""
      number = []
      messages = []
      for result in check:
              lol = json.loads(result['emojis'])
              mes = f"{mes}`{k}` {result['trigger']} - {''.join(l for l in lol)}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=self.bot.color, title=f"autoreactions ({len(check)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
      messages.append(mes)
      embed = discord.Embed(color=self.bot.color, title=f"autoreactions ({len(check)})", description=messages[i])
      number.append(embed)
      await ctx.paginator(number) 
    
async def setup(bot):
    await bot.add_cog(Chat(bot))