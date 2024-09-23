from bot.bot import Evict
import os, dotenv, logging
from discord.ext import commands
import discord

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

dotenv.load_dotenv(verbose=True)

token=os.environ['token']

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

bot = Evict()
    
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
 
 embed = discord.Embed(color=bot.color, description="Do you **agree** to our [privacy policy](https://evict.cc/privacy) and for your data to be used for commands?\n**DISAGREEING** will result in a blacklist from using bot's commands")
 yes = discord.ui.Button(emoji=bot.yes, style=discord.ButtonStyle.gray)
 no = discord.ui.Button(emoji=bot.no, style=discord.ButtonStyle.gray)
 
 async def yes_callback(interaction: discord.Interaction): 
    
    channel = bot.get_channel(1258940601458757803)
    
    if interaction.user != ctx.author: return await interaction.response.send_message(embed=discord.Embed(color=bot.color, description=f"{bot.warning} {interaction.user.mention}: This is not your message"), ephemeral=True)
    
    await bot.db.execute("INSERT INTO nodata VALUES ($1,$2)", ctx.author.id, "true")                     
    await interaction.message.delete()
    await bot.process_commands(ctx.message)
    
    embed = discord.Embed(title="Evict Logs", description="User agreed to Evict's privacy policy & terms of service.", color=bot.color)
    embed.add_field(name="User", value=f"{interaction.user}", inline=False)
    embed.add_field(name="User ID", value=f"{interaction.user.id}", inline=False)
    embed.add_field(name="Guild", value=f"{ctx.guild.name}", inline=False)
    embed.add_field(name="Guild ID", value=f"{ctx.guild.id}", inline=False)
    embed.set_thumbnail(url=bot.user.avatar.url)
    await channel.send(embed=embed)

 yes.callback = yes_callback

 async def no_callback(interaction: discord.Interaction):
    
    channel = bot.get_channel(1258940601458757803)
    
    if interaction.user != ctx.author: return await interaction.response.send_message(embed=discord.Embed(color=bot.color, description=f"{bot.warning} {interaction.user.mention}: This is not your message"), ephemeral=True)
    
    await bot.db.execute("INSERT INTO nodata VALUES ($1,$2)", ctx.author.id, "false")                        
    await interaction.response.edit_message(embed=discord.Embed(color=bot.color, description=f"You got blacklisted from using bot's commands. If this is a mistake, please check our [**support server**](https://discord.gg/evict)"), view=None)
    
    embed = discord.Embed(title="Evict Logs", description="User got blacklisted for saying no on callback.", color=bot.color)
    embed.add_field(name="User", value=f"{interaction.user}", inline=False)
    embed.add_field(name="User ID", value=f"{interaction.user.id}", inline=False)
    embed.add_field(name="Guild", value=f"{ctx.guild.name}", inline=False)
    embed.add_field(name="Guild ID", value=f"{ctx.guild.id}", inline=False)
    embed.set_thumbnail(url=bot.user.avatar.url)
    await channel.send("<@214753146512080907>")
    await channel.send(embed=embed)
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
  if check: await ctx.warning(f"The command **{cmd.name}** is **disabled**")     
  return check is None    

@bot.check
async def restricted_command(ctx: commands.Context):
  
  if ctx.author.id == ctx.guild.owner.id: return True
  if ctx.author.id in bot.owner_ids: return True

  if check := await ctx.bot.db.fetch("SELECT * FROM restrictcommand WHERE guild_id = $1 AND command = $2",ctx.guild.id, ctx.command.qualified_name):
    for row in check:
      role = ctx.guild.get_role(row["role_id"])
      if not role:
        await ctx.bot.db.execute("DELETE FROM restrictcommand WHERE role_id = $1", row["role_id"])
      if not role in ctx.author.roles:
        await ctx.warning(f"You cannot use `{ctx.command.qualified_name}`")
        return False
      return True
  return True
  
if __name__ == '__main__':
  bot.run(token, reconnect=True)