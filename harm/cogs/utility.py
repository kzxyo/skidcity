import discord 
import aiohttp
import asyncio 
import re
import datetime

from typing import Optional
from discord.ext import commands 
from discord import Embed, File, TextChannel, Member, User, Role, Status, Message, Spotify, Message, AllowedMentions
from tools.bot import DiscordBot
from tools.context import HarmContext


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

class Utility(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot
        self.deleted_messages = {}


    @commands.Cog.listener()
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


    @commands.hybrid_command(help="afk", description="afk man", usage="[command]")
    async def afk(self, ctx, *, reason="AFK"):       
      result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id) 
      if result is None:
          await self.bot.db.execute("INSERT INTO afk (guild_id, user_id, reason) VALUES ($1, $2, $3)", ctx.guild.id, ctx.author.id, reason)
          embed = discord.Embed(description=f"> You're now AFK with the status: **{reason}**", color = 0xA8E97C)
          await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
      if message.author.bot:
          return

      mentioned_users = message.mentions
      for user in mentioned_users:
          result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, user.id)
          if result:
            await message.channel.send(embed=discord.Embed(description=f"{user.mention} is AFK: **{result['reason']}**", color = self.bot.color))
    
      result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)
      if result:
        await self.bot.db.execute("DELETE FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)
        await message.channel.send(embed=discord.Embed(description="> Welcome back, you are no longer AFK.", color = self.bot.color)) 

    @commands.hybrid_command(aliases=['sav', 'serveravatar'])
    async def memberavatar(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.guild_avatar
        if avatar_url:
            embed = discord.Embed(title=f"{member.name}'s server avatar", url=avatar_url)
            embed.set_image(url=avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("This member doesn't have a server avatar set.")

    @commands.hybrid_command(aliases=['av', 'pfp'])
    async def avatar(self, ctx, *, member: Optional[discord.User | discord.Member] = None):
        member = member or ctx.author
        avatar_url = member.avatar
        if avatar_url:
            embed = discord.Embed(title=f"{member.name}'s avatar", url=avatar_url, color=0x2f3136)
            embed.set_image(url=avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("This member doesn't have an avatar set.")

    @commands.hybrid_command()
    async def banner(self, ctx, user: discord.Member = None):
      if user == None:
          user = ctx.author
      req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
      banner_id = req["banner"]
      if banner_id:
          banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}?size=1024"
          
          embed = discord.Embed(title=f"{user.name}'s banner", url=banner_url, color=0x2f3136)
          embed.set_image(url=banner_url)
          await ctx.send(embed=embed)
      else:
          await ctx.send("This member doesn't have an banner set.")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.content:
            channel_id = message.channel.id
            if channel_id not in self.deleted_messages:
                self.deleted_messages[channel_id] = []

            content = message.content
            if self.contains_invite_link(content):
                content = f" {Emoji.warn} This message contains an invite link."

            self.deleted_messages[channel_id].append((content, message.author.name, message.created_at))

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            await self.on_message_delete(before)

    def contains_invite_link(self, content):
        invite_pattern = r"(discord.gg/|discord.com/invite/|discordapp.com/invite/)[a-zA-Z0-9]+"
        return bool(re.search(invite_pattern, content))

    @commands.hybrid_command(aliases=['s'])
    async def snipe(self, ctx, index: int = 1):
        channel_id = ctx.channel.id
        if channel_id in self.deleted_messages:
            deleted_list = self.deleted_messages[channel_id]
            total_deleted = len(deleted_list)
            if 1 <= index <= total_deleted:
                content, author, created_at = deleted_list[-index]

                embed = discord.Embed(description=content, color=0x2f3136)
                embed.set_author(name=author)

                central_tz = datetime.timezone(datetime.timedelta(hours=-4))
                created_at_central = created_at.astimezone(central_tz)
                time_difference = datetime.datetime.now(central_tz) - created_at_central

                embed.set_footer(text=f"{index}/{total_deleted}  |  {created_at_central.strftime('%I:%M %p')}")

                await ctx.send(embed=embed)
            else:
                await ctx.send("Invalid message.")
        else:
            await ctx.send("No recently deleted messages to snipe.")

    @commands.hybrid_command(aliases=['whois', 'wi', 'userinfo', 'user'])
    async def ui(self, ctx, member: discord.Member = None):
      member = member or ctx.author

      embed = discord.Embed(title="User Information", color=member.color)
      embed.set_thumbnail(url=member.avatar.url)
      embed.add_field(name="Name", value=member.name)
      embed.add_field(name="ID", value=member.id)
      embed.add_field(name="Created At",
                      value=member.created_at.strftime("%b %d, %Y %H:%M:%S UTC"))

      if member.top_role != member.guild.default_role:
        embed.add_field(name="Top Role", value=member.top_role.mention)
      embed.set_footer(text=f"Requested by {ctx.author.name}",
                       icon_url=ctx.author.avatar.url)
      await ctx.send(embed=embed)

    @commands.hybrid_command(      name="serverinfo",
      description="shows the information for your server",
      aliases=["si"]
    )
    async def serverinfo(self, ctx):
        guild = ctx.guild

        

        server_id = guild.id
        server_owner = guild.owner
        server_created_at = int(ctx.guild.created_at.timestamp())
        
        member_count = guild.member_count
        online_members = len([member for member in guild.members])

        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        category_channels = len(guild.categories)

        
        verification_level = str(guild.verification_level)

        
        server_icon_url = str(guild.icon) if guild.icon else None

        
        embed = discord.Embed(title="Server Info:", color=self.bot.color)
        embed.set_thumbnail(url=server_icon_url)
        embed.add_field(name="Server ID", value=server_id, inline=False)
        embed.add_field(name="Owner", value=server_owner, inline=False)
        embed.add_field(name ="server created:", value=f"<t:{server_created_at}:R>", inline=False)
        embed.add_field(name="Members", value=f"Total: {member_count}", inline=False)
        embed.add_field(name="Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}\nCategories: {category_channels}", inline=False)
        embed.add_field(name="Verification Level", value=verification_level, inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name='clearsnipe', aliases=['cs'])
    @commands.bot_has_guild_permissions(manage_messages=True)
    async def clearsnipe(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.deleted_messages:
            del self.deleted_messages[channel_id]
            await ctx.message.add_reaction("✅")

    @commands.hybrid_command(help="play blacktea with your friends", description="fun")
    async def blacktea(self, ctx): 
     try:
      if BlackTea.MatchStart[ctx.guild.id] is True: 
       return await ctx.reply("somebody in this server is already playing blacktea", mention_author=False)
     except KeyError: pass 

     BlackTea.MatchStart[ctx.guild.id] = True 
     embed = discord.Embed(color=self.bot.color, title="BlackTea Matchmaking", description=f"⏰ Waiting for players to join. To join react with 🍵.\nThe game will begin in **20 seconds**")
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
      return await ctx.send("😦 {}, not enough players joined to start blacktea".format(ctx.author.mention)) 
  
     while len(players) > 1: 
      for player in players: 
       strin = await BlackTea.get_string()
       await ctx.send(f"⏰ <@{player}>, type a word containing **{strin.upper()}** in **10 seconds**")
      
       def is_correct(msg): 
        return msg.author.id == player
      
       try: 
        message = await self.bot.wait_for('message', timeout=10, check=is_correct)
       except asyncio.TimeoutError: 
          try: 
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
            if BlackTea.lifes[player] == 3: 
              await ctx.send(f" <@{player}>, you're eliminated ☠️")
              BlackTea.lifes[player] = 0
              players.remove(player)
              continue 
          except KeyError:  
            BlackTea.lifes[player] = 0   
          await ctx.send(f"💥 <@{player}>, you didn't reply on time! **{2-BlackTea.lifes[player]}** lifes remaining")    
          continue
       if not strin.lower() in message.content.lower() or not message.content.lower() in await BlackTea.get_words():
          try: 
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
            if BlackTea.lifes[player] == 3: 
              await ctx.send(f" <@{player}>, you're eliminated ☠️")
              BlackTea.lifes[player] = 0
              players.remove(player)
              continue 
          except KeyError:  
            BlackTea.lifes[player] = 0 
          await ctx.send(f"💥 <@{player}>, incorrect word! **{2-BlackTea.lifes[player]}** lifes remaining")
       else: await message.add_reaction("✅")  
          
     await ctx.send(f"👑 <@{players[0]}> won the game!", allowed_mentions=AllowedMentions(users=True))
     BlackTea.lifes[players[0]] = 0
     BlackTea.MatchStart[ctx.guild.id] = False   
       
    @commands.hybrid_command(aliases=["mc"], help="check how many members does your server have", description="utility")
    async def membercount(self, ctx):
      b=len(set(b for b in ctx.guild.members if b.bot))
      h=len(set(b for b in ctx.guild.members if not b.bot))
      embed = discord.Embed(color=self.bot.color)
      embed.set_author(name=f"{ctx.guild.name}'s member count", icon_url=ctx.guild.icon)
      embed.add_field(name=f"members (+{len([m for m in ctx.guild.members if (datetime.datetime.now() - m.joined_at.replace(tzinfo=None)).total_seconds() < 3600*24 and not m.bot])})", value=h)
      embed.add_field(name="total", value=ctx.guild.member_count) 
      embed.add_field(name="bots", value=b)
      await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["rs"], help="check the latest reaction removal of a channel", usage="<channel>", description="utility")
    async def reactionsnipe(self, ctx, *, channel: TextChannel=None):
        if channel is None:
         channel = ctx.channel 
        try: 
         em = discord.Embed(color=self.bot.color, description=f"{reaction_message_emoji_name[channel.id]}\n[emoji link]({reaction_message_emoji_url[channel.id]})\n[message link](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{reaction_message_id[channel.id]})")
         em.set_author(name=reaction_message_author[channel.id], icon_url=reaction_message_author_avatar[channel.id])
         em.set_image(url=reaction_message_emoji_url[channel.id])
         await ctx.send(em=embed)
        except: 
          await ctx.send("there is no deleted reaction in {}".format(channel.mention))

    @commands.hybrid_command(aliases=["es"], help="check the latest edited messsage from a channel", usage="<channel>", description="utility") 
    async def editsnipe(self, ctx, *, channel: TextChannel=None):
     if channel is None: 
      channel = ctx.channel 
     try:
        em = Embed(color=self.bot.color, description=f"edited message in {channel.mention}- [jump](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{edit_message_id[channel.id]})")
        em.set_author(name=edit_message_author[channel.id], icon_url=edit_message_author_avatar[channel.id])
        em.add_field(name="old", value=edit_message_content1[channel.id])
        em.add_field(name="new", value=edit_message_content2[channel.id])
        await ctx.send(em=em)
     except:
        await ctx.send(f"there is no edited message in {channel.mention}")

async def setup(bot: DiscordBot):
    return await bot.add_cog(Utility(bot))    