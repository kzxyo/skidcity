import discord, datetime
from discord.ext import commands

class Messages(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.snipes = {}
    
    @commands.Cog.listener('on_message')
    async def boost_listener(self, message: discord.Message): 
     if "MessageType.premium_guild" in str(message.type):
      if message.guild.id == 1060502285383376916: 
       member = message.author
       check = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = $1", member.id)
       if check: return 
       ts = int(datetime.datetime.now().timestamp())
       await self.bot.db.execute("INSERT INTO donor VALUES ($1,$2)", member.id, ts)  
       return await message.channel.send(f"{member.mention} ty for boosting, enjoy your perks! <:joobiheart:1083091785015885836>")    
    
    @commands.Cog.listener("on_message")
    async def seen_listener(self, message: discord.Message): 
      if not message.guild: return 
      if message.author.bot: return
      check = await self.bot.db.fetchrow("SELECT * FROM seen WHERE guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id))
      if check is None: return await self.bot.db.execute("INSERT INTO seen VALUES ($1,$2,$3)", message.guild.id, message.author.id, int(datetime.datetime.now().timestamp()))  
      ts = int(datetime.datetime.now().timestamp())
      await self.bot.db.execute("UPDATE seen SET time = $1 WHERE guild_id = $2 AND user_id = $3", ts, message.guild.id, message.author.id)
    
    @commands.Cog.listener("on_message")
    async def reposter(self, message: discord.Message): 
      if not message.guild: return 
      if message.author.bot: return 
      args = message.content.split(" ")
      if (args[0] == "vilan"):
        url = args[1] 
        if "tiktok" in url:
         async with message.channel.typing():  
          x = await self.bot.session.json("https://tikwm.com/api/", params={"url": url}) 
          video = x["data"]["play"]
          file = discord.File(fp=await self.bot.getbyte(video), filename="vilantiktok.mp4")
          embed = discord.Embed(color=self.bot.color, description=f"[{x['data']['title']}]({url})").set_author(name=f"@{x['data']['author']['unique_id']}", icon_url=x["data"]["author"]["avatar"])
          x = x["data"]
          embed.set_footer(text=f"❤ {self.bot.ext.human_format(x['digg_count'])}  💬 {self.bot.ext.human_format(x['comment_count'])}  🔗 {self.bot.ext.human_format(x['share_count'])}  👀 {self.bot.ext.human_format(x['play_count'])} | {message.author}", icon_url="https://media.discordapp.net/attachments/1060506008868376667/1124034551635771494/trapstar.png")
          await message.channel.send(embed=embed, file=file)
          try: await message.delete()
          except: pass
    
    @commands.Cog.listener("on_message")
    async def afk_listener(self, message: discord.Message):
     if not message.guild: return 
     if message.author.bot: return
     if message.mentions: 
      if len(message.mentions) == 1: 
        mem = message.mentions[0]
        check = await self.bot.db.fetchrow("SELECT * from afk where guild_id = $1 AND user_id = $2", message.guild.id, mem.id) 
        if check:
         em = discord.Embed(color=self.bot.color, description=f"**{mem}** is AFK since <t:{int(check['time'])}:R> - **{check['reason']}**")
         await message.reply(embed=em)
      else: 
       embeds = [] 
       for mem in message.mentions:
         check = await self.bot.db.fetchrow("SELECT * from afk where guild_id = $1 AND user_id = $2", message.guild.id, mem.id) 
         if check:
          em = discord.Embed(color=self.bot.color, description=f"**{mem}** is AFK since <t:{int(check['time'])}:R> - **{check['reason']}**")
          embeds.append(em)
         if len(embeds) == 10: 
           await message.reply(embeds=embeds)
           embeds = []
       if len(embeds) > 0: await message.reply(embeds=embeds)
       embeds = []

     che = await self.bot.db.fetchrow("SELECT * from afk where guild_id = $1 AND user_id = $2", message.guild.id, message.author.id) 
     if che:
      embed = discord.Embed(color=self.bot.color, description=f"You're back **{message.author}**, your AFK has been removed")
      await message.reply(embed=embed)
      await self.bot.db.execute("DELETE FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)    
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
     if not message.guild: return 
     if message.author.bot: return
     invites = ["discord.gg/", ".gg/", "discord.com/invite/"]
     if any(invite in message.content for invite in invites): return

     attachment = message.attachments[0].url if message.attachments else "none"
     author = str(message.author)
     content = message.content
     avatar = message.author.display_avatar.url 
     await self.bot.db.execute("INSERT INTO snipe VALUES ($1,$2,$3,$4,$5,$6,$7)", message.guild.id, message.channel.id, author, content, attachment, avatar, datetime.datetime.now())
    
async def setup(bot):
    await bot.add_cog(Messages(bot))