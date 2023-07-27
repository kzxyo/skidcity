import discord, os, asyncpg, typing, time, random, string, io, dotenv, datetime, multiprocessing
from humanfriendly import format_timespan
from discord.ext import commands, tasks
from tools.utils.utils import StartUp, create_db, Paginator
from cogs.music import Music
from io import BytesIO
from cogs.voicemaster import vmbuttons
from discord.gateway import DiscordWebSocket
from cogs.ticket import CreateTicket, DeleteTicket
from tools.utils.ext import Client, HTTP
from typing import Optional, List
dotenv.load_dotenv(verbose=True)
token=os.environ["token"]
temp="http://dgoubioi-rotate:suitth0qbw0l@p.webshare.io:80/"
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

intents = discord.Intents.all()

class Context(commands.Context): 
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
 
 async def send_neutral(self, message: str) -> discord.Message:  
  return await self.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.author.mention}: {message}") )
 
 async def paginator(self, embeds: List[discord.Embed]):
  if len(embeds) == 1: return await self.send(embed=embeds[0])
  view = Paginator(self, embeds)
  view.message = await self.reply(embed=embeds[0], view=view)

 async def cmdhelp(self): 
    command = self.command
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    if command.cog_name == "owner": return
    if command.cog_name == "auth": return
    embed = discord.Embed(color=bot.color, title=commandname, description=command.description)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
    embed.add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False)
    embed.set_footer(text=f"aliases: {', '.join(map(str, command.aliases)) or 'none'} • module: {command.help}")
    await self.reply(embed=embed)

 async def create_pages(self): 
  embeds = []
  p=0
  for command in self.command.commands: 
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    p+=1 
    embeds.append(discord.Embed(color=bot.color, title=f"{commandname}", description=command.description).set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url).add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False).set_footer(text=f"page: {p}/{len(self.command.commands)} • aliases: {', '.join(a for a in command.aliases) if len(command.aliases) > 0 else 'none'} ・ module: {command.help}"))
     
  return await self.paginator(embeds)

class Help(commands.HelpCommand):
  def __init__(self, **kwargs):
   super().__init__(**kwargs)
  
  async def send_bot_help(self, mapping):
    
    embed = discord.Embed(color=self.context.bot.color, description="command arguments\n```[] - required\n<> - optional```")
    embed.add_field(name="contact", value="need help? join the [**support server**](https://discord.gg/kQcYeuDjvN)")
    embed.set_author(name=self.context.author.name, icon_url=self.context.author.display_avatar.url)
    embed.set_footer(text=f"commands: {len(set(bot.walk_commands()))}")
    options = [
       discord.SelectOption(
         label="home",
         description="return to the main page",
         emoji="<:vilan_home:1130855008338972819>"
       ),
       discord.SelectOption(
         label="info",
         description="view information about the bot",
         emoji="<:vilan_info:1130854980904030350>"
       ),
       discord.SelectOption(
         label="moderation",
         description="keep your server safe",
         emoji="<:vilan_staff:1130856645652656198>"
       ),
       discord.SelectOption(
         label="antiraid",
         description="protect your server against raids",
         emoji="<:vilan_saturn:1130856389397467238>"
       ),
       discord.SelectOption(
         label="automod",
         description="doing the mod's job",
         emoji="<:vilan_lightbulb:1130857183945445496>"
       ),
       discord.SelectOption(
         label="antinuke",
         description="protect your server against unfaithful admins",
         emoji="<:vilan_hammer:1130855101951655986>"
       ),
       discord.SelectOption(
         label="emoji",
         description="manage the emojis in your server",
         emoji="<:vilan_calendar:1130855821706809474>"
       ),
       discord.SelectOption(
         label="utility",
         description="not the most commands are here",
         emoji="<:vilan_globe:1130855045181734963>"
       ),
       discord.SelectOption(
         label="config",
         description="configure your server",
         emoji="<:vilan_wrench:1130856148472447056>"
       ),
       discord.SelectOption(
         label="economy",
         description="economy commands",
         emoji="🏦"
       ),
       discord.SelectOption(
         label="giveaway",
         description="giveaway commands",
         emoji="🎉"
       ),
       discord.SelectOption(
         label="lastfm",
         description="lastfm integration with the bot",
         emoji="<:lastfm:1123217269397393479>"
       ),
       discord.SelectOption(
         label="music",
         description="play music with the bot",
         emoji="🎵"
       ),
       discord.SelectOption(
         label="fun",
         description="commands to use when you are bored",
         emoji="🎮"
       ),
       discord.SelectOption(
         label="roleplay",
         description="this is self explanatory",
         emoji="🎭"
       ),
       discord.SelectOption(
         label="donor",
         description="only rich people use these",
         emoji="<:boosts:1079296391605661886>"
       )
    ]
    #for c in self.categories: options.append(discord.SelectOption(label=c, description=self.categories.get(c)))
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
    if command.cog_name == "auth": return
    embed = discord.Embed(color=bot.color, title=commandname, description=command.description)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
    embed.add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False)
    embed.set_footer(text=f"aliases: {', '.join(map(str, command.aliases)) or 'none'} • module: {command.help}")
    channel = self.get_destination()
    await channel.send(embed=embed)
  
  async def send_group_help(self, group: commands.Group): 
   ctx = self.context
   embeds = []
   p=0
   for command in group.commands: 
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    p+=1 
    embeds.append(discord.Embed(color=bot.color, title=f"{commandname}", description=command.description).set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url).add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False).set_footer(text=f"page: {p}/{len(group.commands)} • aliases: {', '.join(a for a in command.aliases) if len(command.aliases) > 0 else 'none'} • module: {command.help}"))
     
   return await ctx.paginator(embeds) 

