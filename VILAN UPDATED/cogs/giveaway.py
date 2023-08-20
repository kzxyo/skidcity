import discord, asyncio, datetime, humanfriendly, json
from discord.ext import commands, tasks
from tools.utils.checks import Perms

async def gwend_task(bot: commands.AutoShardedBot, result, date: datetime.datetime): 
  members = json.loads(result['members'])
  winners = result['winners']
  channel_id = result['channel_id']
  message_id = result['message_id']
  channel = bot.get_channel(channel_id)
  if channel:   
    message = await channel.fetch_message(message_id)
    if message:    
      wins = []
      if len(members) <= winners:       
        embed = discord.Embed(color=bot.color, title=message.embeds[0].title, description=f"Hosted by: <@!{result['host']}>\nEntries: **{len(json.loads(result['members']))}**\n\nNot enough entries to determine the winners!")
        await message.edit(embed=embed, view=None)
      else:  
       for _ in range(winners): wins.append(random.choice(members))
       embed = discord.Embed(color=bot.color, title=message.embeds[0].title, description=f"Ended: <t:{int(date.timestamp())}:R>\nHosted by: <@!{result['host']}>\nEntries: **{len(json.loads(result['members']))}").add_field(name="winners", value='\n'.join([f"**{bot.get_user(w)}** ({w})" for w in wins]))
       await message.edit(embed=embed, view=None)
       await message.reply(f"**{result['title']}** winners:\n" + '\n'.join([f"<@{w}> ({w})" for w in wins])) 
  await bot.db.execute("INSERT INTO gw_ended VALUES ($1,$2,$3)", channel_id, message_id, json.dumps(members))
  await bot.db.execute("DELETE FROM giveaway WHERE channel_id = $1 AND message_id = $2", channel_id, message_id)

@tasks.loop(seconds=5)
async def gw_loop(bot: commands.AutoShardedBot):
  results = await bot.db.fetch("SELECT * FROM giveaway")
  date = datetime.datetime.now()
  for result in results: 
   if date.timestamp() > result['finish'].timestamp(): await gwend_task(bot, result, date)

class GiveawayJoin(discord.ui.View): 
  def __init__(self): 
   super().__init__(timeout=None) 

  @discord.ui.button(emoji="🎉", style=discord.ButtonStyle.blurple, custom_id="persistent:join_gw")
  async def join_gw(self, interaction: discord.Interaction, button: discord.ui.Button):
   check = await interaction.client.db.fetchrow("SELECT * FROM giveaway WHERE guild_id = $1 AND message_id = $2", interaction.guild.id, interaction.message.id)
   lis = json.loads(check['members'])
   if interaction.user.id in lis: 
    button1 = discord.ui.Button(label="Leave the Giveaway", style=discord.ButtonStyle.danger)

    async def button1_callback(inter: discord.Interaction): 
      lis.remove(interaction.user.id)
      await interaction.client.db.execute("UPDATE giveaway SET members = $1 WHERE guild_id = $2 AND message_id = $3", json.dumps(lis), inter.guild.id, interaction.message.id) 
      
      await interaction.message.edit(embed=discord.Embed(color=interaction.client.color, title=check['title'], description=f"Ends: <t:{check['finish']}:R> (<t:{check['finish']}:F>)\nHosted by: <@!{check['host']}>\nEntries: **{len(lis)}**\nWinners: **{check['winners']}**"))
      return await inter.response.edit_message(content="You have succesfully left the giveaway", view=None)
    button1.callback = button1_callback
    vi = discord.ui.View()
    vi.add_item(button1)
    return await interaction.response.send_message(content="You already entered this giveaway", view=vi, ephemeral=True)
   else: 
    lis.append(interaction.user.id)
    await interaction.client.db.execute("UPDATE giveaway SET members = $1 WHERE guild_id = $2 AND message_id = $3", json.dumps(lis), interaction.guild.id, interaction.message.id) 
    
    return await interaction.response.edit_message(embed=discord.Embed(color=interaction.client.color, title=check['title'], description=f"Ends: <t:{check['finish']}:R> (<t:{check['finish']}:F>)\nHosted by: <@!{check['host']}>\nEntries: **{len(lis)}**\nWinners: **{check['winners']}**"))

