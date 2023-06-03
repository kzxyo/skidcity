import discord, io, emoji, re 
from discord.ext import commands
from tools.checks import Perms
from typing import Union

def has_booster_role(): 
 async def predicate(ctx: commands.Context): 
  che = await ctx.bot.db.fetchrow("SELECT * FROM booster_module WHERE guild_id = {}".format(ctx.guild.id))
  if che is None:
    await ctx.send_warning("Booster role module is not configured")
    return False
  check = await ctx.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
  if check is None:  
   await ctx.send_warning("You do not have a booster role")
   return False 
  return True 
 return commands.check(predicate)

class Modals: 
   class Name(discord.ui.Modal, title="change the role name"):
      name = discord.ui.TextInput(
        label='role name',
        placeholder='your new role name here',
        style=discord.TextStyle.short,
        required=True
    )

      async def on_submit(self, interaction: discord.Interaction):
         check = await interaction.client.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id))         
         if check is None: return await interaction.client.ext.send_warning(interaction, "You don't have a booster role. Please use `boosterrole create` command first", ephemeral=True)
         role = interaction.guild.get_role(check['role_id'])
         await role.edit(name=self.name.value)
         return await interaction.client.ext.send_success(interaction, "Changed the **booster role** name in **{}**".format(self.name.value), ephemeral=True)

   class Icon(discord.ui.Modal, title="change the role icon"):
      name = discord.ui.TextInput(
        label='role icon',
        placeholder='this should be an emoji',
        style=discord.TextStyle.short,
        required=True
    )

      async def on_submit(self, interaction: discord.Interaction):
       try: 
         check = await interaction.client.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id))         
         if check is None: return await interaction.client.ext.send_warning(interaction, "You don't have a booster role. Please use `boosterrole create` command first", ephemeral=True)
         role = interaction.guild.get_role(check['role_id'])
         icon = ""
         if emoji.is_emoji(self.name.value): icon = self.name.value 
         else:
          emojis = re.findall(r'<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>', self.name.value)
          emoj = emojis[0]
          format = ".gif" if emoj[0] == "a" else ".png"
          url = "https://cdn.discordapp.com/emojis/{}{}".format(emoj[2], format)
          icon = await interaction.client.session.read(url)
         await role.edit(display_icon=icon) 
         return await interaction.client.ext.send_success(interaction, "Changed the **booster role** icon", ephemeral=True)  
       except: return await interaction.client.ext.send_error(interaction, "Unable to change the role icon", ephemeral=True)

   class Color(discord.ui.Modal, title="change the role colors"):
      name = discord.ui.TextInput(
        label='role color',
        placeholder='this should be a hex code',
        style=discord.TextStyle.short,
        required=True
    )

      async def on_submit(self, interaction: discord.Interaction):
       try: 
         check = await interaction.client.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id))         
         if check is None: return await interaction.client.ext.send_warning(interaction, "You don't have a booster role. Please use `boosterrole create` command first", ephemeral=True)
         role = interaction.guild.get_role(check['role_id'])
         color = self.name.value.replace("#", "")
         color = int(color, 16)
         await role.edit(color=color)
         return await interaction.client.ext.send_success(interaction, "Changed the **booster role** color", ephemeral=True)
       except: return await interaction.client.ext.send_error(interaction, "Unable to change the role color", ephemeral=True)

