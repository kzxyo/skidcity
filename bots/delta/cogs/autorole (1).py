import discord, json
from discord.ext import commands
from pymongo import MongoClient 

with open("./config.json") as f:
    data = json.load(f)
    mongo = data["mongo"]

cluster = MongoClient(mongo)
db = cluster["test"]

class autorole(commands.Cog):
 def __init__(self, bot):
        self.bot = bot
        self._last_member = None

 @commands.Cog.listener()
 async def on_member_join(self, member):
  if member.bot:
        autorole = db["autorole_bots"]
        chek = autorole.find_one({"_id": member.guild.id})
        if chek is None:
            pass
        else:
            try:
             role_id = chek["role"]
             role = member.guild.get_role(role_id)
             await member.add_roles(role)
            except:
                pass   
  else:
        auto = db["autorole_humans"]
        chec = auto.find_one({"_id": member.guild.id})
        if chec is None:
            try: 
             jail = db["jail_member"]
             isjail = db["jail"]
             checkisjail = isjail.find_one({"_id": member.guild.id})
             if checkisjail is None:
                pass

             isjailed = jail.find_one({"guildid": member.guild.id, "memberid": member.id})
             if isjailed is not None:
                roleid = checkisjail["role"]
                role = member.guild.get_role(roleid)
                await member.add_roles(role)
                pass
             elif isjailed is None:
              role_id = chec["role"]
              role = member.guild.get_role(role_id)
              await member.add_roles(role)  
            except:
               pass  
        elif chec is not None:
           try: 
            jail = db["jail_member"]
            isjail = db["jail"]
            checkisjail = isjail.find_one({"_id": member.guild.id})
            if checkisjail is None:
                pass

            isjailed = jail.find_one({"guildid": member.guild.id, "memberid": member.id})
            if isjailed is not None:
                roleid = checkisjail["role"]
                role = member.guild.get_role(roleid)
                await member.add_roles(role)
                pass
            elif isjailed is None: 
             role_id = chec["role"]
             role = member.guild.get_role(role_id)
             await member.add_roles(role)  
           except:
               pass              

 @commands.command()
 async def autorole(self, ctx, option=None, category=None, *, role: discord.Role=None):
  if (not ctx.author.guild_permissions.manage_guild):
     emb = discord.Embed(color=discord.Color.yellow(), description=f"> {ctx.author.mention} you are missing permissions __`manage_server`__")
     await ctx.reply(embed=e, mention_author=False)
     return  
  if option == None:
            emb = discord.Embed(color=0x2f3136, title="**autorole**", description="> __gives specific role if a member or bot joins the server__")
            emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            emb.add_field(name="**category**", value="> __config__")
            emb.add_field(name="**permissions**", value="> __manage_server__")
            emb.add_field(name="**usage**", value="> ```autorole [set / unset] [bots / humans] <role> (role optional if unset option was choosen)```", inline=False)
            emb.add_field(name="**aliases**", value="> __none__")
            await ctx.reply(embed=emb, mention_author=False) 
            return  
  if option == "set":
      if category == "bots":
          if role == None:
            emb = discord.Embed(color=0x2f3136, title="**autorole**", description="> __gives specific role if a member or bot joins the server__")
            emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            emb.add_field(name="**category**", value="> __config__")
            emb.add_field(name="**permissions**", value="> __manage_server__")
            emb.add_field(name="**usage**", value="> ```autorole [set / unset] [bots / humans] <role> (role optional if unset option was choosen)\n> autorole set bots bot```", inline=False)
            emb.add_field(name="**aliases**", value="> __none__")
            await ctx.reply(embed=emb, mention_author=False)  
          else:  
           collection = db["autorole_bots"]
           check = collection.find_one({"_id": ctx.guild.id})
           if check is None:
              insert = {
                "_id": ctx.guild.id, "role": role.id
              }
              collection.insert_one(insert)
              embed = discord.Embed(color=discord.Color.green(), description=f"**{ctx.author.mention}** **{role.mention}** set as autorole for __bots__")
              await ctx.reply(embed=embed, mention_author=False)
              return
           else:
               collection.update_one({"_id": ctx.author.id}, {"$set": {"role": role.id}})
               emb = discord.Embed(color=discord.Color.green(), description=f"**{ctx.author.mention} {role.mention} ** updated as autorole for __bots__")   
               await ctx.reply(embed=emb, mention_author=False)
               return
      elif category == "humans":
            if role == None:
             emb = discord.Embed(color=0x2f3136, title="**autorole**", description="> __gives specific role if a member or bot joins the server__")
             emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
             emb.add_field(name="**category**", value="> __config__")
             emb.add_field(name="**permissions**", value="> __manage_server__")
             emb.add_field(name="**usage**", value="> ```autorole [set / unset] [bots / humans] <role> (role optional if unset option was choosen)\n> autorole set bots bot```", inline=False)
             emb.add_field(name="aliases", value="none")
             await ctx.reply(embed=emb, mention_author=False)  
            else:  
             collection = db["autorole_humans"]
             check = collection.find_one({"_id": ctx.guild.id})
             if check is None:
              insert = {
                "_id": ctx.guild.id, "role": role.id
              }
              collection.insert_one(insert)
              embed = discord.Embed(color=discord.Color.green(), description=f"**{ctx.author.mention} {role.mention}** set as autorole for __humans__")
              await ctx.reply(embed=embed, mention_author=False)
              return
             else:
               collection.update_one({"_id": ctx.author.id}, {"$set": {"role": role.id}})
               emb = discord.Embed(color=discord.Color.green(), description=f"**{ctx.author.mention} {role.mention} ** updated as autorole for __humans__")   
               await ctx.reply(embed=emb, mention_author=False)   
               return
  elif option == "unset":  
      if category == "bots":
        if role == None:
            collection = db["autorole_bots"]
            check = collection.find_one({"_id": ctx.guild.id})
            if check is None:
                emb = discord.Embed(color=discord.Color.yellow(), description=f"{ctx.author.mention} i can't delete an unexisting autorole")
                await ctx.reply(embed=emb, mention_author=False)
            else:
                collection.delete_one({"_id": ctx.guild.id})
                e = discord.Embed(color=discord.Color.green(), description=f"**{ctx.author.mention}**: cleared the autorole for __bots__")
                await ctx.reply(embed=e, mention_author=False) 
                return
        else:
            collection = db["autorole_bots"]
            check = collection.find_one({"_id": ctx.guild.id})
            if check is None:
                emb = discord.Embed(color=discord.Color.yellow(), description=f"**{ctx.author.mention}** i can't delete an unexisting autorole")
                await ctx.reply(embed=emb, mention_author=False)
            else:
                collection.delete_one({"_id": ctx.guild.id})
                e = discord.Embed(color=discord.Color.green(), description=f"**{ctx.author.mention}**: cleared the autorole for __bots__")
                await ctx.reply(embed=e, mention_author=False)  
                return
      if category == "humans":  
             if role == None:
               collection = db["autorole_humans"]
               check = collection.find_one({"_id": ctx.guild.id})
               if check is None:
                emb = discord.Embed(color=discord.Color.yellow(), description=f"**{ctx.author.mention}** i can't delete an unexisting __autorole__")
                await ctx.reply(embed=emb, mention_author=False)
                return
               else:
                collection.delete_one({"_id": ctx.guild.id})
                e = discord.Embed(color=discord.Color.green(), description=f"**{ctx.author.mention}**: cleared the autorole for __humans__")
                await ctx.reply(embed=e, mention_author=False) 
                return
             else:
                collection = db["autorole_humans"]
                check = collection.find_one({"_id": ctx.guild.id})
             if check is None:
                emb = discord.Embed(color=discord.Color.yellow(), description=f"**{ctx.author.mention}** i can't delete an __unexisting autorole__")
                await ctx.reply(embed=emb, mention_author=False)
             else:
                collection.delete_one({"_id": ctx.guild.id})
                e = discord.Embed(color=discord.Color.green(), description=f"**{ctx.author.mention}**: cleared the autorole for __humans__")
                await ctx.reply(embed=e, mention_author=False)  
                return
  elif option == "list":
      col1 = db["autorole_bots"]
      col2 = db["autorole_humans"]
      humans = "None"
      bots = "None"
      check1 = col1.find_one({"_id": ctx.guild.id})
      check2 = col2.find_one({"_id": ctx.guild.id})
      if check1 is not None:
          nuj = check1["role"]
          bots = f"<@&{nuj}>"
      if check2 is not None:
          nuj2 = check2["role"]
          humans = f"<@&{nuj2}>"

      embed = discord.Embed(color=0x2f3136, title="**autorole list**")
      embed.add_field(name="> **humans**", value=humans)
      embed.add_field(name="> **bots**", value=bots)   
      await ctx.reply(embed=embed, mention_author=False)     

async def setup(bot) -> None:
    await bot.add_cog(autorole(bot))        