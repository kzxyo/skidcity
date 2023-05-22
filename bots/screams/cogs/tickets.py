import discord 
from discord.ext import commands, tasks
import random
import string
from utils.classes import colors, emojis
from discord.ui import Modal
from cogs.events import noperms, commandhelp


class closeticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
      
    @discord.ui.button(label = "Close", emoji = f"<:x_interface_lock:1059195157980926133>", style=discord.ButtonStyle.grey, custom_id="persistent_view:closeticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
      async with interaction.client.db.cursor() as cursor: 
        await cursor.execute("DELETE FROM ticketusers WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id))
        await interaction.client.db.commit()  
        await interaction.response.send_message("Closing Ticket...", ephemeral=True)
        await interaction.channel.delete()

class ticketb(discord.ui.View):
    def __init__(self):
     super().__init__(timeout=None)
      
    @discord.ui.button(label = "Create Ticket", emoji = f"<:x_ticket:1059195114574073876>", style=discord.ButtonStyle.grey, custom_id="persistent_view:ticket")
    async def ticketbt(self, interaction: discord.Interaction, button: discord.ui.Button):
      async with interaction.client.db.cursor() as cursor: 
        await cursor.execute("SELECT * FROM ticketusers WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id))
        check = await cursor.fetchone()
        if check is not None:
          embed=discord.Embed(description=f"{emojis.warn} {interaction.user.mention} you already have a ticket made, please close it before making a new one", color=colors.default)
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
            await channel.send(f"{interaction.user.mention}", embed=discord.Embed(title = f"<:x_ticket:1059195114574073876> Ticket Created", description = "Thank you for creating a ticket, staff will be right with you shortly.", color = colors.default), view=closeticket())
        
class tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      
    @commands.Cog.listener()
    async def on_ready(self): 
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS tickets (guild_id INTEGER, text INTEGER)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS ticketusers (guild_id INTEGER, user_id INTEGER)")
            await self.bot.db.commit()  
    
    @commands.command(help="adds ticket module to your server", description="config", brief=">>> ticket set - setups ticket module\nticket unset - remove ticket module", usage="[option]") 
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def ticket(self, ctx, option=None):
        if (not ctx.author.guild_permissions.administrator):
            await noperms(self, ctx, "administrator")
            return
        elif option == "set":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM tickets WHERE guild_id = {}".format(ctx.guild.id))
                check = await cursor.fetchone()
                if check is not None:
                    em = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} the ticket module has already been setup for this server")
                    await ctx.reply(embed=em, mention_author=False)
                    return
                elif check is None:
                    category = await ctx.guild.create_category("tickets")
                    overwrite = {ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False)}
                    embed = discord.Embed(title = f"<:x_ticket:1059195114574073876> Tickets <:x_ticket:1059195114574073876>", description = f"To create a ticket, press the <:x_ticket:1059195114574073876> button below this message.", color=colors.default)
                    embed.set_footer(text = f"powered by {self.bot.user.name}", icon_url = self.bot.user.avatar.url)
                    text = await ctx.guild.create_text_channel("tickets", category=category, overwrites=overwrite)
                    await text.send(embed=embed, view=ticketb())
                    await cursor.execute("INSERT INTO tickets VALUES (?,?)", (ctx.guild.id, text.id))
                    await self.bot.db.commit()
                    e = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} successfully configured ticket module")
                    await ctx.reply(embed=e, mention_author=False)
        elif option == "unset":
            async with self.bot.db.cursor() as cursor:
              await cursor.execute("SELECT * FROM tickets WHERE guild_id = {}".format(ctx.guild.id))
              check = await cursor.fetchone() 
              if check is None:
                em = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} ticket module isn't set")
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
                  embed = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} ticket module has been disabled")
                  await ctx.reply(embed=embed, mention_author=False) 
                  return
                except:
             
                 await cursor.execute("DELETE FROM tickets WHERE guild_id = {}".format(ctx.guild.id))
                 await self.bot.db.commit()
                 embed = discord.Embed(color=colors.default, description=f"{emojis.approve} {ctx.author.mention} ticket module has been disabled")
                 await ctx.reply(embed=embed, mention_author=False)  
        elif option == None:
            await commandhelp(self, ctx, ctx.command.name)
            return 

async def setup(bot):
    await bot.add_cog(tickets(bot))