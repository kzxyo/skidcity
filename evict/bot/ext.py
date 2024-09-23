from discord.ext import commands
import discord, datetime, time
from typing import Union
from math import log, floor


class Client(object): 
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
    
  async def success(self, ctx: Union[commands.Context, discord.Interaction], message: str, ephemeral: bool=True) -> discord.Message: 
   if isinstance(ctx, commands.Context): return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: {message}"))
   else: return await ctx.response.send_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.user.mention}: {message}"), ephemeral=ephemeral)
  
  async def error(self, ctx: Union[commands.Context, discord.Interaction], message: str, ephemeral: bool=True) -> discord.Message: 
   if isinstance(ctx, commands.Context): return await ctx.reply(embed=discord.Embed(color=self.bot.error_color, description=f"{self.bot.no} {ctx.author.mention}: {message}"))
   else: return await ctx.response.send_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.user.mention}: {message}"), ephemeral=ephemeral)
  
  async def warning(self, ctx: Union[commands.Context, discord.Interaction], message: str, ephemeral: bool=True) -> discord.Message: 
   if isinstance(ctx, commands.Context): return await ctx.reply(embed=discord.Embed(color=self.bot.error_color, description=f"{self.bot.warning} {ctx.author.mention}: {message}"))
   else: return await ctx.response.send_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.user.mention}: {message}"), ephemeral=ephemeral)
   
  async def link_to_message(self, link: str) -> discord.Message: 
   link = link.replace("https://discord.com/channels/", "")
   link = link.split("/")
   return await self.bot.get_guild(int(link[0])).get_channel(int(link[1])).fetch_message(int(link[2]))  

  def is_dangerous(self, role: discord.Role) -> bool:
     permissions = role.permissions
     return any([
      permissions.kick_members, permissions.ban_members,
      permissions.administrator, permissions.manage_channels,
      permissions.manage_guild, permissions.manage_messages,
      permissions.manage_roles, permissions.manage_webhooks,
      permissions.manage_emojis_and_stickers, permissions.manage_threads,
      permissions.mention_everyone, permissions.moderate_members])
     
  def human_format(self, number) -> str:
    units = ['', 'K', 'M', 'G', 'T', 'P']
    if number < 1000:
      return number

    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])
  
  def relative_time(self, date):
    """Take a datetime and return its "age" as a string.
    The age can be in second, minute, hour, day, month or year. Only the
    biggest unit is considered, e.g. if it's 2 days and 3 hours, "2 days" will
    be returned.
    Make sure date is not in the future, or else it won't work.
    """

    def formatn(n, s):
        """Add "s" if it's plural"""

        if n == 1:
            return "1 %s" % s
        elif n > 1:
            return "%d %ss" % (n, s)

    def qnr(a, b):
        """Return quotient and remaining"""

        return a / b, a % b

    class FormatDelta:

        def __init__(self, dt):
            now = datetime.datetime.now()
            delta = now - dt
            self.day = delta.days
            self.second = delta.seconds
            self.year, self.day = qnr(self.day, 365)
            self.month, self.day = qnr(self.day, 30)
            self.hour, self.second = qnr(self.second, 3600)
            self.minute, self.second = qnr(self.second, 60)

        def format(self):
            for period in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                n = getattr(self, period)
                if n >= 1:
                    return '{0} ago'.format(formatn(n, period))
            return "just now"

    return FormatDelta(date).format()
    
  @property 
  def uptime(self) -> str:
    uptime = int(time.time() - self.bot.uptime)
    seconds_to_minute   = 60
    seconds_to_hour     = 60 * seconds_to_minute
    seconds_to_day      = 24 * seconds_to_hour

    days    =   uptime // seconds_to_day
    uptime    %=  seconds_to_day

    hours   =   uptime // seconds_to_hour
    uptime    %=  seconds_to_hour

    minutes =   uptime // seconds_to_minute
    uptime    %=  seconds_to_minute

    seconds = uptime
    if days > 0: return ("{} days, {} hours, {} minutes, {} seconds".format(days, hours, minutes, seconds))
    if hours > 0 and days == 0: return ("{} hours, {} minutes, {} seconds".format(hours, minutes, seconds))
    if minutes > 0 and hours == 0 and days == 0: return ("{} minutes, {} seconds".format(minutes, seconds))
    if minutes == 0 and hours == 0 and days == 0: return ("{} seconds".format(seconds))  

  @property
  def ping(self) -> int: 
    return round(self.bot.latency * 1000)
  
  def is_dangerous(self, role: discord.Role) -> bool:
     permissions = role.permissions
     return any([
      permissions.kick_members, permissions.ban_members,
      permissions.administrator, permissions.manage_channels,
      permissions.manage_guild, permissions.manage_messages,
      permissions.manage_roles, permissions.manage_webhooks,
      permissions.manage_emojis_and_stickers, permissions.manage_threads,
      permissions.mention_everyone, permissions.moderate_members])
  
  def ordinal(self, num: int) -> str:
     """Convert from number to ordinal (10 - 10th)""" 
     numb = str(num) 
     if numb.startswith("0"): numb = numb.strip('0')
     if numb in ["11", "12", "13"]: return numb + "th"
     if numb.endswith("1"): return numb + "st"
     elif numb.endswith("2"):  return numb + "nd"
     elif numb.endswith("3"): return numb + "rd"
     else: return numb + "th"
     
