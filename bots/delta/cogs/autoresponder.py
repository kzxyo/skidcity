import discord, json
from discord.ext import commands
from pymongo import MongoClient 
from pymongo.database import Database

class ar(commands.Cog):
    def __init__(self, bot):
       self.bot: commands.Bot = bot
       self.db: Database = self.bot.cluster["vilan"]
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
      if message.author != self.bot.user:
         auto = self.db["autoresponder"]
         che = auto.find_one({"guildid": message.guild.id, "trigger": message.content.lower()})
         if che is not None:
            response = che["response"]
            res = response.replace("[user_mention]", f"{message.author.mention}").replace("[user_tag]", f"{message.author}").replace("[user_name]", f"{message.author.name}")
            await message.channel.send(res)
         else:
            pass
    
    @commands.command(aliases=["ar"])
    async def autoresponder(self, ctx: commands.Context, subcommand: str=None, trigger: str=None, *, response: str=None) -> None:
     if (not ctx.author.guild_permissions.manage_guild):
      emb = discord.Embed(color=discord.Color.yellow(), description=f"> {ctx.author.mention} you are missing __permissions__ `manage_server`")
      await ctx.reply(embed=emb, mention_author=False)
      return

     if subcommand is None:
       e = discord.Embed(color=0x2f3136, title="**autoresponder**", description="> sets a __autoresponder__ for your server")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="**category**", value="> __config__", inline=True)
       e.add_field(name="**permissions**", value="> __manage_server__", inline=True)
       e.add_field(name="**subcommands**", value="> set - sets the autoresponder\n> unset - unsets the autoresponder\n> variables - check autoresponder's variables", inline=False)
       e.add_field(name="**usage**", value=f"> ```usage: autoresponder [subcommand] [trigger] [response]```", inline=False)
       e.add_field(name="**aliases**", value="> __ar__")
       await ctx.reply(embed=e, mention_author=False)  
       return 

     if subcommand == "set":
      if trigger is None or response is None:
         e = discord.Embed(color=0xff0000, description=f"> {ctx.author.mention} __trigger and reponse__ are required")
         await ctx.reply(embed=e, mention_author=False)
         return 

      collection = self.db["autoresponder"]
      check = collection.find_one({"guildid": ctx.guild.id, "trigger": trigger})
      if check is None:
         insert = {
             "guildid": ctx.guild.id, "trigger": trigger, "response": response
         }    
         collection.insert_one(insert)
         embed = discord.Embed(color=0x2f3136, title=f"> autoresponder __set__")
         res = response.replace("[user_mention]", f"{ctx.author.mention}").replace("[user_tag]", f"{ctx.author}").replace("[user_name]", f"{ctx.author.name}")
         embed.add_field(name="**trigger**", value=trigger)
         embed.add_field(name="**response**", value=res)
         await ctx.reply(embed=embed, mention_author=False)
         return
      elif check is not None:
         collection.update_one({"guildid": ctx.guild.id, "trigger": trigger}, {"$set": {"response": response}})
         e = discord.Embed(color=0x2f3136, title="> autoresponder __updated__")
         res = response.replace("[user_mention]", f"{ctx.author.mention}").replace("[user_tag]", f"{ctx.author}").replace("[user_name]", f"{ctx.author.name}")
         e.add_field(name="**trigger**", value=trigger)
         e.add_field(name="**response**", value=res)
         await ctx.reply(embed=e, mention_author=False)    
     elif subcommand == "unset":
      if trigger is None:
         e = discord.Embed(color=0xff0000, description=f"> {ctx.author.mention} __trigger__ is required")
         await ctx.reply(embed=e, mention_author=False)
         return

      collection = self.db["autoresponder"]
      check = collection.find_one({"guildid": ctx.guild.id, "trigger": trigger})
      if check is None:
         embed = discord.Embed(color=discord.Color.yellow(), description=f"> there isn't a autoresponder set with this __trigger__")
         await ctx.reply(embed=embed, mention_author=False)
         return
      elif check is not None:
         collection.delete_one({"guildid": ctx.guild.id, "trigger": trigger})
         e = discord.Embed(color=0x2f3136, title="autoresponder __deleted__")
         e.add_field(name="**trigger**", value=trigger)
         await ctx.reply(embed=e, mention_author=False)   

     elif subcommand == "variables":
      embed = discord.Embed(color=0x2f3136, title="> autoresponder __variables__", description=f"> [user_mention] - mentions user - {ctx.author.mention}\n > [user_tag] - shows user's full name - {ctx.author}\n > [user_name] - shows user's name - {ctx.author.name}")
      embed.set_thumbnail(url=self.bot.user.avatar.url)
      embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
      await ctx.reply(embed=embed, mention_author=False)   

async def setup(bot) -> None:
    await bot.add_cog(ar(bot))    