import os, time, discord, asyncpg, aiohttp, random, string, asyncio, datetime
from discord.ext import commands
from discord.gateway import DiscordWebSocket
from cogs.voicemaster import vmbuttons
from cogs.ticket import CreateTicket, DeleteTicket
from tools.utils import StartUp, create_db
from tools.ext import Client, HTTP
from humanfriendly import format_timespan
from rivalapi import RivalAPI
from cogs.giveaway import GiveawayView
from typing import List 
from tools.utils import PaginatorView
from io import BytesIO 
import typing
import dotenv
dotenv.load_dotenv(verbose=True)
token=os.environ['token']
temp="http://14a4a94eff770:c3ac0449fd@104.234.255.18:12323"
#temp=""
def generate_key():
  return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

async def checkthekey(key: str):
  check = await bot.db.fetchrow("SELECT * FROM cmderror WHERE code = $1", key)
  if check: 
    newkey = await generate_key(key)
    return await checkthekey(newkey)
  return key  

DiscordWebSocket.identify = StartUp.identify
    
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

async def botrun():
  await bot.start(lol, reconnect=True)

async def getprefix(bot, message):
       if not message.guild: return ";"
       check = await bot.db.fetchrow("SELECT * FROM selfprefix WHERE user_id = $1", message.author.id) 
       if check: selfprefix = check["prefix"]
       res = await bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", message.guild.id) 
       if res: guildprefix = res["prefix"]
       else: guildprefix = ";"    
       if not check and res: selfprefix = res["prefix"]
       elif not check and not res: selfprefix = ";"
       return guildprefix, selfprefix 

intents=discord.Intents.all()
intents.presences = False

class NeoContext(commands.Context): 
 def __init__(self, **kwargs): 
  super().__init__(**kwargs) 

 def find_role(self, name: str): 
   for role in self.guild.roles:
    if role.name == "@everyone": continue  
    if name.lower() in role.name.lower(): return role 
   return None 
 
 async def send_success(self, message: str) -> discord.Message:  
  return await self.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {self.author.mention}: {message}") )
 
 async def send_error(self, message: str) -> discord.Message: 
  return await self.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.no} {self.author.mention}: {message}") ) 
 
 async def send_warning(self, message: str) -> discord.Message: 
  return await self.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {self.author.mention}: {message}") )
 
 async def paginator(self, embeds: List[discord.Embed]):
  if len(embeds) == 1: return await self.send(embed=embeds[0]) 
  view = PaginatorView(self, embeds)
  view.message = await self.reply(embed=embeds[0], view=view) 
 
 async def cmdhelp(self): 
    command = self.command
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    if command.cog_name == "owner": return
    embed = discord.Embed(color=bot.color, title=commandname, description=command.description)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
    embed.add_field(name="category", value=command.help)
    embed.add_field(name="aliases", value=', '.join(map(str, command.aliases)) or "none")
    embed.add_field(name="permissions", value=command.brief or "any")
    embed.add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False)
    await self.reply(embed=embed)

 async def create_pages(self): 
  embeds = []
  i=0
  for command in self.command.commands: 
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    i+=1 
    embeds.append(discord.Embed(color=bot.color, title=f"{commandname}", description=command.description).set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url).add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False).set_footer(text=f"aliases: {', '.join(a for a in command.aliases) if len(command.aliases) > 0 else 'none'} ・ {i}/{len(self.command.commands)}"))
     
  return await self.paginator(embeds)  

