import discord, datetime , re, requests, aiohttp, button_paginator as pg, io
from discord.ext import commands 
from core.utils.classes import Colors, Emojis

session = requests.Session()
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
    e = discord.Embed(color=Colors.green, description=f"<a:b1wave:1074001869250240543> **{ctx.author.mention}:** You are missing permission **{permission}**")
    await sendmsg(self, ctx, None, e, None, None, None)

def blacklist(): 
        async def predicate(ctx): 
            if ctx.guild is None:
             return False
            async with ctx.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(ctx.author.id))
                check = await cursor.fetchone()
                if check is not None: 
                   await ctx.reply(embed=discord.Embed(color=0x2f3136, description=f"{Emojis.Emojis.warninging} {ctx.author.mention}: You are blacklisted. dm marian#0001 for any question about your blacklist"), mention_author=False)
                return check is None
        return commands.check(predicate)   

async def sendmsg(self, ctx, content, embed, view, file, allowed_mentions): 
    if ctx.guild is None: return
    try:
       await ctx.reply(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, mention_author=False)
    except:
        await ctx.send(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions) 

async def commandhelp(self, ctx, cmd):
    prefix = self.bot.command_prefix
    try:
       command = self.bot.get_command(cmd)
       if command.usage is None:
        usage = ""
       else:
        usage = command.usage 

       embed = discord.Embed(color=Colors.green, title=command, description=command.help)
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="category", value=command.description)
       if command.brief:
        embed.add_field(name="commands", value=command.brief, inline=False)
       embed.add_field(name="usage", value=f"```{prefix}{cmd} {usage}```", inline=False)
       embed.add_field(name="aliases", value=', '.join(map(str, command.aliases)) or "none")
       await ctx.reply(embed=embed, mention_author=False)
    except:
       await ctx.reply(f"command `{cmd}` not found", mention_author=False)

class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot    

    @commands.Cog.listener()
    async def on_ready(self): 
      log = self.bot.get_channel(1073901344026529833)
      embed = discord.Embed(color=Colors.green, description=f"**@{self.bot.user.name}** is back up! serving **{len(self.bot.guilds)}** servers at ping : **{round(self.bot.latency * 1000)}**")
      await log.send(embed=embed) 

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
      channel = self.bot.get_channel(1073902243843145818) 
      embed = discord.Embed(color=Colors.green, description=f"joined **{guild.name}** (`{guild.id}`) owned by {guild.owner} ({guild.member_count})")
      await channel.send(embed=embed)             

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
      channel = self.bot.get_channel(1073902243843145818) 
      embed = discord.Embed(color=Colors.green, description=f"left **{guild.name}** (`{guild.id}`) owned by {guild.owner} ({guild.member_count})")
      await channel.send(embed=embed)        
 
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
       if message.content == f"<@{self.bot.user.id}>": 
        await message.reply("My prefix is `,`")  
          
    @commands.Cog.listener()
    async def on_message_edit(self, before, after): 
        await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): 
       if isinstance(error, commands.CommandNotFound): return
       elif isinstance(error, commands.CheckFailure): return 
       else:   
        try:
         e = discord.Embed(color=Colors.green, description=f"**{ctx.author.mention}: {error}**")
         await ctx.reply(embed=e, mention_author=False)
        except: 
            pass

async def setup(bot):
    await bot.add_cog(Events(bot))             



