import discord, os, asyncio
from discord.ext import commands
from tools.utils.checks import Perms
from tools.utils.utils import EmbedBuilder

async def make_transcript(c):
   filename = f"{c.name}.txt"
   with open(filename, "w") as file:
    async for msg in c.history(oldest_first=True):
     if not msg.author.bot: file.write(f"{msg.created_at} - {msg.author.display_name}: {msg.clean_content}")
    return filename

class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Create", emoji="🎫", style=discord.ButtonStyle.gray, custom_id="persistent_view:create")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await interaction.client.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", interaction.guild.id)
        if not check: return await interaction.client.ext.send_warning("Ticket module is **not** enabled", ephemeral=True)
        chec = await interaction.client.db.fetchrow("SELECT * FROM opened_tickets WHERE guild_id = $1 AND user_id = $2", interaction.guild.id, interaction.user.id)
        if chec: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.warning} {interaction.user.mention}: You already have a ticket opened"), ephemeral=True)
        text = await interaction.guild.create_text_channel(name="ticket-{}".format(interaction.user.name), category=interaction.guild.get_channel(check["category"]) or None)
        overwrites = discord.PermissionOverwrite()
        overwrites.send_messages = True
        overwrites.view_channel = True
        overwrites.attach_files = True
        overwrites.embed_links = True
        await text.set_permissions(interaction.user, overwrite=overwrites)
        embed = discord.Embed(color=interaction.client.color, description="Someone will be with you shortly\nTo close this ticket press <:trash:1128623776221909052>")
        embed.set_footer(text="vilan", icon_url=interaction.client.user.display_avatar.url)
        await interaction.client.db.execute("INSERT INTO opened_tickets VALUES ($1,$2,$3)", interaction.guild.id, text.id, interaction.user.id)
        mes = await text.send(content=f"{interaction.user.mention} welcome", embed=embed, allowed_mentions=discord.AllowedMentions.all(), view=DeleteTicket())
        await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.yes} {interaction.user.mention}: Opened ticket in {text.mention}"), ephemeral=True)
        return

class DeleteTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="", emoji="<:trash:1128623776221909052>", style=discord.ButtonStyle.gray, custom_id="persistent_view:delete")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
      yes = discord.ui.Button(label="close", style=discord.ButtonStyle.danger)
      no = discord.ui.Button(label="cancel", style=discord.ButtonStyle.gray)
      
      async def yes_callback(inte: discord.Interaction):
          check = await inte.client.db.fetchrow("SELECT logs FROM tickets WHERE guild_id = $1", inte.guild.id)
          if check:
              filename = await make_transcript(interaction.channel)
              embed = discord.Embed(color=inte.client.color, title="ticket logs", description="logs for ticket `{}` | closed by **{}**".format(inte.channel.id, inte.user), timestamp=discord.utils.utcnow())
              try: await inte.guild.get_channel(check["logs"]).send(embed=embed, file=discord.File(filename))
              except: pass
              os.remove(filename)
          await inte.client.db.execute("DELETE FROM opened_tickets WHERE channel_id = $1 AND guild_id = $2", inte.channel.id, inte.guild.id)
          await inte.response.edit_message(content=f"ticket closed by {inte.user.mention}", view=None)
          await asyncio.sleep(2)
          await inte.channel.delete()
          
      yes.callback = yes_callback
      
      async def no_callback(inte: discord.Interaction):
         await inte.response.edit_message(content="aborting action...", view=None)
      
      no.callback = no_callback
        
      view = discord.ui.View()
      view.add_item(yes)
      view.add_item(no)
      await interaction.response.send_message("Are you sure you want to close this ticket?", view=view)

