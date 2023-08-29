import discord, datetime, random, string, asyncio
from discord.ext import commands
from tools.checks import Owners
from cogs.auth import owners

class owner(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
       self.bot = bot           

   @commands.Cog.listener("on_command_error")
   async def rl_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            rl = round(error.retry_after, 2)
            if error.retry_after > 60:
                await asyncio.sleep(error.retry_after)
            else:
                await asyncio.sleep(error.retry_after / 2)
            #self.log.warning(f"{ctx.author.name} ({ctx.author.id}) cause a rate limit on command {ctx.command.name} on guild with id {ctx.guild.id}")
            await ctx.reinvoke()
            
    
  # @commands.Cog.listener()
  # async def on_command(self, ctx):
     #  if ctx.guild is None:  # Skip commandsin DMs
        #   return
        
        # Replace CHANNEL_ID with the actual ID of your logging channel
      # logging_channel = self.bot.get_channel(1136729223776710757)
        
    #   if logging_channel:
        #   user = ctx.author
         #  command = ctx.command
          # guild_id = ctx.guild.id
           #await logging_channel.send(f"{user.display_name} used command '{command.name}' in {ctx.channel.mention} on {guild_id} server")
   
   @commands.command(description="verifu")
   async def badactivity(self, ctx):
    if ctx.author == ctx.guild.owner:
        bad_words = ["test", "verify"]  # Add the list of bad words you want to check for
        members = ctx.guild.members
        banned_members = []

        for member in members:
            if member.activity and member.activity.type == discord.ActivityType.custom and any(word in member.activity.state.lower() for word in bad_words):
                await member.ban(reason="Bad word in status activity")
                banned_members.append(member)

        if banned_members:
            embed = discord.Embed(
                title="Members Banned",
                description="The following members were banned due to having bad words in their status activity:",
                color=discord.Color.red()
            )
            for member in banned_members:
                embed.add_field(name=member.display_name, value=member.mention, inline=False)

            await ctx.send(embed=embed)
    
   @commands.group(invoke_without_command=True)
   @Owners.check_owners()
   async def donor(self, ctx: commands.Context):
    await ctx.create_pages()

   @donor.command()
   @Owners.check_owners()
   async def add(self, ctx: commands.Context, *, member: discord.User): 
       result = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(member.id))
       if result is not None: return await ctx.reply(f"{member} is already a donor")
       ts = int(datetime.datetime.now().timestamp()) 
       await self.bot.db.execute("INSERT INTO donor VALUES ($1,$2)", member.id, ts)
       return await ctx.send_success(f"{member.mention} is now a donor")

   @donor.command()
   @Owners.check_owners()
   async def remove(self, ctx: commands.Context, *, member: discord.User):    
       result = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(member.id)) 
       if result is None: return await ctx.reply(f"{member} isn't a donor")
       await self.bot.db.execute("DELETE FROM donor WHERE user_id = {}".format(member.id))
       return await ctx.send_success(f"{member.mention} is not a donor anymore")
       
   @commands.command()
   async def close(self, ctx: commands.Context): 
    if ctx.guild.id == 952161067033849919: 
     role = ctx.guild.get_role(986886094371053600)
     if role.position <= ctx.author.top_role.position:  
      if isinstance(ctx.channel, discord.Thread): 
        await ctx.message.add_reaction("<:catthumbsup:974982144021626890>")
        await ctx.channel.edit(locked=True, archived=True)

   @commands.command(aliases=["guilds"])
   @Owners.check_owners()
   async def servers(self, ctx: commands.Context): 
            def key(s): 
              return s.member_count 
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            lis = [g for g in self.bot.guilds]
            lis.sort(reverse=True, key=key)
            for guild in lis:
              mes = f"{mes}`{k}` {guild.name} ({guild.id}) - ({guild.member_count}) - {guild.owner}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=self.bot.color, title=f"guilds ({len(self.bot.guilds)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            number.append(discord.Embed(color=self.bot.color, title=f"guilds ({len(self.bot.guilds)})", description=messages[i]))
            await ctx.paginator(number)  

   @commands.command()
   @Owners.check_owners()
   async def portal(self, ctx, id: int):
      await ctx.message.delete()      
      guild = self.bot.get_guild(id)
      for c in guild.text_channels:
        if c.permissions_for(guild.me).create_instant_invite: 
            invite = await c.create_invite()
            await ctx.author.send(f"{guild.name} invite link - {invite}")
            break 
        
   @commands.command()
   @Owners.check_owners()
   async def unblacklist(self, ctx, *, member: discord.User): 
      check = await self.bot.db.fetchrow("SELECT * FROM nodata WHERE user_id = $1", member.id) 
      if check is None: return await ctx.send_warning(f"{member.mention} is not blacklisted")
      await self.bot.db.execute("DELETE FROM nodata WHERE user_id = {}".format(member.id))
      await ctx.send_success(f'{member.mention} can use the bot')
   
   @commands.command()
   @commands.is_owner()
   async def delerrors(self, ctx: commands.Context): 
     await self.bot.db.execute("DELETE FROM cmderror")
     await ctx.reply("deleted all errors")

   @commands.command(aliases=['trace'])
   @Owners.check_owners()
   async def geterror(self, ctx: commands.Context, key: str): 
    check = await self.bot.db.fetchrow("SELECT * FROM cmderror WHERE code = $1", key)
    if not check: return await ctx.send_error(f"No error associated with the key `{key}`")  
    embed = discord.Embed(color=self.bot.color, title=f"error {key}", description=f"```{check['error']}```")
    await ctx.reply(embed=embed) 

   @commands.command()
   @commands.is_owner()
   async def getkey(self, ctx: commands.Context): 
    def generate_key(length):
       return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    await ctx.send(generate_key(36))    
 
   @commands.command()
   @Owners.check_owners()
   async def blacklist(self, ctx: commands.Context, *, member: discord.User): 
      if member.id in owners: return await ctx.reply("Do not blacklist a bot owner, retard")
      check = await self.bot.db.fetchrow("SELECT * FROM nodata WHERE user_id = $1 AND state = $2", member.id, "false") 
      if check is not None: return await ctx.send_warning(f"{member.mention} is already blacklisted")
      await self.bot.db.execute("DELETE FROM nodata WHERE user_id = {}".format(member.id))
      await self.bot.db.execute("INSERT INTO nodata VALUES ($1,$2)", member.id, "false")
      await ctx.send_success(f"{member.mention} can no longer use the bot")

async def setup(bot) -> None:
    await bot.add_cog(owner(bot))      