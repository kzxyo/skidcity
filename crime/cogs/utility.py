import discord, aiohttp, button_paginator as pg, json, random, asyncio, datetime, os, io
from discord import Embed, Member, User, AllowedMentions, Message
from discord.ext import tasks
from discord.ext.commands import Cog, command, Context, cooldown, BucketType, AutoShardedBot as Bot
from .utils.util import Emojis, Colors
from typing import Union
from datetime import datetime
from discord.ui import View, Button, Select
from cogs.utilevents import blacklist, sendmsg, noperms, commandhelp
from cogs.utils import http
from .utils.embedparser import to_object
from io import BytesIO
from .modules.tiktokapi import for_you
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
       

class utility(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

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
          em = Embed(color=0xf7f9f8, description=f"{mem.mention} is AFK since <t:{int(check[3])}:R> - **{check[2]}**")
          await sendmsg(self, message, None, em, None, None, None)

     async with self.bot.db.cursor() as curs:
        await curs.execute("SELECT * from afk where guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id)) 
        check = await curs.fetchone()
        if check is not None:
         embed = Embed(color=0xf7f9f8, description=f"👋 Welcome back {message.author.mention}! You were AFK since <t:{int(check[3])}:R>")
         await sendmsg(self, message, None, embed, None, None, None)
         await curs.execute("DELETE FROM afk WHERE guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id))
     await self.bot.db.commit()

    @command(help="create an embed", description="fun", aliases=["ce"])
    @blacklist()
    async def createembed(self, ctx, *, code: str=None):
        if not ctx.author.guild_permissions.manage_guild: 
            await noperms(self, ctx, "manage_guild")
            return 
        if not code:
            e = discord.Embed(
                description=f"> {Emojis.warn} please provide embed code [here](https://crimebot.site/embed)",
                color=0xf7f9f8
            )
            return await ctx.reply(embed=e)
            return 
        e = await to_object(code)
        await ctx.send(**e)


    @command(help="let everyone know you are away", description="utility", usage="<reason>")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
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
        embed = Embed(color=0xf7f9f8, description=f"{ctx.author.mention}: You're now AFK with the status: **{reason}**")
        await sendmsg(self, ctx, None, embed, None, None, None)


    @command(help="returns a random bible verse", description="fun", aliases=["verse"])
    @blacklist()
    @cooldown(1, 4, BucketType.guild)
    async def bible(self, ctx): 
     async with aiohttp.ClientSession() as cs:
      async with cs.get("https://labs.bible.org/api/?passage=random&type=json") as r:
       byte = await r.read()
       data = str(byte, 'utf-8')
       data = data.replace("[", "").replace("]", "")
       bible = json.loads(data) 
       embed = discord.Embed(color=0x2F3136, description=bible["text"]).set_author(name="{} {}:{}".format(bible["bookname"], bible["chapter"], bible["verse"]), icon_url="https://imgs.search.brave.com/gQ1kfK0nmHlQe2XrFIoLH9vtFloO3HRTDaCwY5oc0Ow/rs:fit:1200:960:1/g:ce/aHR0cDovL3d3dy5w/dWJsaWNkb21haW5w/aWN0dXJlcy5uZXQv/cGljdHVyZXMvMTAw/MDAvdmVsa2EvNzU3/LTEyMzI5MDY0MTlC/MkdwLmpwZw") 
       await ctx.reply(embed=embed, mention_author=False)

    @command(name='seticon', aliases=["changeserverav", 'changeicon', 'setavatar'], description="change guild avatar", extras={'perms':'administrator'}, brief='url/image', usage='```Syntax: !setsplash <url/image>\nExample: !setsplash https://rival.rocks/image.png```')
    @blacklist()
    async def seticon(self, ctx, url: str = None):
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None
        if not ctx.author.guild_permissions.manage_guild:
            await noperms(self, ctx, "manage_guild")
            return
        try:    
            bio = await http.get(url, res_method="read")
            guild = ctx.guild
            await guild.edit(icon=bio)
            embed=discord.Embed(description=f"*guild icon is now set to:*", color=0x2F3136)
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        except aiohttp.InvalidURL:
            embed=discord.Embed(description=f"*Please enter a real url or upload an image*", color=0x2F3136)
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            embed=discord.Embed(description=f"*Please enter a real url or upload an image*", color=0x2F3136)
            await ctx.reply(embed = embed, mention_author = False)
        except:
            embed=discord.Embed(description=f"*Your current url is not a supported image.*", color=0x2F3136)
            await ctx.reply(embed = embed, mention_author = False)
    @command(name='setbanner', aliases=["changebnr"], description="change guild banner", extras={'perms':'administrator'}, usage='```Syntax: !setbanner <url/image>\nExample: !setbanner https://crimebot.site/image.png```')
    @blacklist()
    async def setbanner(self, ctx, url: str = None):
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None
        if not ctx.author.guild_permissions.manage_guild:
            await noperms(self, ctx, "manage_guild")
            return
        try:
            bio = await http.get(url, res_method="read")
            guild = ctx.guild
            await guild.edit(banner=bio)
            embed=discord.Embed(description=f"*guild banner is now set to:*", color=0x2F3136)
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        except aiohttp.InvalidURL:
            await ctx.reply(embed = embed, mention_author = False)
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            embed=discord.Embed(description=f"*Please enter a real url or upload an image*", color=0x2F3136)
            await ctx.reply(embed = embed, mention_author = False)
        except:
            embed=discord.Embed(description=f"*Your current url is not a supported image.*", color=0x2F3136)
            await ctx.reply(embed = embed, mention_author = False)
    @command(name='setsplash', aliases=["changesplash"], description="change guild splash", extras={'perms':'administrator'}, usage='```Syntax: !setsplash <url/image>\nExample: !setsplash https://crimebot.site/image.png```')
    @blacklist()
    async def setsplash(self, ctx, url: str = None):
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None
        if not ctx.author.guild_permissions.manage_guild:
            await noperms(self, ctx, "manage_guild")
            return
        try:
            bio = await http.get(url, res_method="read")
            guild = ctx.guild
            await guild.edit(splash=bio)
            embed=discord.Embed(description=f"*guild splash is now set to:*", color=0x2F3136)
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        except aiohttp.InvalidURL:
            embed=discord.Embed(description=f"*Please enter a real url or upload an image*", color=0x2F3136)
            await ctx.reply(embed = embed, mention_author = False)
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            embed=discord.Embed(description=f"*Please enter a real url or upload an image*", color=0x2F3136)
            await ctx.reply(embed = embed, mention_author = False)
        except:
            embed=discord.Embed(description=f"*Your current url is not a supported image.*", color=0x2F3136)
            await ctx.reply(embed = embed, mention_author = False)

    @command(help="see user's avatar", description="utility", usage="<user>", aliases=["av", "pfp"])
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def avatar(self, ctx: Context, *, member: Union[Member, User]=None):
      if member is None: 
        member = ctx.author 

      if isinstance(member, Member): 
        embed = Embed(color=0xf7f9f8, title=f"{member.name}'s avatar", url=member.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        await sendmsg(self, ctx, None, embed, None, None, None)
      elif isinstance(member, User):
        embed = Embed(color=0xf7f9f8, title=f"{member.name}'s avatar", url=member.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        await sendmsg(self, ctx, None, embed, None, None, None) 
    
    @command(help="see someone's banner", description="utility", usage="<user>")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def banner(self, ctx: Context, *, member: User=None):
     if member is None:
      member = ctx.author 

     user = await self.bot.fetch_user(member.id)
     if not user.banner:
      hexcolor = hex(user.accent_colour.value)
      hex2 = hexcolor.replace("0x", "")
      e = Embed(color=0xf7f9f8, title=f"{user.name}'s banner", url=f"https://singlecolorimage.com/get/{hex2}/400x100")
      e.set_image(url=f"https://singlecolorimage.com/get/{hex2}/400x100")
      await sendmsg(self, ctx, None, e, None, None, None)
      return 

     embed = Embed(color=0xf7f9f8, title=f"{user.name}'s banner", url=user.banner.url)
     embed.set_image(url=user.banner.url)
     await sendmsg(self, ctx, None, embed, None, None, None)

    @command(help="play blacktea with your friends", description="fun")
    @cooldown(1, 20, BucketType.guild)
    @blacklist()
    async def blacktea(self, ctx: Context): 
     try:
      if BlackTea.MatchStart[ctx.guild.id] is True: 
       return await ctx.reply("somebody in this server is already playing blacktea", mention_author=False)
     except KeyError: pass 

     BlackTea.MatchStart[ctx.guild.id] = True 
     embed = Embed(color=0xf7f9f8, title="BlackTea Matchmaking", description=f"⏰ Waiting for players to join. To join react with 🍵.\nThe game will begin in **20 seconds**")
     embed.add_field(name="goal", value="You have **10 seconds** to say a word containing the given group of **3 letters.**\nIf failed to do so, you will lose a life. Each player has **2 lifes**")
     embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)  
     mes = await ctx.send(embed=embed)
     await mes.add_reaction("🍵")
     await asyncio.sleep(20)
     me = await ctx.channel.fetch_message(mes.id)
     players = [user.id async for user in me.reactions[0].users()]
     players.remove(self.bot.user.id)

     if len(players) < 2:
      BlackTea.MatchStart[ctx.guild.id] = False
      return await ctx.send("😦 {}, not enough players joined to start blacktea".format(ctx.author.mention), allowed_mentions=AllowedMentions(users=True)) 
  
     while len(players) > 1: 
      for player in players: 
       strin = await BlackTea.get_string()
       await ctx.send(f"⏰ <@{player}>, type a word containing **{strin.upper()}** in **10 seconds**", allowed_mentions=AllowedMentions(users=True))
      
       def is_correct(msg): 
        return msg.author.id == player
      
       try: 
        message = await self.bot.wait_for('message', timeout=10, check=is_correct)
       except asyncio.TimeoutError: 
          try: 
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
            if BlackTea.lifes[player] == 3: 
              await ctx.send(f" <@{player}>, you're eliminated ☠️", allowed_mentions=AllowedMentions(users=True))
              BlackTea.lifes[player] = 0
              players.remove(player)
              continue 
          except KeyError:  
            BlackTea.lifes[player] = 0   
          await ctx.send(f"💥 <@{player}>, you didn't reply on time! **{2-BlackTea.lifes[player]}** lifes remaining", allowed_mentions=AllowedMentions(users=True))    
          continue
       if not strin.lower() in message.content.lower() or not message.content.lower() in await BlackTea.get_words():
          try: 
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
            if BlackTea.lifes[player] == 3: 
              await ctx.send(f" <@{player}>, you're eliminated ☠️", allowed_mentions=AllowedMentions(users=True))
              BlackTea.lifes[player] = 0
              players.remove(player)
              continue 
          except KeyError:  
            BlackTea.lifes[player] = 0 
          await ctx.send(f"💥 <@{player}>, incorrect word! **{2-BlackTea.lifes[player]}** lifes remaining", allowed_mentions=AllowedMentions(users=True))
       else: await message.add_reaction("✅")  
          
     await ctx.send(f"👑 <@{players[0]}> won the game!", allowed_mentions=AllowedMentions(users=True))
     BlackTea.lifes[players[0]] = 0
     BlackTea.MatchStart[ctx.guild.id] = False  

    @command(aliases=["ocr"])
    @blacklist()
    async def opticalcharacterrecognition(self, ctx, image: discord.Attachment):

        await ctx.typing()
        if isinstance(image, discord.Attachment):

            payload = {
                "url": image.url,
                "isOverlayRequired": False,
                "apikey": "K88991768788957",
                "language": "eng",
            }
            x = await self.bot.session.post(
                "https://api.ocr.space/parse/image", data=payload
            )

            x = await x.read()
            await ctx.reply(
                embed=discord.Embed(
                    color=0x2F3136,
                    description=json.loads(x.decode())["ParsedResults"][0][
                        "ParsedText"
                    ],
                )
            )

        elif isinstance(image, str):

            payload = {
                "url": __import__("yarl").URL(image),
                "isOverlayRequired": False,
                "apikey": "K88991768788957",
                "language": "eng",
            }
            x = await self.bot.session.post(
                "https://api.ocr.space/parse/image", data=payload
            )

            x = await x.read()
            await ctx.reply(
                embed=discord.Embed(
                    color=0x2F3136,
                    description=json.loads(x.decode())["ParsedResults"][0][
                        "ParsedText"
                    ],
                )
            )


    @command(help="view the first message of the channel", description="utility", usage="[none]", aliases=['firstmsg'])
    @blacklist()
    async def firstmessage(self, ctx):
        async for message in ctx.channel.history(limit=1, oldest_first=True):
            await ctx.reply(
                view=discord.ui.View().add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.link,
                        label="first message",
                        url=message.jump_url,
                    )
                )
            )

    @command(help=f"crime repeats the message you request", description="utility", usage="[user]", aliases=['move'])
    @blacklist()
    async def say(self, ctx, message=None):
        if not message: 
            e = Embed(
                description=f"{Emojis.warn} tell crime to say something",
                color=0xf7f9f8
            )
            await ctx.reply(embed=e, mention_author=False)  
            return
        e = Embed(
            description=f"**{message}**",
            color=0xf7f9f8
        ).set_footer(text=f"requested by {ctx.author}")
        await ctx.send(embed=e, mention_author=False)

    @command(help=f"deletes the channel and clones it", description="utility", usage="[NONE]", aliases=['clone'])
    @blacklist()
    async def nuke(self, ctx):
        if not ctx.author.guild_permissions.manage_channels:
            await noperms(self, ctx, "manage_channels")
            return
        invoker = ctx.author.id
        channel = ctx.channel

        class disabledbuttons(discord.ui.View):
            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=True,
                emoji=Emojis.check,
            )
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != invoker:
                    return
                await channel.delete()
                ch = await interaction.channel.clone(
                    name=interaction.channel.name,
                    reason=f"original channel nuked by {invoker}",
                )
                ch = await interaction.guild.fetch_channel(ch.id)
                e = discord.Embed(description=f"<@{invoker}>: channel has been nuked successfully", color=0xf7f9f8)
                await ch.send(embed=e)

            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=True,
                emoji=Emojis.deny,
            )
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                embed = discord.Embed(description="Are you sure you want to nuke this channel?\nIt will remove all webhooks and invites.", color=0xf7f9f8)
                await interaction.response.edit_message(content=None, embed=embed, view=None)
                embed = discord.Embed(description=f"<@{interaction.user.id}>: channel nuke has been cancelled", color=0xf7f9f8)
                await interaction.channel.send(embed=embed)

        class buttons(discord.ui.View):
            @discord.ui.button(
                style=discord.ButtonStyle.grey, emoji=Emojis.check
            )
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != invoker:
                    return
                await channel.delete()
                ch = await interaction.channel.clone(
                    name=interaction.channel.name,
                    reason=f"original channel nuked by {invoker}",
                )
                ch = await interaction.guild.fetch_channel(ch.id)
                e = discord.Embed(description=f"<@{invoker}>: channel has been nuked successfully", color=0xf7f9f8)
                await ch.send(embed=e)

            @discord.ui.button(
                style=discord.ButtonStyle.grey, emoji=Emojis.deny
            )
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                embed = discord.Embed(description="Are you sure you want to nuke this channel?\nIt will remove all webhooks and invites.", color=0xf7f9f8)
                await interaction.response.edit_message(content=None, embed=embed, view=disabledbuttons())
                embed = discord.Embed(description=f"<@{interaction.user.id}>: channel nuke has been cancelled", color=0xf7f9f8)
                await interaction.channel.send(embed=embed)
        embed = discord.Embed(description="Are you sure you want to nuke this channel?\nIt will remove all webhooks and invites.", color=0xf7f9f8)
        await ctx.reply(embed=embed, view=buttons())

    @command(aliases=["screenshot"], usage="[topic]")
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def ss(awlf, ctx, *, ssig):
        """Returns With Screenshot Of Given Link"""
        idk = ctx.message.content.lower()
        if "porn" in idk or "sex" in idk or "xxxx" in idk or "xham" in idk or "hellmom" in idk or "xvid" in idk or "shameless" in idk or "play-asia.com" in idk or "miakhal" in idk or "cum" in idk or "orgasm" in idk or "xvid" in idk or "slut" in idk or "naked" in idk or "brazzers" in idk or "nig" in idk or "slut" in idk or "horny" in idk or "rule34video" in idk or "fuck" in idk:
            await ctx.reply(f"**18+ websites are not allowed!!**",
                            mention_author=True,
                            delete_after=3)
        elif "jerk" in idk or "redgif" in idk or "anybunny" in idk or "hentai" in idk or "nude" in idk or "bangbros" in idk or "onlyfans" in idk or "naught" in idk or "boobs" in idk or "blonde" in idk or "tits" in idk or "titties" in idk or "wetgif" in idk or "pussy" in idk or "hanime" in idk or "gay" in idk or " tiava" in idk or "blowjob" in idk or "beeg" in idk:
            await ctx.reply(f"** 18+ websites aren't allowed!**",
                            mention_author=True,
                            delete_after=5)
        elif "bit.ly" in idk or "shorturl" in idk or "cutt.ly" in idk:
            await ctx.reply(f"**url shorteners aren't allowed!**",
                            mention_author=True,
                            delete_after=5)
        elif "https" in idk or "http" in idk:
            embed = discord.Embed(title=f"Screenshot of {ssig}", color = 0xf7f9f8)
            embed.set_image(url=f"https://image.thum.io/get/{ssig}")
            embed.set_footer(text="powered by crime")
            await ctx.reply(embed=embed, mention_author=True)
        else:
            embed = discord.Embed(title=f"Screenshot Of {ssig}", color = 0xf7f9f8)
            embed.set_image(url=f"https://image.thum.io/get/https://{ssig}")
            embed.set_footer(text="powered by crime")
            await ctx.reply(embed=embed, mention_author=False)

    @command(help=f"returns the boost count of your guild", description="utility", usage="[NONE]")
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def boostcount(self, ctx):
        embed = discord.Embed(
        description = f'> **{ctx.guild.name}**\'s Boost Count is {str(ctx.guild.premium_subscription_count)}',
         colour=0xf7f9f8
         )
        await ctx.reply(embed = embed, mention_author=False)

    @command(help=f"returns the boost count of your guild", description="utility", usage="[member]", aliases=["ui", "whois"])
    @cooldown(1, 3,BucketType.user)
    @blacklist()
    async def userinfo(self, ctx, *, member: Union[discord.Member, discord.User] = None):
        if member is None:
            member = ctx.author
        k = 0
        for guild in self.bot.guilds:
            if guild.get_member(member.id) is not None:
                k += 1

        if isinstance(member, discord.Member):
            if str(member.status) == "online":
                status = "<:crimeonline:1084947192881631332>"
            elif str(member.status) == "dnd":
                status = "<:crimednd:1084947194899091567>"
            elif str(member.status) == "idle":
                status = "<:crimeidle:1084947194198634618>"
            elif str(member.status) == "offline":
                status = "<:crimeoffline:1084947313430106233>"
            embed = discord.Embed(color=0xf7f9f8)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(name=member.name,
                             icon_url=member.display_avatar.url)
            embed.add_field(
                name="joined",
                value=
                f"<t:{int(member.joined_at.timestamp())}:F>\n<t:{int(member.joined_at.timestamp())}:R>",
                inline=False)
            if member.activity:
                activity = member.activity.name
            else:
                activity = ""

            embed.add_field(name="> __status__",
                            value=status + " " + activity,
                            inline=False)
            embed.add_field(
                name="> registered",
                value=
                f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>",
                inline=False)
            if len(member.roles) > 1:
                role_string = ' '.join([r.mention for r in member.roles][1:])
                embed.add_field(
                    name="> roles [{}]".format(len(member.roles) - 1),
                    value=role_string,
                    inline=False)
            embed.set_footer(text='ID: ' + str(member.id))
            await ctx.reply(embed=embed, mention_author=False)
            return
        elif isinstance(member, discord.User):
            e = discord.Embed(color=0xf7f9f8)
            e.set_author(name=f"{member}", icon_url=member.display_avatar.url)
            e.set_thumbnail(url=member.display_avatar.url)
            e.add_field(
                name="> registered",
                value=
                f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>",
                inline=False)
            embed.set_footer(text='ID: ' + str(member.id))

            await ctx.reply(embed=e, mention_author=False)

    @command(help=f"returns the urban dictionary meaning of the word", description="utility", usage="[word]", aliases=["ud"])
    @blacklist()
    async def urban(self, ctx, *, word):
        if word is None:
           e = discord.Embed(
              description="> please provide a word"
           )
           await ctx.send(embed=e)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.urbandictionary.com/v0/define?term={word}') as resp:
                    data = await resp.json()
            if not data['list']:
                await ctx.send(f"No results found for {word}.")
                return
            definition = data['list'][0]['definition']
            example = data['list'][0]['example']
            embed = discord.Embed(title=f"Urban Dictionary: {word}", color=0x7289da)
            embed.add_field(name="Definition", value=definition, inline=False)
            embed.add_field(name="Example", value=example, inline=False)
            embed.set_thumbnail(url="https://imgs.search.brave.com/CrwNIBGq0wryzQTxOpFlsZTHvf7jCqcXU7Di-qqkU60/rs:fit:512:512:1/g:ce/aHR0cHM6Ly9zbGFj/ay1maWxlczIuczMt/dXMtd2VzdC0yLmFt/YXpvbmF3cy5jb20v/YXZhdGFycy8yMDE4/LTAxLTExLzI5NzM4/NzcwNjI0NV84NTg5/OWE0NDIxNmNlMTYw/NGM5M181MTIuanBn")
            await ctx.send(embed=embed)
            
    @command(help=f"reverse image searches your image", description="utility", usage="[image]", aliases=["rev"])
    @blacklist()
    async def reverse(self, ctx, *, img):
        try:
            link=f"https://images.google.com/searchbyimage?image={img}"
            em = discord.Embed(description=f"{ctx.author}'s reverse search", color=0xf7f9f8).set_footer(text=f"Requested by {ctx.author}")
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label='reverse', url=link))
            await ctx.send(embed=em, view=view)
        except Exception as e:
            print(f"[ERROR]: {e}")
    
    @command(help=f"reverse image searches your avatar", description="utility", usage="[user]", aliases=["revav", "rav"])
    @blacklist()
    async def reverseav(self, ctx, *, user: Union[discord.Member, discord.User] = None):
        if user is None:
            user = ctx.author
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)
        try:
            link=f"https://images.google.com/searchbyimage?image={user.display_avatar}"
            em = discord.Embed(color=0xf7f9f8, description=f"{user.name}'s reverse search").set_footer(text=f"Requested by {ctx.author}")
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f"{user.name}'s revav", url=link))
            await ctx.send(embed=em, view=view)
        except Exception as e:
            print(f"[ERROR]: {e}")

    @command(name="ben", description="utility", help="ask ben a question", usage="(question)")
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def ben(self, ctx, *, question: str = None):
        if not question:
         await commandhelp(self, ctx, ctx.command.name)
         return
        async with ctx.typing():
            video = random.choice(os.listdir("ben"))
            await ctx.reply(file=discord.File(f"ben/{video}"))

    @command(name='xbox', description="show a xbox account", brief='username')
    @blacklist()
    async def xbox(self, ctx, *, username):
        try:
            try:
                username=username.replace(" ", "%20")
            except:
                pass
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
                async with client.get(f"https://playerdb.co/api/player/xbox/{username}") as r:
                    data = await r.json()
                    try:
                        embed=discord.Embed(title=data['data']['player']['username'], color=int("0f7c0f", 16), url=f"https://xboxgamertag.com/search/{username}").add_field(name='Gamerscore', value=data['data']['player']['meta']['gamerscore'], inline=True).add_field(name='Tenure', value=data['data']['player']['meta']['tenureLevel'], inline=True).add_field(name='Tier', value=data['data']['player']['meta']['accountTier'], inline=True).add_field(name='Rep', value=data['data']['player']['meta']['xboxOneRep'].strip("Player"), inline=True).set_author(name=ctx.author, icon_url=ctx.author.display_avatar).set_footer(text="Xbox", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png")
                        embed.set_thumbnail(url=data['data']['player']['avatar']).add_field(name="ID", value=data['data']['player']['id'], inline=True)
                        if data['data']['player']['meta']['bio']:
                            embed.description=data['data']['player']['meta']['bio']
                        await ctx.reply(embed=embed)
                    except:
                        embed=discord.Embed(title=data['data']['player']['username'], color=int("0f7c0f", 16), url=f"https://xboxgamertag.com/search/{username}").add_field(name='Gamerscore', value=data['data']['player']['meta']['gamerscore'], inline=True).add_field(name='Tenure', value=data['data']['player']['meta']['tenureLevel'], inline=True).add_field(name='Tier', value=data['data']['player']['meta']['accountTier'], inline=True).add_field(name='Rep', value=data['data']['player']['meta']['xboxOneRep'].strip("Player"), inline=True).set_author(name=ctx.author, icon_url=ctx.author.display_avatar).set_footer(text="Xbox", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png").add_field(name="ID", value=data['data']['player']['id'], inline=True)
                        if data['data']['player']['meta']['bio']:
                            embed.description=data['data']['player']['meta']['bio']
                        await ctx.reply(embed=embed)
        except:
            return await ctx.reply(embed=discord.Embed(description=f"{Emojis.warn} Gamertag **`{username}`** not found", color=int("f7f9f8", 16)))
    @command(help="add an emoji", description="emoji", usage="[emoji] <name>", aliases=['steal', 'add', 'emojiadd'])
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def addemoji(self, ctx, emoji: Union[discord.Emoji, discord.PartialEmoji]=None, *, name=None):
        if (not ctx.author.guild_permissions.manage_emojis_and_stickers):
            await noperms(self, ctx, "manage_emojis_and_stickers")
            return
        if emoji is None: return await commandhelp(self, ctx, ctx.command.name) 
        if name == None:
            name = emoji.name

        url = emoji.url
        async with aiohttp.ClientSession() as ses: 
            async with ses.get(url) as r:
                try:
                    img = BytesIO(await r.read())
                    bytes = img.getvalue()
                    emoji = await ctx.guild.create_custom_emoji(image=bytes, name=name)
                    await sendmsg(self, ctx, f"added emoji `{name}` | {emoji}", None, None, None, None)
                except discord.HTTPException as re:
                    pass

    @command(help="add multiple emojis", description="emoji", usage="[emojis]", aliases=["am]"])
    @cooldown(1, 6, BucketType.guild)
    @blacklist()
    async def addmultiple(self, ctx: Context, *emoji: Union[discord.Emoji, discord.PartialEmoji]):
        if (not ctx.author.guild_permissions.manage_emojis_and_stickers):
            await noperms(self, ctx, "manage_emojis_and_stickers")
            return
        if len(emoji) == 0: return await commandhelp(self, ctx, ctx.command.name) 
        if len(emoji) > 20: return await ctx.reply("you can only add up to 20 emojis at once")
        emojis = []
        await ctx.channel.typing()
        for emo in emoji:
            url = emo.url
            async with aiohttp.ClientSession() as ses: 
                async with ses.get(url) as r:
                    try:
                        img = BytesIO(await r.read())
                        bytes = img.getvalue()
                        emoj = await ctx.guild.create_custom_emoji(image=bytes, name=emo.name)
                        emojis.append(f"{emoj}")
                    except discord.HTTPException as re:
                        pass

        embed = discord.Embed(color=0xf7f9f8, title=f"added {len(emoji)} emojis") 
        embed.description = "".join(map(str, emojis))    
        await sendmsg(self, ctx, None, embed, None, None, None)

    @command(help="returns a list of server's emojis", description="emoji", aliases=['guildemojis'])
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def emojilist(self, ctx: Context):
                i=0
                k=1
                l=0
                mes = ""
                number = []
                messages = []
                for emoji in ctx.guild.emojis:
                    mes = f"{mes}`{k}` {emoji} - ({emoji.name})\n"
                k+=1
                l+=1
                if l == 10:
                    messages.append(mes)
                number.append(discord.Embed(color=0xf7f9f8, title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]", description=messages[i]))
                i+=1
                mes = ""
                l=0
        
                messages.append(mes)
                number.append(discord.Embed(color=0xf7f9f8, title=f"emojis in {ctx.guild.name} [{len(ctx.guild.emojis)}]", description=messages[i]))
                paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
                paginator.add_button('prev', emoji= "<:crimeleft:1082120060556021781>")
                paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
                paginator.add_button('next', emoji="<:crimeright:1082120065853423627>")
                await paginator.start()        

    @command(aliases=["downloademoji", "e"], help="gets an image version of your emoji", description="emoji", usage="[emoji]")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def enlarge(self, ctx, emoji: Union[discord.PartialEmoji, str]=None):
            if emoji is None:
                await commandhelp(self, ctx, ctx.command.name)
                return  
            elif isinstance(emoji, discord.PartialEmoji): 
                await sendmsg(self, ctx, emoji.url, None, None, None, None)
                return
            elif isinstance(emoji, str):
                ordinal = ord(emoji)
                await sendmsg(self, ctx, f"https://twemoji.maxcdn.com/v/latest/72x72/{ordinal:x}.png", None, None, None, None)
            else:
                e = discord.Embed(color=Colors.yellow, description=f"{Emojis.warn} {ctx.author.mention}: emoji not found")
                await sendmsg(self, ctx, None, e, None, None, None)

    @command(help="gets the banner from a server based by invite code", description="utility", usage="[invite code]")
    @blacklist()
    async def sbanner(self, ctx, *, link=None):
      if link == None:
        embed = Embed(color=0xf7f9f8, title=f"{ctx.guild.name}'s banner")
        embed.set_image(url=ctx.guild.banner)
        await sendmsg(self, ctx, None, embed, None, None, None)
      else:
        invite_code = link
        async with aiohttp.ClientSession() as cs:
          async with cs.get(DISCORD_API_LINK + invite_code) as r:
            data = await r.json()
          format = ""
          if "a_" in data["guild"]["banner"]:
            format = ".gif"
          else:
            format = ".png"

          embed = Embed(color=0xf7f9f8, title=f"{ctx.guild.name}'s banner")
          embed.set_image(url="https://cdn.discordapp.com/banners/" + data["guild"]["id"] + "/" + data["guild"]["banner"] + f"{format}?size=1024")
          await sendmsg(self, ctx, None, embed, None, None, None)


    @command(help="gets the icon from a server based by invite code", description="utility", usage="[invite code]")
    @blacklist()
    async def sicon(self, ctx, *, link=None):
      if link == None:
        embed = Embed(color=0xf7f9f8, title=f"{ctx.guild.name}'s icon")
        embed.set_image(url=ctx.guild.icon)
        await sendmsg(self, ctx, None, embed, None, None, None)
      else:
        invite_code = link
        async with aiohttp.ClientSession() as cs:
          async with cs.get(DISCORD_API_LINK + invite_code) as r:
            data = await r.json()

          format = ""
          if "a_" in data["guild"]["icon"]:
            format = ".gif"
          else:
            format = ".png"
              
          embed = Embed(color=0xf7f9f8, title=f"{ctx.guild.name}'s icon")
          embed.set_image(url="https://cdn.discordapp.com/icons/" + data["guild"]["id"] + "/" + data["guild"]["icon"] + f"{format}?size=1024")
          await sendmsg(self, ctx, None, embed, None, None, None) 

    @command(help ="repost a random tiktok video")
    @blacklist()
    async def fyp(self, ctx):
        async with ctx.typing():
            fyp_videos = await for_you()
            videos = []
            for video in fyp_videos:
                videos.append(video)
            data = random.choice(videos)
            download = data["download_urls"]["no_watermark"]
            async with aiohttp.ClientSession() as session:
                async with session.get(download) as r:
                    data = await r.read()
            file = discord.File(io.BytesIO(data), filename=f"{self.bot.user.name}tok.mp4")
            await ctx.reply(file=file)
            return

    @command()
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def mods(self, ctx):
        """ Check which mods are online on current guild """
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "<:crimeonline:1084947192881631332>"},
            "idle": {"users": [], "emoji": "<:crimeidle:1084947194198634618>"},
            "dnd": {"users": [], "emoji": "<:crimednd:1084947194899091567>"},
            "offline": {"users": [], "emoji": "<:crimeoffline:1084947313430106233>"}
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"
        await ctx.send(embed=Embed(
           title="All Discord Moderators Online",
           description=f">>> {message}"
        ))
async def setup(bot):
    await bot.add_cog(utility(bot))