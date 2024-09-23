import discord, os, asyncio
from discord.ext import commands 
from patches.permissions import Permissions
from utils.utils import EmbedBuilder

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
    label="Topic Name",
    placeholder="The ticket topics name.",
    required=True, 
    style=discord.TextStyle.short 
  )

  description = discord.ui.TextInput(
    label="Topic Description",
    placeholder="The description of the ticket topic.", 
    required=False, 
    max_length=100,
    style=discord.TextStyle.long 
  )

  async def on_submit(self, interaction: discord.Interaction):
      check = await interaction.client.db.fetchrow('SELECT * FROM ticket_topics WHERE guild_id = $1 AND name = $2', interaction.guild.id, self.name.value)
      if check is not None: return await interaction.client.ext.warning(interaction, f"A topic with the name **{self.name.value}** already exists", ephemeral=True)
      await interaction.client.db.execute("INSERT INTO ticket_topics VALUES ($1,$2,$3)", interaction.guild.id, self.name.value, self.description.value)
      return await interaction.client.ext.success(interaction, f"Added new ticket topic **{self.name.value}**", ephemeral=True)

class CreateTicket(discord.ui.View): 
    def __init__(self): 
      super().__init__(timeout=None)   

    @discord.ui.button(label='Create', emoji="🎫", style=discord.ButtonStyle.gray, custom_id='persistent_view:create')
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):      
        check = await interaction.client.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", interaction.guild.id)
        if check is None: return await interaction.client.ext.warning(interaction, "Ticket module was disabled", ephemeral=True)
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
           overwrite1 = text.overwrites_for(interaction.guild.default_role)
           overwrite1.view_channel = False
           await text.set_permissions(interaction.guild.default_role, overwrite=overwrite1)
           embed = discord.Embed(color=int(check['color']) or interaction.client.color, description="Support will be with you shortly, please be patient.\n\nTo close the ticket press the button down below.")
           embed.set_footer(text="evict.cc", icon_url=interaction.client.user.display_avatar.url)
           await interaction.client.db.execute("INSERT INTO opened_tickets VALUES ($1,$2,$3)", interaction.guild.id, text.id, interaction.user.id)
           mes = await text.send(content=f"{interaction.user.mention}, Welcome.", embed=embed, view=DeleteTicket(), allowed_mentions=discord.AllowedMentions.all())
           await interaction.response.send_message(embed=discord.Embed(color=int(check['color']) or interaction.client.color, description=f"{interaction.client.yes} {interaction.user.mention}: Opened ticket in {text.mention}"), ephemeral=True)
           
           supportRoles = await interaction.client.db.fetch("SELECT * FROM ticket_support WHERE guild_id = $1", interaction.guild.id)
           for support in supportRoles:
             await text.send(f'<@&{support["role_id"]}>', allowed_mentions=discord.AllowedMentions(roles=True), delete_after=5)
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
            overwrite1 = text.overwrites_for(interaction.guild.default_role)
            overwrite1.view_channel = False
            await text.set_permissions(interaction.guild.default_role, overwrite=overwrite1)
            e = discord.Embed(color=int(check['color']) if check['color'] is not None else inte.client.color, title=f"{select.values[0]}", description="Support will be with you shortly, please be patient.\n\nTo close the ticket press the button down below.")
            e.set_footer(text="evict.cc", icon_url=interaction.client.user.display_avatar.url)
            await inte.client.db.execute("INSERT INTO opened_tickets VALUES ($1,$2,$3)", interaction.guild.id, text.id, interaction.user.id)
            await inte.response.edit_message(embed=discord.Embed(color=int(check['color']) if check['color'] is not None else inte.client.color, description=f"{inte.client.yes} {inte.user.mention}: Opened ticket in {text.mention}"), view=None)
            mes = await text.send(content=f"{interaction.user.mention}, Welcome.", embed=e, view=DeleteTicket(), allowed_mentions=discord.AllowedMentions.all())
            supportRoles = await interaction.client.db.fetch("SELECT * FROM ticket_support WHERE guild_id = $1", interaction.guild.id)
            for support in supportRoles:
              await text.send(f'<@&{support["role_id"]}>', allowed_mentions=discord.AllowedMentions(roles=True))
            return await mes.pin()

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)    

