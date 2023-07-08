import discord, time, requests, calendar, json, asyncio
from discord.ext import commands
from typing import Union
from discord.ui import View, Button
from classes import Emotes, Colors, API_Keys
from pymongo import MongoClient
from pymongo.database import Database
start_time = time.time()
async def get(session: object, url: object) -> object:
    async with session.get(url) as response:
        return await response.text()

with open("db\config.json") as f:
    data = json.load(f)
    mongo = data["mongo"]


cluster = MongoClient(mongo)
db = cluster["roleplay"]


class roleplay(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.db: Database = self.bot.cluster["roleplay"]
# --------------------------------------------------------------------------------------- Kill command

    @commands.command(name = "kill", description = "Kill's specified user",aliases=['murder'], usage = "kill [user]")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kill(self, ctx, member:discord.Member = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You must mention someone", color=Colors.normal)
            await ctx.reply(embed=embed)
            return
        response = requests.get("https://api.waifu.pics/sfw/kill")
        data = response.json()
        s = discord.Embed(description=f"{ctx.author.mention} kills {member.mention}.", color=Colors.normal)
        s.set_footer(text="category: fun・Miro")
        s.set_image(url=data["url"])
        await ctx.send(embed=s)


# --------------------------------------------------------------------------------------- Smile command

    @commands.command(name = "smile", description = "Make user smile",aliases=['smiles'], usage = "smile")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def smile(self, ctx):
        response = requests.get("https://api.waifu.pics/sfw/smile")
        data = response.json()
        c = discord.Embed(description=f"{ctx.author.mention} smiles.", color=Colors.normal)
        c.set_footer(text="category: fun・Miro")
        c.set_image(url=data["url"])
        await ctx.send(embed=c)

# --------------------------------------------------------------------------------------- Advice Command
    
    @commands.command(name = "advice", description = "Give random advice/tips",aliases=['tips'], usage = "advice")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def advice(self, ctx):
        response = requests.get("https://luminabot.xyz/api/json/advice")
        data = response.json()
        advice = discord.Embed(description=f"**" + data["advice"] + "**", color=Colors.normal)
        advice.set_author(name="Miro's Advice", icon_url=f"{self.bot.user.avatar.url}", url="https://discord.gg/mirobot")
        advice.set_footer(text="category: fun・Miro")
        await ctx.send(embed=advice)


    @commands.command(name = "marry", description = "Marry specified user", aliases=['bond'], usage = "marry <user>")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def marry(self, ctx, *, member: discord.Member=None):
     if member == None:
       emb = discord.Embed(color=0x4c5264, title="**marry**", description="> __marry an user__")
       emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       emb.add_field(name="**category**", value="> __roleplay__")
       emb.add_field(name="**permissions**", value="> __any__")
       emb.add_field(name="**usage**", value="> ``marry [user]``", inline=False)
       emb.add_field(name="**aliases**", value="> __none__")
       await ctx.reply(embed=emb, mention_author=False) 
       return
     elif member == ctx.author:
        embe = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} you can't __marry yourself__")
        await ctx.reply(embed=embe, mention_author=False) 
        return 
     elif member.bot:
        em = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} robots can't __consent marriage__")
        await ctx.reply(embed=em, mention_author=False)
        return     
     else:
       collection = self.db["marry"]
       ts = calendar.timegm(time.gmtime())  
       meri = collection.find_one({"_id": member.id})
       if meri is not None:
           await ctx.reply("> uh oh! this user is __already married!__", mention_author=False)
           return
       else:
           mer = collection.find_one({"soulmate": member.id})
           if mer is not None:
               await ctx.reply("> uh oh! this user is __already married!__", mention_author=False)
               return
                    
       check = collection.find_one({"_id": ctx.author.id})
       if check is not None:
           emb = discord.Embed(color=discord.Color.yellow(), description=f"> {ctx.author.mention} you are already __married.__ don't try to **cheat!**")
           await ctx.reply(embed=emb, mention_author=False)
           return
       else:
           check2 = collection.find_one({"soulmate": ctx.author.id})
           if check2 is not None:
             emb = discord.Embed(color=discord.Color.yellow(), description=f"> {ctx.author.mention} you are already __married.__ don't try to **cheat!**")
             await ctx.reply(embed=emb, mention_author=False)  
             return
           else:
             button1 = Button(label="accept", style=discord.ButtonStyle.green)
             button2 = Button(label="refuse", style=discord.ButtonStyle.red)
             embed = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} wants to __marry you.__ do you accept?")
             async def button1_callback(interaction):
                 if interaction.user == ctx.author:
                     await interaction.response.send_message("> you can't accept your own __marriage__", ephemeral=True)
                 elif interaction.user != member:
                     await interaction.response.send_message("> you can't accept **this**", ephemeral=True)
                 else:                         
                  insert = {
                      "_id": ctx.author.id, "soulmate": member.id, "time": f"{ts}"
                  }
                  collection.insert_one(insert) 
                  embe = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} got __married__ with **{member.mention}**")
                  await interaction.response.edit_message(content=None, embed=embe, view=None)       
             button1.callback = button1_callback  

             async def button2_callback(interaction):
                  if interaction.user == ctx.author:
                     await interaction.response.send_message("> you can't accept your own __marriage__", ephemeral=True)
                  elif interaction.user != member:
                     await interaction.response.send_message("> you can't __accept__ this", ephemeral=True)
                  else:                         
                   embe = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} i'm sorry, but __{member.mention}__ is probably not the right person for you")
                   await interaction.response.edit_message(content=None, embed=embe, view=None)
             button2.callback = button2_callback  

             marry = View()
             marry.add_item(button1)
             marry.add_item(button2)
             await ctx.send(f"{member.mention}", embed=embed, view=marry) 

    @commands.command(name = "divorce", description = "Divorce specified user", aliases=['unbond'], usage = "divorce")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def divorce(self, ctx):
     collection = self.db["marry"]
     check = collection.find_one({"_id": ctx.author.id})
     if check is not None:
        button1 = Button(label="stay", style=discord.ButtonStyle.green)
        button2 = Button(label="divorce", style=discord.ButtonStyle.red)
        partner = check["soulmate"]
        embed = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} are you sure you want to __divorce__ with <@{partner}>")
        async def button1_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("> you can't interact with this __message__", ephemeral=True)
            else:
                collection.delete_one({"_id": ctx.author.id})
                emb = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} i'm sorry that you have decided to __divorce__")
                await interaction.response.edit_message(embed=emb, view=None)

        button1.callback = button1_callback

        async def button2_callback(interaction):
              if interaction.user != ctx.author:
                await interaction.response.send_message("> you can't __interact with this message__", ephemeral=True)
              else:
                emb = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} alright you __changed your mind__")
                await interaction.response.edit_message(embed=emb, view=None)

        button2.callback = button2_callback

        divorce = View()
        divorce.add_item(button1)
        divorce.add_item(button2)
        await ctx.send(embed=embed, view=divorce)   
     elif check is None:
        check2 = collection.find_one({"soulmate": ctx.author.id})
        if check2 is not None:
             button3 = Button(label="stay", style=discord.ButtonStyle.green)
             button4 = Button(label="divorce", style=discord.ButtonStyle.red)
             partner = check2["_id"]
             embed = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} are you sure you want to __divorce with <@{partner}> __")
             async def button3_callback(interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message("> you can't __interact with this message__", ephemeral=True)
                else:
                  collection.delete_one({"_id": partner})
                  emb = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} i'm sorry that you __have decided to divorce__")
                  await interaction.response.edit_message(embed=emb, view=None)

             button3.callback = button3_callback

             async def button4_callback(interaction):
                if interaction.user != ctx.author:
                  await interaction.response.send_message("> you can't __interact with this message__", ephemeral=True)
                else:
                  emb = discord.Embed(color=0x4c5264, description=f"> {ctx.author.mention} alright you __changed your mind__")
                  await interaction.response.edit_message(embed=emb, view=None)

             button4.callback = button4_callback

             divorce2 = View()
             divorce2.add_item(button3)
             divorce2.add_item(button4)
             await ctx.send(embed=embed, view=divorce2)  
        elif check2 is None: 
            embe = discord.Embed(color=discord.Color.yellow(), description=f"> {ctx.author.mention} you are not even __married__ <:sad:1115322647333568512>")
            await ctx.send(embed=embe)        

    @commands.command(name = "marriage", description = "Check marriage info", aliases=['wedding'], usage = "marriage")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def marriage(self, ctx, *, user: discord.User=None):
     if user == None:
        user = ctx.author

     collection = self.db["marry"]
     check = collection.find_one({"_id": user.id})
     if check is not None:
        time = check["time"]
        partner = check["soulmate"]
        embed = discord.Embed(color=0x4c5264, description = f"> __{user.mention} ❤️ <@{partner}>__\n<t:{time}:R>")
        await ctx.reply(embed=embed, mention_author=False)
     else:
        check2 = collection.find_one({"soulmate": user.id})
        if check2 is not None:
           time = check2["time"]
           partner = check2["_id"]
           embed = discord.Embed(color=0x4c5264, description = f"> __{user.mention} ❤️ <@{partner}>__\n<t:{time}:R>")
           await ctx.reply(embed=embed, mention_author=False)  
        else:
            embe = discord.Embed(color=0x4c5264, description=f"> {user.mention} __isn't even married <:sad:1115322647333568512> __")
            await ctx.reply(embed=embe, mention_author=False)         



    @commands.command(name="adopt", description="Adopt specified user", usage="adopt <user>", aliases=['adoption'])
    async def adopt(self, ctx, *, member: discord.Member = None):
        if member is None:
            await ctx.reply("Please specify a user to adopt.", mention_author=False)
            return

        collection = self.db["adopt"]

        check = collection.find_one({"_id": member.id})
        if check is not None:
            await ctx.reply(f"{member.mention} is already adopted.", mention_author=False)
            return

        embed = discord.Embed(
            color=0x4c5264,
            description=f"{ctx.author.mention} wants to adopt {member.mention}. Do you accept?",
        )
        embed.set_footer(text="React with ✅ to accept or ❌ to decline.")

        message = await ctx.send(embed=embed)
        await message.add_reaction("<:miroapprove:1117144152363245638>")
        await message.add_reaction("<:mirodeny:1117144156507209829>")

        def check_reaction(reaction, user):
            return user == member and str(reaction.emoji) in ["<:miroapprove:1117144152363245638>", "<:mirodeny:1117144156507209829>"] and reaction.message.id == message.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check_reaction)
        except asyncio.TimeoutError:
            await ctx.send("Adoption request timed out.")
            return

        if str(reaction.emoji) == "<:miroapprove:1117144152363245638>":
            insert = {"_id": member.id, "adopter": ctx.author.id}
            collection.insert_one(insert)

            embed = discord.Embed(
                color=0x4c5264,
                description=f"{ctx.author.mention} has successfully adopted {member.mention}.",
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                color=0x4c5264,
                description=f"{ctx.author.mention} has declined to adopt {member.mention}.",
            )
            await ctx.send(embed=embed)

    @commands.command(name="children", description="Show all children of specified user", usage="children [user]", aliases=['childs', 'kids'])
    async def children(self, ctx, *, member: discord.Member = None):
        if member is None:
            member = ctx.author

        collection = self.db["adopt"]

        children = list(collection.find({"adopter": member.id}))
        count = len(children)  # Count the documents

        if count == 0:
            await ctx.reply(f"{member.mention} does not have any children.", mention_author=False)
            return

        embed = discord.Embed(color=0x4c5264)
        embed.set_author(name=f"Children of {member.name}", icon_url=member.avatar.url)

        child_mentions = [f"<@{child['_id']}>" for child in children]
        children_text = "\n".join(child_mentions)

        embed.add_field(name="Children", value=children_text)

        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="disown", description="Disown an adopted kid", usage="disown <user>", aliases=['abandon'])
    async def disown(self, ctx, *, member: discord.Member = None):
        if member is None:
            await ctx.reply("Please specify a user to disown.", mention_author=False)
            return

        collection = self.db["adopt"]

        child = collection.find_one({"adopter": ctx.author.id, "_id": member.id})

        if child is None:
            await ctx.reply(f"{ctx.author.mention}, you have not adopted {member.mention}.", mention_author=False)
            return

        embed = discord.Embed(
            color=0x4c5264,
            description=f"{ctx.author.mention}, are you sure you want to disown {member.mention}?"
        )
        embed.set_footer(text="React with ✅ to confirm or ❌ to cancel.")

        message = await ctx.send(embed=embed)
        await message.add_reaction("<:miroapprove:1117144152363245638>")
        await message.add_reaction("<:mirodeny:1117144156507209829>")

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["<:miroapprove:1117144152363245638>", "<:mirodeny:1117144156507209829>"] and reaction.message.id == message.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check_reaction)
        except asyncio.TimeoutError:
            await ctx.send("Disown operation timed out.")
            return

        if str(reaction.emoji) == "<:miroapprove:1117144152363245638>":
            collection.delete_one({"adopter": ctx.author.id, "_id": member.id})
            await ctx.send(f"{ctx.author.mention}, you have disowned {member.mention}.")
        else:
            await ctx.send("Disown operation canceled.")

    @commands.command(name="runaway", description="Run away from your adoptive parent", usage="runaway")
    async def runaway(self, ctx):
        collection = self.db["adopt"]

        child = collection.find_one({"_id": ctx.author.id})

        if child is None:
            await ctx.reply("You are not currently adopted.", mention_author=False)
            return

        parent = ctx.guild.get_member(child["adopter"])

        embed = discord.Embed(
            color=0x4c5264,
            description=f"{ctx.author.mention} wants to run away from {parent.mention}. Are you sure?"
        )

        confirmation_message = await ctx.send(embed=embed)
        await confirmation_message.add_reaction("<:miroapprove:1117144152363245638>")
        await confirmation_message.add_reaction("<:mirodeny:1117144156507209829>")

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["<:miroapprove:1117144152363245638>", "<:mirodeny:1117144156507209829>"] and reaction.message.id == confirmation_message.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=35.0, check=check_reaction)
        except asyncio.TimeoutError:
            await confirmation_message.edit(content="Running away operation timed out.")
            return

        if str(reaction.emoji) == "<:miroapprove:1117144152363245638>":
            collection.delete_one({"_id": ctx.author.id})
            await ctx.send(f"{ctx.author.mention}, you have successfully run away from {parent.mention}.")
        elif str(reaction.emoji) == "<:mirodeny:1117144156507209829>":
            await ctx.send("Running away canceled.")

async def setup(bot) -> None:
    await bot.add_cog(roleplay(bot))