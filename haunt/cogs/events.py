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
                   await ctx.reply("nope.", mention_author=False)
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

class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot          
    
    @commands.Cog.listener()
    async def on_ready(self):
      online = "<:icons_goodping:1106138130081386527>"
      embed = discord.Embed(color=Colors.default, title="<a:whiteloading:1103721417322790952> **restarted**", description=f"> {online} abort is back online")
      on_ready = bot.get_channel(1107120847036092467)
      await on_ready.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
      channel = self.bot.get_channel(1104265807065788466) 
      embed = discord.Embed(color=Colors.default, description=f"joined **{guild.name}** (`{guild.id}`) owned by {guild.owner} ({guild.member_count})")
      await channel.send(embed=embed)             

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
      channel = self.bot.get_channel(1104265807065788466) 
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
            await message.reply(content=f"<:info:1108885085916246026> prefix is  " + " ".join(f"(`{g}`)" for g in prefixes), mention_author=False)

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

    @commands.Cog.listener()
    async def on_ready(self): 
      message = self.bot.get_channel(1107561338143785041)
      embed = discord.Embed(color=Colors.default, title=f"**cogs:**")
      embed = discord.Embed(color=Colors.default, title=f"**cogs:**", description=f"> took `{round(self.bot.latency * 1000)}ms` to load")
      embed.set_footer(text="connected to discord API as: haunt#8429")      
      await message.send(embed=embed)  


    @commands.Cog.listener()
    async def on_ready(self): 
      online = "<:icons_goodping:1106138130081386527>"
      message = self.bot.get_channel(1107120847036092467)
      embed = discord.Embed(color=Colors.default, title=f"<a:whiteloading:1103721417322790952> **restarted**", description=f"> {online} haunt is back online")
      embed.set_footer(text="connected to discord API as: haunt#8429")    
      await message.send(embed=embed) 

@commands.Cog.listener()
async def on_member_join(member):
	channel = client.get_channel(1106000731724595290)
	embed = discord.Embed(title= f"Welcome to **{member.guild.name}**", description= f"Welcome to /abort! {member.mention}! Hope you enjoy our community!", color=Colors.default)
	embed.set_footer(text = "/abort")
	embed.set_thumbnail(url = member.avatar_url)
	await channel.send(embed = embed)

@commands.Cog.listener()
async def on_member_remove(member):
    channel = client.get_channel(1104430991830945945)
    embed=discord.Embed(title="Goodbye!", description=f"{member.mention} just left the {member.guild.name}, hope to see you again, {member.display_name}!", color=Colors.default)
    embed.set_thumbnail(url = member.avatar_url)
    embed.set_footer(text = "/abort")
    await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Events(bot))             