class Giveaway(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_connect(self): 
     gw_loop.start(self.bot)

    @commands.command(name="gcreate", brief="manage server", description="create a giveaway in this server", help="giveaway", usage="<channel>")
    @Perms.get_perms("manage_guild")
    async def gcreate(self, ctx: commands.Context, *, channel: discord.TextChannel=None):  
     return await ctx.invoke(self.bot.get_command('giveaway create'), channel=channel or ctx.channel) 
  
    @commands.command(brief="manage_server", description="end a giveaway", help="giveaway", usage="[message id] <channel>")
    @Perms.get_perms("manage_guild") 
    async def gend(self, ctx: commands.Context, message_id: int, *, channel: discord.TextChannel=None): 
     await ctx.invoke(self.bot.get_command('giveaway end'), message_id=message_id, channel=channel or ctx.channel) 
  
    @commands.command(help="giveaway", description="reroll a giveaway", brief="manage server", usage="[message id] <channel>")
    @Perms.get_perms("manage_guild") 
    async def greroll(self, ctx: commands.Context, message_id: int, *, channel: discord.TextChannel=None): 
     await ctx.invoke(self.bot.get_command('giveaway reroll'), message_id=message_id, channel=channel or ctx.channel)  
    
    @commands.group(invoke_without_command=True, aliases=["gw"])
    async def giveaway(self, ctx):
      return await ctx.create_pages()
    
    @giveaway.command(name="end", brief="manage_server", description="end a giveaway", help="giveaway", usage="[message id] <channel>")
    @Perms.get_perms("manage_guild")
    async def gw_end(self, ctx: commands.Context, message_id: int, *, channel: discord.TextChannel=None): 
     if not channel: channel = ctx.channel
     check = await self.bot.db.fetchrow("SELECT * FROM giveaway WHERE guild_id = $1 AND channel_id = $2 AND message_id = $3", ctx.guild.id, channel.id, message_id) 
     if not check: return await ctx.send_warning("This message is not a  giveaway or if it was one it ended")
     await gwend_task(self.bot, check, datetime.datetime.now())
     return await ctx.send_success(f"Ended giveaway in {channel.mention}")

    @giveaway.command(name="reroll", help="giveaway", description="reroll a giveaway", brief="manage server", usage="[message id] <channel>")
    @Perms.get_perms("manage_guild")
    async def gw_reroll(self, ctx: commands.Context, message_id: int, *, channel: discord.TextChannel=None): 
     if not channel: channel = ctx.channel
     check = await self.bot.db.fetchrow("SELECT * FROM gw_ended WHERE channel_id = $1 AND message_id = $2", channel.id, message_id)  
     if not check: return await ctx.send_warning(f"This message is not a  giveaway or if it was one it ended. Use `{ctx.clean_prefix}gend` to end the giveaway")
     members = json.loads(check['members'])
     await ctx.reply(f"**New winner:** <@!{random.choice(members)}>")
    
    @giveaway.command(name="create", brief="manage server", description="create a giveaway in this server", help="giveaway", usage="<channel>")
    @Perms.get_perms("manage_guild")
    async def gw_create(self, ctx: commands.Context, *, channel: discord.TextChannel=None):
      if not channel: channel = ctx.channel
      await ctx.reply(f"Starting giveawy in {channel.mention}...")
      messages = []
      for r in ["What should be the prize for this giveway?", "For how long should the giveaway last?", "How many winners should this giveaway have?"]:
        await ctx.send(r)
        try:
          def is_author(m): return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
          msg = await self.bot.wait_for('message', check=is_author, timeout=15.0)
          messages.append(msg.content)
          await msg.add_reaction("<:catthumbsup:1081227675462533161>")
        except asyncio.TimeoutError: return await ctx.send(content="You didn't reply in time")
      description = messages[0]
      try: seconds = humanfriendly.parse_timespan(messages[1])
      except humanfriendly.InvalidTimespan: return await ctx.send(content="Invalid time parsed")
      try: winners = int(messages[2])
      except ValueError: return await ctx.send(content="Invalid number of winners") 
      embed = discord.Embed(color=self.bot.color, title=description, description=f"Ends: <t:{int((datetime.datetime.now() + datetime.timedelta(seconds=seconds)).timestamp())}:R> (<t:{int((datetime.datetime.now() + datetime.timedelta(seconds=seconds)).timestamp())}:F>)\nHosted by: {ctx.author.mention}\nEntries: **0**\nWinners: **{winners}**")
      await ctx.send(f"Giveaway setup completed! Check {channel.mention}")
      mes = await channel.send(embed=embed, view=GiveawayJoin())
      ts = int((datetime.datetime.now() + datetime.timedelta(seconds=seconds)).timestamp())
      await self.bot.db.execute("INSERT INTO giveaway VALUES ($1,$2,$3,$4,$5,$6,$7,$8)", ctx.guild.id, channel.id, mes.id, winners, json.dumps([]), ts, ctx.author.id, description)
    
async def setup(bot):
    await bot.add_cog(Giveaway(bot))