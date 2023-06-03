import discord, datetime
from discord.ext import commands, tasks 
from typing import Union

owners = [1107903478451408936]

def is_owner(): 
 async def predicate(ctx: commands.Context): 
    return ctx.author.id in owners 
 return commands.check(predicate)     

@tasks.loop(minutes=10)
async def servers_check(bot: commands.AutoShardedBot): 
  results = await bot.db.fetch("SELECT * FROM authorize WHERE billing IS NOT NULL")
  for result in results: 
   if result['billing'].timestamp() < datetime.datetime.now().timestamp(): 
    guild = bot.get_guild(result['guild_id'])
    if guild: await guild.leave()  
    await bot.get_channel(1110897152135274538).send(f"Leaving **{result['guild_id']}** since no one paid the monthly bill")
    await bot.db.execute("DELETE FROM authorize WHERE guild_id = $1", result['guild_id']) 

class Auth(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
        self.bot = bot 
    
    @commands.Cog.listener()
    async def on_ready(self): 
      servers_check.start(self.bot)

    @commands.Cog.listener()
    async def subscriber_join(self, member: discord.Member): 
      if member.guild.id == 1110287100814827542:
       check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE buyer = $1", member.id)
       if check: await member.add_roles(member.guild.get_role(1110897351222108221))

    @commands.command()
    @is_owner()
    async def authorize(self, ctx: commands.Context, guildid: int=None, buyer: Union[discord.Member, discord.User]=None, offer: str=None): 
     if guildid is None or buyer is None: return await ctx.reply("command usage: {}authorize [server id] [buyer mention] [monthly/onetime]".format(ctx.clean_prefix)) 
     check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1", guildid)
     if check is not None: return await ctx.reply(f"this server is already authorized. please use `{ctx.clean_prefix}transfer` to transfer a server authorization")
     
     if not offer.lower() in ["monthly", "onetime"]: return await ctx.reply("command usage: {}authorize [server id] [buyer mention] [monthly/onetime]".format(ctx.clean_prefix)) 
     await self.bot.db.execute("INSERT INTO authorize VALUES ($1,$2,$3,$4,$5)", guildid, buyer.id, str(bool(offer == "monthly")).lower(), 2, (datetime.datetime.now() + datetime.timedelta(weeks=4)) if offer == "monthly" else None)
     await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"Added **{guildid}** as an authorized server"))
     member = self.bot.get_guild(1110287100814827542).get_member(buyer.id)
     if member: await member.add_roles(self.bot.get_guild(1110287100814827542).get_role(1110897351222108221), reason="member became a subscriber")
     view = discord.ui.View()
     view.add_item(discord.ui.Button(label="invite", url=discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions.all())))
     try: await buyer.send(f"Congratulations! You **{offer}** subscription for **{guildid}** has been activated!\n{f'Billing date: '+ discord.utils.format_dt((datetime.datetime.now() + datetime.timedelta(weeks=4)), style='R') if offer == 'monthly' else ''}", view=view)
     except: pass
    
    @commands.command()
    @is_owner()
    async def updatebill(self, ctx: commands.Context, id: int): 
     check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1 AND billing IS NOT NULL", id)
     if not check: return await ctx.send_warning("This server is not included in a monthly subscription")
     await self.bot.db.execute("UPDATE authorize SET billing = $1 WHERE guild_id = $2", (datetime.datetime.now() + datetime.timedelta(weeks=4)), id) 
     await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"Updated monthly subscription for **{id}**"))
     
    @commands.command()
    @is_owner()
    async def getauth(self, ctx: commands.Context, *, member: discord.User): 
     results = await self.bot.db.fetch("SELECT * FROM authorize WHERE buyer = $1", member.id)
     if len(results) == 0: return await ctx.reply("no server authorized for **{}**".format(member))
     i=0
     k=1
     l=0
     mes = ""
     number = []
     messages = []          
     for result in results:
       
      mes = f"{mes}`{k}` `{result['guild_id']}` - {'monthly | ' + discord.utils.format_dt(result['billing'], style='R') if result['monthly'] == 'true' else 'onetime'}\n"
      k+=1
      l+=1
      if l == 10:
       messages.append(mes)
       number.append(discord.Embed(color=self.bot.color, title=f"purchased servers ({len(results)})", description=messages[i]))
       i+=1
       mes = ""
       l=0
    
     messages.append(mes)
     number.append(discord.Embed(color=self.bot.color, title=f"purchased servers ({len(results)})", description=messages[i]))
     await ctx.paginator(number) 

    @commands.command()
    @commands.is_owner()
    async def unauthorize(self, ctx: commands.Context, id:int=None): 
        if id is None: return await ctx.reply("commands usage: {}unauthorize [guild id]".format(ctx.clean_prefix))
        check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1", id)
        if check is None: return await ctx.reply(f"unable to find this server")
        await self.bot.db.execute("DELETE FROM authorize WHERE guild_id = $1", id)
        await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"Unauthorized **{id}**"))

    @commands.command()
    @is_owner()
    async def transfer(self, ctx: commands.Context, oldserver: int=None, newserver: int=None):  
        if oldserver is None or newserver is None: return await ctx.reply("command usage: {}transfer [old server id] [new server id]".format(ctx.clean_prefix))
        check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1", oldserver)
        if check is None: return await ctx.reply(f"unable to find this server")
        buyer = check["buyer"]
        mode = check['monthly']
        transfers = int(check["transfers"])
        if transfers == 0: return await ctx.send_error(f"**{await self.bot.fetch_user(buyer)}** ran out of transfers. Let a developer deal with this situation")
        await self.bot.db.execute("DELETE FROM authorize WHERE guild_id = $1", oldserver)
        if mode == "false": await self.bot.db.execute("INSERT INTO authorize VALUES ($1,$2,$3,$4,$5)", newserver, buyer, mode, transfers-1, None)
        else: await self.bot.db.execute("UPDATE authorize SET guild_id = $1 WHERE buyer = $2 AND guild_id = $3", newserver, buyer, oldserver)
        await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"Transfered **{oldserver}** to **{newserver}**\n{f'**{await self.bot.fetch_user(buyer)}** does not have any transfer remaining for this server' if transfers-1 == 0 else ''}"))
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="invite", url=discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions.all())))
        try: await (await self.bot.fetch_user(buyer)).send(f"**abort** premium subscription has been transfered from **{oldserver}** to {newserver} **successfully**\n{f'Now you do not have any available transfers for **{newserver}**' if transfers-1 == 0 else ''}", view=view)
        except: pass

async def setup(bot): 
    await bot.add_cog(Auth(bot))    