class DeleteTicket(discord.ui.View): 
  def __init__(self): 
      super().__init__(timeout=None)   

  @discord.ui.button(label='', emoji="<:trash:1263727144832602164>", style=discord.ButtonStyle.gray, custom_id='persistent_view:delete')
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
       await inte.response.edit_message(content="Aborting closure...", view=None)

    cancel.callback = cancel_callback

    view = discord.ui.View()
    view.add_item(close)
    view.add_item(cancel)
    await interaction.response.send_message("Are you sure you want to close the ticket?", view=view)       

class tickets(commands.Cog): 
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

    @ticket.command(description="add a person to the ticket", usage="[member]", brief="manage channels")
    @Permissions.has_permission(manage_channels=True)
    @get_ticket()
    async def add(self, ctx: commands.Context, *, member: discord.Member):
     overwrites = discord.PermissionOverwrite()  
     overwrites.send_messages = True
     overwrites.view_channel = True 
     overwrites.attach_files = True 
     overwrites.embed_links = True
     await ctx.channel.set_permissions(member, overwrite=overwrites) 
     return await ctx.success( "I have added **{}** to the ticket.".format(member))
    
    @ticket.command(description="remove a member from the ticket", usage="[member]", brief="manage channels")
    @Permissions.has_permission(manage_channels=True)
    @get_ticket() 
    async def remove(self, ctx: commands.Context, *, member: discord.Member): 
     overwrites = discord.PermissionOverwrite()  
     overwrites.send_messages = False
     overwrites.view_channel = False 
     overwrites.attach_files = False 
     overwrites.embed_links = False
     await ctx.channel.set_permissions(member, overwrite=overwrites) 
     return await ctx.success( "I have removed **{}** from the ticket.".format(member))

    @ticket.command(description="manage the ticket topics", brief="administrator")
    @Permissions.has_permission(administrator=True)
    async def topics(self, ctx: commands.Context): 
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if check is None: return await ctx.reply("no ticket panel created") 
        results = await self.bot.db.fetch("SELECT * FROM ticket_topics WHERE guild_id = $1", ctx.guild.id) 
        embed = discord.Embed(color=self.bot.color, description=f"🔍 Choose a setting")
        button1 = discord.ui.Button(label="add topic", style=discord.ButtonStyle.gray)
        button2 = discord.ui.Button(label="remove topic", style=discord.ButtonStyle.red, disabled=len(results) == 0)

        async def button1_callback(interaction: discord.Interaction): 
          if interaction.user != ctx.author: return await interaction.client.ext.warning(interaction, "You are **not** the author of this message.", ephemeral=True)
          add = TicketTopic()
          return await interaction.response.send_modal(add)

        async def button2_callback(interaction: discord.Interaction): 
          if interaction.user != ctx.author: return await interaction.client.ext.warning(interaction, "You are **not** the author of this message.", ephemeral=True)
          e = discord.Embed(color=self.bot.color, description=f"🔍 Select a topic to delete.")
          options = []
          for result in results: options.append(discord.SelectOption(label=result[1], description=result[2]))
          select = discord.ui.Select(options=options, placeholder="Select a topic.")
          async def select_callback(inter: discord.Interaction):
            if inter.user != ctx.author: return await interaction.client.ext.warning(interaction, "You are **not** the author of this message.", ephemeral=True)
            await self.bot.db.execute("DELETE FROM ticket_topics WHERE guild_id = $1 AND name = $2", inter.guild.id, select.values[0])
            await self.bot.ext.success(inter, f"I have removed **{select.values[0]}** topic.", ephemeral=True)

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

    @ticket.command(description="configure the ticket message", usage="[embed code]", brief="administrator")
    @Permissions.has_permission(administrator=True)
    async def message(self, ctx: commands.Context, *, message: str=None):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if message is not None:
         if check is None: await self.bot.db.execute("INSERT INTO tickets (guild_id, message) VALUES ($1,$2)", ctx.guild.id, message)  
         else: await self.bot.db.execute("UPDATE tickets SET message = $1 WHERE guild_id = $2", message, ctx.guild.id) 
         return await ctx.success( f"I have set the **ticket message** as\n```{message}```")
        else: 
          if check is None: return await ctx.warning("There is **no** custom ticket message.")
          await self.bot.db.execute("UPDATE tickets SET message = $1 WHERE guild_id = $2", None, ctx.guild.id)
          return await ctx.success( "I have set the message as **default**.")
    
    @ticket.command(description="configure the ticket support role (will be pinged)", usage="[role]", brief="administrator")
    @Permissions.has_permission(administrator=True)
    async def support(self, ctx: commands.Context, role: discord.Role=None):
      if role == None:
        await self.bot.db.execute("DELETE FROM ticket_support WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success('I have removed **support roles**.')
     
      await self.bot.db.execute("INSERT INTO ticket_support (guild_id, role_id) VALUES ($1, $2)", ctx.guild.id, role.id)
      return await ctx.success(f'I have added **{role.name}** as a **support role**.')
      
      
    @ticket.command(description="configure the ticket category", usage="[category]", brief="administrator")
    @Permissions.has_permission(administrator=True)
    async def category(self, ctx: commands.Context, *, channel: discord.CategoryChannel=None):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if channel is not None:
         if check is None: await self.bot.db.execute("INSERT INTO tickets (guild_id, category) VALUES ($1,$2)", ctx.guild.id, channel.id)   
         else: await self.bot.db.execute("UPDATE tickets SET category = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
         await ctx.success( "tickets category set to {}".format(channel.mention))
        else: 
            if check is None: return await ctx.warning("Tickets channel is **not** set.")
            await self.bot.db.execute("UPDATE tickets SET category = $1 WHERE guild_id = $2", None, ctx.guild.id)
            await ctx.success( "I have **removed** tickets category.")

    @ticket.command(description="configure the ticket channel", usage="[channel]", brief="administrator")
    @Permissions.has_permission(administrator=True)
    async def channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None):  
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if channel is not None:
         if check is None: await self.bot.db.execute("INSERT INTO tickets (guild_id, channel_id) VALUES ($1,$2)", ctx.guild.id, channel.id)   
         else: await self.bot.db.execute("UPDATE tickets SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
         await ctx.success( "tickets channel set to {}".format(channel.mention))
        else: 
            if check is None: return await ctx.warning("Tickets channel is **not** set.")
            await self.bot.db.execute("UPDATE tickets SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
            await ctx.success( "I have **removed** the tickets channel.") 

    @ticket.command(description="configure the ticket logging channel", usage="[channel]", brief="administrator")
    @Permissions.has_permission(administrator=True)
    async def logs(self, ctx: commands.Context, *, channel: discord.TextChannel=None):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if channel is not None:
         if check is None: await self.bot.db.execute("INSERT INTO tickets (guild_id, logs) VALUES ($1,$2)", ctx.guild.id, channel.id)   
         else: await self.bot.db.execute("UPDATE tickets SET logs = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
         await ctx.success( "tickets logs set to {}".format(channel.mention))
        else: 
            if check is None: return await ctx.warning("Ticket logs are **not** set.")
            await self.bot.db.execute("UPDATE tickets SET logs = $1 WHERE guild_id = $2", None, ctx.guild.id)
            await ctx.success("I have **removed** the tickets logs.") 

    @ticket.command(description="sends the ticket panel", brief="administrator")
    @Permissions.has_permission(administrator=True)
    async def send(self, ctx: commands.Context): 
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if check is None: return await ctx.warning("You have **not** sent a ticket panel.")
        if ctx.guild.get_channel(check['channel_id']) is None: return await ctx.warning("I could **not** find that channel.")
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
          await channel.send(embed=embed, view=CreateTicket())
        
        await ctx.success("Sent the **ticket** message to {}".format(channel.mention)) 
        await self.bot.db.execute("UPDATE tickets SET color = $1 WHERE guild_id = $2", self.bot.color or message.embeds[0].color.value, ctx.guild.id)
      
    @ticket.command(description="check the ticket panel's settings")
    async def settings(self, ctx: commands.Context):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if check is None: return await ctx.reply("You have **not** created a ticket panel.")
        embed1 = discord.Embed(color=self.bot.color, title="Ticket Settings", description="Settings for **{}**".format(ctx.guild.name))
        embed1.add_field(name="Ticket Channel", value=ctx.guild.get_channel(check['channel_id']).mention if ctx.guild.get_channel(check['channel_id']) is not None else "N/A")
        embed1.add_field(name="Logs Channel", value=ctx.guild.get_channel(check['logs']).mention if ctx.guild.get_channel(check['logs']) is not None else "N/A")
        embed1.add_field(name="Category", value=ctx.guild.get_channel(check['category']).mention if ctx.guild.get_channel(check['category']) is not None else "N/A")
        embed2 = discord.Embed(color=self.bot.color, title="ticket message", description="```{}```".format(check['message']) if check['message'] is not None else "default")
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)
    
async def setup(bot: commands.Bot): 
    await bot.add_cog(tickets(bot))