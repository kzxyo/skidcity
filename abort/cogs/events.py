import discord, datetime 
import asyncio
import time
from discord.ext import commands 
from utils.classes import Colors, Emojis

def seconds_to_dhms(time):
    seconds_to_minute   = 60
    seconds_to_hour     = 60 * seconds_to_minute
    seconds_to_day      = 24 * seconds_to_hour

    days    =   time // seconds_to_day
    time    %=  seconds_to_day

    hours   =   time // seconds_to_hour
    time    %=  seconds_to_hour

    minutes =   time // seconds_to_minute
    time    %=  seconds_to_minute

    seconds = time
    return ("%d days, %d hours, %d minutes, %d seconds" % (days, hours, minutes, seconds))

async def noperms(self, ctx, permission):
    e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: you are missing permission `{permission}`")
    await sendmsg(self, ctx, None, e, None, None, None)

def blacklist(): 
        async def predicate(ctx): 
            if ctx.guild is None:
             return False
            async with ctx.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(ctx.author.id))
                check = await cursor.fetchone()
                if check is not None: 
                   await ctx.reply(embed=discord.Embed(color=Colors.red, description=f"{Emojis.warning} {ctx.author.mention}: ur blacklisted by `ethot#0001 & arturo#0001`, bitchboy. :nerd:"), mention_author=False)
                return check is None
        return commands.check(predicate)   

async def sendmsg(self, ctx, content, embed, view, file, allowed_mentions): 
    if ctx.guild is None: return
    try:
       await ctx.reply(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, mention_author=False)
    except:
        await ctx.send(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions) 

async def commandhelp(self, ctx, cmd):
    prefixes = []
    for l in set(p for p in await self.bot.command_prefix(self.bot, ctx.message)):
      prefixes.append(l)
    try:
       command = self.bot.get_command(cmd)
       if command.usage is None:
        usage = ""
       else:
        usage = command.usage 

       embed = discord.Embed(color=Colors.default, title=command, description=command.help)
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="category", value=command.description)
       if command.brief:
        embed.add_field(name="commands", value=command.brief, inline=False)
       embed.add_field(name="usage", value=f"```{prefixes[0]}{cmd} {usage}```", inline=False)
       embed.add_field(name="aliases", value=', '.join(map(str, command.aliases)) or "none")
       await ctx.reply(embed=embed, mention_author=False)
    except:
       await ctx.reply(f"command `{cmd}` not found", mention_author=False)

async def noperms(self, ctx, permission):
    e = discord.Embed(color=Colors.default, description=f"{emojis.warning} {ctx.author.mention} you are missing permission `{permission}`")
    await sendmsg(self, ctx, None, e, None, None, None)

class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot         

    @commands.Cog.listener()
    async def on_ready(self): 
      online = "<:status_mobile:1046294140863914084>"
      log = self.bot.get_channel(1110172344011464776)
      embed = discord.Embed(color=0xb4baf7, description=f"{online} {self.bot.user.name} is back up! serving `{len(self.bot.guilds)}` servers with about `{len(set(self.bot.get_all_members()))}` members at `{round(self.bot.latency * 1000)}ms`")
      await log.send(embed=embed) 
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
      channel = self.bot.get_channel(1106508097452785734) 
      embed = discord.Embed(color=0xb4baf7, description=f"joined **{guild.name}** (`{guild.id}`) owned by {guild.owner} ({guild.member_count})")
      await channel.send(embed=embed)             

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
      channel = self.bot.get_channel(1106508097452785734) 
      embed = discord.Embed(color=0xb4baf7, description=f"left **{guild.name}** (`{guild.id}`) owned by {guild.owner} ({guild.member_count})")
      await channel.send(embed=embed)        
 
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild: return
        if message.author.bot: return 
        if message.content == f"<@{self.bot.user.id}>":           
            prefixes = []
            for l in set(p for p in await self.bot.command_prefix(self.bot, message)):
             prefixes.append(l)
            await message.reply(content="prefixes: " + " ".join(f"`{g}`" for g in prefixes))
        
        async with self.bot.db.cursor() as cursor: 
          await cursor.execute("SELECT * FROM seen WHERE guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id))
          check = await cursor.fetchone()
          if check is None: 
            await cursor.execute("INSERT INTO seen VALUES (?,?,?)", (message.guild.id, message.author.id, int(datetime.datetime.now().timestamp())))
            await self.bot.db.commit()
          elif check is not None: 
           try: 
            ts = int(datetime.datetime.now().timestamp())
            sql = ("UPDATE seen SET time = ? WHERE guild_id = ? AND user_id = ?")
            val = (ts, message.guild.id, message.author.id)
            await cursor.execute(sql, val)
            await self.bot.db.commit()  
           except Exception as e: print(e)  
          
    @commands.Cog.listener()
    async def on_message_edit(self, before, after): 
        await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): 
       if isinstance(error, commands.CommandNotFound): return
       elif isinstance(error, commands.CheckFailure): return 
       else:   
        try:
         e = discord.Embed(color=Colors.red, description=f"{Emojis.warning} {ctx.author.mention}: {error}")
         await ctx.reply(embed=e, mention_author=False)
        except: 
            pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if guild.member_count < 30:
          for member in guild.members:
            if member.id == guild.owner_id:
             dm_channel = await member.create_dm()
             time.sleep(3)
             await dm_channel.send("i have left your server because it has less than 30 members.")
             await guild.leave()

async def setup(bot):
    await bot.add_cog(Events(bot))             



