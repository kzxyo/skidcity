import discord, os, asyncio
from discord.ext import commands 
from tools.checks import Perms as utils
from tools.utils import EmbedBuilder

def get_ticket():
 async def predicate(ctx: commands.Context):  
  check = await ctx.bot.db.fetchrow("SELECT * FROM opened_tickets WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, ctx.channel.id)
  if check is None: return False 
  return True 
 return commands.check(predicate)   

async def make_transcript(c): 
   filename = f"{c.name}.txt"
   with open(filename, "w") as file:
    async for msg in c.history(oldest_first=True):
      if not msg.author.bot: file.write(f"{msg.created_at} -  {msg.author.display_name}: {msg.clean_content}\n")
    return filename  

class TicketTopic(discord.ui.Modal, title="Add a ticket topic"): 

  name = discord.ui.TextInput(
    label="topic name",
    placeholder="the ticket topic's name..",
    required=True, 
    style=discord.TextStyle.short 
  )

  description = discord.ui.TextInput(
    label="topic description",
    placeholder="the description of the ticket topic...", 
    required=False, 
    max_length=100,
    style=discord.TextStyle.long 
  )

  async def on_submit(self, interaction: discord.Interaction):
      check = await interaction.client.db.fetchrow('SELECT * FROM ticket_topics WHERE guild_id = $1 AND name = $2', interaction.guild.id, self.name.value)
      if check is not None: return await interaction.client.ext.send_warning(interaction, f"A topic with the name **{self.name.value}** already exists", ephemeral=True)
      await interaction.client.db.execute("INSERT INTO ticket_topics VALUES ($1,$2,$3)", interaction.guild.id, self.name.value, self.description.value)
      return await interaction.client.ext.send_success(interaction, f"Added new ticket topic **{self.name.value}**", ephemeral=True)

class CreateTicket(discord.ui.View): 
    def __init__(self): 
      super().__init__(timeout=None)   

    @discord.ui.button(label='Create', emoji="🎫", style=discord.ButtonStyle.gray, custom_id='persistent_view:create')
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):      
        check = await interaction.client.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", interaction.guild.id)
        if check is None: return await interaction.client.ext.send_warning(interaction, "Ticket module was disabled", ephemeral=True)
        re = await interaction.client.db.fetchrow("SELECT * FROM opened_tickets WHERE guild_id = $1 AND user_id = $2", interaction.guild.id, interaction.user.id)
        if re is not None: return await interaction.response.send_message(embed=discord.Embed(color=int(check['color']) if check[4] is not None else interaction.client.color, description=f"{interaction.client.warning} {interaction.user.mention}: You already have a ticket opened"), ephemeral=True)
        results = await interaction.client.db.fetch("SELECT * FROM ticket_topics WHERE guild_id = $1", interaction.guild.id)
        if len(results) == 0: 
           text = await interaction.guild.create_text_channel(name="ticket-{}".format(interaction.user.name), reason="opened ticket", category=interaction.client.get_channel(check['category']) or None)
           overwrites = discord.PermissionOverwrite()
           overwrites.send_messages = True
           overwrites.view_channel = True 
           overwrites.attach_files = True 
           overwrites.embed_links = True
           await text.set_permissions(interaction.user, overwrite=overwrites)
           embed = discord.Embed(color=int(check['color']) or interaction.client.color, description="Support will be with you shortly\nTo close the ticket please press <:trash:1083457276393820181>")
           embed.set_footer(text="pretend.space", icon_url=interaction.client.user.display_avatar.url)
           await interaction.client.db.execute("INSERT INTO opened_tickets VALUES ($1,$2,$3)", interaction.guild.id, text.id, interaction.user.id)
           mes = await text.send(content=f"{interaction.user.mention} welcome", embed=embed, view=DeleteTicket(), allowed_mentions=discord.AllowedMentions.all())
           await interaction.response.send_message(embed=discord.Embed(color=int(check['color']) or interaction.client.color, description=f"{interaction.client.yes} {interaction.user.mention}: Opened ticket in {text.mention}"), ephemeral=True)
           return await mes.pin()
        options = []
        for result in results: 
          options.append(discord.SelectOption(label=result['name'], description=result['description']))

        embed = discord.Embed(color=int(check['color']) if check['color'] is not None else interaction.client.color, description="🔍 Please choose a topic")
        select = discord.ui.Select(options=options, placeholder="select a topic...")

        async def select_callback(inte: discord.Interaction):   
            check = await inte.client.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", interaction.guild.id)   
            if check is None: return await interaction.response.send_message(embed=discord.Embed(color=inte.client.color, description=f"{inte.client.warning} {inte.user.mention}: Ticket module was disabled"), ephemeral=True)
            text = await interaction.guild.create_text_channel(name="ticket-{}".format(interaction.user.name), reason="opened ticket", category=interaction.client.get_channel(check[3]) or None)
            overwrites = discord.PermissionOverwrite()
            overwrites.send_messages = True
            overwrites.view_channel = True 
            overwrites.attach_files = True 
            overwrites.embed_links = True
            await text.set_permissions(interaction.user, overwrite=overwrites)
            e = discord.Embed(color=int(check['color']) if check['color'] is not None else inte.client.color, title=f"topic: {select.values[0]}", description="Support will be with you shortly\nTo close the ticket please press <:trash:1083457276393820181>")
            e.set_footer(text="pretend.space", icon_url=interaction.client.user.display_avatar.url)
            await inte.client.db.execute("INSERT INTO opened_tickets VALUES ($1,$2,$3)", interaction.guild.id, text.id, interaction.user.id)
            await inte.response.edit_message(embed=discord.Embed(color=int(check['color']) if check['color'] is not None else inte.client.color, description=f"{inte.client.yes} {inte.user.mention}: Opened ticket in {text.mention}"), view=None)
            mes = await text.send(content=f"{interaction.user.mention} welcome", embed=e, view=DeleteTicket(), allowed_mentions=discord.AllowedMentions.all())
            return await mes.pin()

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)    

