import discord, json, humanfriendly, asyncio, datetime, random 
from discord.ext import commands
from patches.permissions import Permissions
from events.tasks import gwend_task, gw_loop

class GiveawayView(discord.ui.View): 
  def __init__(self): 
   super().__init__(timeout=None) 

  @discord.ui.button(emoji="🎉", style=discord.ButtonStyle.green, custom_id="persistent:join_gw")
  async def join_gw(self, interaction: discord.Interaction, button: discord.ui.Button):
   check = await interaction.client.db.fetchrow("SELECT * FROM giveaway WHERE guild_id = $1 AND message_id = $2", interaction.guild.id, interaction.message.id)
   lis = json.loads(check['members'])
   if interaction.user.id in lis: 
    button1 = discord.ui.Button(label="Leave the Giveaway", style=discord.ButtonStyle.danger)

    async def button1_callback(inter: discord.Interaction): 
      lis.remove(interaction.user.id)
      await interaction.client.db.execute("UPDATE giveaway SET members = $1 WHERE guild_id = $2 AND message_id = $3", json.dumps(lis), inter.guild.id, interaction.message.id) 
      interaction.message.embeds[0].set_field_at(0, name="entries", value=f"{len(lis)}")
      await interaction.message.edit(embed=interaction.message.embeds[0])
      return await inter.response.edit_message(content="You left the giveaway", view=None)
    button1.callback = button1_callback
    vi = discord.ui.View()
    vi.add_item(button1)
    return await interaction.response.send_message(content="You are already in this giveaway", view=vi, ephemeral=True)
   else: 
    lis.append(interaction.user.id)
    await interaction.client.db.execute("UPDATE giveaway SET members = $1 WHERE guild_id = $2 AND message_id = $3", json.dumps(lis), interaction.guild.id, interaction.message.id) 
    interaction.message.embeds[0].set_field_at(0, name="entries", value=f"{len(lis)}")
    return await interaction.response.edit_message(embed=interaction.message.embeds[0])
      
