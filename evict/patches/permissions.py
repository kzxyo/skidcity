from discord.ext import commands
from typing import Union 
import discord, json

OWNERS = [214753146512080907, 598125772754124823]
AUTHORIZATION = [598125772754124823, 547882311983824907, 831953870133133332, 900446386833727489, 595239050273619969, 987183275560820806]
  
class Permissions:
    
    def has_permission(**perms: bool) -> commands.check:
        
        invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
        if invalid:
            raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

        def predicate(ctx: commands.Context) -> bool:
            
            permissions = ctx.permissions
            
            if discord.Permissions.administrator in permissions: return True
            
            missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

            if ctx.author.id in ctx.bot.owner_ids or not missing: return True

            raise commands.MissingPermissions(missing)

        return commands.check(predicate)
        
    def check_hierarchy(bot: commands.Bot, author: discord.Member, target: discord.Member):
        if target.id in OWNERS: raise commands.CommandInvokeError("You cannot perform this action on a bot owner.")
        if target.id == author.id: raise commands.CommandInvokeError("You cannot perform this action on yourself.")
        if target.id in bot.owner_ids: raise commands.CommandInvokeError("You cannot perform this action on a bot owner.")
        if author.id == author.guild.owner.id: return True
        if author.id in bot.owner_ids: return True
        if target.id == author.guild.owner.id: raise commands.CommandInvokeError("You cannot perform this action on the server owner.")
        if target.top_role >= author.top_role: raise commands.CommandInvokeError("You cannot perform this action on a higher role than you.")
        return True
    
    def server_owner():
     
     async def server_owner(ctx: commands.Context):
            if ctx.author.id == ctx.guild.owner_id: return True
            if ctx.author.id in OWNERS: return True
            else: raise commands.CommandInvokeError("You need to be the server owner to run this command.")
     
     return commands.check(server_owner)
    
    def authorize():
     
     async def authorize(ctx: commands.Context):
            if ctx.author.id in AUTHORIZATION: return True
            else: raise commands.CommandInvokeError("You **need** to have authorization permissions to authorize servers.")
     
     return commands.check(authorize)
        
    def booster():
     
     async def booster(ctx: commands.Context):
            
            che = await ctx.bot.db.fetchrow("SELECT * FROM booster_module WHERE guild_id = {}".format(ctx.guild.id))
            if che is None: raise commands.CommandInvokeError("the booster role module is **not** configured.")
            
            check = await ctx.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
            if check is None: raise commands.CommandInvokeError("You don't have a booster role.")
     
     return commands.check(booster)
    
    def donor():
     
     async def donor(ctx: commands.Context):
            if ctx.command.name in ["hardban", "uwulock", "unhardban"]: 
                if ctx.author.id == ctx.guild.owner_id: return True
                if ctx.author.id in OWNERS: return True
            check = await ctx.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(ctx.author.id))              
            if check is None: raise commands.CommandInvokeError("You need to be a donor to run this command.")
     
     return commands.check(donor)
 
class Boosters:
    
    async def booster(ctx: commands.Context):
            
            che = await ctx.bot.db.fetchrow("SELECT * FROM booster_module WHERE guild_id = {}".format(ctx.guild.id))
            if che is None: raise commands.CommandInvokeError("the booster role module is **not** configured.")
            
            check = await ctx.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
            if check is None: raise commands.CommandInvokeError("You don't have a booster role.")
     
            return commands.check(Boosters)
 
class GoodRole(commands.Converter):
  async def convert(self, ctx: commands.Context, argument):
    try: role = await commands.RoleConverter().convert(ctx, argument)
    except commands.BadArgument: role = discord.utils.get(ctx.guild.roles, name=argument) 
    if role is None: role = ctx.find_role(argument)
    if role is None: raise commands.BadArgument(f"No role called **{argument}** found") 
    if role.position >= ctx.guild.me.top_role.position: raise commands.BadArgument("This role cannot be managed by the bot") 
    if ctx.author.id == ctx.guild.owner_id: return role
    if ctx.author.id in OWNERS: return role
    if role.position >= ctx.author.top_role.position: raise commands.BadArgument(f"You cannot manage this role")
    return role

class PositionConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> int:
        try:
            position = int(argument)
        except ValueError:
            raise commands.BadArgument("The position must be an integer.")
        max_guild_text_channels_position = len(
            [c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)]
        )
        if position <= 0 or position >= max_guild_text_channels_position + 1:
            raise commands.BadArgument(
                f"The indicated position must be between 1 and {max_guild_text_channels_position}."
            )
        position -= 1
        return position
    
class Whitelist: 
  
  async def whitelist_things(ctx: commands.Context, module: str, target: Union[discord.Member, discord.User, discord.TextChannel]): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    if check: return await ctx.warning( f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is **already** whitelisted for **{module}**")
    await ctx.bot.db.execute("INSERT INTO whitelist VALUES ($1,$2,$3,$4)", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    return await ctx.success(f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is now whitelisted for **{module}**")

  async def unwhitelist_things(ctx: commands.Context, module: str, target: Union[discord.Member, discord.TextChannel]): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    if not check: return await ctx.warning( f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is **not** whitelisted from **{module}**")
    await ctx.bot.db.execute("DELETE FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    return await ctx.success(f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is now unwhitelisted from **{module}**")

  async def whitelisted_things(ctx: commands.Context, module: str, target: str): 
   i=0
   k=1
   l=0
   mes = ""
   number = []
   messages = []  
   results = await ctx.bot.db.fetch("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND mode = $3", ctx.guild.id, module, target)
   if len(results) == 0: return await ctx.warning( f"No whitelisted **{target}s** found for **{module}**")  
   for result in results:
    id = result['object_id'] 
    if target == "channel": mes = f"{mes}`{k}` {f'{ctx.guild.get_channel(id).mention} ({id})' if ctx.guild.get_channel(result['object_id']) is not None else result['object_id']}\n"
    else: mes = f"{mes} `{k}` {await ctx.bot.fetch_user(id)} ({id})\n"
    k+=1
    l+=1
    if l == 10:
     messages.append(mes)
     number.append(discord.Embed(color=ctx.bot.color, title=f"whitelisted {target}s ({len(results)})", description=messages[i]))
     i+=1
     mes = ""
     l=0
    
   messages.append(mes)  
   number.append(discord.Embed(color=ctx.bot.color, title=f"whitelisted {target}s ({len(results)})", description=messages[i]))
   await ctx.paginate(number)
   
class Perms: 

  def server_owner(): 
   async def predicate(ctx: commands.Context): 
    if ctx.author.id != ctx.guild.owner_id: 
      await ctx.send_warning( f"This command can be used only by **{ctx.guild.owner}**") 
      return False 
    return True   
   return commands.check(predicate)   
  
  def check_whitelist(module: str):
   async def predicate(ctx: commands.Context):
    if ctx.guild is None: return False 
    if ctx.author.id == ctx.guild.owner.id: return True
    check = await ctx.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND object_id = $2 AND mode = $3 AND module = $4", ctx.guild.id, ctx.author.id, "user", module)   
    if check is None: 
     await ctx.send_warning( f"You are not **whitelisted** for **{module}**") 
     return False      
    return True
   return commands.check(predicate) 

  def get_perms(perm: str=None):
   async def predicate(ctx: commands.Context):  
    if perm is None: return True 
    if ctx.guild.owner == ctx.author: return True
    if ctx.author.guild_permissions.administrator: return True
    for r in ctx.author.roles:
     if perm in [str(p[0]) for p in r.permissions if p[1] is True]: return True 
     check = await ctx.bot.db.fetchrow("SELECT permissions FROM fake_permissions WHERE role_id = $1 and guild_id = $2", r.id, r.guild.id)
     if check is None: continue 
     permissions = json.loads(check[0])
     if perm in permissions or "administrator" in permissions: return True
    raise commands.MissingPermissions([perm])
   return commands.check(predicate)  

  async def has_perms(ctx: commands.Context, perm: str=None): 
    if perm is None: return True 
    if ctx.guild.owner == ctx.author: return True
    if ctx.author.guild_permissions.administrator: return True
    for r in ctx.author.roles:
     if perm in [str(p[0]) for p in r.permissions if p[1] is True]: return True 
     check = await ctx.bot.db.fetchrow("SELECT permissions FROM fake_permissions WHERE role_id = $1 and guild_id = $2", r.id, r.guild.id)
     if check is None: continue 
     permissions = json.loads(check[0])
     if perm in permissions or "administrator" in permissions: return True
    return False  