class Ticket(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel): 
      if isinstance(channel, discord.TextChannel): 
            check = await self.bot.db.fetchrow("SELECT * FROM opened_tickets WHERE guild_id = $1 AND channel_id = $2", channel.guild.id, channel.id)       
            if check is not None: await self.bot.db.execute("DELETE FROM opened_tickets WHERE guild_id = $1 AND channel_id = $2", channel.guild.id, channel.id)
    
    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def ticket(self, ctx):
      await ctx.create_pages()
    
    @ticket.command(description="configure the ticket message", help="config", usage="[message]")
    @Perms.get_perms("administrator")
    async def message(self, ctx: commands.Context, *, message: str=None):
        check = await self.bot.db.execute("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if message:
         if not check: await self.bot.db.execute("INSERT INTO tickets (guild_id, message) VALUES ($1,$2)", ctx.guild.id, message)
         else: await self.bot.db.execute("UPDATE tickets SET message = $1 WHERE guild_id = $2", message, ctx.guild.id)
         return await ctx.send_success(f"Ticket message set to\n```{message}```")
        else:
          if not check: return await ctx.send_warning("No custom ticket message found")
          else: await self.bot.db.execute("UPDATE tickets SET message = $1 WHERE guild_id = $2", None, ctx.guild.id)
          return await ctx.send_success("Ticket message set to default")
    
    @ticket.command(description="configure the ticket category", help="config", usage="[category]")
    @Perms.get_perms("administrator")
    async def category(self, ctx: commands.Context, *, channel: discord.CategoryChannel=None):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if channel:
         if not check: await self.bot.db.execute("INSERT INTO tickets (guild_id, category) VALUES ($1,$2)", ctx.guild.id, channel.id)
         else: await self.bot.db.execute("UPDATE tickets SET category = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
         return await ctx.send_success("Ticket category set to {}".format(channel.mention))
        else:
          if not check: return await ctx.send_warning("No ticket channel found")
          else: await self.bot.db.execute("UPDATE tickets SET category = $1 WHERE guild_id = $2", None, ctx.guild.id)
          return await ctx.send_success("Removed ticket category")
    
    @ticket.command(description="configure the ticket channel", help="config", usage="[channel]")
    @Perms.get_perms("administrator")
    async def channel(self, ctx: commands.Context, *, channel: discord.TextChannel=None):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if channel:
         if not check: await self.bot.db.execute("INSERT INTO tickets (guild_id, channel_id) VALUES ($1,$2)", ctx.guild.id, channel.id)
         else: await self.bot.db.execute("UPDATE tickets SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
         return await ctx.send_success("Ticket channel set to {}".format(channel.mention))
        else:
          if not check: return await ctx.send_warning("No ticket channel found")
          else: await self.bot.db.execute("UPDATE tickets SET channel_id = $1 WHERE guild_id = $2", None, ctx.guild.id)
          return await ctx.send_success("Removed ticket channel")
    
    @ticket.command(description="configure the ticket logging channel", help="config", usage="[channel]")
    @Perms.get_perms("administrator")
    async def logs(self, ctx: commands.Context, *, channel: discord.TextChannel=None):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if channel:
         if not check: await self.bot.db.execute("INSERT INTO tickets (guild_id, logs) VALUES ($1,$2)", ctx.guild.id, channel.id)
         else: await self.bot.db.execute("UPDATE tickets SET logs = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
         return await ctx.send_success("Ticket logs set to {}".format(channel.mention))
        else:
          if not check: return await ctx.send_warning("No ticket logs found")
          else: await self.bot.db.execute("UPDATE tickets SET logs = $1 WHERE guild_id = $2", None, ctx.guild.id)
          return await ctx.send_success("Removed tickeg logs")
    
    @ticket.command(description="send the ticket panel", help="config")
    @Perms.get_perms("administrator")
    async def send(self, ctx: commands.Context):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if not check: return await ctx.send_warning("No ticket panel found")
        if not ctx.guild.get_channel(check["channel_id"]): return await ctx.send_warning("Channel not found")
        channel = ctx.guild.get_channel(check["channel_id"])
        message = None
        if check["message"]:
         view = CreateTicket()
         try:
           x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, check['message']))
           message = await channel.send(content=x[0], embed=x[1], view=view)
         except: message = await channel.send(EmbedBuilder.embed_replacement(ctx.author, check['message']), view=view)               
        else:
          embed = discord.Embed(color=self.bot.color, title="Create a ticket", description="Click on the button below to create a ticket")
          embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
          message = await channel.send(embed=embed, view=CreateTicket())
          await ctx.send_success("Ticket message sent to {}".format(channel.mention))

    @ticket.command(description="check the ticket panel settings", help="config")
    @Perms.get_perms("administrator")
    async def settings(self, ctx: commands.Context):
        check = await self.bot.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if not check: return await ctx.send_warning("No ticket panel found")
        embed = discord.Embed(color=self.bot.color, title="ticket settings", description="settings for **{}**".format(ctx.guild.name))
        embed.add_field(name="channel", value=ctx.guild.get_channel(check["channel_id"]).mention if ctx.guild.get_channel(check["channel_id"]) else "none")
        embed.add_field(name="logs", value=ctx.guild.get_channel(check["logs"]).mention if ctx.guild.get_channel(check["logs"]) else "none")
        embed.add_field(name="category", value=ctx.guild.get_channel(check["category"]).mention if ctx.guild.get_channel(check["category"]) else "none")
        embed.add_field(name="message", value="```{}```".format(check["message"]) if check["message"] else "default", inline=False)
        await ctx.reply(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Ticket(bot))