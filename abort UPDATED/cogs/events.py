import discord, datetime
import asyncio
import time
from discord.ext import commands 
from datetime import timedelta
from utils.classes import Colors, Emojis

def uptime(self): 
   time = (datetime.datetime.now() - self.time).total_seconds()
   day = time // (24 * 3600)
   time = time % (24 * 3600)
   hour = time // 3600
   time %= 3600
   minutes = time // 60
   time %= 60
   seconds = time 
   result = [f"{int(day)}d", f"{int(hour)}h", f"{int(minutes)}m", f"{int(seconds)}s"]
   return [r for r in result if int(r[0]) > 0]   
async def noperms(self, ctx, permission):
    e = discord.Embed(color=Colors.yellow, description=f"> {Emojis.warning} {ctx.author.mention}: you are missing permission `{permission}`")
    await sendmsg(self, ctx, None, e, None, None, None)

def blacklist(): 
 async def predicate(ctx): 
   if ctx.guild is None:
     return False
   async with ctx.bot.db.cursor() as cursor:
    await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(ctx.author.id))
    check = await cursor.fetchone()
    if check is not None: 
     await ctx.reply(embed=discord.Embed(color=Colors.default, description=f"{ctx.author.mention}: you're blacklisted. [join support](https://discord.gg/abort) to be unblacklisted."), mention_author=False)
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
       await ctx.reply(f"> command `{cmd}` not found", mention_author=False)

class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot          

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM authorize WHERE guild_id = {}".format(guild.id))
        check = await cursor.fetchone()
        if check is None:
            try:
                async for logs in guild.audit_logs(limit=1, after=datetime.datetime.now() - timedelta(seconds=3), action=discord.AuditLogAction.bot_add):
                    toDM = logs.user
                await toDM.send(embed=discord.Embed(color=Colors.default, title="hi there", description=f"your server isn't **authorized** so abort left, to get your server authorised join the [support server](https://discord.gg/abort)"))
                await guild.leave()
            except:
                pass
        channel = self.bot.get_channel(1108881321540988980) 
        embed = discord.Embed(color=Colors.default, description=f"joined **{guild.name}** (`{guild.id}`) owned by {guild.owner} ({guild.member_count})")
        await channel.send(embed=embed)      
       
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
      channel = self.bot.get_channel(1108881321540988980) 
      embed = discord.Embed(color=Colors.default, description=f"left **{guild.name}** (`{guild.id}`) owned by {guild.owner} ({guild.member_count})")
      await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild: return
        if message.author.bot: return 
        if message.content == f"<@{self.bot.user.id}>":           
            prefixes = []
            for l in set(p for p in await self.bot.command_prefix(self.bot, message)):
             prefixes.append(l)
            await message.reply(content=f":shark: my prefix is: " + " ".join(f"(`{g}`)" for g in prefixes), mention_author=False)

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
         e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: {error}")
         await ctx.reply(embed=e, mention_author=False)
        except: 
            pass

async def setup(bot):
    await bot.add_cog(Events(bot))             



