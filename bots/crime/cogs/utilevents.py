import discord, datetime, io, requests, aiohttp ; from discord import Embed ; from discord.ext import commands ; from bs4 import BeautifulSoup

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
    e = discord.Embed(color=0x2f3136, description=f"> you are missing permission `{permission}`")
    await sendmsg(self, ctx, None, e, None, None, None)

def blacklist(): 
        async def predicate(ctx): 
            if ctx.guild is None:
             return False
            async with ctx.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(ctx.author.id))
                check = await cursor.fetchone()
                if check is not None: 
                   await ctx.reply(embed=discord.Embed(color=0x2f3136, description=f"{ctx.author.mention}: You are blacklisted, dm xano#0001 for any question about your blacklist."), mention_author=False)
                return check is None
        return commands.check(predicate) 

async def sendmsg(self, ctx, content, embed, view, file, allowed_mentions): 
    if ctx.guild is None: return
    try:
       await ctx.reply(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, mention_author=False)
    except:
        await ctx.send(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions) 

async def accept(self, ctx, content, embed, view, file, allowed_mentions): 
    if ctx.guild is None: return
    try:
       await ctx.reply(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, mention_author=False)
    except:
        await ctx.send(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions) 

async def commandhelp(self, ctx, cmd):
    try:
       command = self.bot.get_command(cmd)
       if command.usage is None:
        usage = ""
       else:
        usage = command.usage 
       embed = discord.Embed(color=0x2f3136, title=command, description=command.help)
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="category", value=command.description)
       if command.brief:
        embed.add_field(name="commands", value=command.brief, inline=False)
       embed.add_field(name="usage", value=f"```,{cmd} {usage}```", inline=False)
       embed.set_footer(text=f"aliases: ', '".join(map(str, command.aliases)) or "none")
       embed.set_thumbnail(url=self.bot.user.display_avatar.url)
       await ctx.reply(embed=embed, mention_author=False)
    except:
       await ctx.reply(f"command `{cmd}` not found", mention_author=False)

class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild: return
        if message.author.bot: return 
        if message.content == f"<@{self.bot.user.id}>":           
            prefixes = []
            for l in set(p for p in await self.bot.command_prefix(self.bot, message)):
             prefixes.append(l)
             e = Embed(
                description="prefixes: " + " ".join(f"`{g}`" for g in prefixes),
                color=0x2f3136
             )
            await message.reply(embed=e, mention_author=False)
        
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
    async def on_message(self, message: discord.Message):
      if not message.guild: return  
      if message.author.bot: return
      try:
        msg = message.content.lower()
        if msg.startswith(f"{self.bot.user.name}"):
          await message.channel.typing()
          prompt = msg.strip(f"hey {self.bot.user.name}")
          async with aiohttp.ClientSession() as tiktok:
            async with tiktok.get("https://tikwm.com/api?url={}".format(prompt)) as x:
              f = await x.json()
              video = f["data"] 
              video_bytes = video["play"] 
              requestss = requests.get(video_bytes).content
              await message.reply(file = discord.File(io.BytesIO(requestss), f"{self.bot.user.name}tok.mp4"), mention_author=False)
      except:
        return await message.reply("there was a error while reposing this video")
      
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): 
       if isinstance(error, commands.CommandNotFound): return
       elif isinstance(error, commands.CheckFailure): return 
       else:   
        try:
         e = discord.Embed(color=0x2f3136, description=f"{ctx.author.mention}: {error}")
         await ctx.reply(embed=e, mention_author=False)
        except: 
            pass


    @commands.Cog.listener()
    async def on_ready(self): 
      async with self.bot.db.cursor() as cursor: 
        await cursor.execute("CREATE TABLE IF NOT EXISTS setme (channel_id INTEGER, role_id INTEGER, guild_id INTEGER)") 
        await cursor.execute("CREATE TABLE IF NOT EXISTS jail (guild_id INTEGER, user_id INTEGER, roles TEXT)") 
      await self.bot.db.commit()  
    


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member): 
     async with self.bot.db.cursor() as cursor:
       await cursor.execute("SELECT * FROM jail WHERE guild_id = {} AND user_id = {}".format(member.guild.id, member.id))
       check = await cursor.fetchone()
       if check is not None: 
         await cursor.execute("SELECT * FROM setme WHERE guild_id = {}".format(member.guild.id))
         chec = await cursor.fetchone()
         if chec is not None: 
          try:
           await member.add_roles(member.guild.get_role(int(chec[1])))   
          except:
            pass 
          

    @commands.Cog.listener()
    async def on_message(self, message):
            try:
                    if "tiktok.com/" in message.content:
                        link = [i for i in message.content.split() if 'tiktok.com/' in i][0]
                        async with aiohttp.ClientSession() as cs:
                            async with cs.get(f"https://tikwm.com/api?url={link}") as e:
                                x = await e.json()
                                video = x['data']
                                play = video['play']
                                r = requests.get(play).content
                                await message.channel.send(file = discord.File(io.BytesIO(r), "crimetiktok.mp4"))

            except KeyError:
                print(KeyError)
  
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if "youtube.com/" in message.content:
                link = [i for i in message.content.split() if 'youtube.com/' in i][0]
                if "<iframe" in message.content:
                    html = [i for i in message.content.split() if '<iframe' in i][0]
                    soup = BeautifulSoup(html, 'html.parser')
                    video_src = soup.iframe['src']
                    video_url = video_src.split('?')[0]
                    async with aiohttp.ClientSession() as session:
                        async with session.get(video_url) as resp:
                            if resp.status != 200:
                                return await message.channel.send('Could not download file...')
                            data = io.BytesIO(await resp.read())
                            await message.channel.send(file=discord.File(data, filename='crimevideo.mp4'))
                else:
                    async with aiohttp.ClientSession() as cs:
                        async with cs.get(f"https://www.youtube.com/oembed?url={link}&format=json") as e:
                            x = await e.json()
                            html = x['html']
                            soup = BeautifulSoup(html, 'html.parser')
                            video_src = soup.iframe['src']
                            video_url = video_src.split('?')[0]
                            async with aiohttp.ClientSession() as session:
                                async with session.get(video_url) as resp:
                                    if resp.status != 200:
                                        return await message.channel.send('Could not download file...')
                                    data = io.BytesIO(await resp.read())
                                    await message.channel.send(file=discord.File(data, filename='crimevideo.mp4'))
        except KeyError:
            print(KeyError)
async def setup(bot):
    await bot.add_cog(Events(bot))             



