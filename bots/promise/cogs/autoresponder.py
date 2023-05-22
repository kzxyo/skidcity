import discord, button_paginator as pg 
from cogs.events import noperms, commandhelp, blacklist, sendmsg
from core.utils.classes import Colors, Emojis
from discord.ext import commands

class autoresponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self._cd = commands.CooldownMapping.from_cooldown(3, 6, commands.BucketType.guild) 

    def get_ratelimit(self, message):
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    @commands.Cog.listener()
    async def on_ready(self):
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS autoresponder (trigger TEXT, response TEXT, guild_id INTEGER)")
        await self.bot.db.commit()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message): 
       if not message.guild: return  
       if message.author.bot: return
       if message.attachments: return 
       if message.stickers: return
       if message.type != discord.MessageType.default and message.type != discord.MessageType.reply: return
       me = message.content.lower().split()
       async with self.bot.db.cursor() as cursor:
        await cursor.execute(f"SELECT * FROM autoresponder WHERE guild_id = {message.guild.id}") 
        results = await cursor.fetchall()
        if results is not None: 
          for result in results: 
            if result[0] in me:
              retry_after = self.get_ratelimit(message)
              if retry_after is not None: return
              return await message.channel.send(result[1], allowed_mentions=discord.AllowedMentions(users=True))
            
    @commands.command(help="set an autoresponder for the server", description="config", usage="[subcommand] [trigger] [response]", brief="autoresponder add - add an autoresponder\nautoresponder remove - remove an autoresponder\nautoresponder list - see a list of autoresponders", aliases=["ar"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def autoresponder(self, ctx: commands.Context, subcommand=None, trigger=None, *, response=None):
     if not ctx.author.guild_permissions.manage_guild:
        await noperms(self, ctx, "manage_guild")
        return 

     if subcommand is None:
        await commandhelp(self, ctx, ctx.command.name)
        return 
     elif subcommand == "add":
        if trigger is None or response is None:
            await commandhelp(self, ctx, ctx.command.name)
            return 
        async with self.bot.db.cursor() as cursor: 
           t = ("%"+trigger.lower()+"%",)
           await cursor.execute(f"SELECT * FROM autoresponder WHERE guild_id = {ctx.guild.id} AND trigger LIKE ?", t)
           check = await cursor.fetchone()
           if check is not None: 
            await cursor.execute("UPDATE autoresponder SET response = ? WHERE guild_id = ? AND trigger LIKE ?", (response, ctx.guild.id, t)) 
            await self.bot.db.commit()
           elif check is None: 
            await cursor.execute("INSERT INTO autoresponder VALUES (?,?,?)", (trigger.lower(), response, ctx.guild.id))
            await self.bot.db.commit() 
           await sendmsg(self, ctx, None, discord.Embed(color=Colors.green, description=f"added autoresponder with trigger `{trigger}` and response {response}"), None, None, None)
     elif subcommand == "remove":
       if trigger is None:
            await commandhelp(self, ctx, ctx.command.name)
            return
       async with self.bot.db.cursor() as cursor: 
           t = ("%"+trigger+"%",)
           await cursor.execute(f"SELECT * FROM autoresponder WHERE guild_id = {ctx.guild.id} AND trigger LIKE ?", t)
           check = await cursor.fetchone()
           if check is not None: 
            await cursor.execute(f"DELETE FROM autoresponder WHERE guild_id = {ctx.guild.id} AND trigger LIKE ?", t) 
            await self.bot.db.commit()      
            await sendmsg(self, ctx, None, discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: deleted autoresponder with trigger `{trigger}`"), None, None, None) 
           elif check is None: 
             await sendmsg(self, ctx, None, discord.Embed(color=Colors.green, description=f"{ctx.author.mention}: there is no autoresponder with trigger `{trigger}`"), None, None, None) 
     elif subcommand == "list":
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM autoresponder WHERE guild_id = {}".format(ctx.guild.id))
            results = await cursor.fetchall()
            if len(results) == 0:
                return await ctx.reply("there are no autoresponders")
            for result in results:
              mes = f"{mes}`{k}` {result[0]} - {(result[1])}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=Colors.green, title=f"autoresponders ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = discord.Embed(color=Colors.green, title=f"autoresponders for this server : {len(results)}", description=messages[i])
            number.append(embed)
            if len(number) > 1:
             paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
             paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
             paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
             paginator.add_button('next', emoji="<:right:1018156484170883154>")
             await paginator.start()
            else:
             await sendmsg(self, ctx, None, embed, None, None, None) 


async def setup(bot):
  await bot.add_cog(autoresponder(bot))        