class DeleteTicket(discord.ui.View): 
  def __init__(self): 
      super().__init__(timeout=None)   

  @discord.ui.button(label='', emoji="<:trash:1083457276393820181>", style=discord.ButtonStyle.gray, custom_id='persistent_view:delete')
  async def delete(self, interaction: discord.Interaction, button: discord.ui.Button): 
    close = discord.ui.Button(label="Close", style=discord.ButtonStyle.red)
    cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.gray)

    async def close_callback(inte: discord.Interaction): 
        check = await inte.client.db.fetchrow("SELECT logs FROM tickets WHERE guild_id = {}".format(inte.guild.id))         
        if check is not None: 
            filename = await make_transcript(interaction.channel)
            embed = discord.Embed(color=inte.client.color, title="ticket logs", description="Logs for ticket `{}` | closed by **{}**".format(inte.channel.id, inte.user), timestamp=discord.utils.utcnow()) 
            try: await inte.guild.get_channel(check['logs']).send(embed=embed, file=discord.File(filename)) 
            except: pass
            os.remove(filename)
        await inte.client.db.execute("DELETE FROM opened_tickets WHERE channel_id = $1 AND guild_id = $2", inte.channel.id, inte.guild.id) 
        await inte.response.edit_message(content=f"closed by {inte.user.mention}", view=None)            
        await asyncio.sleep(2)
        await inte.channel.delete()

    close.callback = close_callback 

    async def cancel_callback(inte: discord.Interaction): 
       await inte.response.edit_message(content="aborting closure...", view=None)

    cancel.callback = cancel_callback

    view = discord.ui.View()
    view.add_item(close)
    view.add_item(cancel)
    await interaction.response.send_message("Are you sure you want to close the ticket?", view=view)       

