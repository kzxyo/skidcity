import discord, aiohttp, datetime, random, random, asyncio, traceback
from discord.ext import commands, tasks 
from cogs.events import commandhelp, blacklist
from io import BytesIO
from utils.classes import colors, emojis

class autopost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
  
    @commands.group(invoke_without_command=True) 
    async def autopost(self, ctx):
       pass

    @autopost.command(aliases=["genre"], description="autopfp")
    @blacklist()
    async def genres(self, ctx):
       embed = discord.Embed(color=colors.default, title="autopfp genres", description="autopfp")
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="genres", value="**autopfp**\n> female\n> male\n> anime\n> random\n", inline=False)
       embed.add_field(name="examples", value="> `$autopfp add female #pfps`", inline=False)
       await ctx.reply(embed=embed, mention_author=False) 

    @autopost.command(aliases=["channel"], description="autopfp")
    @blacklist()
    async def channels(self, ctx):
      k = 0
      async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM female WHERE guild_id = {}".format(ctx.guild.id))
        female = await cursor.fetchone()
        await cursor.execute("SELECT * FROM male WHERE guild_id = {}".format(ctx.guild.id))
        male = await cursor.fetchone()
        await cursor.execute("SELECT * FROM anime WHERE guild_id = {}".format(ctx.guild.id))
        anime = await cursor.fetchone()
        await cursor.execute("SELECT * FROM random WHERE guild_id = {}".format(ctx.guild.id))
        random = await cursor.fetchone()        
        await cursor.execute("SELECT * FROM fgifs WHERE guild_id = {}".format(ctx.guild.id))
        fgifs = await cursor.fetchone()        
        await cursor.execute("SELECT * FROM mgifs WHERE guild_id = {}".format(ctx.guild.id))
        mgifs = await cursor.fetchone()        
        await cursor.execute("SELECT * FROM agifs WHERE guild_id = {}".format(ctx.guild.id))
        agifs = await cursor.fetchone()        
        await cursor.execute("SELECT * FROM banner WHERE guild_id = {}".format(ctx.guild.id))
        autobanner = await cursor.fetchone()        
        await cursor.execute("SELECT * FROM automeme WHERE guild_id = {}".format(ctx.guild.id))
        automeme = await cursor.fetchone()        
        await cursor.execute("SELECT * FROM autonsfw WHERE guild_id = {}".format(ctx.guild.id))
        autonsfw = await cursor.fetchone()
        if female is not None:
            female_id = f"<#{female[1]}>"
            k = k +1
        elif female is None:
            female_id = "not set"
        if male is not None:
            male_id = f"<#{male[1]}>"
            k = k +1
        elif male is None:
            male_id = "not set"
        if anime is not None:
            anime_id = f"<#{anime[1]}>"
            k = k +1
        elif anime is None:
            anime_id = "not set"
        if random is not None:
            random_id = f"<#{random[1]}>"
            k = k +1
        elif random is None:
            random_id = "not set"
        if fgifs is not None:
            fgifs_id = f"<#{fgifs[1]}>"
            k = k +1
        elif fgifs is None:
            fgifs_id = "not set"
        if mgifs is not None:
            mgifs_id = f"<#{mgifs[1]}>"
            k = k +1
        elif mgifs is None:
            mgifs_id = "not set"
        if agifs is not None:
            agifs_id = f"<#{agifs[1]}>"
            k = k +1
        elif agifs is None:
            agifs_id = "not set"
        if autobanner is not None:
            autobanner_id = f"<#{autobanner[1]}>"
            k = k +1
        elif autobanner is None:
            autobanner_id = "not set"
        if automeme is not None:
            automeme_id = f"<#{automeme[1]}>"
            k = k +1
        elif automeme is None:
            automeme_id = "not set"
        if autonsfw is not None:
            autonsfw_id = f"<#{autonsfw[1]}>"
            k = k +1
        elif autonsfw is None:
            autonsfw_id = "not set"
        embed = discord.Embed(color=colors.default, title="autopost channels")
        embed.add_field(name="autopfp", value=f"**female** {female_id}\n**male** {male_id}\n**anime** {anime_id}\n**random** {random_id}", inline=False)
        embed.add_field(name="autogif", value=f"**female** {fgifs_id}\n**male** {mgifs_id}\n**anime** {agifs_id}", inline=False)
        embed.add_field(name="extra", value=f"**banners** {autobanner_id}\n**memes** {automeme_id}\n**nsfw** {autonsfw_id}", inline=False)
        embed.set_footer(text=f"{k}/10 channels set", icon_url="https://cdn.discordapp.com/emojis/1043225723739058317.gif?size=96&quality=lossless")
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.reply(embed=embed, mention_author=False) 
        return

    @commands.command(help="adds autopfp module for your server", description="autopfp", brief="> autopfp add [genre] [channel] - adds your autopfp channel\n> autopfp remove [genre] - removes your autopfp channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def autopfp(self, ctx: commands.Context, decide: str=None, genre: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "add" and genre == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "remove" and genre == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "add" and genre == "female" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "male" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "anime" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "random" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autopfp add [genre] [channel]`") 
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} now sending female icons to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autopfp channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autopfp channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} i am already posting female icons for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "female":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM female WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autopfps for female icons isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM female WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} autopfps for female icons removed")
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} now sending male icons to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autopfp channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autopfp channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} i am already posting male icons for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "male":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM male WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autopfps for male icons isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM male WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} autopfps for male icons removed")
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} now sending anime icons to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autopfp channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autopfp channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} i am already posting anime icons for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "anime":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM anime WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autopfps for anime icons isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM anime WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} autopfps for anime icons removed")
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} now sending random icons to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autopfp channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autopfp channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} i am already posting random icons for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "random":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM random WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autopfps for random icons isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM random WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} autopfps for random icons removed")
          await ctx.reply(embed=e, mention_author=False)
          return

    @commands.command(aliases=["autogifs"], help="adds autogif module for your server", description="autopfp", brief="> autogif add [genre] [channel] - adds your autogif channel\n> autopfp remove [genre] - removes your autogif channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def autogif(self, ctx: commands.Context, decide: str=None, genre: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autogif add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "remove" and genre == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autopfp add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return
      if decide == "add" and genre == "female" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autogif add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "male" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autogif add [genre] [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and genre == "anime" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autogif add [genre] [channel]`") 
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} now sending female gifs to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autogif channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autogif channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} i am already posting female gifs for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "female":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM fgifs WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autogifs for female gifs isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM fgifs WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} autogifs for female gifs removed")
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} now sending male gifs to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autogif channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autogif channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} i am already posting male gifs for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "male":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM mgifs WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autogifs for male gifs isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM mgifs WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} autogifs for male gifs removed")
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} now sending anime gifs to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autogif channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autogif channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} i am already posting anime gifs for this server, please remove it to add it to another channel")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove" and genre == "anime":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM agifs WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autogifs for anime gifs isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM agifs WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} autogifs for anime gifs removed")
          await ctx.reply(embed=e, mention_author=False)
          return

    @commands.command(aliases=["autobanners"], help="adds autobanner module for your server", description="autopfp", brief="> autobanner add [channel] - adds your autobanner channel\n> autobanner remove - removes your autobanner channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def autobanner(self, ctx: commands.Context, decide: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autobanner add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False)  
        return 
      if decide == "add" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autobanner add [channel]`") 
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} added autobanner channel to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autobanner channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add autobanner channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autobanner channel is already added, please remove it before adding a new one")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM banner WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autobanner channel isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM banner WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} autobanner channel removed")
          await ctx.reply(embed=e, mention_author=False)
          return

    @commands.command(help="adds automeme module for your server", description="autopfp", brief="> automeme add [channel] - adds your auto meme channel\n> automeme remove - removes your automeme channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def automeme(self, ctx: commands.Context, decide: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: automeme add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False)  
        return 
      if decide == "add" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: automeme add [channel]`") 
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} added automeme channel to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add automeme channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add automeme channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} automeme channel is already added, please remove it before adding a new one")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM automeme WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} automeme channel isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM automeme WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} automeme channel removed")
          await ctx.reply(embed=e, mention_author=False)
          return

    @commands.command(help="adds automeme module for your server", description="autopfp", brief="> automeme add [channel] - adds your auto meme channel\n> automeme remove - removes your automeme channel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist()
    async def autonsfw(self, ctx: commands.Context, decide: str=None, channel: discord.TextChannel=None):
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return 
      if decide == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autonsfw add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      if decide == "add" and channel == None:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} `syntax: autonsfw add [channel]`") 
        await ctx.reply(embed=embed, mention_author=False) 
        return 
      elif decide == "add" and channel != None:
       if channel.is_nsfw() is False:
          e = discord.Embed(color=colors.default, description=F"{emojis.warn} {ctx.author.mention} {channel.mention} is not age restricted")
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
                embe = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} added autonsfw channel to {channel.mention}")
                await ctx.reply(embed=embe, mention_author=False)
                return
             else:
                embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add nsfw channel")
                await ctx.reply(embed=embed, mention_author=False)
            except:
             embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} failed to add nsfw channel")
             await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} nsfw channel is already added, please remove it before adding a new one")
         await ctx.reply(embed=embed, mention_author=False)
         return 
      elif decide == "remove":
       async with self.bot.db.cursor() as cursor:  
        await cursor.execute("SELECT * FROM autonsfw WHERE guild_id = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None: 
         embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} autonsfw channel isn't added")
         await ctx.reply(embed=embed, mention_author=False)
         return  
        elif check is not None:   
          await cursor.execute("DELETE FROM autonsfw WHERE guild_id = {}".format(ctx.guild.id))
          await self.bot.db.commit()
          e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} autonsfw channel removed")
          await ctx.reply(embed=e, mention_author=False)
          return
      
async def setup(bot) -> None:
    await bot.add_cog(autopost(bot))