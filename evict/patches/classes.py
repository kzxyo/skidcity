import datetime, discord, emoji, re, arrow, pomice, random
from typing import Any, Coroutine
from discord import Embed, Message, HTTPException
from contextlib import suppress
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from discord.ext import commands
from discord.ext.commands import Context
from bot.helpers import EvictContext

class ValidAutoreact(commands.EmojiConverter):
    async def convert(self, ctx: commands.Context, argument: str):
        try:
            emoj = await super().convert(ctx, argument)
        except commands.BadArgument:
            if not emoji.is_emoji(argument):
                return None

            emoj = argument
        return emoj

class TimeConverter(object): 
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
     
class Modals: 
   class Name(discord.ui.Modal, title="change the role name"):
      name = discord.ui.TextInput(
        label='role name',
        placeholder='your new role name here',
        style=discord.TextStyle.short,
        required=True
    )

      async def on_submit(self, interaction: discord.Interaction):
         check = await interaction.client.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id))         
         if check is None: return await interaction.client.ext.warning(interaction, "You don't have a booster role. Please use `boosterrole create` command first", ephemeral=True)
         role = interaction.guild.get_role(check['role_id'])
         await role.edit(name=self.name.value)
         return await interaction.client.ext.success(interaction, "Changed the **booster role** name in **{}**".format(self.name.value), ephemeral=True)

   class Icon(discord.ui.Modal, title="change the role icon"):
      name = discord.ui.TextInput(
        label='role icon',
        placeholder='this should be an emoji',
        style=discord.TextStyle.short,
        required=True
    )

      async def on_submit(self, interaction: discord.Interaction):
       try: 
         check = await interaction.client.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id))         
         if check is None: return await interaction.client.ext.warning(interaction, "You don't have a booster role. Please use `boosterrole create` command first", ephemeral=True)
         role = interaction.guild.get_role(check['role_id'])
         icon = ""
         if emoji.is_emoji(self.name.value): icon = self.name.value 
         else:
          emojis = re.findall(r'<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>', self.name.value)
          emoj = emojis[0]
          format = ".gif" if emoj[0] == "a" else ".png"
          url = "https://cdn.discordapp.com/emojis/{}{}".format(emoj[2], format)
          icon = await interaction.client.session.read(url)
         await role.edit(display_icon=icon) 
         return await interaction.client.ext.success(interaction, "Changed the **booster role** icon", ephemeral=True)  
       except: return await interaction.client.ext.error(interaction, "Unable to change the role icon", ephemeral=True)

   class Color(discord.ui.Modal, title="change the role colors"):
      name = discord.ui.TextInput(
        label='role color',
        placeholder='this should be a hex code',
        style=discord.TextStyle.short,
        required=True
    )

      async def on_submit(self, interaction: discord.Interaction):
       try: 
         check = await interaction.client.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id))         
         if check is None: return await interaction.client.ext.warning(interaction, "You don't have a booster role. Please use `boosterrole create` command first", ephemeral=True)
         role = interaction.guild.get_role(check['role_id'])
         color = self.name.value.replace("#", "")
         color = int(color, 16)
         await role.edit(color=color)
         return await interaction.client.ext.success(interaction, "Changed the **booster role** color", ephemeral=True)
       except: return await interaction.client.ext.error(interaction, "Unable to change the role color", ephemeral=True)

class OwnerConfig:
    async def send_dm(ctx: commands.Context, member: discord.Member, action: str, reason: str): 
        embed = discord.Embed(color=ctx.bot.color, description=f"You have been **{action}** in every server evict is in.\n{f'**Reason:** {reason}' if reason != 'No reason provided' else ''}")
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"sent from {ctx.author}", disabled=True))
        try: await member.send(embed=embed, view=view)
        except: pass
        
class Time:
    def format_duration(self, timestamp):
        duration = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)
        years = duration.days // 365
        months = duration.days % 365 // 30
        days = duration.days % 30
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if years > 0:
            parts.append(f"{years} {'year' if years == 1 else 'years'}")
        if months > 0:
            parts.append(f"{months} {'month' if months == 1 else 'months'}")
        if days > 0:
            parts.append(f"{days} {'day' if days == 1 else 'days'}")
        if hours > 0:
            parts.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
        if minutes > 0:
            parts.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")
        if seconds > 0:
            parts.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")

        return ", ".join(parts)
      
class ValidWebhookCode(commands.Converter):
  async def convert(self, ctx: EvictContext, argument: str):
   check = await ctx.bot.db.fetchrow("SELECT * FROM webhook WHERE guild_id = $1 AND code = $2", ctx.guild.id, argument)
   if not check:
    raise commands.BadArgument("There is no webhook associated with this code")
   return argument
 