class vilan(commands.AutoShardedBot):
    def __init__(self):
        super().__init__( command_prefix=getprefix, help_command=Help(), intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False), case_sensitive=False, strip_after_prefix=True, owner_ids=[994896336040239114],
        )
        self.uptime = time.time()
        self.persistent_views_added = False
        self.cogs_loaded = False
        self.pretend_api = "4GKJVG97YXB6Z7JG"
        self.color = 0x6d827d
        self.yes = "<:check:1128624983481008188>"
        self.no = "<:stop:1128624954737426473>"
        self.warning = "<:warning:1128624932272734229>"
        self.left = "<:left:1018156480991612999>"
        self.right = "<:right:1018156484170883154>"
        self.proxy_url = "http://dgoubioi-rotate:suitth0qbw0l@p.webshare.io:80/"
        self.m_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.member)
        self.c_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.channel)
        self.m_cd2=commands.CooldownMapping.from_cooldown(1,10,commands.BucketType.member)
        self.global_cd = commands.CooldownMapping.from_cooldown(2, 3, commands.BucketType.member)
        self.ext = Client(self)
        self.session_id = "59071245027%3AD0cDcLaxyzVyVQ%3A16%3AAYdIOvL5SM85A62N-zDxn04CaabIDHneyhA6I0r6VQ"
    async def create_db_pool(self):
        self.db = await asyncpg.create_pool(port=5432, user=os.environ["pguser"], database=os.environ["pgdb"], password=os.environ["pgpass"], host=os.environ["pghost"])
    
    async def get_context(self, message, *, cls=Context):
     return await super().get_context(message, cls=cls)
    
    async def setup_hook(self) -> None:
      print("Attempting to connect")
      self.session = HTTP()
      bot.loop.create_task(bot.create_db_pool())
      await self.load_extension("jishaku")
      self.add_view(vmbuttons())
      self.add_view(CreateTicket())
      self.add_view(DeleteTicket())
      bot.loop.create_task(StartUp.startup(bot))
    
    @property
    def ping(self) -> int:
      return round(self.latency * 1000) / 4
    
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
    
    async def getbyte(self, video: str): 
      return BytesIO(await self.session.read(video, proxy=self.proxy_url, ssl=False)) 
    
    async def prefixes(self, message: discord.Message) -> List[str]: 
     prefixes = []
     for l in set(p for p in await self.command_prefix(self, message)): prefixes.append(l)
     return prefixes  
    
    async def guild_change(self, mes: str, guild: discord.Guild) -> discord.Message: 
     channel = self.get_channel(1120603031805886474)
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
      await Music(self).start_node()
      await create_db(self)
      if self.cogs_loaded == False:
        await StartUp.loadcogs(self)
      print(f"Connected in as {self.user} {self.user.id}")
    
    async def on_message_edit(self, before, after):
        if before.content != after.content: await self.process_commands(after)

    async def on_message(self, message: discord.Message): 
      channel_rl=await self.channel_ratelimit(message)
      member_rl=await self.member_ratelimit(message)
      if channel_rl == True:
          return
      if member_rl == True:
          return
      if message.content == "<@{}>".format(self.user.id): return await message.reply(content="prefix: " + " ".join(f"`{g}`" for g in await self.prefixes(message)))
      await bot.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
      if isinstance(error, commands.CommandNotFound): return 
      elif isinstance(error, commands.NotOwner): pass
      elif isinstance(error, commands.CheckFailure): 
        if isinstance(error, commands.MissingPermissions): return await ctx.send_warning(f"This command requires **{error.missing_permissions[0]}** permissions")
      elif isinstance(error, commands.CommandOnCooldown): 
        if ctx.command.name != "hit": return #await ctx.reply(embed=discord.Embed(color=0x6d827d, description=f"<:warning:1124999030158655519> {ctx.author.mention}: You are on cooldown. Try again in {format_timespan(error.retry_after)}"), mention_author=False)    
      elif isinstance(error, commands.MissingRequiredArgument): return await ctx.cmdhelp()
      elif isinstance(error, commands.EmojiNotFound): return await ctx.send_warning(f"Unable to convert {error.argument} into an **emoji**")
      elif isinstance(error, commands.MemberNotFound): return await ctx.send_warning(f"Unable to find member **{error.argument}**")
      elif isinstance(error, commands.UserNotFound): return await ctx.send_warning(f"Unable to find user **{error.argument}**")
      elif isinstance(error, commands.RoleNotFound): return await ctx.send_warning(f"Couldn't find role **{error.argument}**")
      elif isinstance(error, commands.ChannelNotFound): return await ctx.send_warning(f"Couldn't find channel **{error.argument}**")
      elif isinstance(error, commands.UserConverter): return await ctx.send_warning(f"Couldn't convert that into an **user** ")
      elif isinstance(error, commands.MemberConverter): return await ctx.send_warning("Couldn't convert that into a **member**")
      elif isinstance(error, commands.BadArgument): return await ctx.send_warning(error.args[0])
      elif isinstance(error, commands.BotMissingPermissions): return await ctx.send_warning("I do not have enough **permission** to do this")
      elif isinstance(error, discord.HTTPException): return await ctx.send_warning("Unable to execute this command")      
      else: 
       key = await checkthekey(generate_key())
       trace = str(error)
       rl=await self.member_ratelimit(ctx.message)
       if rl == True:
           return
       await self.db.execute("INSERT INTO cmderror VALUES ($1,$2)", key, trace)
       await self.ext.send_error(ctx, f"An unexpected error was found while processing the command **{ctx.command.name}**. Please report the code `{key}` in our [**support server**](https://discord.gg/kQcYeuDjvN)")