class giveaway(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
  
  @commands.Cog.listener()
  async def on_connect(self): 
   gw_loop.start(self.bot)

  @commands.command(name="gcreate", brief="manage server", description="create a giveaway in this server", usage="<channel>")
  @Permissions.has_permission(manage_guild=True) 
  async def gcreate(self, ctx: commands.Context, *, channel: discord.TextChannel=None):  
   return await ctx.invoke(self.bot.get_command('giveaway create'), channel=channel or ctx.channel) 
  
  @commands.command(description="returns a list of active giveaways in the server", help="config")
  @Permissions.has_permission(manage_guild=True) 
  async def glist(self, ctx: commands.Context): 
   return await ctx.invoke(self.bot.get_command('giveaway list')) 
  
  @commands.command(brief="manage_server", description="end a giveaway", usage="[message id] <channel>")
  @Permissions.has_permission(manage_guild=True) 
  async def gend(self, ctx: commands.Context, message_id: int, *, channel: discord.TextChannel=None): 
   await ctx.invoke(self.bot.get_command('giveaway end'), message_id=message_id, channel=channel or ctx.channel) 
  
  @commands.command(description="reroll a giveaway", brief="manage server", usage="[message id] <channel>")
  @Permissions.has_permission(manage_guild=True) 
  async def greroll(self, ctx: commands.Context, message_id: int, *, channel: discord.TextChannel=None): 
   await ctx.invoke(self.bot.get_command('giveaway reroll'), message_id=message_id, channel=channel or ctx.channel)  

  @commands.group(invoke_without_command=True, aliases=['gw'])
  async def giveaway(self, ctx): 
    return await ctx.create_pages()
  
  @giveaway.command(name="end", brief="manage_server", description="end a giveaway", usage="[message id] <channel>")
  @Permissions.has_permission(manage_guild=True) 
  async def gw_end(self, ctx: commands.Context, message_id: int, *, channel: discord.TextChannel=None): 
   if not channel: channel = ctx.channel
   check = await self.bot.db.fetchrow("SELECT * FROM giveaway WHERE guild_id = $1 AND channel_id = $2 AND message_id = $3", ctx.guild.id, channel.id, message_id) 
   if not check: return await ctx.warning("This message is not a  giveaway or it ended if it was one")
   await gwend_task(self.bot, check, datetime.datetime.now())
   return await ctx.success(f"Ended giveaway in {channel.mention}")

  @giveaway.command(name="reroll", description="reroll a giveaway", brief="manage server", usage="[message id] <channel>")
  @Permissions.has_permission(manage_guild=True) 
  async def gw_reroll(self, ctx: commands.Context, message_id: int, *, channel: discord.TextChannel=None): 
   if not channel: channel = ctx.channel
   check = await self.bot.db.fetchrow("SELECT * FROM gw_ended WHERE channel_id = $1 AND message_id = $2", channel.id, message_id)  
   if not check: return await ctx.warning(f"This message is not a giveaway or it didn't end if it is one. Use `{ctx.clean_prefix}gend` to end the giveaway")
   members = json.loads(check['members'])
   await ctx.reply(f"**New winner:** <@!{random.choice(members)}>")

  @giveaway.command(name="list", description="returns a list of active giveaways in the server", help="config")
  @Permissions.has_permission(manage_guild=True) 
  async def gw_list(self, ctx: commands.Context): 
    i=0
    k=1
    l=0
    mes = ""
    number = []
    messages = []
    results = await self.bot.db.fetch("SELECT * FROM giveaway WHERE guild_id = $1", ctx.guild.id)
    if len(results) == 0: return await ctx.error("There are no giveaways")
    for result in results:
      mes = f"{mes}`{k}` [**{result['title']}**](https://discord.com/channels/{ctx.guild.id}/{result['channel_id']}/{result['message_id']}) ends <t:{int(result['finish'].timestamp())}:R>\n"
      k+=1
      l+=1
      if l == 10:
        messages.append(mes)
        number.append(discord.Embed(color=self.bot.color, title=f"giveaways ({len(results)})", description=messages[i]))
        i+=1
        mes = ""
        l=0
    
    messages.append(mes)
    number.append(discord.Embed(color=self.bot.color, title=f"giveaways ({len(results)})", description=messages[i]))
    await ctx.paginate(number)  

  @giveaway.command(name="create", brief="manage server", description="create a giveaway in this server", usage="<channel>")
  @Permissions.has_permission(manage_guild=True) 
  async def gw_create(self, ctx: commands.Context, *, channel: discord.TextChannel=None):
   if not channel: channel = ctx.channel 
   await ctx.reply(f"Starting giveaway in {channel.mention}...")
   responses = [] 
   for me in ["What is the prize for this giveaway?", "How long should the Giveaway last?", "How many winners should this Giveaway have?"]:
     await ctx.send(me)
     try: 
       def is_author(m): return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id 
       message = await self.bot.wait_for('message', check=is_author, timeout=10.0)
       responses.append(message.content)
       await message.add_reaction("<:catthumbsup:1208425783912177695>")
     except asyncio.TimeoutError: return await ctx.send(content="You didn't reply in time") 
   description = responses[0]
   try: seconds = humanfriendly.parse_timespan(responses[1])
   except humanfriendly.InvalidTimespan: return await ctx.send(content="Invalid time parsed")
   try: winners = int(responses[2])
   except ValueError: return await ctx.send(content="Invalid number of winners") 
   embed = discord.Embed(color=self.bot.color, title=description, description=f"Ends: <t:{int((datetime.datetime.now() + datetime.timedelta(seconds=seconds)).timestamp())}> (<t:{int((datetime.datetime.now() + datetime.timedelta(seconds=seconds)).timestamp())}:R>)\nHosted by: {ctx.author.mention}\nWinners: **{winners}**")
   embed.add_field(name="Entries", value="0")
   view=GiveawayView()
   await ctx.send(content=f"Giveaway setup completed! Check {channel.mention}")
   mes = await channel.send(embed=embed, view=view)
   await self.bot.db.execute("INSERT INTO giveaway VALUES ($1,$2,$3,$4,$5,$6,$7,$8)", ctx.guild.id, channel.id, mes.id, winners, json.dumps([]), (datetime.datetime.now() + datetime.timedelta(seconds=seconds)), ctx.author.id, description)

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(giveaway(bot))        