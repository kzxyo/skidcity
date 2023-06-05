import discord, button_paginator as pg 
from cogs.events import noperms, commandhelp, sendmsg, blacklist
from utils.classes import Colors, Emojis
from discord.ext import commands

class chatfilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS chatfilter (trigger TEXT, guild_id INTEGER)")
        await self.bot.db.commit()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
       if not message.guild: return
       if message.author.bot: return
       if message.type != discord.MessageType.default and message.type != discord.MessageType.reply: return
       me = message.content.lower()
       async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM chatfilter WHERE guild_id = {}".format(message.guild.id))
        results = await cursor.fetchall()
        if results is not None: 
          for result in results: 
            if result[0] in me:
              await message.delete()
    
    @commands.command(aliases=["cf"], help= "set blacklisted words for this server", description="config", usage="[subcommand] [word]", brief="chatfilter add - add a blacklisted word\nchatfilter remove - remove a blacklisted word\nchatfilter list - see a list of blacklisted words")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def chatfilter(self, ctx: commands.Context, subcommand=None, *, trigger=None):
     if not ctx.author.guild_permissions.manage_guild:
        await noperms(self, ctx, "manage_guild")
        return 

     if subcommand is None:
        await commandhelp(self, ctx, ctx.command.name)
        return 
     elif subcommand == "add":
        if trigger is None:
            await commandhelp(self, ctx, ctx.command.name)
            return 
        async with self.bot.db.cursor() as cursor: 
           t = ("%"+trigger.lower()+"%",)
           await cursor.execute(f"SELECT * FROM chatfilter WHERE guild_id = {ctx.guild.id} AND trigger LIKE ?", t)
           check = await cursor.fetchone()
           if check is None: 
            await cursor.execute("INSERT INTO chatfilter VALUES (?,?)", (trigger.lower(), ctx.guild.id))
            await self.bot.db.commit() 
           await sendmsg(self, ctx, None, discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: added `{trigger}` as blacklisted word"), None, None, None)
     elif subcommand == "remove":
       if trigger is None:
            await commandhelp(self, ctx, ctx.command.name)
            return
       async with self.bot.db.cursor() as cursor: 
           t = ("%"+trigger+"%",)
           await cursor.execute(f"SELECT * FROM chatfilter WHERE guild_id = {ctx.guild.id} AND trigger LIKE ?", t)
           check = await cursor.fetchone()
           if check is not None: 
            await cursor.execute(f"DELETE FROM chatfilter WHERE guild_id = {ctx.guild.id} AND trigger LIKE ?", t) 
            await self.bot.db.commit()      
            await sendmsg(self, ctx, None, discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: deleted `{trigger}` from blacklisted words"), None, None, None) 
           elif check is None: 
             await sendmsg(self, ctx, None, discord.Embed(color=Colors.yellow, description=f"{Emojis.warning} {ctx.author.mention}: there is no blacklisted word with this trigger `{trigger}`"), None, None, None) 
     elif subcommand == "list":
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM chatfilter WHERE guild_id = {}".format(ctx.guild.id))
            results = await cursor.fetchall()
            if len(results) == 0:
                return await ctx.reply("there are no blacklisted words")
            for result in results:
              mes = f"{mes}`{k}` {result[0]} - {(result[1])}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(discord.Embed(color=Colors.default, title=f"blacklisted words ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
            
            messages.append(mes)
            embed = discord.Embed(color=Colors.default, title=f"blacklisted words ({len(results)})", description=messages[i])
            number.append(embed)
            if len(number) > 1:
             paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
             paginator.add_button('prev', emoji= "<:left:1076415738493018112>")
             paginator.add_button('delete', emoji = "<:delete:1076415715449516083>")
             paginator.add_button('next', emoji="<:right:1076415697510477856>")
             await paginator.start()
            else:
             await sendmsg(self, ctx, None, embed, None, None, None)

async def setup(bot):
  await bot.add_cog(chatfilter(bot))  