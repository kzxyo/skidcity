import discord, aiohttp, datetime, random, random, asyncio, traceback
from discord.ext import commands, tasks 
from cogs.events import commandhelp, blacklist
from io import BytesIO
from utils.classes import Colors, Emojis


class autopost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
  
    @commands.Cog.listener()
    async def on_ready(self):
      async with self.bot.db.cursor() as cursor: 
        await cursor.execute("CREATE TABLE IF NOT EXISTS female (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS male (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS anime (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS banner (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS random (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS fgifs (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS mgifs (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS agifs (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS automeme (guild_id INTEGER, channel_id INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS autonsfw (guild_id INTEGER, channel_id INTEGER)")
      await self.bot.db.commit() 

    @commands.group(invoke_without_command=True) 
    @blacklist()
    async def autopost(self, ctx):
       pass

    @autopost.command(aliases=["genre"], description="anti+")
    @blacklist()
    async def genres(self, ctx):
       embed = discord.Embed(color=Colors.default, title="autopfp genres", description="anti+")
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="genres", value="*autopfp*\n> female\n> male\n> anime\n> random\n**autogif**\n> female\n> male\n> anime", inline=False)
       embed.add_field(name="examples", value="> `$autopfp add female #pfps`\n> `$autogif add female #pfps`", inline=False)
       await ctx.reply(embed=embed, mention_author=False) 

    @autopost.command(aliases=["channel"], description="anti+")
    @blacklist()
    async def channels(self, ctx):
      k = 0
      async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM female WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        channel_id = check[1]
        if check is not None:
          female = f"<#{channel_id}>"
          k += 1
        elif check is None:
          female = f"not set"
          await cursor.execute("SELECT * FROM male WHERE guild_id = {}".format(ctx.guild.id))
          check = await cursor.fetchone()
          channel_id = check[1]
          if check is not None:
            male = f"<#{channel_id}>"
            k += 1
          elif check is None:
            male = f"not set"
            await cursor.execute("SELECT * FROM anime WHERE guild_id = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            channel_id = check[1]
            if check is not None:
              anime = f"<#{channel_id}>"
              k += 1
            elif check is None:
              anime = f"not set"
              await cursor.execute("SELECT * FROM random WHERE guild_id = {}".format(ctx.guild.id))
              check = await cursor.fetchone()
              channel_id = check[1]
              if check is not None:
                random = f"<#{channel_id}>"
                k += 1
              elif check is None:
                random = f"not set"
                await cursor.execute("SELECT * FROM fgifs WHERE guild_id = {}".format(ctx.guild.id))
                check = await cursor.fetchone()
                channel_id = check[1]
                if check is not None:
                  fgifs = f"<#{channel_id}>"
                  k += 1
                elif check is None:
                  fgifs = f"not set"
                  await cursor.execute("SELECT * FROM mgifs WHERE guild_id = {}".format(ctx.guild.id))
                  check = await cursor.fetchone()
                  channel_id = check[1]
                  if check is not None:
                    mgifs = f"<#{channel_id}>"
                    k += 1
                  elif check is None:
                    mgifs = f"not set"
                    await cursor.execute("SELECT * FROM agifs WHERE guild_id = {}".format(ctx.guild.id))
                    check = await cursor.fetchone()
                    channel_id = check[1]
                    if check is not None:
                      agifs = f"<#{channel_id}>"
                      k += 1
                    elif check is None:
                      agifs = f"not set"
                      await cursor.execute("SELECT * FROM banner WHERE guild_id = {}".format(ctx.guild.id))
                      check = await cursor.fetchone()
                      channel_id = check[1]
                      if check is not None:
                        banner = f"<#{channel_id}>"
                        k += 1
                      elif check is None:
                        banner = f"not set"
                        await cursor.execute("SELECT * FROM automeme WHERE guild_id = {}".format(ctx.guild.id))
                        check = await cursor.fetchone()
                        channel_id = check[1]
                        if check is not None:
                          automeme = f"<#{channel_id}>"
                          k += 1
                        elif check is None:
                          automeme = f"not set"
                          await cursor.execute("SELECT * FROM autonsfw WHERE guild_id = {}".format(ctx.guild.id))
                          check = await cursor.fetchone()
                          channel_id = check[1]
                          if check is not None:
                            autonsfw = f"<#{channel_id}>"
                            k += 1
                          elif check is None:
                            autonsfw = f"not set"
                            embed = discord.Embed(color=Colors.default, title="autopost channels")
                            embed.add_field(name="autopfp", value=f"**female** {female}\n**male** {male}\n**anime** {anime}\n**random** {random}", inline=False)
                            embed.add_field(name="autogif", value=f"**female** {fgifs}\n**male** {mgifs}\n**anime** {agifs}", inline=False)
                            embed.add_field(name="autobanner", value=f"{banner}", inline=False)
                            embed.add_field(name="automeme", value=f"{automeme}", inline=False)
                            embed.add_field(name="autonsfw", value=f"{autonsfw}", inline=False)
                            embed.set_footer(text=f"{k}/10 set channels", icon_url="https://cdn.discordapp.com/emojis/1043225723739058317.gif?size=96&quality=lossless")
                            await ctx.reply(embed=embed, mention_author=False) 
                            return

    @commands.command(help="adds autopfp module for your server", description="anti+", brief="> autopfp add [genre] [channel] - adds your autopfp channel\n> autopfp remove [genre] - removes your autopfp channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def autopfp(self, ctx: commands.Context, decide: str=None, genre: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "add" and genre == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "remove" and genre == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "add" and genre == "female" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "male" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "anime" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "random" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      elif decide == "add" and genre == "female" and channel != None:
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM female WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO female VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} now sending female icons to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autopfp channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autopfp channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} i am already posting female icons for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "female":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM female WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autopfps for female icons isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM female WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} autopfps for female icons removed")
          await ctx.reply(embed=e, mention_author=False)
          return
      elif decide == "add" and genre == "male" and channel != None:
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM male WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO male VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} now sending male icons to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autopfp channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autopfp channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} i am already posting male icons for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "male":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM male WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autopfps for male icons isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM male WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} autopfps for male icons removed")
          await ctx.reply(embed=e, mention_author=False)
          return
      elif decide == "add" and genre == "anime" and channel != None:
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM anime WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO anime VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} now sending anime icons to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autopfp channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autopfp channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} i am already posting anime icons for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "anime":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM anime WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autopfps for anime icons isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM anime WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} autopfps for anime icons removed")
          await ctx.reply(embed=e, mention_author=False)
          return
      elif decide == "add" and genre == "random" and channel != None:
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM random WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO random VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} now sending random icons to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autopfp channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autopfp channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} i am already posting random icons for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "random":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM random WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autopfps for random icons isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM random WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} autopfps for random icons removed")
          await ctx.reply(embed=e, mention_author=False)
          return

    @commands.command(aliases=["autogifs"], help="adds autogif module for your server", description="anti+", brief="> autogif add [genre] [channel] - adds your autogif channel\n> autopfp remove [genre] - removes your autogif channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def autogif(self, ctx: commands.Context, decide: str=None, genre: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autogif add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "remove" and genre == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "add" and genre == "female" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autogif add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "male" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autogif add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "anime" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autogif add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      elif decide == "add" and genre == "female" and channel != None:
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM fgifs WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO fgifs VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} now sending female gifs to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autogif channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autogif channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} i am already posting female gifs for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "female":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM fgifs WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autogifs for female gifs isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM fgifs WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} autogifs for female gifs removed")
          await ctx.reply(embed=e, mention_author=False)
          return
      elif decide == "add" and genre == "male" and channel != None:
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM mgifs WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO mgifs VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} now sending male gifs to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autogif channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autogif channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} i am already posting male gifs for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "male":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM mgifs WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autogifs for male gifs isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM mgifs WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} autogifs for male gifs removed")
          await ctx.reply(embed=e, mention_author=False)
          return
      elif decide == "add" and genre == "anime" and channel != None:
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM agifs WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO agifs VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} now sending anime gifs to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autogif channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autogif channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} i am already posting anime gifs for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "anime":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM agifs WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autogifs for anime gifs isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM agifs WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} autogifs for anime gifs removed")
          await ctx.reply(embed=e, mention_author=False)
          return

    @commands.command(aliases=["autobanners"], help="adds autobanner module for your server", description="anti+", brief="> autobanner add [channel] - adds your autobanner channel\n> autobanner remove - removes your autobanner channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def autobanner(self, ctx: commands.Context, decide: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autobanner add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False)  
        return 
      if decide == "add" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autobanner add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      elif decide == "add" and channel != None:
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM banner WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO banner VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} added autobsnner channel to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autobanner channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add autobanner channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autobanner channel is already added, please remove it before adding a new one")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM banner WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autobanner channel isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM banner WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} autobanner channel removed")
          await ctx.reply(embed=e, mention_author=False)
          return

    @commands.command(help="adds automeme module for your server", description="anti+", brief="> automeme add [channel] - adds your auto meme channel\n> automeme remove - removes your automeme channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def automeme(self, ctx: commands.Context, decide: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: automeme add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False)  
        return 
      if decide == "add" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: automeme add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      elif decide == "add" and channel != None:
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM automeme WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO automeme VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} added automeme channel to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add automeme channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add automeme channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} automeme channel is already added, please remove it before adding a new one")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM automeme WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} automeme channel isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM automeme WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} automeme channel removed")
          await ctx.reply(embed=e, mention_author=False)
          return

    @commands.command(help="adds automeme module for your server", description="anti+", brief="> automeme add [channel] - adds your auto meme channel\n> automeme remove - removes your automeme channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def autonsfw(self, ctx: commands.Context, decide: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autonsfw add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and channel == None:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} `syntax: autonsfw add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      elif decide == "add" and channel != None:
       if channel.is_nsfw() is False:
          e = discord.Embed(color=Colors.default, description=F"{Emojis.warning} {ctx.author.mention} {channel.mention} is age restricted")
          await ctx.reply(embed=e, mention_author=False)
          return 
       async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM autonsfw WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
         url = self.bot.user.avatar.url   
         async with aiohttp.ClientSession() as ses: 
           async with ses.get(url) as r:
            try:
             if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await cursor.execute("INSERT INTO autonsfw VALUES (?, ?)", (ctx.guild.id, channel.id))
                await self.bot.db.commit()
                embe = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} added autonsfw channel to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add nsfw channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} failed to add nsfw channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} nsfw channel is already added, please remove it before adding a new one")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM autonsfw WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=Colors.default, description=f"{Emojis.warning} {ctx.author.mention} autonsfw channel isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM autonsfw WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=Colors.default, description=f"{Emojis.check} {ctx.author.mention} autonsfw channel removed")
          await ctx.reply(embed=e, mention_author=False)
          return
      
async def setup(bot) -> None:
    await bot.add_cog(autopost(bot))