import discord
import button_paginator as pg, datetime, aiohttp, humanfriendly, os, random, asyncio
from discord import Embed, File, TextChannel, Member, User, Role, Status, Message, Spotify, Message, AllowedMentions
from discord.ext.commands import Cog, command, Context, cooldown, BucketType, AutoShardedBot as Bot
from cogs.events import commandhelp, blacklist, sendmsg, noperms
from utils.classes import Colors, Emojis, Func
from discord.ui import Button, View
from .modules.embedparser import to_object
from wordcloud import WordCloud
from typing import Union

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

reaction_message_author = {}
reaction_message_author_avatar = {}
reaction_message_emoji_url = {}
reaction_message_emoji_name = {}
reaction_message_id = {}
edit_message_author = {}
edit_message_content1 = {}
edit_message_content2 = {}
edit_message_author_avatar = {}
edit_message_id = {}
downloadCount = 0

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

class Utility(Cog):
    def __init__(self, bot: Bot):
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
    async def on_message_delete(self, message: Message):
        if not message.guild: return 
        if message.author.bot: return
        if message.attachments:
         attachment = message.attachments[0].url
        else:
         attachment = "none"

        author = str(message.author)
        content = message.content
        avatar = message.author.display_avatar.url
        async with self.bot.db.cursor() as curso: 
         await curso.execute("INSERT INTO snipe VALUES (?,?,?,?,?,?)", (message.guild.id, message.channel.id, author, content, attachment, avatar))
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
          em = Embed(color=Colors.default, description=f"{mem.mention} is AFK since <t:{int(check[3])}:R> - **{check[2]}**")
          await sendmsg(self, message, None, em, None, None, None)

     async with self.bot.db.cursor() as curs:
        await curs.execute("SELECT * from afk where guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id)) 
        check = await curs.fetchone()
        if check is not None:
         embed = Embed(color=Colors.default, description=f"<a:wave:1020721034934104074> Welcome back {message.author.mention}! You were AFK since <t:{int(check[3])}:R>")
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

    @Cog.listener()
    async def on_message_edit(self, old, new):
     if old.author.bot: return
     if old.content == new.content: return
     edit_message_author[old.channel.id] = old.author
     edit_message_author_avatar[old.channel.id] = old.author.display_avatar.url
     edit_message_content1[old.channel.id] = old.content
     edit_message_content2[new.channel.id] = new.content
     edit_message_id[old.channel.id] = new.id   

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
      guild = self.bot.get_guild(payload.guild_id)
      member = guild.get_member(payload.user_id)  
      if member is None: return
      if member.bot: return
      reaction_message_author[payload.channel_id] = member.name
      reaction_message_author_avatar[payload.channel_id] = member.display_avatar.url   
      reaction_message_emoji_url[payload.channel_id] = payload.emoji.url
      reaction_message_emoji_name[payload.channel_id] = payload.emoji.name
      reaction_message_id[payload.channel_id] = payload.message_id 

    @command(help="create an embed", description="fun", aliases=["ce"])
    @blacklist()
    async def createembed(self, ctx, *, code: str=None):
        if not ctx.author.guild_permissions.manage_guild: 
            await noperms(self, ctx, "manage_guild")
            return 
        if not code:
            e = discord.Embed(
                description=f"> {Emojis.warning} please provide embed code [here](https://tear.lol/embed)",
                color=0xf7f9f8
            )
            return await ctx.reply(embed=e)
            return 
        e = await to_object(code)
        await ctx.send(**e)
    
    @command(help="play blacktea with your friends", description="fun")
    @cooldown(1, 20, BucketType.guild)
    @blacklist()
    async def blacktea(self, ctx: Context): 
     try:
      if BlackTea.MatchStart[ctx.guild.id] is True: 
       return await ctx.reply("somebody in this server is already playing blacktea", mention_author=False)
     except KeyError: pass 

     BlackTea.MatchStart[ctx.guild.id] = True 
     embed = Embed(color=Colors.default, title="BlackTea Matchmaking", description=f"⏰ Waiting for players to join. To join react with 🍵.\nThe game will begin in **20 seconds**")
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
       
    @command(help="set your own prefix", usage="[prefix]", description="utility")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def selfprefix(self, ctx: Context, prefix=None):
      if prefix == None:
        await commandhelp(self, ctx, ctx.command.name)
        return 
      
      async with self.bot.db.cursor() as cursor:
       if prefix.lower() == "none": 
        await cursor.execute("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id)) 
        check = await cursor.fetchone()
        if check is not None:
          await cursor.execute("DELETE FROM selfprefix WHERE user_id = {}".format(ctx.author.id))
          await self.bot.db.commit()
          await sendmsg(self, ctx, None, Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: removed your self prefix"), None, None, None)
        elif check is None:
           await sendmsg(self, ctx, None, Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: you don't have a self prefix"), None, None, None) 
       else:    
        await cursor.execute("SELECT * FROM selfprefix WHERE user_id = {}".format(ctx.author.id)) 
        result = await cursor.fetchone()
        if result is not None:
         sql = ("UPDATE selfprefix SET pref = ? WHERE user_id = ?")
         val = (prefix, ctx.author.id)
         await cursor.execute(sql, val)
         embed = Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: self prefix changed to `{prefix}`")
         await sendmsg(self, ctx, None, embed, None, None, None)
         await self.bot.db.commit()  
        elif result is None:
         sql = ("INSERT INTO selfprefix VALUES(?,?)")
         val = (prefix, ctx.author.id)
         await cursor.execute(sql, val)
         embed =Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: self prefix changed to `{prefix}`")
         await sendmsg(self, ctx, None, embed, None, None, None)
         await self.bot.db.commit()    
        
    @command(aliases=['wc'], description="utility", help="send a wordcloud with channel's messages")
    async def wordcloud(self, ctx: Context, limit: int=None):
        if limit is None or limit > 100: limit = 100
        async with ctx.typing():
            text=[message.content async for message in ctx.channel.history(limit=limit)]
            wc = WordCloud(mode = "RGBA", background_color=None,  height=400, width=700)
            wc.generate(' '.join(text))
            wc.to_file(filename=f'{ctx.author.id}.png')
    
            await ctx.send(file=File(f"{ctx.author.id}.png"))
            os.remove(f'{ctx.author.id}.png')

    @command(help="clear your usernames", description="utility", aliases=["clearusernames", "clearusers"])
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def clearnames(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM oldusernames WHERE user = ?", (ctx.author.id,))
            await sendmsg(self, ctx, "👍", None, None, None, None)
            await self.bot.db.commit()
        except Exception as e:
            print(e)


    @command(help="changes the guild prefix", usage="[prefix]", description="utility")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def prefix(self, ctx: Context, prefix=None):
      if not ctx.author.guild_permissions.manage_guild:
        await noperms(self, ctx, "manage_guild")
        return 
      if prefix == None:
        await commandhelp(self, ctx, ctx.command.name)
        return 
      
      async with self.bot.db.cursor() as cursor:
       await cursor.execute("SELECT prefix, * FROM prefixes WHERE guild_id = {}".format(ctx.guild.id)) 
       check = await cursor.fetchone()
       if check is not None:
        sql = ("UPDATE prefixes SET prefix = ? WHERE guild_id = ?")
        val = (prefix, ctx.guild.id)
        await cursor.execute(sql, val)
        embed = Embed(color=Colors.default, description=f"guild prefix changed to `{prefix}`")
        await sendmsg(self, ctx, None, embed, None, None, None)
       elif check is None:
        sql = ("INSERT INTO prefixes VALUES(?,?)")
        val = (ctx.guild.id, prefix)
        await cursor.execute(sql, val)
        embed =Embed(color=Colors.default, description=f"guild prefix changed to `{prefix}`")
        await sendmsg(self, ctx, None, embed, None, None, None)
       await self.bot.db.commit()         
            
    @command(aliases = ['names', 'usernames'], help="check an user's past usernames", usage="<user>", description="utility")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
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
                    embed = Embed(description = auto, color = Colors.default)
                    embed.set_author(name = f"{member}'s past usernames", icon_url = member.display_avatar)
                    number.append(embed)
                    if len(number) > 1:
                     paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
                     paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
                     paginator.add_button('goto', emoji = "🔢")
                     paginator.add_button('next', emoji="<:right:1018156484170883154>")
                     await paginator.start()  
                    else:
                      await sendmsg(self, ctx, None, embed, None, None, None)      
                else:
                    await sendmsg(self, ctx, f"no logged usernames for {member}", None, None, None, None)
        except Exception as e:
            print(e)
    
    @command(help="see when a user was last seen", description="utility", usage="[member]")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def seen(self, ctx, *, member: Member=None):
      if member is None: return await commandhelp(self, ctx, ctx.command.name)
      async with self.bot.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM seen WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
        check = await cursor.fetchone()
        if check is None: return await sendmsg(self, ctx, None, Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: I didn't see **{member}**"), None, None, None) 
        ts = check[2]
        await ctx.reply(embed=Embed(color=Colors.default, description="{}: **{}** was last seen <t:{}:R>".format(ctx.author.mention, member, ts)))   

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
        embed = Embed(color=Colors.default, description=f"{ctx.author.mention}: You're now AFK with the status: **{reason}**")
        await sendmsg(self, ctx, None, embed, None, None, None)

    @command(aliases=["es"], help="check the latest edited messsage from a channel", usage="<channel>", description="utility") 
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def editsnipe(self, ctx, *, channel: TextChannel=None):
     if channel is None: 
      channel = ctx.channel 
     try:
        em = Embed(color=Colors.default, description=f"edited message in {channel.mention}- [jump](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{edit_message_id[channel.id]})")
        em.set_author(name=edit_message_author[channel.id], icon_url=edit_message_author_avatar[channel.id])
        em.add_field(name="old", value=edit_message_content1[channel.id])
        em.add_field(name="new", value=edit_message_content2[channel.id])
        await sendmsg(self, ctx, None, em, None, None, None)
     except:
        await sendmsg(self, ctx, f"there is no edited message in {channel.mention}", None, None, None, None)

    @command(aliases=["rs"], help="check the latest reaction removal of a channel", usage="<channel>", description="utility")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def reactionsnipe(self, ctx, *, channel: TextChannel=None):
        if channel is None:
         channel = ctx.channel 
        try: 
         em = Embed(color=Colors.default, description=f"{reaction_message_emoji_name[channel.id]}\n[emoji link]({reaction_message_emoji_url[channel.id]})\n[message link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{reaction_message_id[channel.id]})")
         em.set_author(name=reaction_message_author[channel.id], icon_url=reaction_message_author_avatar[channel.id])
         em.set_image(url=reaction_message_emoji_url[channel.id])
         await sendmsg(self, ctx, None, em, None, None, None)
        except: 
          await sendmsg(self, ctx, "there is no deleted reaction in {}".format(channel.mention), None, None, None, None)

    @command(help="check your spotify activity", description="utility", aliases=["sp"])
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def spotify(self, ctx: Context, *, member: Member=None):
      if member is None: 
        member = ctx.author 

      if member.activity:
        if isinstance(member.activity, Spotify):
          embed = Embed(color=member.activity.color)
          embed.set_author(name=member.name, icon_url=member.display_avatar.url, url=member.activity.track_url) 
          embed.add_field(name="Track:", value=f"[{member.activity.title}]({member.activity.track_url})", inline=False)
          embed.add_field(name="Artist:", value=f"[{member.activity.artist}]({member.activity.track_url})", inline=False)
          embed.set_thumbnail(url=member.activity.album_cover_url)
          embed.set_footer(text=f"duration: {humanfriendly.format_timespan(member.activity.duration.total_seconds())}・album: {member.activity.album}", icon_url="https://cdn.discordapp.com/emojis/1022181543202017380.webp?size=56&quality=lossless")
          await sendmsg(self, ctx, None, embed, None, None, None)
        else: return await sendmsg(self, ctx, None, Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: This member isn't listening to spotify"), None, None, None)  
      else: return await sendmsg(self, ctx, None, Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: This member isn't listening to spotify"), None, None, None)  
      
    @command(aliases=["s"], help="check the latest deleted message from a channel", usage="<channel>", description="utility")
    @cooldown(1, 2, BucketType.user)
    @blacklist()
    async def snipe(self, ctx: Context):
     async with self.bot.db.cursor() as cursor: 
      await cursor.execute("SELECT * FROM snipe WHERE guild_id = {} AND channel_id = {}".format(ctx.guild.id, ctx.channel.id))
      chec = await cursor.fetchall()
      embeds = []
      try:
       results = chec[::-1]
       i=0
       for check in results: 
        i+=1
        sniped = check
        em = Embed(color=Colors.default, description=sniped[3] + f"\n[Video]({check[4]})" if ".mp4" in sniped[4] or ".mov" in sniped[4] else sniped[3])
        em.set_author(name=sniped[2], icon_url=sniped[5]) 
        em.set_footer(text="{}/{}".format(i, len(results)))
        if check[4] != "none":
           em.set_image(url=sniped[4] if not ".mp4" in sniped[4] or not ".mov" in sniped[4] else "")
        embeds.append(em)
       if len(embeds) == 1: return await ctx.reply(embed=embeds[0], mention_author=False)
       else:  
        paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
        paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
        paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
        paginator.add_button('next', emoji="<:right:1018156484170883154>")
        await paginator.start() 
      except IndexError:
        if len(check) == 0: return await sendmsg(self, ctx, None, Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: there are no deleted messages in {ctx.channel.mention}"), None, None, None)
        await sendmsg(self, ctx, None, Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: current snipe limit is **{len(check)}**"), None, None, None)

    @command(aliases=["mc"], help="check how many members does your server have", description="utility")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def membercount(self, ctx: Context):
      await ctx.reply(embed=Embed(color=Colors.default, description="**{}** members".format(ctx.guild.member_count)), mention_author=False)

    @command(help="see user's avatar", description="utility", usage="<user>", aliases=["av", "pfp"])
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def avatar(self, ctx: Context, *, member: Union[Member, User]=None):
      if member is None: 
        member = ctx.author 

      if isinstance(member, Member): 
        embed = Embed(color=Colors.default, title=f"{member.name}'s avatar", url=member.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        await sendmsg(self, ctx, None, embed, None, None, None)
      elif isinstance(member, User):
        embed = Embed(color=Colors.default, title=f"{member.name}'s avatar", url=member.display_avatar.url)
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
      e = Embed(color=Colors.default, title=f"{user.name}'s banner", url=f"https://singlecolorimage.com/get/{hex2}/400x100")
      e.set_image(url=f"https://singlecolorimage.com/get/{hex2}/400x100")
      await sendmsg(self, ctx, None, e, None, None, None)
      return 

     embed = Embed(color=Colors.default, title=f"{user.name}'s banner", url=user.banner.url)
     embed.set_image(url=user.banner.url)
     await sendmsg(self, ctx, None, embed, None, None, None)
       
    @command(help="see all members in a role", description="utility", usage="[role]")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def inrole(self, ctx: Context, *, role: Role=None):
            if role is None:
             await commandhelp(self, ctx, ctx.command.name)
             return 

            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for member in role.members:
              mes = f"{mes}`{k}` {member} - ({member.id})\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=Colors.default, title=f"members in {role.name} [{len(role.members)}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = Embed(color=Colors.default, title=f"members in {role.name} [{len(role.members)}]", description=messages[i])
            number.append(embed)
            if len(number) > 1:
             paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
             paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
             paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
             paginator.add_button('next', emoji="<:right:1018156484170883154>")
             await paginator.start()    
            else:
              await sendmsg(self, ctx, None, embed, None, None, None)

    @command(help="see all server boosters", description="utility")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def boosters(self, ctx: Context):
            if not ctx.guild.premium_subscriber_role:
                e = Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: booster role doesn't exist")
                await sendmsg(self, ctx, None, e, None, None, None)
                return 
            if len(ctx.guild.premium_subscriber_role.members) == 0:
                e = Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: this server doesn't have any boosters")
                await sendmsg(self, ctx, None, e, None, None, None)
                return 

            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for member in ctx.guild.premium_subscriber_role.members: 
              mes = f"{mes}`{k}` {member} - <t:{int(member.premium_since.timestamp())}:R> \n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=Colors.default, title=f"{ctx.guild.name} boosters [{len(ctx.guild.premium_subscriber_role.members)}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = Embed(color=Colors.default, title=f"{ctx.guild.name} boosters [{len(ctx.guild.premium_subscriber_role.members)}]", description=messages[i])
            number.append(embed)
            if len(number) > 1:
             paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
             paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
             paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
             paginator.add_button('next', emoji="<:right:1018156484170883154>")
             await paginator.start()
            else:
              await sendmsg(self, ctx, None, embed, None, None, None)  
    
    @command(help="see all server roles", description="utility")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
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
               number.append(Embed(color=Colors.default, title=f"{ctx.guild.name} roles [{len(ctx.guild.roles)}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = Embed(color=Colors.default, title=f"{ctx.guild.name} roles [{len(ctx.guild.roles)}]", description=messages[i])
            number.append(embed)
            if len(number) > 1:
             paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
             paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
             paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
             paginator.add_button('next', emoji="<:right:1018156484170883154>")
             await paginator.start() 
            else:
              await sendmsg(self, ctx, None, embed, None, None, None)

    @command(help="see all server's bots", description="utility")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def bots(self, ctx: Context):
            i=0
            k=1
            l=0
            b=0
            mes = ""
            number = []
            messages = []
            for member in ctx.guild.members:
             if member.bot:  
              b+=1   
              mes = f"{mes}`{k}` {member} - ({member.id})\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=Colors.default, title=f"{ctx.guild.name} bots [{b}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = Embed(color=Colors.default, title=f"{ctx.guild.name} bots [{b}]", description=messages[i])
            number.append(embed)
            if len(number) > 1:
             paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
             paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
             paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
             paginator.add_button('next', emoji="<:right:1018156484170883154>")
             await paginator.start()  
            else:
              await sendmsg(self, ctx, None, embed, None, None, None)
                
    @command(help="show user information", description="utility", usage=">user>", aliases=["whois", "ui", "user"])
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def userinfo(self, ctx: Context, *, member: Union[Member, User]=None):
     if member is None:
        member = ctx.author 
     
     button = Button(label="profile", url=f"https://discord.com/users/{member.id}")
     view = View()
     view.add_item(button)
     
     user = await self.bot.fetch_user(member.id)
     discrim = ["0001", "1337", "0002", "9999", "0666", "0888", "6969", "0069"]
     badges = []
     devices = []
     if user.public_flags.early_supporter:
      badges.append("<:early:1059877874099826700>")
     if user.public_flags.verified_bot_developer:
       badges.append("<:developer:1059877861202342008>")
     if user.public_flags.staff: 
      badges.append("<:tl_staff:1059877847562465392>")
     if user.public_flags.bug_hunter:
      badges.append("<:bughunter:1059877929267507313>") 
     if user.public_flags.bug_hunter_level_2:
      badges.append("<:goldbughunter:1059877941393248367>")   
     if user.public_flags.partner:
      badges.append("<:partner:1059877903988445284>")
     if user.public_flags.discord_certified_moderator:
      badges.append("<:moderator:1059877885420261406>")
     if user.public_flags.hypesquad_bravery:
      badges.append("<:badgehypebravery:1059878083827617904>")
     if user.public_flags.hypesquad_balance:
      badges.append("<:badgehypebalanced:1059878101045215273>")
     if user.public_flags.hypesquad_brilliance:
      badges.append("<:badgehypebriliance:1059878064634470450>")  
     if user.discriminator in discrim or user.display_avatar.is_animated() or user.banner is not None:
      badges.append("<:nitro:1059878045818814506>")

     for guild in self.bot.guilds: 
      mem = guild.get_member(user.id)
      if mem is not None:
       if mem.premium_since is not None:
         badges.append("<:boost:1059878015099740211>")
         break

     if isinstance(member, Member):
      if member.mobile_status != Status.offline:
        devices.append("<:mobile:1059878291592458281>")
      if member.web_status != Status.offline:
        devices.append("<:global:1060930550044557342>")
      if member.desktop_status != Status.offline:
        devices.append("<:dsk:1059878231148347493>")

      if str(member.status) == "online":
       status = "<:o_online:1059878146914140271>"
      elif str(member.status) == "dnd":
       status = "<:o_dnd:1059878166484758698>"
      elif str(member.status) == "idle":
       status = "<:o_idle:1059878275641520128>"
      elif str(member.status) == "offline": 
       status = "<:o_offline:1059878189855428618>"
      e = Embed(color=Colors.default)
      e.title = user.name + " " + "".join(map(str, badges))
      if member.activities:
        for a in member.activities:
          if isinstance(a, Spotify):
            e.description = f"<:spotify:1059910363811942543> listening to [**{a.title}**]({a.track_url}) by [**{a.artist}**]({a.track_url}) on spotify"
      members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
      ordinal = Func.ordinal(int(members.index(member)+1))
      if member.premium_since:
        boosted = f"<t:{int(member.premium_since.timestamp())}:R>"
      else:
        boosted = "no"  
      e.set_author(name=f"{member} • {ordinal} member", icon_url=member.display_avatar.url)
      e.set_thumbnail(url=member.display_avatar.url)
      e.add_field(name="dates", value=f"**joined:** <t:{int(member.joined_at.timestamp())}:R>\n**created:** <t:{int(member.created_at.timestamp())}:R>\n**boosted:** {boosted}", inline=False)
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
        role_string = "None" 
      e.add_field(name="others", value=f"**status:** {active}\n**platform{'s' if len(devices) > 1 else ''}:** {platform}\n**roles:** {role_string}", inline=False) 
      try:  
       e.set_footer(text='ID: ' + str(member.id) + f" | {len(member.mutual_guilds)} mutual server(s)")
      except: 
         e.set_footer(text='ID: ' + str(member.id))
      await sendmsg(self, ctx, None, e, view, None, None)
      return
     elif isinstance(member, User):
      e = Embed(color=Colors.default)
      e.title = user.name + " " + "".join(map(str, badges))
      e.set_author(name=f"{member}", icon_url=member.display_avatar.url)
      e.set_thumbnail(url=member.display_avatar.url)
      e.add_field(name="created", value=f"<t:{int(member.created_at.timestamp())}:F>\n<t:{int(member.created_at.timestamp())}:R>", inline=False)
      e.set_footer(text='ID: ' + str(member.id))
      await sendmsg(self, ctx, None, e, None, None, None)

    @command(help="show server information", aliases=["si", "serverinfo", "guild"], description="utility", usage="[subcommand] <server id>", brief="server info - shows server info\nserver avatar - shows server's avatar\nserver banner - shows server's banner\nserver splash - shows server's invite background")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def server(self, ctx: Context, choice=None, *, id: int=None):
      if choice == "info" or choice is None:
        if id is None:
           guild = ctx.guild
        else:
            guild = self.bot.get_guild(id)
        
        if guild is None:
            e = Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: unable to find this guild")
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
         icon = "no icon"

        if guild.splash is not None:
         splash = f"[splash]({guild.splash.url})"
        else:
         splash = "no splash"

        if guild.banner is not None:
         banner = f"[banner]({guild.banner.url})"
        else:
         banner = "no banner"

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

        embed = Embed(color=Colors.default, title=guild.name, description=f"created <t:{int(guild.created_at.timestamp())}:F> (<t:{int(guild.created_at.timestamp())}:R>)\n{desc}")   
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="owner", value=f"{guild.owner.mention}\n{guild.owner}")
        embed.add_field(name=f"channels ({len(ctx.guild.channels)})", value=f"**text:** {len(guild.text_channels)}\n**voice:** {len(guild.voice_channels)}\n**categories** {len(guild.categories)}")
        embed.add_field(name="members", value=f"**users:** {i} ({(i/guild.member_count) * 100:.2f}%)\n**bots:** {j} ({(j/guild.member_count) * 100:.2f}%)\n**total:** {guild.member_count}")
        embed.add_field(name="links", value=f"{icon}\n{splash}\n{banner}")
        embed.add_field(name="info", value=f"**verification:** {guild.verification_level}\n**vanity:** {guild.vanity_url_code}")
        embed.add_field(name="counts", value=f"**roles:** {len(guild.roles)}/250\n**boosts:** {guild.premium_subscription_count} (level {guild.premium_tier})\n**boosters:** {b}\n**emojis:** {len(guild.emojis)}/{guild.emoji_limit*2}\n**stickers:** {len(guild.stickers)}/{guild.sticker_limit}")
        embed.set_footer(text=f"ID: {guild.id}")
        await sendmsg(self, ctx, None, embed, None, None, None)
      elif choice == "banner":
        if id is None:
           guild = ctx.guild
        else:
            guild = self.bot.get_guild(id)
        
        if guild is None:
            e = Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: unable to find this guild")
            await sendmsg(self, ctx, None, e, None, None, None)
            return 

        if not guild.banner:
            em = Embed(color=Colors.yellow, description=f"{Emojis.wrong} {ctx.author.mention}: this server has no banner")
            await sendmsg(self, ctx, None, em, None, None, None)
            return 

        embed = Embed(color=Colors.default, title=f"{guild.name}'s banner", url=guild.banner.url)   
        embed.set_image(url=guild.banner.url)
        await sendmsg(self, ctx, None, embed, None, None, None)
      elif choice == "avatar" or choice == "icon":
        if id is None:
           guild = ctx.guild
        else:
            guild = self.bot.get_guild(id)
        
        if guild is None:
            e = Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: unable to find this guild")
            await sendmsg(self, ctx, None, e, None, None, None)
            return 

        if not guild.icon:
            em = Embed(color=Colors.yellow, description=f"{Emojis.wrong} {ctx.author.mention}: this server has no icon")
            await sendmsg(self, ctx, None, em, None, None, None)
            return 
        
        if guild.icon is not None:
            embed = Embed(color=Colors.default, title=f"{guild.name}'s avatar", url=guild.icon.url)   
            embed.set_image(url=guild.icon.url)
            await sendmsg(self, ctx, None, embed, None, None, None)   
      elif choice == "splash":
        if id is None:
           guild = ctx.guild
        else:
            guild = self.bot.get_guild(id)
        
        if guild is None:
            e = Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: unable to find this guild")
            await sendmsg(self, ctx, None, e, None, None, None)
            return 

        if not guild.splash:
            em = Embed(color=Colors.yellow, description=f"{Emojis.wrong} {ctx.author.mention}: this server has no splash")
            await sendmsg(self, ctx, None, em, None, None, None)
            return 

        embed = Embed(color=Colors.default, title=f"{guild.name}'s splash", url=guild.splash.url)   
        embed.set_image(url=guild.splash.url)
        await sendmsg(self, ctx, None, embed, None, None, None)
      else:
        await commandhelp(self, ctx, ctx.command.name)  

    @command(help="shows the number of invites an user has", usage="<user>", description="utility")
    @cooldown(1, 3, BucketType.user)
    @blacklist()
    async def invites(self, ctx: Context, *, member: Member=None):
      if member is None: member = ctx.author 
      inviteuses = 0 
      invites = await ctx.guild.invites()
      for invite in invites:
        if invite.inviter.id == member.id:
         inviteuses = inviteuses + invite.uses
      await sendmsg(self, ctx, f"{member} has **{inviteuses}** invites", None, None, None, None)

    @command(help="gets the invite link with administrator permission of a bot", description="utility", usage="[bot id]")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def getbotinvite(self, ctx, id: User=None):
     if id is None:
        await commandhelp(self, ctx, ctx.command.name)
        return
     else:    
      if not id.bot: return await sendmsg(self, ctx, "this isn't a bot", None, None, None, None)
      embed = Embed(color=Colors.default, description=f"**[invite the bot](https://discord.com/api/oauth2/authorize?client_id={id.id}&permissions=8&scope=bot%20applications.commands)**")
      await sendmsg(self, ctx, None, embed, None, None, None)
   
    @command(help="gets the banner from a server based by invite code\n(misery doesn't need to be in the server)", description="utility", usage="[invite code]")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
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

      embed = Embed(color=Colors.default, title=data["guild"]["name"] + "'s banner")
      embed.set_image(url="https://cdn.discordapp.com/banners/" + data["guild"]["id"] + "/" + data["guild"]["banner"] + f"{format}?size=1024")
      await sendmsg(self, ctx, None, embed, None, None, None)
     except:
      e = Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: Couldn't get **" + data["guild"]["name"] + "'s** banner")
      await sendmsg(self, ctx, None, e, None, None, None)

    @command(help="gets the splash from a server based by invite code\n(misery doesn't need to be in the server)", description="utility", usage="[invite code]")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def splash(self, ctx, *, link=None):
     if link == None:
      await commandhelp(self, ctx, ctx.command.name)
      return

     try: 
      invite_code = link
      async with aiohttp.ClientSession() as cs:
       async with cs.get(DISCORD_API_LINK + invite_code) as r:
        data = await r.json()

      embed = Embed(color=Colors.default, title=data["guild"]["name"] + "'s splash")
      embed.set_image(url="https://cdn.discordapp.com/splashes/" + data["guild"]["id"] + "/" + data["guild"]["splash"] + ".png?size=1024")
      await sendmsg(self, ctx, None, embed, None, None, None)
     except:
      e = Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: Couldn't get **" + data["guild"]["name"] + "'s** splash image")
      await sendmsg(self, ctx, None, e, None, None, None)

    @command(help="gets the icon from a server based by invite code\n(abort doesn't need to be in the server)", description="utility", usage="[invite code]")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
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
          
      embed = Embed(color=Colors.default, title=data["guild"]["name"] + "'s icon")
      embed.set_image(url="https://cdn.discordapp.com/icons/" + data["guild"]["id"] + "/" + data["guild"]["icon"] + f"{format}?size=1024")
      await sendmsg(self, ctx, None, embed, None, None, None)
     except:
      e = Embed(color=Colors.red, description=f"{Emojis.wrong} {ctx.author.mention}: Couldn't get **" + data["guild"]["name"] + "'s** icon")
      await sendmsg(self, ctx, None, e, None, None, None)              
  
    @command(help="gets information about a github user", aliases=["gh"], description="utility", usage="[user]")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def github(self, ctx, *, user=None):
        if user == None:
            await commandhelp(self, ctx, ctx.command.name)
            return
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f'https://api.github.com/users/{user}') as r:
                    res = await r.json()
                    name=res['login']
                    avatar_url=res['avatar_url']
                    html_url=res['html_url']
                    email=res['email']
                    public_repos=res['public_repos']
                    followers=res['followers']
                    following=res['following']
                    twitter = res['twitter_username']
                    location=res['location']
                    embed = Embed(color=Colors.default, title = f"@{name}", url=html_url)
                    embed.set_thumbnail(url=avatar_url)
                    embed.add_field(name="Followers", value=followers)
                    embed.add_field(name="Following", value=following)
                    embed.add_field(name="Repos", value=public_repos)
                    if email:
                        embed.add_field(name="Email", value=email)
                    if location:
                        embed.add_field(name="Location", value=location)
                    if twitter:
                        embed.add_field(name="Twitter", value=twitter)
                    
                    embed.set_thumbnail(url=avatar_url)
                    await sendmsg(self, ctx, None, embed, None, None, None)
        except:
            e = Embed(color=Colors.yellow, description=f"{Emojis.Emojis.warninging} {ctx.author.mention}: Could not find [@{user}](https://github.com/@{user})")
            await sendmsg(self, ctx, None, e, None, None, None) 

    @command(aliases=["tr"], help="translate words in the language you want", description="utility", usage="[language] [word]")
    @cooldown(1, 4, BucketType.user)
    @blacklist()
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
      embed = Embed(color=Colors.default, title=f"translated to {lang}", description=text, timestamp=datetime.datetime.now())
      await sendmsg(self, ctx, None, embed, None, None, None)

async def setup(bot):
    await bot.add_cog(Utility(bot))        