class GoToModal(discord.ui.Modal, title="change the page"):
  page = discord.ui.TextInput(label="page", placeholder="change the page", max_length=3)

  async def on_submit(self, interaction: discord.Interaction) -> None:
   if int(self.page.value) > len(self.embeds): return await interaction.client.ext.warning(interaction, f"You can only select a page **between** 1 and {len(self.embeds)}", ephemeral=True) 
   await interaction.response.edit_message(embed=self.embeds[int(self.page.value)-1]) 
  
  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
    await interaction.client.ext.warning(interaction, "I am unable to change the page", ephemeral=True)
     
class PaginatorView(discord.ui.View): 
    def __init__(self, ctx: commands.Context, embeds: list): 
      super().__init__()  
      self.embeds = embeds
      self.ctx = ctx
      self.i = 0
      
    @discord.ui.button(emoji="<:filter:1263727034798968893>")
    async def goto(self, interaction: discord.Interaction, button: discord.ui.Button): 
     if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")     
     modal = GoToModal()
     modal.embeds = self.embeds
     await interaction.response.send_modal(modal)
     await modal.wait()
     try:
      self.i = int(modal.page.value)-1
     except: pass 
     
    @discord.ui.button(emoji="<:left:1263727060078035066>", style=discord.ButtonStyle.secondary)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.warning(interaction, "You are not the author of this embed")            
      if self.i == 0: 
        await interaction.response.edit_message(embed=self.embeds[-1])
        self.i = len(self.embeds)-1
        return
      self.i = self.i-1
      return await interaction.response.edit_message(embed=self.embeds[self.i])

    @discord.ui.button(emoji="<:right:1263727130370637995>", style=discord.ButtonStyle.secondary)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.warning(interaction, "You are not the author of this embed")     
      if self.i == len(self.embeds)-1: 
        await interaction.response.edit_message(embed=self.embeds[0])
        self.i = 0
        return 
      self.i = self.i + 1  
      return await interaction.response.edit_message(embed=self.embeds[self.i])   
    
    @discord.ui.button(emoji="<:deny:1263727013433184347>", style=discord.ButtonStyle.secondary)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.warning(interaction, "You are not the author of this embed")         
      await interaction.message.delete()

    async def on_timeout(self) -> None: 
        
        mes = await self.message.channel.fetch_message(self.message.id)
        if mes is None: return
        
        if len(mes.components) == 0: return
        
        for item in self.children:
            item.disabled = True

        try: await self.message.edit(view=self)   
        except: pass