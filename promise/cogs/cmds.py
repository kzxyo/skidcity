import discord, time, datetime, psutil, random, os, requests, aiohttp , asyncio, humanfriendly
from discord.ext import commands
from discord.ext.commands import Cog, command, Context, cooldown, BucketType
from bs4 import BeautifulSoup
import button_paginator as pg
from discord import Embed, File, TextChannel, Member, User, Role, Status, Message, Spotify, Message, AllowedMentions
from cogs.events import commandhelp, sendmsg, noperms
from core.utils.classes import Colors, Emojis, Func
from random import choice as randchoice
from random import randint
from typing import Union
from discord.ui import View, Button, Select

global start
session = requests.Session()
DISCORD_API_LINK = "https://discord.com/api/invite/"

class BlackTea: 
    """BlackTea backend variables"""
    MatchStart = {}
    lifes = {}
    
    async def get_string(): 
      lis = await BlackTea.get_words()
      word = random.choice(lis)
      return word[:3]

    async def get_words(): 
      async with aiohttp.ClientSession() as cs: 
       async with cs.get("https://www.mit.edu/~ecprice/wordlist.10000") as r: 
        byte = await r.read()
        data = str(byte, 'utf-8')
        return data.splitlines()

class cmds(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @Cog.listener()
    async def on_ready(self):
     async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS oldusernames (username TEXT, discriminator TEXT, time INTEGER, user INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS selfprefix (pref TEXT, user_id INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS snipe (guild_id INTEGER, channel_id INTEGER, author TEXT, content TEXT, attachment TEXT, avatar TEXT)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS seen (guild_id INTEGER, user_id INTEGER, time INTEGER);")
            await cursor.execute("CREATE TABLE IF NOT EXISTS afk (guild_id INTEGER, user_id INTEGER, reason TEXT, time INTEGER);")
            await cursor.execute("CREATE TABLE IF NOT EXISTS selfprefix (pref TEXT, user_id INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id INTEGER, prefix TEXT);") 
     await self.bot.db.commit()
    
    @Cog.listener()
    async def on_message(self, message: Message):
     if not message.guild: return 
     if message.author.bot: return
     if message.mentions: 
       async with self.bot.db.cursor() as cursor:
        for mem in message.mentions:
         await cursor.execute("SELECT * from afk where guild_id = {} AND user_id = {}".format(message.guild.id, mem.id)) 
         check = await cursor.fetchone()
         if check is not None:
          em = Embed(color=Colors.default, description=f"{mem.mention} is AFK about <t:{int(check[3])}:R> - **{check[2]}**")
          await sendmsg(self, message, None, em, None, None, None)

     async with self.bot.db.cursor() as curs:
        await curs.execute("SELECT * from afk where guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id)) 
        check = await curs.fetchone()
        if check is not None:
         embed = Embed(color=Colors.default, description=f"{message.author.mention} You was afk since <t:{int(check[3])}:R>, Welcome Back!")
         await sendmsg(self, message, None, embed, None, None, None)
         await curs.execute("DELETE FROM afk WHERE guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id))
     await self.bot.db.commit()
    
    @Cog.listener()
    async def on_user_update(self, before, after):
     try:
      if before.name == after.name: return
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("INSERT INTO oldusernames (username, discriminator, time, user) VALUES (?, ?, ?, ?)", (before.name, before.discriminator, int(datetime.datetime.now().timestamp()), before.id,))
        await self.bot.db.commit()
     except:
        pass
    
    @command(help="play blacktea with your friends", description="fun")
    @cooldown(1, 20, BucketType.guild)
    async def blacktea(self, ctx: Context): 
     try:
      if BlackTea.MatchStart[ctx.guild.id] is True: 
       return await ctx.reply("somebody in this server is already playing blacktea", mention_author=False)
     except KeyError: pass 

     BlackTea.MatchStart[ctx.guild.id] = True 
     embed = Embed(color=Colors.default, title="BlackTea Matchmaking", description=f"⏰ Waiting for players to join. To join react with 🍵.\nThe game will begin in **10 seconds**")
     embed.add_field(name="goal", value="You have **10 seconds** to say a word containing the given group of **3 letters.**\nIf failed to do so, you will lose a life. Each player has **2 lifes**")
     embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)  
     mes = await ctx.send(embed=embed)
     await mes.add_reaction("🍵")
     await asyncio.sleep(10)
     me = await ctx.channel.fetch_message(mes.id)
     players = [user.id async for user in me.reactions[0].users()]
     players.remove(self.bot.user.id)

     if len(players) < 2:
      BlackTea.MatchStart[ctx.guild.id] = False
      return await ctx.send("{}, not enough players joined to start blacktea".format(ctx.author.mention), allowed_mentions=AllowedMentions(users=True)) 
  
     while len(players) > 1: 
      for player in players: 
       strin = await BlackTea.get_string()
       await ctx.send(f"<@{player}>, type a word containing **{strin.upper()}** in **10 seconds**", allowed_mentions=AllowedMentions(users=True))
      
       def is_correct(msg): 
        return msg.author.id == player
      
       try: 
        message = await self.bot.wait_for('message', timeout=10, check=is_correct)
       except asyncio.TimeoutError: 
          try: 
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
            if BlackTea.lifes[player] == 3: 
              await ctx.send(f" <@{player}>, you're eliminated ", allowed_mentions=AllowedMentions(users=True))
              BlackTea.lifes[player] = 0
              players.remove(player)
              continue 
          except KeyError:  
            BlackTea.lifes[player] = 0   
          await ctx.send(f"<@{player}>, you didn't reply on time! **{2-BlackTea.lifes[player]}** lifes remaining", allowed_mentions=AllowedMentions(users=True))    
          continue
       if not strin.lower() in message.content.lower() or not message.content.lower() in await BlackTea.get_words():
          try: 
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
            if BlackTea.lifes[player] == 3: 
              await ctx.send(f" <@{player}>, you're eliminated ", allowed_mentions=AllowedMentions(users=True))
              BlackTea.lifes[player] = 0
              players.remove(player)
              continue 
          except KeyError:  
            BlackTea.lifes[player] = 0 
          await ctx.send(f"<@{player}>, incorrect word! **{2-BlackTea.lifes[player]}** lifes remaining", allowed_mentions=AllowedMentions(users=True))
       else: await message.add_reaction("<:cheac:1058649808644083762>")  
          
     await ctx.send(f"<:owner:1058649581551890452> <@{players[0]}> won the game!", allowed_mentions=AllowedMentions(users=True))
     BlackTea.lifes[players[0]] = 0
     BlackTea.MatchStart[ctx.guild.id] = False
    
    @command(aliases = ['names', 'usernames'], help="check an user's past usernames", usage="<user>", description="utility")
    @cooldown(1, 4, BucketType.user)
    async def pastusernames(self, ctx, member: User = None):
        try:
            if member == None:
                member = ctx.author
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT username, discriminator, time FROM oldusernames WHERE user = ?", (member.id,))
                data = await cursor.fetchall()
                i=0
                k=1
                l=0
                number = []
                messages = []
                num = 0
                auto = ""
                if data:
                    for table in data:
                        username = table[0]
                        discrim = table[1]
                        num += 1
                        auto += f"\n`{num}` {username}#{discrim}: <t:{int(table[2])}:R> "
                        k+=1
                        l+=1
                        if l == 10:
                          messages.append(auto)
                          number.append(Embed(color=Colors.default).set_author(name = f"{member}'s past usernames", icon_url = member.display_avatar))
                          i+=1
                          auto = ""
                          l=0
                    messages.append(auto)
                    embed = Embed(description = auto, color=Colors.green)
                    embed.set_author(name = f"Old {member} name's : ", icon_url = member.display_avatar)
                    number.append(embed)
                    if len(number) > 1:
                     paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
                     paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
                     paginator.add_button('goto', emoji = "📜")
                     paginator.add_button('next', emoji="<:right:1018156484170883154>")
                     await paginator.start()  
                    else:
                      await sendmsg(self, ctx, None, embed, None, None, None)      
                else:
                    await sendmsg(self, ctx, f"no logged usernames for {member}", None, None, None, None)
        except Exception as e:
            print(e)
    
    @commands.command(aliases=['8ball', '8b'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def question(self, ctx, *, question):

        responses = ["definitely", "maybe","yes", "no", "as i see it, yes", "factual", "as i see it, no", "idk", "Ok", "Due to your nationality being Bosnian, I cannot answer the question you just asked me.", "🤓", "hell no" , "FRRR"]
        embed = discord.Embed(color=Colors.green)
        embed.add_field(name = "Question", value = f"{question}")
        embed.add_field(name = "Answer", value = f"{random.choice(responses)}")
        await ctx.reply(embed=embed)
    
    @command(help="let everyone know you are away", description="utility", usage="<reason>")
    @cooldown(1, 4, BucketType.user)
    async def afk(self, ctx: Context, *, reason=None):
      if reason is None: 
        reason = "AFK"
      
      ts = int(datetime.datetime.now().timestamp())   
      async with self.bot.db.cursor() as cursor:
       await cursor.execute("SELECT * FROM afk WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
       result = await cursor.fetchone() 
       if result is None:
        sql =  ("INSERT INTO afk VALUES(?,?,?,?)")
        val = (ctx.guild.id, ctx.author.id, reason, ts)
        await cursor.execute(sql, val)
        await self.bot.db.commit()
        embed = Embed(color=Colors.default, description=f"{ctx.author.mention}: You set your afk status to : **{reason}**")
        await sendmsg(self, ctx, None, embed, None, None, None)
    
    @command(help="show server information", aliases=["si", "serverinfo", "guild"], description="utility", usage="server info")
    @cooldown(1, 4, BucketType.user)
    async def server(self, ctx: Context, choice=None, *, id: int=None):
      if choice == "info" or choice is None:
        if id is None:
           guild = ctx.guild
        else:
            guild = self.bot.get_guild(id)
        
        if guild is None:
            e = Embed(color=Colors.green, description=f"{ctx.author.mention}: unable to find this guild")
            await sendmsg(self, ctx, None, e, None, None, None)
            return 

        i=0
        j=0
        icon=""
        splash=""
        banner=""  
        if guild.icon is not None:
         icon = f"[icon]({guild.icon.url})"
        else:
         icon = "this server has no icon"

        if guild.splash is not None:
         splash = f"[splash]({guild.splash.url})"
        else:
         splash = "this server has no splash"

        if guild.banner is not None:
         banner = f"[banner]({guild.banner.url})"
        else:
         banner = "this server has no banner"

        for member in guild.members:  
         if member.bot:
            j+=1
         else:
            i+=1 
        if guild.description is None:
            desc = ""
        else:
            desc = guild.description 
        
        if guild.premium_subscriber_role is None:
            b = 0
        else:
            b = len(guild.premium_subscriber_role.members) 

        embed = Embed(color=Colors.green, description=f"**This server was created on <t:{int(guild.created_at.timestamp())}:F> <t:{int(guild.created_at.timestamp())}:R>**\n‎")   
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="owner", value=f"‎ {guild.owner}\n‎ {guild.name}")
        embed.add_field(name=f"channels({len(ctx.guild.channels)})", value=f"**‎ text:** {len(guild.text_channels)}\n**‎ voice:** {len(guild.voice_channels)}\n**‎ categories:** {len(guild.categories)}")
        embed.add_field(name="members", value=f"**‎ users:** {i} ({(i/guild.member_count) * 100:.2f}%)\n**‎ bots:** {j} ({(j/guild.member_count) * 100:.2f}%)\n**‎ total:** {guild.member_count}")
        embed.add_field(name="**vanity:**", value=f"‎ {guild.vanity_url_code}")
        await sendmsg(self, ctx, None, embed, None, None, None)
        
    @command(aliases=["tr"], help="translate every word you want to translate!", description="utility", usage="[language] [word]")
    @cooldown(1, 4, BucketType.user)
    async def translate(self, ctx: Context, lang=None, *, query=None):
     if lang == None or query == None:
        await commandhelp(self, ctx, ctx.command.name)
        return
     else:
      word = query.replace(" ", "+")
      async with aiohttp.ClientSession() as cs: 
       async with cs.get(f"https://api.popcat.xyz/translate?to={lang}&text={word}") as r:
        re = await r.json()

      text = re["translated"]
      embed = Embed(color=Colors.green, title=f"Your word/s was translated in {lang}", description=text)
      await sendmsg(self, ctx, None, embed, None, None, None)
       
    @commands.command(help="shows a tiktok video by the link", usage="[video from tiktok]", description="promise")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tiktok(self, ctx):
     embed = discord.Embed(color=Colors.green, title=f"tiktok", description="shows a tiktok video from link, command works only without prefix")
     embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
     embed.add_field(name="category", value=f"utility")
     embed.add_field(name="usage", value=f"```tiktok [tiktok video link]```", inline=False)
     embed.add_field(name="aliases", value="none")
     await ctx.reply(embed=embed, mention_author=False)
        
    @commands.command(aliases=["sm"], help="add slowmode to a channel", description="moderation", usage="<channel>")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def slowmode(self, ctx, seconds: int=None, channel: discord.TextChannel=None):
     if (not ctx.author.guild_permissions.manage_channels):
      await noperms(self, ctx, "manage_channels")
      return 

     chan = channel or ctx.channel
     await chan.edit(slowmode_delay=seconds)
     em = discord.Embed(color=Colors.green, description=f"{ctx.author.mention} was setting slowtime on {chan.mention} to **{seconds} seconds**")
     await sendmsg(self, ctx, None, em, None, None, None)
        
    @commands.command(aliases=["webshoty", "ws"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def webshot(self, ctx, *, link:str = None) -> None:
      if link == None:
          em = discord.Embed(color=Colors.green,description=f"Please provide a `link`")
          await ctx.send(embed=em)
          return
      links = ["https://", "http://"]
      if not (link.startswith(tuple(links))):
          await ctx.send(embed=discord.Embed(color=Colors.green, description=f"You didn't input https before the link provided"))
          return
      else:
          n = discord.Embed(description=f"`{link.replace('https://', '').replace('http://', '')}`", color=Colors.green)
          n.set_image(url='https://api.popcat.xyz/screenshot?url=' + str(link.replace("http://", "https://")))
          await ctx.reply(embed=n, mention_author=False)
        
    @commands.command(name="boosters", description="Shows the boosters in the server", usage="boosters")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def boosters(self, ctx):
        embeds = []
        boosters = [m for m in ctx.guild.members if m.premium_since]
        boosters = sorted(boosters, key=lambda m: m.joined_at, reverse=True)
        if len(boosters) == 0:
            embed = discord.Embed(
                color=Colors.green,
                description=f"{ctx.guild.name} its not boosted yet"
            )
            return await ctx.send(embed=embed)
        maxpages = 0
        boosterscount = 0
        pagenum = 0
        for i in range(0, len(boosters), 10): maxpages += 1
        for i in range(0, len(boosters), 10):
            pagenum += 1
            embed = discord.Embed(
                color=Colors.green
            )
            boosterslist = ""
            for booster in boosters[i:i + 10]:
                boosterscount += 1
                boosterslist += f"`{boosterscount}` {booster.mention} - <t:{int(booster.premium_since.timestamp())}:R>\n"
            embed.description = boosterslist
            embed.set_footer(text=f"Page {pagenum}/{maxpages} | {len(boosters)} boosters")
            embeds.append(embed)
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji='<:leftt:1058649217893146684>')
            paginator.add_button('delete', emoji='<:stip:1058649399175151686>')
            paginator.add_button('next', emoji='<:rigt:1058649293050888192>')
            await paginator.start()
        
    @commands.command(help="Stop Users To Send Messages To The Channel", description="moderation", usage="<channel>")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def lock(self, ctx, channel : discord.TextChannel=None):
     if (not ctx.author.guild_permissions.manage_roles):
      await noperms(self, ctx, "manage_roles")
      return 
     channel = channel or ctx.channel
     overwrite = channel.overwrites_for(ctx.guild.default_role)
     overwrite.send_messages = False
     await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
     e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: locked {channel.mention}")
     await sendmsg(self, ctx, None, e, None, None, None)

    @commands.command(help="Allow Users To Send Messages To The Channel", description="moderation", usage="<channel>")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def unlock(self, ctx, channel : discord.TextChannel=None):
     if (not ctx.author.guild_permissions.manage_roles):
      await noperms(self, ctx, "manage_roles")
      return 

     channel = channel or ctx.channel
     overwrite = channel.overwrites_for(ctx.guild.default_role)
     overwrite.send_messages = True
     await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
     e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: unlocked {channel.mention}")
     await sendmsg(self, ctx, None, e, None, None, None)
 
    @commands.command(help="untimeout a user", usage="[member]", description="moderation")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def untimeout(self, ctx, member: discord.Member=None):
     if (not ctx.author.guild_permissions.moderate_members):
      await noperms(self, ctx, "timeout_members")
      return     
     try: 
      if member == None:
        await commandhelp(self, ctx, ctx.command.name) 
        return

      await member.timeout(None, reason=f'unmuted by {ctx.author}')
      e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention} unmuted {member.mention}")
      await sendmsg(self, ctx, None, e, None, None, None)
     except:
       emb = discord.Embed(color=Colors.green, description=f" {ctx.author.mention}: i can't unmute this member")  
       await sendmsg(self, ctx, None, emb, None, None, None) 
        
    @commands.command(help="Give a role to the member", description="moderation", usage="[member] [role]")
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def role(self, ctx, user : discord.Member=None, *, role : discord.Role=None):
     if (not ctx.author.guild_permissions.manage_roles):
      await noperms(self, ctx, "manage_roles")
      return
  
     if role == None or user == None:
        await commandhelp(self, ctx, ctx.command.name)
        return 

     if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner.id: 
      e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: that role is above your top role")  
      return await sendmsg(self, ctx, None, e, None, None, None)
     if role in user.roles:
       await user.remove_roles(role)
       embed = discord.Embed(color=Colors.green, description=f"**{ctx.author.mention}** you remove {role.mention} from **{user.mention}**") 
       await sendmsg(self, ctx, None, embed, None, None, None)
     else:
       await user.add_roles(role)
       emb = discord.Embed(color=Colors.green, description=f"**{ctx.author.mention}** you give {role.mention} to the {user.mention}") 
       await sendmsg(self, ctx, None, emb, None, None, None)
    
    @commands.command(help="see all server roles", description="utility")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def roles(self, ctx: Context):
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for role in ctx.guild.roles: 
              mes = f"{mes}`{k}` {role.mention} - <t:{int(role.created_at.timestamp())}:R> ({len(role.members)} members)\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=Colors.default, title=f"There are : {len(ctx.guild.roles)} roles in {ctx.guild.name}", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = discord.Embed(color=Colors.green, title=f"There are : {len(ctx.guild.roles)} roles in {ctx.guild.name}", description=messages[i])
            number.append(embed)
            if len(number) > 1:
             paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
             paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
             paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
             paginator.add_button('next', emoji="<:right:1018156484170883154>")
             await paginator.start() 
            else:
              await sendmsg(self, ctx, None, embed, None, None, None)
        
    @commands.command(help="Get the banner from a server based by invite code", description="utility", usage="[invite code]")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def sbanner(self, ctx, *, link=None):
     if link == None:
      await commandhelp(self, ctx, ctx.command.name)
      return  

     invite_code = link
     async with aiohttp.ClientSession() as cs:
      async with cs.get(DISCORD_API_LINK + invite_code) as r:
       data = await r.json()

     try: 
      format = ""
      if "a_" in data["guild"]["banner"]:
        format = ".gif"
      else:
        format = ".png"

      embed = discord.Embed(color=Colors.green, title=data["guild"]["name"] + "'s banner")
      embed.set_image(url="https://cdn.discordapp.com/banners/" + data["guild"]["id"] + "/" + data["guild"]["banner"] + f"{format}?size=1024")
      await sendmsg(self, ctx, None, embed, None, None, None)
     except:
      e = discord.Embed(color=Colors.green, description=f"**{ctx.author.mention}**: Couldn't get **" + data["guild"]["name"] + "'s** banner")
      await sendmsg(self, ctx, None, e, None, None, None)
        
    @commands.command(help="Get the splash from a server based by invite code", description="utility", usage="[invite code]")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def splash(self, ctx, *, link=None):
     if link == None:
      await commandhelp(self, ctx, ctx.command.name)
      return

     try: 
      invite_code = link
      async with aiohttp.ClientSession() as cs:
       async with cs.get(DISCORD_API_LINK + invite_code) as r:
        data = await r.json()

      embed = discord.Embed(color=Colors.green, title=data["guild"]["name"] + "'s splash")
      embed.set_image(url="https://cdn.discordapp.com/splashes/" + data["guild"]["id"] + "/" + data["guild"]["splash"] + ".png?size=1024")
      await sendmsg(self, ctx, None, embed, None, None, None)
     except:
      e = discord.Embed(color=Colors.green, description=f"**{ctx.author.mention}**: Couldn't get **" + data["guild"]["name"] + "'s** splash image")
      await sendmsg(self, ctx, None, e, None, None, None)
        
    @commands.command(help="Get the icon from a server based by invite code", description="utility", usage="[invite code]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sicon(self, ctx, *, link=None):
     if link == None:
      await commandhelp(self, ctx, ctx.command.name)
      return 

     invite_code = link
     async with aiohttp.ClientSession() as cs:
      async with cs.get(DISCORD_API_LINK + invite_code) as r:
       data = await r.json()

     try: 
      format = ""
      if "a_" in data["guild"]["icon"]:
        format = ".gif"
      else:
        format = ".png"
          
      embed = discord.Embed(color=Colors.green, title=data["guild"]["name"] + "'s icon")
      embed.set_image(url="https://cdn.discordapp.com/icons/" + data["guild"]["id"] + "/" + data["guild"]["icon"] + f"{format}?size=1024")
      await sendmsg(self, ctx, None, embed, None, None, None)
     except:
      e = discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: Couldn't get **" + data["guild"]["name"] + "'s** icon")
      await sendmsg(self, ctx, None, e, None, None, None)
        
    @commands.command(aliases=["av"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def avatar(self,
                     ctx: commands.Context,
                     *,
                     member: discord.Member = None):
        if member is None:
            member = ctx.author

        embed = discord.Embed(color=Colors.green,
                              title=f"{member.name}'s avatar",
                              url=member.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def banner(self,
                     ctx: commands.Context,
                     *,
                     member: discord.Member = None):
        if member == None:
            member = ctx.author

        user = await self.bot.fetch_user(member.id)
        if user.banner == None:
            em = discord.Embed(
                color=Colors.green,
                description=
                f"**{member.mention}** doesn't have a banner"
            )
            await ctx.reply(embed=em, mention_author=False)
        else:
            banner_url = user.banner.url
            e = discord.Embed(color=Colors.green,
                              title=f"{member.name}'s banner",
                              url=user.banner.url)
            e.set_image(url=banner_url)
            await ctx.reply(embed=e, mention_author=False)

    @banner.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            e = discord.Embed(color=Colors.green,
                              description=f"{ctx.author.mention} {error}")
            await ctx.reply(embed=e, mention_author=False)
        
    @commands.command(aliases=["ub"], name="urban", help="Searches the urban dictionary for a term" , description="utility",
                      usage="(term)")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def urban(self, ctx, *, term = None):
        if not term:
         await commandhelp(self, ctx, ctx.command.name)
         return
        allmeanings = []
        req = session.get(f"https://www.urbandictionary.com/define.php?term={term}")
        soup = BeautifulSoup(req.text, "html.parser")
        if f"Sorry, we couldn't find: {term}" in req.text:
            embed = discord.Embed(
                description=f"**{ctx.author.mention}**: No results found for `{term}`",
                color=Colors.green
            )
            return await ctx.send(embed=embed)
        for link in soup.find_all('a'):
            if link.get('href') and link.get('href').startswith("/define.php?term=") and link.get('aria-label') == "Last page":
                if "page=" in link.get('href'):
                    lastpage = int(link.get('href').split("page=")[1])
                else:
                    lastpage = 1
        if lastpage > 5:
            lastpage = 5
        for i in range(1, lastpage + 1):
            resp = session.get(f'https://api.urbandictionary.com/v0/define?term={term}&page={i}')
            data = resp.json()
            for meaning in data['list']:
                allmeanings.append({
                    'permalink': meaning['permalink'],
                    'definition': meaning['definition'],
                    'thumbs_up': meaning['thumbs_up'],
                    'thumbs_down': meaning['thumbs_down']
                })

        embeds = []
        maxpages = 0
        pagenum = 0
        for i in range(0, len(allmeanings)): maxpages += 1
        for i in range(0, len(allmeanings)):
            pagenum += 1

            embed = discord.Embed(
                description=f"[**{term}**]({allmeanings[i]['permalink']})\n\n{allmeanings[i]['definition']}",
                color=Colors.green
            )
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else "https://cdn.discordapp.com/embed/avatars/0.png")
            embed.set_footer(text=f"👍 {allmeanings[i]['thumbs_up']} | 👎 {allmeanings[i]['thumbs_down']} | Page {pagenum}/{maxpages}")
            embeds.append(embed)
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
        paginator.add_button('prev', emoji='<:left:1052989837428396062>')
        paginator.add_button('delete', emoji='<:no:1052268147589271572>')
        paginator.add_button('next', emoji='<:right:1052989878574518292>')
        await paginator.start()
        
    @commands.hybrid_command(aliases = ['spotify','sp'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def track(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        spotify_result = next((activity for activity in user.activities if isinstance(activity, discord.Spotify)), None)
        
        if spotify_result is None:
            await ctx.send(f'{ctx.author.mention} is not listening to Spotify.')
        else:
            embed = discord.Embed(title="**Spotify**", description=f"__[{spotify_result.title}](https://open.spotify.com/track/{spotify_result.track_id})__\n__[{spotify_result.artist}](https://discord.gg/EvuxyxFSQh)__", color=Colors.green)
            embed.set_thumbnail(url=f'{spotify_result.album_cover_url}')
            await ctx.reply(embed=embed, mention_author=False)
        
    @commands.hybrid_command(help="show user information", description="check info about a user", usage=">user>", aliases=["ui", "whois", "user"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx: Context, *, member: Union[Member, User]=None):
     if member is None:
        member = ctx.author 
     
     button = Button(label="user profile", url=f"https://discord.com/users/{member.id}")
     view = View()
     view.add_item(button)
     
     user = await self.bot.fetch_user(member.id)
     discrim = ["0001", "1337", "0002", "9999", "0666", "0888", "6969", "0069"]
     badges = []
     devices = []
     if user.public_flags.early_supporter:
      badges.append("<:early:1073689098763640872>")
     if user.public_flags.active_developer:
      badges.append("<:active_dev:1073689092040179753>")
     if user.public_flags.verified_bot_developer:
       badges.append("<:BadgeEarlyVerifiedBotDeveloper:1073689336505176155>")
     if user.public_flags.hypesquad_bravery:
      badges.append("<:hypesquad_bravery:1049008914143916203>")
     if user.public_flags.hypesquad_balance:
      badges.append("<:hypesquad_balance:1049008947295686656>")
     if user.public_flags.hypesquad_brilliance:
      badges.append("<:hypesquad_bravery:1049008766194044949>")  
     if user.discriminator in discrim or user.display_avatar.is_animated() or user.banner is not None:
      badges.append("<:nitro:1049008750389903390>")

     for guild in self.bot.guilds: 
      mem = guild.get_member(user.id)
      if mem is not None:
       if mem.premium_since is not None:
         badges.append("<:boosts:1073689095441756251>")
         break

     if isinstance(member, Member):
      if member.mobile_status != Status.offline:
        devices.append("<:mobile:1048997078799487056>")
      if member.web_status != Status.offline:
        devices.append("<a:emoji_10:1048997107790520421>")
      if member.desktop_status != Status.offline:
        devices.append("<:desktopp:1048996906006741052>")

      if str(member.status) == "online":
       status ="<:online:1049000510167973898>"
      elif str(member.status) == "dnd":
       status = "<:dnd:1048996799920210020>"
      elif str(member.status) == "idle":
       status = "<:inactive:1048997004212174919>"
      elif str(member.status) == "offline": 
       status = "<:offline:1048996780076978256>"
      e = discord.Embed(color=Colors.green)
      e.title = user.name + " " + "".join(map(str, badges))
      if member.activities:
        for a in member.activities:
          if isinstance(a, Spotify):
            e.description = f"<:Spotify:1073690039248224369> listening to [**{a.title}**]({a.track_url}) by [**{a.artist}**]({a.track_url}) on spotify"
      members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
      ordinal = Func.ordinal(int(members.index(member)+1))
      if member.premium_since:
        boosted = f"<t:{int(member.premium_since.timestamp())}:R>"
      else:
        boosted = "no"  
      e.set_author(name=f"{member} • {ordinal} member", icon_url=member.display_avatar.url)
      e.set_thumbnail(url=member.display_avatar.url)
      e.add_field(name="info", value=f"**joined:** <t:{int(member.joined_at.timestamp())}:R>\n**created:** <t:{int(member.created_at.timestamp())}:R>\n**server booster:** {boosted}", inline=False)
      if member.activity:
        active = f"{status} {member.activity.name}"
      else:
        active = status
      if member.status != Status.offline:
       platform = " ".join([str(device) for device in devices])
      else:
        platform = "" 
      if len(member.roles) > 1:
        role_string = ' '.join([r.mention for r in member.roles][1:])
      else:
        role_string = "No Roles" 
      e.add_field(name="profile", value=f"**custom status:** {active}\n**device{'s' if len(devices) > 1 else ''}:** {platform}\n**server roles:** {role_string}", inline=False) 
      try:  
       e.set_footer(text='ID: ' + str(member.id) + f" | {len(member.mutual_guilds)} mutual server(s)")
      except: 
         e.set_footer(text='ID: ' + str(member.id))
      await sendmsg(self, ctx, None, e, view, None, None)
      return
     elif isinstance(member, User):
      e = discord.Embed(color=Colors.green)
      e.title = user.name + " " + "".join(map(str, badges))
      e.set_author(name=f"{member}", icon_url=member.display_avatar.url)
      e.set_thumbnail(url=member.display_avatar.url)
      e.add_field(name="created", value=f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>", inline=False)
      e.set_footer(text='ID: ' + str(member.id))
      await sendmsg(self, ctx, None, e, None, None, None)
        
    @commands.command(help="gets the invite link with administrator permission of a bot", description="utility", usage="[bot id]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def getbotinvite(self, ctx, id: User=None):
     if id is None:
        await commandhelp(self, ctx, ctx.command.name)
        return
     else:    
      if not id.bot: return await sendmsg(self, ctx, "this isn't a bot", None, None, None, None)
      embed = discord.Embed(color=Colors.green, description=f"Click **[here](https://discord.com/api/oauth2/authorize?client_id={id.id}&permissions=8&scope=bot%20applications.commands)** to invite the bot")
      await sendmsg(self, ctx, None, embed, None, None, None)
        
    @commands.command(aliases=["pi"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def profileicon(self,
                     ctx: commands.Context,
                     *,
                     member: Union[discord.Member, discord.User] = None):
        if member is None:
            member = ctx.author
        user = await self.bot.fetch_user(member.id)
        avatar_url = user.display_avatar.url
        banner_url = user.banner.url
        if not user.banner.url: banner_url = None
            
        embed = discord.Embed(color=Colors.green,
                              title=f"@promise",
                              description=f"**Here are the icons for [{member.name}](https://discord.gg/EvuxyxFSQh)**\n**You need nitro to work and a banner for profileicon**")
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_image(url=user.banner.url)
        await ctx.reply(embed=embed, mention_author=False)
        
    @commands.command(name="ben", description="utility", help="ask ben a question", usage="(question)")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ben(self, ctx, *, question: str = None):
        if not question:
         await commandhelp(self, ctx, ctx.command.name)
         return
        async with ctx.typing():
            video = random.choice(os.listdir("stuff"))
            await ctx.reply(file=discord.File(f"stuff/{video}"))
            
async def setup(bot):
    await bot.add_cog(cmds(bot))          