class Boosters(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
      self.bot = bot    
    
    @commands.Cog.listener()
    async def on_member_remove(self, before: discord.Member): 
        check = await self.bot.db.fetchrow("SELECT role_id FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(before.guild.id, before.id))        
        if check: 
          role = before.guild.get_role(int(check['role_id']))  
          await self.bot.db.execute("DELETE FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(before.guild.id, before.id))      
          await role.delete()
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):   
      await self.bot.db.execute("DELETE FROM booster_roles WHERE guild_id = {} AND role_id = {}".format(role.guild.id, role.id)) 

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member): 
     if before.guild.premium_subscriber_role in before.roles and not before.guild.premium_subscriber_role in after.roles: 
        check = await self.bot.db.fetchrow("SELECT role_id FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(before.guild.id, before.id))
        if check: 
          role = before.guild.get_role(int(check['role_id']))  
          await self.bot.db.execute("DELETE FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(before.guild.id, before.id))     
          await role.delete()

    @commands.group(invoke_without_command=True, aliases=["br"])
    async def boosterrole(self, ctx: commands.Context): 
      await ctx.create_pages()

    @boosterrole.command(name="setup", help="config", description="set the boosterrole module", brief="manage guild") 
    @Perms.get_perms("manage_guild")
    async def br_setup(self, ctx: commands.Context):      
        check = await self.bot.db.fetchrow("SELECT * FROM booster_module WHERE guild_id = {}".format(ctx.guild.id))
        if check is not None: return await ctx.send_warning("booster role module is **already** configured".capitalize())
        await self.bot.db.execute("INSERT INTO booster_module (guild_id) VALUES ($1)", ctx.guild.id)
        return await ctx.send_success("Configured booster role module")

    @boosterrole.command(help="config", description="unset the boosterrole module", brief="manage guild") 
    @Perms.get_perms("manage_guild")
    async def unset(self, ctx: commands.Context): 
        check = await self.bot.db.fetchrow("SELECT * FROM booster_module WHERE guild_id = {}".format(ctx.guild.id))        
        if check is None: return await ctx.send_warning("booster role module is **not** configured".capitalize())
        embed = discord.Embed(color=self.bot.color, description="Are you sure you want to unset the boosterrole module? This action is **IRREVERSIBLE**")
        yes = discord.ui.Button(emoji=self.bot.yes)
        no = discord.ui.Button(emoji=self.bot.no)
        async def yes_callback(interaction: discord.Interaction):
          if interaction.user != ctx.author: return await self.bot.ext.send_warning(interaction, "This is not your message", ephemeral=True)
          await self.bot.db.execute("DELETE FROM booster_module WHERE guild_id = $1", ctx.guild.id)
          await self.bot.db.execute("DELETE FROM booster_roles WHERE guild_id = $1", ctx.guild.id)        
          return await interaction.response.edit_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: Booster role module cleared"), view=None)

        async def no_callback(interaction: discord.Interaction): 
          if interaction.user != ctx.author: return await self.bot.ext.send_warning(interaction, "This is not your message", ephemeral=True)
          return await interaction.response.edit_message(embed=discord.Embed(color=self.bot.color, description="Alright you changed your mind"), view=None)

        yes.callback = yes_callback
        no.callback = no_callback
        view = discord.ui.View() 
        view.add_item(yes)
        view.add_item(no)
        await ctx.reply(embed=embed, view=view, mention_author=False) 

    @boosterrole.command(description="set a base role for boosterrole module", help="config", brief="manage guild")
    @Perms.get_perms("manage_guild") 
    async def base(self, ctx: commands.Context, *, role: discord.Role=None):
      check = await self.bot.db.fetchrow("SELECT base FROM booster_module WHERE guild_id = {}".format(ctx.guild.id))      
      if role is None:
        if check is None: return await ctx.send_warning("Booster role module **base role** isn't set") 
        await self.bot.db.execute("UPDATE booster_module SET base = $1 WHERE guild_id = $2", None, ctx.guild.id) 
        return await ctx.send_success("Removed base role")
      
      if role.position >= ctx.guild.get_member(self.bot.user.id).top_role.position: return await ctx.send_warning("This role can't be configured as booster role base")
      await self.bot.db.execute("UPDATE booster_module SET base = $1 WHERE guild_id = $2", role.id, ctx.guild.id) 
      return await ctx.send_success(f"set {role.mention} as base role".capitalize())
    
    @boosterrole.command(description="create a booster role", help="config", usage="<name>")
    async def create(self, ctx: commands.Context, name: str=None): 
      if not ctx.author in ctx.guild.premium_subscribers: return await ctx.send_warning("You are not a booster")
      che = await self.bot.db.fetchrow("SELECT * FROM booster_module WHERE guild_id = {}".format(ctx.guild.id))
      if che is None: return await ctx.send_warning("Booster role module is not configured")
      check = await self.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
      if check is not None: return await ctx.send_warning(f"You already have a booster role. Use `{ctx.clean_prefix}boosterrole edit` command for more")
      ro = ctx.guild.get_role(che['base'])
      role = await ctx.guild.create_role(name=f"{ctx.author.name}'s role" if not name else name)  
      await role.edit(position=ro.position if ro is not None else 1)
      await ctx.author.add_roles(role)
      await self.bot.db.execute("INSERT INTO booster_roles VALUES ($1,$2,$3)", ctx.guild.id, ctx.author.id, role.id)
      await ctx.invoke(self.bot.get_command('boosterrole edit'))
    
    @boosterrole.command(description="edit the booster role name", help="config", usage="[name]")
    @has_booster_role()
    async def name(self, ctx: commands.Context, *, name: str): 
      check = await self.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
      role = ctx.guild.get_role(check['role_id'])
      await role.edit(name=name)
      await ctx.send_success(f"Booster role name changed to: {name}")
    
    @boosterrole.command(description="edit the role icon", help="config", usage="[emoji]")
    @has_booster_role()
    async def icon(self, ctx: commands.Context, *, emoji: Union[discord.PartialEmoji, str]):      
      check = await self.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
      role = ctx.guild.get_role(check['role_id'])
      if isinstance(emoji, discord.PartialEmoji): icon = await self.bot.session.read(emoji.url)
      elif isinstance(emoji, str): icon = emoji  
      try:
       await role.edit(display_icon=icon)
       await ctx.send_success(f"Booster role icon changed")
      except discord.Forbidden as e: return await ctx.send_error(str(e))
        
    @boosterrole.command(description="change the booster role color", help="config", usage="[color]")
    @has_booster_role()
    async def color(self, ctx: commands.Context, color: str): 
     check = await self.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
     role = ctx.guild.get_role(check['role_id']) 
     color = color.replace("#", "")
     color = int(color, 16)
     await role.edit(color=color)
     return await ctx.send_success("Changed the **booster role** color") 

    @boosterrole.command(description="edit the role hoist", help="config")
    @has_booster_role()
    async def hoist(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
     role = ctx.guild.get_role(check['role_id']) 
     await role.edit(hoist=False if role.hoist else True)
     return await ctx.send_success("changed your role hoist status")

    @boosterrole.command(description="delete the booster role", help="config")
    @has_booster_role()
    async def delete(self, ctx: commands.Context): 
      check = await self.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
      role = ctx.guild.get_role(check['role_id'])  
      await role.delete()
      await ctx.send_success("Deleted the booster role")
     
    @boosterrole.command(description="edit a booster role", help="config")
    async def edit(self, ctx: commands.Context): 
        che = await self.bot.db.fetchrow("SELECT * FROM booster_module WHERE guild_id = {}".format(ctx.guild.id))
        if che is None: return await ctx.send_warning("Booster role module is not configured")
        check = await self.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
        if check is None: return await ctx.invoke(self.bot.get_command('boosterrole create'))         
        role = ctx.guild.get_role(check['role_id'])
        if role is None: options = [
            discord.SelectOption( 
            label="delete",
            description="delete your booster role",
            emoji="<:trash:1053281188036485190>"
          ),
            discord.SelectOption(
            label="cancel",
            description="cancel the booster role edit",
            emoji=self.bot.no
            )]
        else: 
          options = [ 
          discord.SelectOption(
            label="name",
            description="change the booster role name",
            emoji="<:chanwhite:1035848708832636929>"
          ),
          discord.SelectOption(
            label="color",
            description="change the color of your role",
            emoji="<:01star:987668422332657724>"
          ),
          discord.SelectOption(
            label="icon",
            description="change the role icon",
            emoji="<a:aw_whiteuser:1048166137826910258>"
          ),
          discord.SelectOption(
            label="hoist", 
            description="make your role hoisted...or not",
            emoji="<:unghost:1048166159918313482>"
          ),
          discord.SelectOption( 
            label="delete",
            description="delete your booster role",
            emoji="<:trash:1053281188036485190>"
          ),
            discord.SelectOption(
            label="cancel",
            description="cancel the booster role edit",
            emoji=self.bot.no
            )
        ]
        embed = discord.Embed(color=self.bot.color, title="booster role edit menu", description="customize your custom role using the dropdown menu below") 
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        select = discord.ui.Select(placeholder="select property..", options=options)

        async def select_callback(interaction: discord.Interaction): 
          if ctx.author != interaction.user: return await self.bot.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True)
          if select.values[0] == "cancel": return await interaction.response.edit_message(view=None)  
          elif select.values[0] == "hoist": 
            await role.edit(hoist=False if role.hoist else True)
            return await interaction.client.ext.send_success(interaction, "changed your role hoist status", ephemeral=True)

          elif select.values[0] == "delete": 
             if role is not None: await role.delete() 
             await self.bot.db.execute("DELETE FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id)) 
             await self.bot.ext.send_success(interaction, "Deleted your booster role", ephemeral=True)
             return await interaction.message.delete()

          elif select.values[0] == "name":
            mod = Modals.Name()
            await interaction.response.send_modal(mod)    

          elif select.values[0] == "icon": 
            mod = Modals.Icon()
            await interaction.response.send_modal(mod)   
          
          elif select.values[0] == "color": 
            mod = Modals.Color()
            await interaction.response.send_modal(mod) 

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)
        await ctx.reply(embed=embed, view=view, mention_author=False)

async def setup(bot): 
    await bot.add_cog(Boosters(bot))        