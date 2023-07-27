import discord, os, sys
from discord.ext import commands
from typing import Union

class GoodRole(commands.Converter):
  async def convert(self, ctx: commands.Context, argument): 
    try: role = await commands.RoleConverter().convert(ctx, argument)
    except commands.BadArgument: role = discord.utils.get(ctx.guild.roles, name=argument) 
    if role is None: 
      role = ctx.find_role(argument)
      if role is None: raise commands.BadArgument(f"No role called **{argument}** found") 
    if role.position >= ctx.guild.me.top_role.position: raise commands.BadArgument("this role is above my top role") 
    if ctx.author.id == ctx.guild.owner_id: return role 
    if role.position >= ctx.author.top_role.position: raise commands.BadArgument(f"this role is above your top role")
    return role

class NoStaff(commands.Converter): 
  async def convert(self, ctx: commands.Context, argument): 
    try: member = await commands.MemberConverter().convert(ctx, argument)
    except commands.BadArgument: member = discord.utils.get(ctx.guild.members, name=argument)
    if member is None: raise commands.BadArgument(f"No member called **{argument}** found")  
    if member.id == ctx.guild.me.id: raise commands.BadArgument("im invincible lol") 
    if member.top_role.position >= ctx.guild.me.top_role.position: raise commands.BadArgument(f"**{member}** is above my top role") 
    if ctx.author.id == ctx.guild.owner_id: return member
    if member.top_role.position >= ctx.author.top_role.position or member.id == ctx.guild.owner_id: raise commands.BadArgument(f"**{member}** is above your top role") 
    return member