class Tickets(commands.Cog): 
    def __init__(self, bot: commands.Bot): 
      self.bot = bot  

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel): 
      if isinstance(channel, discord.TextChannel): 
            check = await self.bot.db.fetchrow("SELECT * FROM opened_tickets WHERE guild_id = $1 AND channel_id = $2", channel.guild.id, channel.id)            
            if check is not None: await self.bot.db.execute("DELETE FROM opened_tickets WHERE guild_id = $1 AND channel_id = $2", channel.guild.id, channel.id)
    
    @commands.group(invoke_without_command=True)
    async def ticket(self, ctx): 
      await ctx.create_pages()  

    @ticket.command(description="add a person to the ticket", help="config", usage="[member]", brief="manage channels")
    @utils.get_perms("manage_channels")
    @get_ticket()
    async def add(self, ctx: commands.Context, *, member: discord.Member):
     overwrites = discord.PermissionOverwrite()  
     overwrites.send_messages = True
     overwrites.view_channel = True 
     overwrites.attach_files = True 
     overwrites.embed_links = True
     await ctx.channel.set_permissions(member, overwrite=overwrites) 
     return await ctx.send_success( "Added **{}** to the ticket".format(member))
    
    @ticket.command(help="config", description="remove a member from the ticket", usage="[member]", brief="manage channels")
    @utils.get_perms("manage_channels")
    @get_ticket() 
    async def remove(self, ctx: commands.Context, *, member: discord.Member): 
     overwrites = discord.PermissionOverwrite()  
     overwrites.send_messages = False
     overwrites.view_channel = False 
     overwrites.attach_files = False 
     overwrites.embed_links = False
     await ctx.channel.set_permissions(member, overwrite=overwrites) 
     return await ctx.send_success( "Removed **{}** from the ticket".format(member))

    @ticket.command(description="manage the ticket topics", help="config", brief="administrator")
    @utils.get_perms("administrator")
    async def topics(self, ctx: commands.Context): 
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if check is None: return await ctx.reply("no ticket panel created") 
        results = await self.bot.db.fetch("SELECT * FROM ticket_topics WHERE guild_id = $1", ctx.guild.id) 
        embed = discord.Embed(color=self.bot.color, description=f"🔍 Choose a setting")
        button1 = discord.ui.Button(label="add topic", style=discord.ButtonStyle.gray)
        button2 = discord.ui.Button(label="remove topic", style=discord.ButtonStyle.red, disabled=len(results) == 0)

        async def button1_callback(interaction: discord.Interaction): 
          if interaction.user != ctx.author: return await interaction.client.ext.send_warning(interaction, "You are not the author of this message", ephemeral=True)
          add = TicketTopic()
          return await interaction.response.send_modal(add)

        async def button2_callback(interaction: discord.Interaction): 
          if interaction.user != ctx.author: return await interaction.client.ext.send_warning(interaction, "You are not the author of this message", ephemeral=True)
          e = discord.Embed(color=self.bot.color, description=f"🔍 Select a topic to delete")
          options = []
          for result in results: options.append(discord.SelectOption(label=result[1], description=result[2]))
          select = discord.ui.Select(options=options, placeholder="select a topic...")
          async def select_callback(inter: discord.Interaction):
            if inter.user != ctx.author: return await interaction.client.ext.send_warning(interaction, "You are not the author of this message", ephemeral=True)
            await self.bot.db.execute("DELETE FROM ticket_topics WHERE guild_id = $1 AND name = $2", inter.guild.id, select.values[0])
            await self.bot.ext.send_success(inter, f"Removed **{select.values[0]}** topic", ephemeral=True)

          select.callback = select_callback 
          v = discord.ui.View()
          v.add_item(select)
          return await interaction.response.edit_message(embed=e, view=v)   

        button1.callback = button1_callback
        button2.callback = button2_callback
        view = discord.ui.View()
        view.add_item(button1)
        view.add_item(button2)
        await ctx.reply(embed=embed, view=view)  

    @ticket.command(description="configure the ticket message", help="config", usage="[embed code]", brief="administrator")
    @utils.get_perms("administrator")
    async def message(self, ctx: commands.Context, *, message: str=None):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if message is not None:
         if check is None: await self.bot.db.execute("INSERT INTO tickets (guild_id, message) VALUES ($1,$2)", ctx.guild.id, message)  
         else: await self.bot.db.execute("UPDATE tickets SET message = $1 WHERE guild_id = $2", message, ctx.guild.id) 
         return await ctx.send_success( f"Ticket message set as\n```{message}```")
        else: 
          if check is None: return await ctx.send_warning("There is no custom ticket message")
          await self.bot.db.execute("UPDATE tickets SET message = $1 WHERE guild_id = $2", None, ctx.guild.id)
          return await ctx.send_success( "Custom ticket message set to default")

    @ticket.command(description="configure the ticket category", help="config", usage="[category]", brief="administrator")
    @utils.get_perms("administrator")
    async def category(self, ctx: commands.Context, *, channel: discord.CategoryChannel=None):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if channel is not None:
         if check is None: await self.bot.db.execute("INSERT INTO tickets (guild_id, category) VALUES ($1,$2)", ctx.guild.id, channel.id)   
         else: await self.bot.db.execute("UPDATE tickets SET category = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
         await ctx.send_success( "tickets category set to {}".format(channel.mention))
        else: 
            if check is None: return await ctx.send_warning("tickets channel is not set")
            await self.bot.db.execute("UPDATE tickets SET category = $1 WHERE guild_id = $2", None, ctx.guild.id)
            await ctx.send_success( "removed tickets category")

    @ticket.command(description="configure the ticket channel", help="config", usage="[channel]", brief="administrator")
    @utils.get_perms("administrator")
    async def channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None):  
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if channel is not None:
         if check is None: await self.bot.db.execute("INSERT INTO tickets (guild_id, channel_id) VALUES ($1,$2)", ctx.guild.id, channel.id)   
         else: await self.bot.db.execute("UPDATE tickets SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
         await ctx.send_success( "tickets channel set to {}".format(channel.mention))
        else: 
            if check is None: return await ctx.send_warning("tickets channel is not set")
            await self.bot.db.execute("UPDATE tickets SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
            await ctx.send_success( "removed tickets channel") 

    @ticket.command(description="configure the ticket logging channel", help="config", usage="[channel]", brief="administrator")
    @utils.get_perms("administrator")
    async def logs(self, ctx: commands.Context, *, channel: discord.TextChannel=None):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if channel is not None:
         if check is None: await self.bot.db.execute("INSERT INTO tickets (guild_id, logs) VALUES ($1,$2)", ctx.guild.id, channel.id)   
         else: await self.bot.db.execute("UPDATE tickets SET logs = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
         await ctx.send_success( "tickets logs set to {}".format(channel.mention))
        else: 
            if check is None: return await ctx.send_warning("tickets logs are not set")
            await self.bot.db.execute("UPDATE tickets SET logs = $1 WHERE guild_id = $2", None, ctx.guild.id)
            await ctx.send_success("removed tickets logs") 

    @ticket.command(description="sends the ticket panel", help="config", brief="administrator")
    @utils.get_perms("administrator")
    async def send(self, ctx: commands.Context): 
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if check is None: return await ctx.send_warning("No ticket panel created")
        if ctx.guild.get_channel(check['channel_id']) is None: return await ctx.send_warning("Channel not found")
        channel = ctx.guild.get_channel(check['channel_id'])
        message = None
        if check['message']:
         view = CreateTicket()
         try: 
           x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, check['message']))
           message = await channel.send(content=x[0], embed=x[1], view=view)
         except: message = await channel.send(EmbedBuilder.embed_replacement(ctx.author, check['message']), view=view)               
        else: 
          embed = discord.Embed(color=self.bot.color, title="Create a ticket", description="Click on the button below this message to create a ticket")
          embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
          message = await channel.send(embed=embed, view=CreateTicket()) 
        await self.bot.db.execute("UPDATE tickets SET color = $1 WHERE guild_id = $2", message.embeds[0].color.value or self.bot.color, ctx.guild.id)
        await ctx.send_success("Sent the **ticket** message to {}".format(channel.mention)) 
      
    @ticket.command(description="check the ticket panel's settings", help="config")
    async def settings(self, ctx: commands.Context):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if check is None: return await ctx.reply("no ticket panel created")
        embed = discord.Embed(color=self.bot.color, title="ticket settings", description="settings for **{}**".format(ctx.guild.name))
        embed.add_field(name="ticket channel", value=ctx.guild.get_channel(check['channel_id']).mention if ctx.guild.get_channel(check['channel_id']) is not None else "none")
        embed.add_field(name="logs channel", value=ctx.guild.get_channel(check['logs']).mention if ctx.guild.get_channel(check['logs']) is not None else "none")
        embed.add_field(name="category", value=ctx.guild.get_channel(check['category']).mention if ctx.guild.get_channel(check['category']) is not None else "none")
        embed.add_field(name="message", value="```{}```".format(check['message']) if check['message'] is not None else "default", inline=False)
        await ctx.reply(embed=embed)  
    
async def setup(bot: commands.Bot): 
    await bot.add_cog(Tickets(bot))        