from discord.ext import tasks, commands
from discord.ext.commands import check
import discord, datetime
import datetime, arrow, random, json

class task(commands.Cog): 
    def __init__(self, bot: commands.Bot): 
      self.bot = bot 

@tasks.loop(minutes=10)
async def counter_update(bot: commands.Bot): 
  results = await bot.db.fetch("SELECT * FROM counters")
  for result in results: 
   channel = bot.get_channel(int(result["channel_id"]))
   if channel: 
    guild = channel.guild 
    module = result["module"]
    if module == "members": target = str(guild.member_count)
    elif module == "humans": target = str(len([m for m in guild.members if not m.bot]))
    elif module == "bots": target = str(len([m for m in guild.members if m.bot])) 
    elif module == "boosters": target = str(len(guild.premium_subscribers))
    elif module == "voice": target = str(sum(len(c.members) for c in guild.voice_channels))     
    name = result["channel_name"].replace("{target}", target)
    await channel.edit(name=name, reason="updating counter")         

@tasks.loop(hours=6)
async def snipe_delete(bot: commands.Bot):
  await bot.db.execute(f"DELETE FROM snipe")

@tasks.loop(hours=6)
async def edit_snipe_delete(bot: commands.Bot):
  await bot.db.execute(f"DELETE FROM editsnipe")

@tasks.loop(hours=6)
async def reaction_snipe_delete(bot: commands.Bot):
  await bot.db.execute(f"DELETE FROM reactionsnipe")   

@tasks.loop(seconds=5)
async def gw_loop(bot: commands.Bot):
  results = await bot.db.fetch("SELECT * FROM giveaway")
  date = datetime.datetime.now()
  for result in results: 
   if date.timestamp() > result['finish'].timestamp(): await gwend_task(bot, result, date)

async def gwend_task(bot: commands.Bot, result, date: datetime.datetime): 
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
        embed = discord.Embed(color=bot.color, title=message.embeds[0].title, description=f"Hosted by: <@!{result['host']}>\n\nNot enough entries to determine the winners!")
        await message.edit(embed=embed, view=None)
      else:  
       for _ in range(winners): wins.append(random.choice(members))
       embed = discord.Embed(color=bot.color, title=message.embeds[0].title, description=f"Ended <t:{int(date.timestamp())}:R>\nHosted by: <@!{result['host']}>").add_field(name="winners", value='\n'.join([f"**{bot.get_user(w)}** ({w})" for w in wins]))
       await message.edit(embed=embed, view=None)
       await message.reply(f"**{result['title']}** winners:\n" + '\n'.join([f"<@{w}> ({w})" for w in wins])) 
  await bot.db.execute("INSERT INTO gw_ended VALUES ($1,$2,$3)", channel_id, message_id, json.dumps(members))
  await bot.db.execute("DELETE FROM giveaway WHERE channel_id = $1 AND message_id = $2", channel_id, message_id)

def is_there_a_reminder(): 
  async def predicate(ctx: commands.Context):
    check = await ctx.bot.db.fetchrow("SELECT * FROM reminder WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
    if not check: await ctx.warning("You don't have a reminder set in this server")
    return check is not None
  return check(predicate) 

@tasks.loop(seconds=5)
async def reminder_task(bot: commands.Bot): 
  results = await bot.db.fetch("SELECT * FROM reminder")
  for result in results: 
   if datetime.datetime.now().timestamp() > result['date'].timestamp(): 
    channel = bot.get_channel(int(result['channel_id']))
    if channel:
      await channel.send(f"🕰️ <@{result['user_id']}> {result['task']}")
      await bot.db.execute("DELETE FROM reminder WHERE guild_id = $1 AND user_id = $2 AND channel_id = $3", channel.guild.id, result['user_id'], channel.id)   

@tasks.loop(seconds=10)
async def bday_task(bot: commands.Bot): 
  results = await bot.db.fetch("SELECT * FROM birthday") 
  for result in results:
   if arrow.get(result['bday']).day == arrow.utcnow().day and arrow.get(result['bday']).month == arrow.utcnow().month:
    if result['said'] == "false":  
     member = await bot.fetch_user(result['user_id'])
     if member: 
      try: 
        await member.send("🎂 Happy birthday!!")
        await bot.db.execute("UPDATE birthday SET said = $1 WHERE user_id = $2", "true", result['user_id'])
      except: continue   
   else: 
     if result['said'] == "true": await bot.db.execute("UPDATE birthday SET said = $1 WHERE user_id = $2", "false", result['user_id'])

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(task(bot))