class Whitelist: 
  async def whitelist_things(ctx: commands.Context, module: str, target: Union[discord.Member, discord.User, discord.TextChannel]): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    if check: return await ctx.send_warning( f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is **already** whitelisted for **{module}**")
    await ctx.bot.db.execute("INSERT INTO whitelist VALUES ($1,$2,$3,$4)", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    return await ctx.send_success(f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is now whitelisted for **{module}**")

  async def unwhitelist_things(ctx: commands.Context, module: str, target: Union[discord.Member, discord.TextChannel]): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    if not check: return await ctx.send_warning( f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is **not** whitelisted for **{module}**")
    await ctx.bot.db.execute("DELETE FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    return await ctx.send_success(f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} has been unwhitelisted from **{module}**")

  async def whitelisted_things(ctx: commands.Context, module: str, target: str): 
   i=0
   k=1
   l=0
   mes = ""
   number = []
   messages = []  
   results = await ctx.bot.db.fetch("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND mode = $3", ctx.guild.id, module, target)
   if len(results) == 0: return await ctx.send_warning( f"No whitelisted **{target}s** found for **{module}**")  
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
   await ctx.paginator(number)

class Invoke:
 
 async def invoke_send(ctx: commands.Context, member: Union[discord.User, discord.Member], reason: str): 
  check = await ctx.bot.db.fetchrow("SELECT embed FROM invoke WHERE guild_id = $1 AND command = $2", ctx.guild.id, ctx.command.name)
  if check: 
     code = check['embed']
     try: 
      x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, Invoke.invoke_replacement(member, code.replace("{reason}", reason))))
      await ctx.reply(content=x[0], embed=x[1], view=x[2])
     except: await ctx.reply(EmbedBuilder.embed_replacement(member, Invoke.invoke_replacement(member, code.replace("{reason}", reason)))) 
     return True 
  return False   
 
 def invoke_replacement(member: Union[discord.Member, discord.User], params: str=None):
  if params is None: return None
  if '{member}' in params: params=params.replace("{member}", str(member))
  if '{member.id}' in params: params=params.replace('{member.id}', str(member.id))
  if '{member.name}' in params: params=params.replace('{member.name}', member.name)
  if '{member.mention}' in params: params=params.replace('{member.mention}', member.mention)
  #if '{member.discriminator}' in params: params=params.replace('{member.discriminator}', member.discriminator)
  if '{member.avatar}' in params: params=params.replace('{member.avatar}', member.display_avatar.url)
  return params

 async def invoke_cmds(ctx: commands.Context, member: Union[discord.Member, discord.User], embed: str) -> discord.Message:
  check = await ctx.bot.db.fetchrow("SELECT embed FROM invoke WHERE guild_id = $1 AND command = $2", ctx.guild.id, ctx.command.name)
  if check:
   code = check['embed']    
   if embed == "none": 
    await ctx.bot.db.execute("DELETE FROM invoke WHERE guild_id = $1 AND command = $2", ctx.guild.id, ctx.command.name)
    return await ctx.send_success( f"Deleted the custom response for **{ctx.command.name}**")
   elif embed == "view": 
    em = discord.Embed(color=ctx.bot.color, title=f"invoke {ctx.command.name} message", description=f"```{code}```")
    return await ctx.reply(embed=em)
   elif embed == code: return await ctx.send_warning( f"This embed is **already** set as the {ctx.command.name} custom response")
   else:
      await ctx.bot.db.execute("UPDATE invoke SET embed = $1 WHERE guild_id = $2 AND command = $3", embed, ctx.guild.id, ctx.command.name)
      return await ctx.send_success( f"Your custom message for **{ctx.command.name}** has been updated to  {'the embed' if '--embed' in embed else ''}\n```{embed}```")
  else: 
   await ctx.bot.db.execute("INSERT INTO invoke VALUES ($1,$2,$3)", ctx.guild.id, ctx.command.name, embed)
   return await ctx.send_success( f"Your custom message for **{ctx.command.name}** has been set to {'the embed' if '--embed' in embed else ''}\n```{embed}```")

class EmbedBuilder:
 def ordinal(self, num: int) -> str:
   """Convert from number to ordinal (10 - 10th)""" 
   numb = str(num) 
   if numb.startswith("0"): numb = numb.strip('0')
   if numb in ["11", "12", "13"]: return numb + "th"
   if numb.endswith("1"): return numb + "st"
   elif numb.endswith("2"):  return numb + "nd"
   elif numb.endswith("3"): return numb + "rd"
   else: return numb + "th"    

 def get_parts(params):
    params=params.replace('{embed}', '')
    return [p[1:][:-1] for p in params.split('$v')]

 def embed_replacement(user: discord.Member, params: str=None):
    if params is None: return None
    if '{user}' in params:
        params=params.replace('{user}', str(user.name) + "#" + str(user.discriminator))
    if '{user.mention}' in params:
        params=params.replace('{user.mention}', user.mention)
    if '{user.name}' in params:
        params=params.replace('{user.name}', user.name)
    if '{user.avatar}' in params:
        params=params.replace('{user.avatar}', str(user.display_avatar.url))
    if '{user.joined_at}' in params:
        params=params.replace('{user.joined_at}', discord.utils.format_dt(user.joined_at, style='R'))
    if '{user.created_at}' in params:
        params=params.replace('{user.created_at}', discord.utils.format_dt(user.created_at, style='R'))
    #if '{user.discriminator}' in params:
        #params=params.replace('{user.discriminator}', user.discriminator)
    if '{user.id}' in params:
        params=params.replace('{user.id}', str(user.id))
    if '{guild.name}' in params:
        params=params.replace('{guild.name}', user.guild.name)
    if '{guild.count}' in params:
        params=params.replace('{guild.count}', str(user.guild.member_count))
    #if '{guild.count.format}' in params:
        #params=params.replace('{guild.count.format}', EmbedBuilder.ordinal(len(user.guild.members)))
    if '{guild.id}' in params:
        params=params.replace('{guild.id}', user.guild.id)
    if '{guild.created_at}' in params:
        params=params.replace('{guild.created_at}', discord.utils.format_dt(user.guild.created_at, style='R'))
    if '{guild.boost_count}' in params:
        params=params.replace('{guild.boost_count}', str(user.guild.premium_subscription_count))
    if '{guild.booster_count}' in params:
        params=params.replace('{guild.booster_count}', str(len(user.guild.premium_subscribers)))
    #if '{guild.boost_count.format}' in params:
        #params=params.replace('{guild.boost_count.format}', EmbedBuilder.ordinal(user.guild.premium_subscription_count))
    #if '{guild.booster_count.format}' in params:
        #params=params.replace('{guild.booster_count.format}', EmbedBuilder.ordinal(len(user.guild.premium_subscribers)))
    if '{guild.boost_tier}' in params:
        params=params.replace('{guild.boost_tier}', str(user.guild.premium_tier))
    #if '{guild.vanity}' in params: 
        #params=params.replace('{guild.vanity}', "/" + user.guild.vanity_url_code or "none")         
    if '{invisible}' in params: 
        params=params.replace('{invisible}', '2f3136') 
    if '{botcolor}' in params: 
        params=params.replace('{botcolor}', '6d827d') 
    if '{guild.icon}' in params:
      if user.guild.icon:
        params=params.replace('{guild.icon}', user.guild.icon.url)
      else: 
        params=params.replace('{guild.icon}', "https://none.none")        

    return params

 async def to_object(params):

    x={}
    fields=[]
    content=None
    view=discord.ui.View()

    for part in EmbedBuilder.get_parts(params):
        
        if part.startswith('content:'):
            content=part[len('content:'):]

        if part.startswith('title:'):
            x['title']=part[len('title:'):]
        
        if part.startswith('description:'):
            x['description']=part[len('description:'):]

        if part.startswith('color:'):
            try:
                x['color']=int(part[len('color:'):].replace("#", ""), 16)
            except:
                x['color']=0x2f3136

        if part.startswith('image:'):
            x['image']={'url': part[len('image:'):]}

        if part.startswith('thumbnail:'):
            x['thumbnail']={'url': part[len('thumbnail:'):]}
        
        if part.startswith('author:'):
            z=part[len('author:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            try:
                url=z[2] if z[2] else None
            except:
                url=None

            x['author']={'name': name}
            if icon_url:
                x['author']['icon_url']=icon_url
            if url:
                x['author']['url']=url

        #if part.startswith('field:'):
            #z=part[len('field:'):].split(' && ')
           # try:
           #     name=z[0] if z[0] else None
           # except:
             #   name=None
            #try:
            #    value=z[1] if z[1] else None
            #except:
                #value=None
            #try:
                #inline=z[2] if z[2] else True
            #except:
                #inline=True

            #if isinstance(inline, str):
                #if inline == 'true':
                    #inline=True

                #elif inline == 'false':
                    #inline=False

            #fields.append({'name': name, 'value': value, 'inline': inline})

        if part.startswith('footer:'):
            z=part[len('footer:'):].split(' && ')
            try:
                text=z[0] if z[0] else None
            except:
                text=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            x['footer']={'text': text}
            if icon_url:
                x['footer']['icon_url']=icon_url
                
        if part.startswith('button:'):
            z=part[len('button:'):].split(' && ')
            disabled=True
            style=discord.ButtonStyle.gray
            emoji=None 
            label=None 
            url=None
            for m in z:
             if "label:" in m: label=m.replace("label:", "")
             if "url:" in m: 
                url=m.replace("url:", "").strip()
                disabled=False
             if "emoji:" in m: emoji=m.replace("emoji:", "").strip()
             if "disabled" in m: disabled=True     
             if "style:" in m: 
               if m.replace("style:", "").strip() == "red": style=discord.ButtonStyle.red 
               elif m.replace("style:", "").strip() == "green": style=discord.ButtonStyle.green 
               elif m.replace("style:", "").strip() == "gray": style=discord.ButtonStyle.gray 
               elif m.replace("style:", "").strip() == "blue": style=discord.ButtonStyle.blurple   

            view.add_item(discord.ui.Button(style=style, label=label, emoji=emoji, url=url, disabled=disabled))
            
    if not x: embed=None
    else:
        #x['fields']=fields
        embed=discord.Embed.from_dict(x)
    return content, embed, view 

class EmbedScript(commands.Converter): 
  async def convert(self, ctx: commands.Context, argument: str):
   x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, argument))
   if x[0] or x[1]: return {"content": x[0], "embed": x[1], "view": x[2]} 
   return {"content": EmbedBuilder.embed_replacement(ctx.author, argument)}

class Paginator(discord.ui.View):
    def __init__(self, ctx: commands.Context, embeds: list):
      super().__init__()
      self.embeds = embeds
      self.ctx = ctx
      self.p = 0
    
    @discord.ui.button(emoji="<:left:1115966984165797969>", style=discord.ButtonStyle.gray)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")
      if self.p == 0:
        await interaction.response.edit_message(embed=self.embeds[-1])
        self.p = len(self.embeds)-1
        return
      self.p = self.p-1
      await interaction.response.edit_message(embed=self.embeds[self.p])
    
    @discord.ui.button(emoji="<:stop2:1115969501138260069>", style=discord.ButtonStyle.gray)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")
      return await interaction.message.delete()
    
    @discord.ui.button(emoji="<:right:1115967005481250828>", style=discord.ButtonStyle.gray)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")
      if self.p == len(self.embeds)-1:
        await interaction.response.edit_message(embed=self.embeds[0])
        self.p = 0
        return
      self.p = self.p + 1
      await interaction.response.edit_message(embed=self.embeds[self.p])
    
    async def on_timeout(self) -> None: 
        mes = await self.message.channel.fetch_message(self.message.id)
        if mes is None: return
        if len(mes.components) == 0: return
        for item in self.children:
            item.disabled = True

        try: await self.message.edit(view=self)   
        except: pass

class StartUp:
 async def startup(bot):
    await bot.wait_until_ready()
    await bot.tree.sync()
    print('Synced applications commands')
    
 async def loadcogs(self):
  for file in os.listdir("./events"):
   if file.endswith(".py"):
    try:
      await self.load_extension(f"events.{file[:-3]}")
      print(f"Loaded event {file[:-3]}")
    except Exception as e: print("Unable to load event {} - {}".format(file[:-3], e))
  for fil in os.listdir("./cogs"):
   if fil.endswith(".py"):
    try:
      await self.load_extension(f"cogs.{fil[:-3]}")
      print(f"Loaded module {fil[:-3]}")
    except Exception as e: print("Unable to load {} - {}".format(fil[:-3], e))
 
 async def identify(self):
    payload = {
        'op': self.IDENTIFY,
        'd': {
            'token': self.token,
            'properties': {
                '$os': sys.platform,
                '$browser': 'Discord iOS',
                '$device': 'Discord iOS',
                '$referrer': '',
                '$referring_domain': ''
            },
            'compress': True,
            'large_threshold': 250,
            'v': 3
        }
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload['d']['presence'] = {
            'status': state._status,
            'game': state._activity,
            'since': 0,
            'afk': False
        }

    if state._intents is not None:
        payload['d']['intents'] = state._intents.value

    await self.call_hooks('before_identify', self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)

async def create_db(self):
  await self.db.execute("CREATE TABLE IF NOT EXISTS cmderror (code TEXT, error TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS fake_permissions (guild_id BIGINT, role_id BIGINT, permissions TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS autoresponder (guild_id BIGINT, trigger TEXT, response TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS autorole (role_id BIGINT, guild_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS oldusernames (username TEXT, time INTEGER, user_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS nodata (user_id BIGINT, state TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS donor (user_id BIGINT, time BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS snipe (guild_id BIGINT, channel_id BIGINT, author TEXT, content TEXT, attachment TEXT, avatar TEXT, time TIMESTAMPTZ)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS afk (guild_id BIGINT, user_id BIGINT, reason TEXT, time INTEGER);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id BIGINT, prefix TEXT)")  
  await self.db.execute("CREATE TABLE IF NOT EXISTS selfprefix (user_id BIGINT, prefix TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS hardban (guild_id BIGINT, banned BIGINT, author BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS seen (guild_id BIGINT, user_id BIGINT, time INTEGER);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS joindm (guild_id BIGINT, message TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS starboardmes (guild_id BIGINT, channel_starboard_id BIGINT, channel_message_id BIGINT, message_starboard_id BIGINT, message_id BIGINT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS starboard (guild_id BIGINT, channel_id BIGINT, count INTEGER, emoji_id BIGINT, emoji_text TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS autoreact (guild_id BIGINT, trigger TEXT, emojis TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS welcome (guild_id BIGINT, channel_id BIGINT, message TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS leave (guild_id BIGINT, channel_id BIGINT, message TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS voicemaster (guild_id BIGINT, channel_id BIGINT, interface BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS vcs (user_id BIGINT, voice BIGINT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS tickets (guild_id BIGINT, message TEXT, channel_id BIGINT, category BIGINT, logs BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS opened_tickets (guild_id BIGINT, channel_id BIGINT, user_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS confess (guild_id BIGINT, channel_id BIGINT, confession INTEGER);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS confess_members (guild_id BIGINT, user_id BIGINT, confession INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS autopfp (guild_id BIGINT, channel_id BIGINT, genre TEXT, type TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS lastfm (user_id BIGINT, username TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS lastfmcc (user_id BIGINT, command TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS lfmode (user_id BIGINT, mode TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS booster_roles (guild_id BIGINT, user_id BIGINT, role_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS booster_module (guild_id BIGINT, base BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS birthday (user_id BIGINT, bday TIMESTAMPTZ, state TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS invoke (guild_id BIGINT, command TEXT, embed TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS antinuke_toggle (guild_id BIGINT, logs BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS antinuke (guild_id BIGINT, module TEXT, punishment TEXT, threshold INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS pingonjoin (channel_id BIGINT, guild_id BIGINT);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS whitelist (guild_id BIGINT, module TEXT, object_id BIGINT, mode TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS mod (guild_id BIGINT, channel_id BIGINT, jail_id BIGINT, role_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS cases (guild_id BIGINT, count INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS jail (guild_id BIGINT, user_id BIGINT, roles TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS antiraid (guild_id BIGINT, command TEXT, punishment TEXT, seconds INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS lfreactions (user_id BIGINT, reactions TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS reactionrole (guild_id BIGINT, message_id BIGINT, channel_id BIGINT, role_id BIGINT, emoji_id BIGINT, emoji_text TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS giveaway (guild_id BIGINT, channel_id BIGINT, message_id BIGINT, winners INTEGER, members TEXT, finish TIMESTAMPTZ, host BIGINT, title TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS gw_ended (channel_id BIGINT, message_id BIGINT, members TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS pot (guild_id BIGINT, hits INTEGER, holder BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS avh (user_id BIGINT, count INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS counters (guild_id BIGINT, channel_type TEXT, channel_id BIGINT, channel_name TEXT, module TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS antiinvite (guild_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS economy (user_id BIGINT, cash INTEGER, bank INTEGER, dice INTEGER, daily INTEGER, rob INTEGER)")