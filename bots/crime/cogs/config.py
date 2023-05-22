
import discord, datetime ; from discord.ext.commands import command, Cog, AutoShardedBot as Bot, cooldown, check, BucketType, group, has_permissions ; import button_paginator as pg, aiohttp
from discord import Embed ; from io import BytesIO
from .utils.util import Colors, Emojis ; from .modules import utils ; from cogs.utilevents import blacklist, commandhelp, noperms, sendmsg
from discord.ui import Modal ; from datetime import datetime

 
def get_ratelimit(self, message):
    bucket = self._cd.get_bucket(message)
    return bucket.update_rate_limit()

class config(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

 

    ##--------------- TICKETS ---------------##




class closeticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
      
    @discord.ui.button(label = "Close", emoji = f"<:crimetlock:1084516538071130252>", style=discord.ButtonStyle.grey, custom_id="persistent_view:closeticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
      async with interaction.client.db.cursor() as cursor: 
        await cursor.execute("DELETE FROM ticketusers WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id))
        await interaction.client.db.commit()  
        await interaction.response.send_message("Closing Ticket...", ephemeral=True)
        await interaction.channel.delete()

class ticketb(discord.ui.View):
    def __init__(self):
     super().__init__(timeout=None)
      
    @discord.ui.button(label = "", emoji = f"<:crimeticket:1084515587851558912>", style=discord.ButtonStyle.grey, custom_id="persistent_view:ticket")
    async def ticketbt(self, interaction: discord.Interaction, button: discord.ui.Button):
      async with interaction.client.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM ticketusers WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id))
        check = await cursor.fetchone()
        if check is not None:
          embed=discord.Embed(description=f"{interaction.user.mention} you already have a ticket made, please close it before making a new one", color=0xf7f9f8)
          await interaction.response.send_message(embed=embed, ephemeral=True)
        elif check is None:
          overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True)
        }
          channel = await interaction.guild.create_text_channel(f'{interaction.user.name}{interaction.user.discriminator}', overwrites=overwrites)
          async with interaction.client.db.cursor() as cursor:  
            await cursor.execute("INSERT INTO ticketusers VALUES (?, ?)", (interaction.guild.id, interaction.user.id))
            await interaction.client.db.commit()  
            await interaction.response.send_message(f"Ticket Created -- {channel.mention}", ephemeral=True)
            await channel.send(f"{interaction.user.mention}", embed=discord.Embed(title = f"<:crimeticket:1084515587851558912> Ticket Created", description = "Thank you for creating a ticket, staff will be right with you shortly.", color = 0xf7f9f8), view=closeticket())

      
    
    @command(help="adds ticket module to your server", description="config", brief=">>> ticket set - setups ticket module\nticket unset - remove ticket module", usage="[option]", aliases=["tickets"]) 
    @blacklist()
    @cooldown(1, 5, BucketType.user)
    async def ticket(self, ctx, option=None):
        if (not ctx.author.guild_permissions.administrator):
            await noperms(self, ctx, "administrator")
            return
        elif option == "set":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM tickets WHERE guild_id = {}".format(ctx.guild.id))
                check = await cursor.fetchone()
                if check is not None:
                    em = discord.Embed(color=0xf7f9f8, description=f"{ctx.author.mention} the ticket module has already been setup for this server")
                    await ctx.reply(embed=em, mention_author=False)
                    return
                elif check is None:
                    category = await ctx.guild.create_category("tickets")
                    overwrite = {ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False)}
                    embed = discord.Embed(title = f"Tickets", description = f"To initiate a ticket, please select the <:crimeticket:1084515587851558912> emoji.", color=0xf7f9f8)
                    embed.set_footer(text = f"powered by {self.bot.user.name}")
                    embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                    text = await ctx.guild.create_text_channel("tickets", category=category, overwrites=overwrite)
                    await text.send(embed=embed, view=ticketb())
                    await cursor.execute("INSERT INTO tickets VALUES (?,?)", (ctx.guild.id, text.id))
                    await self.bot.db.commit()
                    e = discord.Embed(color=0xf7f9f8, description=f"{Emojis.check} {ctx.author.mention} successfully configured ticket module")
                    await ctx.reply(embed=e, mention_author=False)
        elif option == "unset":
            async with self.bot.db.cursor() as cursor:
              await cursor.execute("SELECT * FROM tickets WHERE guild_id = {}".format(ctx.guild.id))
              check = await cursor.fetchone() 
              if check is None:
                em = discord.Embed(color=0xf7f9f8, description=f"{ctx.author.mention} ticket module isn't set")
                await ctx.reply(embed=em, mention_author=False)
                return
              elif check is not None:
                try:
                  interfaceid = check[1]
                  channel = ctx.guild.get_channel(interfaceid)
                  category = channel.category
                  channels = category.channels
                  for chan in channels:
                     try:
                         await chan.delete()
                     except:
                        continue

                  await category.delete()    
                  await channel.delete()      
                  await cursor.execute("DELETE FROM tickets WHERE guild_id = {}".format(ctx.guild.id))
                  await self.bot.db.commit()
                  embed = discord.Embed(color=0xf7f9f8, description=f"{Emojis.check} {ctx.author.mention} ticket module has been disabled")
                  await ctx.reply(embed=embed, mention_author=False) 
                  return
                except:
             
                 await cursor.execute("DELETE FROM tickets WHERE guild_id = {}".format(ctx.guild.id))
                 await self.bot.db.commit()
                 embed = discord.Embed(color=0xf7f9f8, description=f"{Emojis.check} {ctx.author.mention} ticket module has been disabled")
                 await ctx.reply(embed=embed, mention_author=False)  
        elif option == None:
            await commandhelp(self, ctx, ctx.command.name)
            return 


 
    @command(help="set an autoresponder for the server", description="config", usage="[subcommand] [trigger] [response]", brief="autoresponder add - add an autoresponder\nautoresponder remove - remove an autoresponder\nautoresponder list - see a list of autoresponders", aliases=["ar"])
    @cooldown(1, 5, BucketType.user)
    @blacklist()
    async def autoresponder(self, ctx, subcommand=None, trigger=None, *, response=None):
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
           await sendmsg(self, ctx, None, discord.Embed(color=Colors.green, description=f"{Emojis.check} {ctx.author.mention}: added autoresponder with trigger `{trigger}` and response {response}"), None, None, None)
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
             await sendmsg(self, ctx, None, discord.Embed(color=Colors.yellow, description=f"{Emojis.warn} {ctx.author.mention}: there is no autoresponder with trigger `{trigger}`"), None, None, None) 
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
               number.append(discord.Embed(color=0xf7f9f8, title=f"autoresponders ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            embed = discord.Embed(color=0xf7f9f8, title=f"autoresponders ({len(results)})", description=messages[i])
            number.append(embed)
            if len(number) > 1:
             paginator = pg.Paginator(self.bot, number, ctx, invoker=ctx.author.id)
             paginator.add_button('prev', emoji= "<:crimeleft:1082120060556021781>")
             paginator.add_button('delete', emoji = "<:crimestop:1082120074585981049>")
             paginator.add_button('next', emoji="<:crimeright:1082120065853423627>")
             await paginator.start()
            else:
             await sendmsg(self, ctx, None, embed, None, None, None) 


      
async def setup(bot):
    await bot.add_cog(config(bot))             