bot = vilan()

@bot.check
async def cooldown_check(ctx: commands.Context):
    bucket = bot.global_cd.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()
    if retry_after: raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.member)
    return True

async def check_ratelimit(ctx):
    cd=bot.m_cd2.get_bucket(ctx.message)
    return cd.update_rate_limit()

bot.check 
async def blacklist(ctx: commands.Context): 
 rl=await check_ratelimit(ctx)
 if rl == True: return
 if ctx.guild is None: return False
 check = await bot.db.fetchrow("SELECT * FROM nodata WHERE user_id = $1", ctx.author.id)
 if check is not None: 
  if check["state"] == "false": return False 
  else: return True 
 embed = discord.Embed(color=bot.color, description="Do you **agree** to our [privacy policy](https://github.com/kysfr/privacy-policy) and for your data to be used for commands?\n**DISAGREEING** will result in a blacklist from using our bot")
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
    await interaction.response.edit_message(embed=discord.Embed(color=bot.color, description=f"You got blacklisted from using our bot. If this is a mistake, please contact us in the [**support server**](https://discord.gg/kQcYeuDjvN)"), view=None)
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
  if check: await bot.ext.send_warning(ctx, f"The command **{cmd.name}** is **disabled** in this guild")     
  return check is None    

if __name__ == '__main__':
    tokens=["MTA1OTgxOTA0MjYxMDg3MjQwMQ.Gf07V5.JVEYoJe0XySksWwIEuqGUI-IUxny_v382EgRDA", "MTEyNTA0NzcxODQ4MjU1ODk4Nw.Gp0yZ9.ePeSDWU8Mq4TFMalXgqr6XF_2RUfHywzuva3wY"]
    #for i in tokens:
    #    token=i
    #    jobs=[]
    #    p=multiprocessing.Process(target=bot.run, args=(token,))
    #    jobs.append(p)
    #    p.start()
    bot.run(tokens[0])