class HelpCommand(commands.HelpCommand):
  def __init__(self, **kwargs):
   self.categories = {
      "home": "return to the main page", 
      "info": "view information about the bot", 
      "moderation": "keep your server safe", 
      "antiraid": "protect your server against raids",
      "automod": "doing the mod's job",
      "antinuke": "protect your server againt unfaithful admins",
      "emoji": "manage the emojis in your server",
      "utility": "most commands are here...",
      "config": "configure your server",
      "lastfm": "lastfm integration with the bot",
      "fun": "commands to use when you are bored",
      "roleplay": "this is self explanatory",
      "donor": "only rich people use these"
      } 
   super().__init__(**kwargs)
  
  async def send_bot_help(self, mapping):
    embed = discord.Embed(color=self.context.bot.color, title="Help menu") 
    embed.add_field(name="help", value="Please use the **dropdown** menu below to view all the bot's commands", inline=False) 
    embed.add_field(name="contact", value="If you need support you can contact us in the [**support server**](https://discord.gg/pretend)", inline=False)
    embed.set_author(name=self.context.author.name, icon_url=self.context.author.display_avatar.url)
    embed.set_footer(text=f"command count: {len(set(bot.walk_commands()))}")
    options = []
    for c in self.categories: options.append(discord.SelectOption(label=c, description=self.categories.get(c)))
    select = discord.ui.Select(options=options, placeholder="Select a category")

    async def select_callback(interaction: discord.Interaction): 
     if interaction.user.id != self.context.author.id: return await self.context.bot.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True)
     if select.values[0] == "home": return await interaction.response.edit_message(embed=embed)
     com = []
     for c in [cm for cm in set(bot.walk_commands()) if cm.help == select.values[0]]:
      if c.parent: 
        if str(c.parent) in com: continue 
        com.append(str(c.parent))
      else: com.append(c.name)  
     e = discord.Embed(color=bot.color, title=f"{select.values[0]} commands", description=f"```{', '.join(com)}```").set_author(name=self.context.author.name, icon_url=self.context.author.display_avatar.url)  
     return await interaction.response.edit_message(embed=e)
    select.callback = select_callback

    view = discord.ui.View(timeout=None)
    view.add_item(select) 
    return await self.context.reply(embed=embed, view=view)
  
  async def send_command_help(self, command: commands.Command): 
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    if command.cog_name == "owner": return
    embed = discord.Embed(color=bot.color, title=commandname, description=command.description)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
    embed.add_field(name="category", value=command.help)
    embed.add_field(name="aliases", value=', '.join(map(str, command.aliases)) or "none")
    embed.add_field(name="permissions", value=command.brief or "any")
    embed.add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False)
    channel = self.get_destination()
    await channel.send(embed=embed)

  async def send_group_help(self, group: commands.Group): 
   ctx = self.context
   embeds = []
   i=0
   for command in group.commands: 
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    i+=1 
    embeds.append(discord.Embed(color=bot.color, title=f"{commandname}", description=command.description).set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url).add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False).set_footer(text=f"aliases: {', '.join(a for a in command.aliases) if len(command.aliases) > 0 else 'none'} ・ {i}/{len(group.commands)}"))
     
   return await ctx.paginator(embeds) 

class CommandClient(commands.AutoShardedBot):
    def __init__(self):
        super().__init__( shard_count=3,
            command_prefix=getprefix, 
            proxy=temp, allowed_mentions=discord.AllowedMentions(roles=False, 
            everyone=False, users=True, replied_user=False), intents=intents, 
            help_command=HelpCommand(), strip_after_prefix=True, 
            activity=discord.Activity(name="pretend.space", 
            type=discord.ActivityType.competing), 
            owner_ids=[371224177186963460, 859646668672598017, 461914901624127489, 352190010998390796]
        )
        self.uptime = time.time()
        self.persistent_views_added = False
        self.rival_api = {"api-key": "0a1400e6-c091-42fb-a8ed-61e658223170"}
        self.pretend_api = {'Authorization': 'EIg6hHY4qTeM6Dmfn7fUCYvEFGgUZqn9A75P'}
        self.cogs_loaded=False
        self.google_api = "AIzaSyDPrFJ8oxPP5YWM82vqCaLq8F6ZdlSGsBo" 
        self.color = 0x6d827d
        self.yes = "<:check:1083455835189022791>"
        self.no = "<:stop:1083455877450834041>"
        self.warning = "<:warning:1083455925798580246>"
        self.left = "<:left:1018156480991612999>"
        self.right = "<:right:1018156484170883154>"
        self.goto = "<:filter:1039235211789078628>"
        self.proxy_url = "http://dtgrlmjf-rotate:p0bl5bes07qp@p.webshare.io:80"
        self.m_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.member)
        self.c_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.channel)
        self.m_cd2=commands.CooldownMapping.from_cooldown(1,10,commands.BucketType.member)
        self.main_guilds = [952161067033849919, 1005150492382478377]
        self.global_cd = commands.CooldownMapping.from_cooldown(2, 3, commands.BucketType.member)
        self.ext = Client(self) 
        self.rival = RivalAPI(self.rival_api.get('api-key'))
        self.session_id = "59071245027%3AD0cDcLaxyzVyVQ%3A16%3AAYdIOvL5SM85A62N-zDxn04CaabIDHneyhA6I0r6VQ"
#        self.http.proxy = self.proxy_url
    async def create_db_pool(self):
        #self.db = await asyncpg.create_pool(port="5433", database="pretend", user="postgres", password="sentbos16")
        self.db = await asyncpg.create_pool(port="5432", database="postgres", user="postgres", host="localhost", password="sentboss16")
    
    async def get_context(self, message, *, cls=NeoContext):
     return await super().get_context(message, cls=cls) 

    async def setup_hook(self) -> None:
       print("Attempting to start")
       self.session = HTTP()
       bot.loop.create_task(bot.create_db_pool())
       await self.load_extension("jishaku")