class Mod: 

  def is_mod_configured(): 
   async def predicate(ctx: commands.Context): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM mod WHERE guild_id = $1", ctx.guild.id)
    if not check: 
     await ctx.warning( f"Moderation isn't **enabled** in this server. Enable it using `{ctx.clean_prefix}setmod` command")
     return False
    return True
   return commands.check(predicate)

  async def check_role_position(ctx: commands.Context, role: discord.Role) -> bool: 
   if (role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id) or not role.is_assignable(): 
    await ctx.warning( "I cannot manage this role for you")
    return False 
   return True

  async def check_hieracy(ctx: commands.Context, member: discord.Member) -> bool: 
   if member.id == ctx.bot.user.id: 
    if ctx.command.name != "nickname":
     await ctx.reply("leave me alone <:mmangry:1081633006923546684>") 
     return False
   if (ctx.author.top_role.position <= member.top_role.position and ctx.guild.owner_id != ctx.author.id) or ctx.guild.me.top_role <= member.top_role or (member.id == ctx.guild.owner_id and ctx.author.id != member.id): 
    await ctx.warning( "You can't do this action on **{}**".format(member))
    return False  
   return True 


class Timezone(object):
  def __init__(self, bot: commands.Bot): 
   """
   Get timezones of people
   """
   self.bot = bot
   self.clock = "🕑"
   self.months = {
     '01': 'January',
     '02': 'February',
     '03': 'March',
     '04': 'April',
     '05': 'May',
     '06': 'June',
     '07': 'July',
     '08': 'August',
     '09': 'September',
     '10': 'October',
     '11': 'November',
     '12': 'December'
   }
  
  async def timezone_send(self, ctx: Context, message: str):
   return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.clock} {ctx.author.mention}: {message}"))
  
  async def timezone_request(self, member: discord.Member):
   coord = await self.get_user_lat_long(member)
   if coord is None: return None
   utc = arrow.utcnow()
   local = utc.to(coord)
   timestring = local.format('YYYY-MM-DD HH:mm').split(" ")
   date = timestring[0][5:].split("-")
   try:
    hours, minutes = [int(x) for x in timestring[1].split(":")[:2]]
   except IndexError:
    return "N/A"

   if hours >= 12:
    suffix = "PM"
    hours -= 12
   else:
    suffix = "AM"
   if hours == 0:
     hours = 12
   return f"{self.months.get(date[0])} {self.bot.ext.ordinal(date[1])} {hours}:{minutes:02d} {suffix}" 
  
  async def get_user_lat_long(self, member: discord.Member): 
   check = await self.bot.db.fetchrow("SELECT * FROM timezone WHERE user_id = $1", member.id) 
   if check is None: return None 
   return check['zone']
  
  async def tz_set_cmd(self, ctx: Context, location: str):
   await ctx.typing()
   geolocator = Nominatim(user_agent="Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36")
   lad = location
   location = geolocator.geocode(lad) 
   if location is None: return await ctx.warning( "Couldn't find a **timezone** for that location")
   check = await self.bot.db.fetchrow("SELECT * FROM timezone WHERE user_id = $1", ctx.author.id) 
   obj = TimezoneFinder()
   result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
   if not check: await self.bot.db.execute("INSERT INTO timezone VALUES ($1,$2)", ctx.author.id, result)
   else: 
     await self.bot.db.execute("DELETE FROM timezone WHERE user_id = $1", ctx.author.id)
     await self.bot.db.execute("INSERT INTO timezone VALUES ($1,$2)", ctx.author.id, result)
   embed = Embed(color=self.bot.color, description=f"Saved your timezone as **{result}**\n{self.clock} Current time: **{await self.timezone_request(ctx.author)}**")
   await ctx.reply(embed=embed)

  async def get_user_timezone(self, ctx: Context, member: discord.Member): 
   if await self.timezone_request(member) is None: 
    if member.id == ctx.author.id: return await ctx.warning( f"You don't have a **timezone** set. Use `{ctx.clean_prefix}tz set` command instead")   
    else: return await ctx.warning( f"**{member.name}** doesn't have their **timezone** set")
   if member.id == ctx.author.id: return await self.timezone_send(ctx, f"Your current time: **{await self.timezone_request(member)}**")
   else: return await self.timezone_send(ctx, f"**{member.name}'s** current time: **{await self.timezone_request(member)}**") 
   
class Player(pomice.Player):
  def __init__(self, *args, **kwargs):
   super().__init__(*args, **kwargs)
   self.ctx: EvictContext = None
   self.queue = pomice.Queue()
   self.loop: bool = False
   self.current_track: pomice.Track = None
   self.awaiting = False

  def set_context(self, ctx: EvictContext):
    self.context = ctx

  def shuffle(self) -> None: 
    return random.shuffle(self.queue) 

  async def set_pause(self, pause: bool) -> Coroutine[Any, Any, bool]:
    if pause is True:
       self.awaiting = True 
    else: 
      if self.awaiting: 
        self.awaiting = False 
    
    return await super().set_pause(pause)  

  async def do_next(self, track: pomice.Track=None) -> None:
    if not self.loop: 
      if not track:
        try:
          track: pomice.Track = self.queue.get()
        except pomice.QueueEmpty:
          return await self.kill()
      
      self.current_track = track 
    
    await self.play(self.current_track)   
    await self.context.send(embed=Embed(color=self.context.bot.color, description=f"🎵 {self.context.author.mention}: Now playing [**{track.title}**]({track.uri})"))
    
    if self.awaiting: 
      self.awaiting = False 
  
  async def kill(self) -> Message:
    with suppress((HTTPException), (KeyError)):
      await self.destroy()
      return await self.context.send_success("Left the voice channel")
  