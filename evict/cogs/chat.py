import discord, json
from utils.embed import Embed
from discord.ext import commands 
from patches.permissions import Permissions

class chat(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
    self._cd = commands.CooldownMapping.from_cooldown(3, 6, commands.BucketType.guild) 

  def get_ratelimit(self, message):
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

  @commands.group(aliases=["ar"], invoke_without_command=True)
  async def autoresponder(self, ctx): 
    await ctx.create_pages()

  @autoresponder.command(name="list")
  async def ar_list(self, ctx: commands.Context): 
        
        results = await self.bot.db.fetch("SELECT * FROM autoresponses WHERE guild_id = $1", ctx.guild.id)
        
        if not results: return await ctx.warning(f"There are no **autoresponders** set.")
        return await ctx.paginate([f"{result['key']} - {result['response']}" for result in results], f"autoresponders ({len(results)})", {"name": ctx.guild.name, "icon_url": ctx.guild.icon})  

  @autoresponder.command(name='delete', description='delete an autoresponder', brief="manage guild", aliases=['del', 'remove', 'rm'], usage="trigger")
  @Permissions.has_permission(manage_guild=True) 
  async def delete(self, ctx: commands.Context, *, toggle: str):
        
        key = await ctx.bot.db.fetch("SELECT * FROM autoresponses WHERE guild_id = $1 AND key = $2", ctx.guild.id, toggle.lstrip())
        if not key: return await ctx.warning(f"You don't have an autoresponse for `{toggle}`")
        
        await ctx.bot.db.execute("DELETE FROM autoresponses WHERE guild_id = $1 AND key = $2", ctx.guild.id, toggle)
        return await ctx.success(f'I have successfully **deleted** the autoresponse for `{toggle}`')
    
  @autoresponder.command(name='add', description='create an autoresponder', brief="manage guild", aliases=['set'], usage="[trigger], [response]")
  @Permissions.has_permission(manage_guild=True) 
  async def add(self, ctx: commands.Context, *, message: str):
        
        autoresponse = message.split(',', 1)
        key = await ctx.bot.db.fetch("SELECT * FROM autoresponses WHERE guild_id = $1 AND key = $2", ctx.guild.id, autoresponse[0])
        if key: return await ctx.warning(f"You **already** have an autoresponse for `{autoresponse[0]}`")
        
        await ctx.bot.db.execute("INSERT INTO autoresponses VALUES ($1, $2, $3)", ctx.guild.id, autoresponse[0], autoresponse[1].lstrip())
        return await ctx.success(f'I have **added** the autoresponse for `{autoresponse[0].lstrip()}` with response `{autoresponse[1].lstrip()}`')

  @autoresponder.command(name="variables", help="config", description="returns variables for autoresponder")
  async def ar_variables(self, ctx: commands.Context): 
    await ctx.invoke(self.bot.get_command('embed variables'))

  @commands.group(invoke_without_command=True)
  async def autoreact(self, ctx): 
    await ctx.create_pages()

  @autoreact.command(name="add", description="make the bot react with emojis on your message", brief="manage guild", usage="[content], [emojis]")     
  @Permissions.has_permission(manage_guild=True) 
  async def autoreact_add(self, ctx: commands.Context, *, content: str):
    
    con = content.split(",")
    if len(con) == 1: return await self.bot.help_command.send_command_help(ctx.command)
    
    emojis = [e for e in con[1].split(" ") if e != " "] 
    if len(emojis) == 0: return await self.bot.help_command.send_command_help(ctx.command)
    
    sql_as_text = json.dumps(emojis)  
    check = await self.bot.db.fetchrow("SELECT * FROM autoreact WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, con[0])
    
    if check: await self.bot.db.execute("UPDATE autoreact SET emojis = $1 WHERE guild_id = $2 AND trigger = $3", sql_as_text, ctx.guild.id, con[0])   
    else: await self.bot.db.execute("INSERT INTO autoreact VALUES ($1,$2,$3)", ctx.guild.id, con[0], sql_as_text)
    
    await ctx.success(f"I have **added** the autoreact for **{con[0]}** - {''.join([e for e in emojis])}")
  
  @autoreact.command(name="remove", help="config", description="remove auto reactions from a content", brief="manage guild", usage='[content]')
  @Permissions.has_permission(manage_guild=True) 
  async def autoreact_remove(self, ctx: commands.Context, *, content: str): 
    
    check = await self.bot.db.fetchrow("SELECT * FROM autoreact WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, content)
    if not check: return await ctx.success(f"No autoreaction found with the content **{content}**")
    
    await self.bot.db.execute("DELETE FROM autoreact WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, content)
    return await ctx.success(f"Deleted autoreaction with the content **{content}**")

  @autoreact.command(name="list", description="return a list of autoreactions in this server")
  async def autoreact_list(self, ctx: commands.Context): 
      check = await self.bot.db.fetch("SELECT * FROM autoreact WHERE guild_id = $1", ctx.guild.id)  
      if len(check) == 0: return await ctx.warning("this server has no **autoreactions**")
      
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
               number.append(discord.Embed(color=self.bot.color, title=f"auto reactions ({len(check)})", description=messages[i]))
               
               i+=1
               mes = ""
               l=0
    
      messages.append(mes)
      
      embed = discord.Embed(color=self.bot.color, title=f"auto reactions ({len(check)})", description=messages[i])
      
      number.append(embed)
      await ctx.paginator(number) 
      
  @commands.Cog.listener('on_message')
  async def auto(self, message: discord.Message):
        if message.author.bot: return
        if message.guild is None: return
        
        autoresponses = await self.bot.db.fetch("SELECT * FROM autoresponses WHERE guild_id = $1", message.guild.id)
        if autoresponses is None: return
        
        for autoresponse in autoresponses:
            if message.content.lower().startswith(autoresponse['key'].lower()) or message.content.lower() == autoresponse['key'].lower():
                
                embed = Embed.from_variable(autoresponse['response'], message.author)
                
                if embed.only_content: return await message.channel.send(embed.content)
                else: return await message.channel.send(content=embed.content, embed=embed.to_embed(), view=embed.to_view())
                
  @commands.Cog.listener('on_message')
  async def on_autoreact(self, message: discord.Message): 

          if message.author.bot: return
          if message.guild is None: return

          retry_after = self.get_ratelimit(message)
          if retry_after: return

          check = await self.bot.db.fetchrow("SELECT emojis FROM autoreact WHERE guild_id = $1 AND trigger = $2", message.guild.id, message.content)
          if check is None:
              return

          check1 = json.loads(check["emojis"])

          if check1: 
            for emoji in check1: 
              try: 
                  await message.add_reaction(emoji)
              except: 
                  continue

async def setup(bot: commands.Bot) -> None: 
    await bot.add_cog(chat(bot))