#       await StartUp.loadcogs(self)
       self.add_view(vmbuttons())
       self.add_view(CreateTicket())
       self.add_view(DeleteTicket())
       self.add_view(GiveawayView())
       bot.loop.create_task(StartUp.startup(bot))     
    
    @property
    def ping(self) -> int: 
     return round(self.latency * 1000) 
    
    def convert_datetime(self, date: datetime.datetime=None):
     if date is None: return None  
     month = f'0{date.month}' if date.month < 10 else date.month 
     day = f'0{date.day}' if date.day < 10 else date.day 
     year = date.year 
     minute = f'0{date.minute}' if date.minute < 10 else date.minute 
     if date.hour < 10: 
      hour = f'0{date.hour}'
      meridian = "AM"
     elif date.hour > 12: 
      hour = f'0{date.hour - 12}' if date.hour - 12 < 10 else f"{date.hour - 12}"
      meridian = "PM"
     else: 
      hour = date.hour
      meridian = "PM"  
     return f"{month}/{day}/{year} at {hour}:{minute} {meridian} ({discord.utils.format_dt(date, style='R')})" 

    def ordinal(self, num: int) -> str:
     """Convert from number to ordinal (10 - 10th)""" 
     numb = str(num) 
     if numb.startswith("0"): numb = numb.strip('0')
     if numb in ["11", "12", "13"]: return numb + "th"
     if numb.endswith("1"): return numb + "st"
     elif numb.endswith("2"):  return numb + "nd"
     elif numb.endswith("3"): return numb + "rd"
     else: return numb + "th" 

    async def getbyte(self, video: str):  
      return BytesIO(await self.session.read(video, proxy=self.proxy_url, ssl=False)) 

    def is_dangerous(self, role: discord.Role) -> bool:
     permissions = role.permissions
     return any([
      permissions.kick_members, permissions.ban_members,
      permissions.administrator, permissions.manage_channels,
      permissions.manage_guild, permissions.manage_messages,
      permissions.manage_roles, permissions.manage_webhooks,
      permissions.manage_emojis_and_stickers, permissions.manage_threads,
      permissions.mention_everyone, permissions.moderate_members
     ])
    
    async def prefixes(self, message: discord.Message) -> List[str]: 
     prefixes = []
     for l in set(p for p in await self.command_prefix(self, message)): prefixes.append(l)
     return prefixes  

    async def guild_change(self, mes: str, guild: discord.Guild) -> discord.Message: 
     return
     channel = self.get_channel(1040684559487995964)
     try: await channel.send(embed=discord.Embed(color=self.color, description=f"{mes} **{guild.name}** owned by **{guild.owner}** with **{guild.member_count}** members"))  
     except: pass

    async def on_guild_join(self, guild: discord.Guild):
      if not guild.chunked: await guild.chunk(cache=True)
      await self.guild_change("joined", guild)

    async def on_guild_remove(self, guild: discord.Guild): 
       await self.guild_change("left", guild) 
   
    async def channel_ratelimit(self,message:discord.Message) -> typing.Optional[int]:
        cd=self.c_cd
        bucket=cd.get_bucket(message)
        return bucket.update_rate_limit()

    async def member_ratelimit(self,message:discord.Message) -> typing.Optional[int]:
        cd=self.m_cd
        bucket=cd.get_bucket(message)
        return bucket.update_rate_limit()

    async def on_ready(self):
       await create_db(self) 
       if self.cogs_loaded == False:
           await StartUp.loadcogs(self)
       print(f"Connected to discord API as {self.user} {self.user.id}")
    
    async def on_message_edit(self, before, after):
        if before.content != after.content: await self.process_commands(after)

    async def on_message(self, message: discord.Message): 
      channel_rl=await self.channel_ratelimit(message)
      member_rl=await self.member_ratelimit(message)
      if channel_rl == True:
          return
      if member_rl == True:
          return
      if message.content == "<@{}>".format(self.user.id): return await message.reply(content="prefixes: " + " ".join(f"`{g}`" for g in await self.prefixes(message)))
      await bot.process_commands(message) 

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
      if isinstance(error, commands.CommandNotFound): return 
      elif isinstance(error, commands.NotOwner): pass
      elif isinstance(error, commands.CheckFailure): 
        if isinstance(error, commands.MissingPermissions): return await ctx.send_warning(f"This command requires **{error.missing_permissions[0]}** permission")
      elif isinstance(error, commands.CommandOnCooldown):
        if ctx.command.name != "hit": return await ctx.reply(embed=discord.Embed(color=0xE1C16E, description=f"⌛ {ctx.author.mention}: You are on cooldown. Try again in {format_timespan(error.retry_after)}"), mention_author=False)    
      elif isinstance(error, commands.MissingRequiredArgument): return await ctx.cmdhelp()
      elif isinstance(error, commands.EmojiNotFound): return await ctx.send_warning(f"Unable to convert {error.argument} into an **emoji**")
      elif isinstance(error, commands.MemberNotFound): return await ctx.send_warning(f"Unable to find member **{error.argument}**")
      elif isinstance(error, commands.UserNotFound): return await ctx.send_warning(f"Unable to find user **{error.argument}**")
      elif isinstance(error, commands.RoleNotFound): return await ctx.send_warning(f"Couldn't find role **{error.argument}**")
      elif isinstance(error, commands.ChannelNotFound): return await ctx.send_warning(f"Couldn't find channel **{error.argument}**")
      elif isinstance(error, commands.UserConverter): return await ctx.send_warning(f"Couldn't convert that into an **user** ")
      elif isinstance(error, commands.MemberConverter): return await ctx.send_warning("Couldn't convert that into a **member**")
      elif isinstance(error, commands.BadArgument): return await ctx.send_warning(error.args[0])
      elif isinstance(error, commands.BotMissingPermissions): return await ctx.send_warning(f"I do not have enough **permissions** to execute this command")
      elif isinstance(error, discord.HTTPException): return await ctx.send_warning("Unable to execute this command")      
      else: 
       key = await checkthekey(generate_key())
       trace = str(error)
       rl=await self.member_ratelimit(ctx.message)
       if rl == True:
           return
       await self.db.execute("INSERT INTO cmderror VALUES ($1,$2)", key, trace)
       await self.ext.send_error(ctx, f"An unexpected error was found. Please report the code `{key}` in our [**support server**](https://discord.gg/pretend)")   

bot = CommandClient()

@bot.check
async def cooldown_check(ctx: commands.Context):
    bucket = bot.global_cd.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()
    if retry_after: raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.member)
    return True

async def check_ratelimit(ctx):
    cd=bot.m_cd2.get_bucket(ctx.message)
    return cd.update_rate_limit()

@bot.check 
async def blacklist(ctx: commands.Context): 
 rl=await check_ratelimit(ctx)
 if rl == True: return
 if ctx.guild is None: return False
 check = await bot.db.fetchrow("SELECT * FROM nodata WHERE user_id = $1", ctx.author.id)
 if check is not None: 
  if check["state"] == "false": return False 
  else: return True 
 embed = discord.Embed(color=bot.color, description="Do you **agree** to our [privacy policy](https://pretend.space/privacy) and for your data to be used for commands?\n**DISAGREEING** will result in a blacklist from using bot's commands")
 yes = discord.ui.Button(emoji=bot.yes, style=discord.ButtonStyle.gray)
 no = discord.ui.Button(emoji=bot.no, style=discord.ButtonStyle.gray)
 async def yes_callback(interaction: discord.Interaction): 
    if interaction.user != ctx.author: return await interaction.response.send_message(embed=discord.Embed(color=bot.color, description=f"{bot.warning} {interaction.user.mention}: This is not your message"), ephemeral=True)
    await bot.db.execute("INSERT INTO nodata VALUES ($1,$2)", ctx.author.id, "true")                     
    await interaction.message.delete()
    await bot.process_commands(ctx.message)

 yes.callback = yes_callback

 async def no_callback(interaction: discord.Interaction): 
    if interaction.user != ctx.author: return await interaction.response.send_message(embed=discord.Embed(color=bot.color, description=f"{bot.warning} {interaction.user.mention}: This is not your message"), ephemeral=True)
    await bot.db.execute("INSERT INTO nodata VALUES ($1,$2)", ctx.author.id, "false")                        
    await interaction.response.edit_message(embed=discord.Embed(color=bot.color, description=f"You got blacklisted from using bot's commands. If this is a mistake, please check our [**support server**](https://pretend.space/discord)"), view=None)
    return 

 no.callback = no_callback

 view = discord.ui.View()
 view.add_item(yes)
 view.add_item(no)
 await ctx.reply(embed=embed, view=view, mention_author=False)   

@bot.check
async def is_chunked(ctx: commands.Context):
  if ctx.guild: 
    if not ctx.guild.chunked: await ctx.guild.chunk(cache=True)
    return True

@bot.check
async def disabled_command(ctx: commands.Context):
  cmd = bot.get_command(ctx.invoked_with)
  if not cmd: return True
  check = await ctx.bot.db.fetchrow('SELECT * FROM disablecommand WHERE command = $1 AND guild_id = $2', cmd.name, ctx.guild.id)
  if check: await bot.ext.send_warning(ctx, f"The command **{cmd.name}** is **disabled**")     
  return check is None    

if __name__ == '__main__':
    #asyncio.run(botrun())
    bot.run(token)
