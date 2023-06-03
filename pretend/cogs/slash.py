import discord, datetime
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, View, Button
from deep_translator import GoogleTranslator

@app_commands.context_menu(name="translate")
async def translate(interaction: discord.Interaction, message: discord.Message): 
  if not message.content: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description="{} {}: There is no message to translate".format(interaction.client.warning, interaction.user.mention)), ephemeral=True)
  options = [
    discord.SelectOption(
      label="english"
    ),
    discord.SelectOption(
      label="romanian"
    ),
    discord.SelectOption(
      label="french"
    ),
    discord.SelectOption(
      label="spanish"
    ),
    discord.SelectOption(
      label="arabic"
    ),
    discord.SelectOption(
      label="russian"
    ),
    discord.SelectOption(
      label="german"
    ),
    discord.SelectOption(
      label="swedish"
    ),
    discord.SelectOption(
      label="chinese"
    ),
    discord.SelectOption(
      label="japanese"
    ),
    discord.SelectOption(
      label="italian"
    )
  ]
  select = discord.ui.Select(options=options, placeholder="select a language...")
  embed = discord.Embed(color=interaction.client.color, description="🔍 {}: Select the language you want to translate `{}` in".format(interaction.user.mention, message.content))

  async def select_callback(inter: discord.Interaction): 
    if inter.user.id != interaction.user.id: return await inter.response.send_message(embed=discord.Embed(color=interaction.client.color, description="{} {}: You are not the author of this embed".format(interaction.client.warning, inter.user.mention)), ephemeral=True)
    translated = GoogleTranslator(source="auto", target=select.values[0]).translate(message.content)
    e = discord.Embed(color=interaction.client.color, title="translated to {}".format(select.values[0]), description="```{}```".format(translated))
    v = discord.ui.View()
    v.add_item(discord.ui.Button(label="original message", url=message.jump_url))
    await inter.response.edit_message(embed=e, view=v)
  select.callback = select_callback  

  view = View()
  view.add_item(select)
  await interaction.response.send_message(embed=embed, view=view)

@app_commands.context_menu(name="steal sticker")
async def steal_sticker(interaction: discord.Interaction, message: discord.Message): 
  if not interaction.user.guild_permissions.manage_emojis_and_stickers: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.warning} {interaction.user.mention}: you are missing permission `manage_emojis_and_stickers`"), ephemeral=True)
  if not message.stickers: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.no} {interaction.user.mention}: This message doesn't have any sticker"), ephemeral=True)
  try:
         url = message.stickers[0].url
         name = message.stickers[0].name
         file = discord.File(fp=await interaction.client.getbyte(url))
         sticker = await interaction.guild.create_sticker(name=name, description=name, emoji="skull", file=file, reason=f"sticker created by {interaction.user}")
         format = str(sticker.format) 
         form = format.replace("StickerFormatType.", "")
         embed = discord.Embed(color=interaction.client.color, title="sticker added")
         embed.set_thumbnail(url=url)
         embed.add_field(name="values", value=f"name: `{name}`\nid: `{sticker.id}`\nformat: `{form}`\nlink: [url]({url})")
         await interaction.response.send_message(embed=embed)
  except Exception as error:
       embed = discord.Embed(color=interaction.client.color, description=f"{interaction.client.no} {interaction.user.mention}: unable to add this sticker - {error}")
       await interaction.response.send_message(embed=embed, ephemeral=True)

@app_commands.context_menu(name="grab sticker")
async def grab_sticker(interaction: discord.Interaction, message: discord.Message): 
  if not message.stickers: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.no} {interaction.user.mention}: This message doesn't have any sticker"), ephemeral=True)
  options = []
  for g in interaction.user.mutual_guilds:
    if g.get_member(interaction.user.id).guild_permissions.manage_emojis_and_stickers and len(g.stickers) < g.sticker_limit: options.append(discord.SelectOption(label=g.name, value=str(g.id), description=g.description))
  
  if len(options) == 0: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.no} {interaction.user.mention}: You can't add this sticker anywhere"), ephemeral=True)
  embed = discord.Embed(color=interaction.client.color, description=f"🔍 Where should `{message.stickers[0].name}` be addded?") 
  select = discord.ui.Select(options=options, placeholder="select a server", max_values=len(options))

  async def select_callback(inte: discord.Interaction): 
    sticker = message.stickers[0]
    url = sticker.url
    name = sticker.name
    for value in select.values: 
         file = discord.File(fp=await interaction.client.ext.getbyte(url))
         sticker = await inte.client.get_guild(int(value)).create_sticker(name=name, description=name, emoji="skull", file=file, reason=f"sticker created by {interaction.user}")
    
    await inte.response.edit_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.yes} {inte.user.mention}: Added `{sticker.name}` in **{len(select.values)}** servers"), view=None)

  select.callback = select_callback
  view = discord.ui.View()
  view.add_item(select)
  await interaction.response.send_message(embed=embed, view=view, ephemeral=True) 

@app_commands.context_menu(name="user avatar")
async def user_avatar(interaction: discord.Interaction, member: discord.Member):
        button1 = Button(label="default avatar", url=member.avatar.url or member.default_avatar.url)
        button2 = Button(label="server avatar", url=member.display_avatar.url)
        embed = discord.Embed(color=interaction.client.color, title=f"{member.name}'s avatar", url=member.display_avatar.url)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        view = View()
        view.add_item(button1)
        view.add_item(button2) 
        await interaction.response.send_message(embed=embed, view=view)

@app_commands.context_menu(name="user banner")
async def user_banner(interaction: discord.Interaction, member: discord.Member): 
     user = await interaction.client.fetch_user(member.id)
     if not user.banner:
      if user.accent_colour is None: return await interaction.client.ext.send_error(interaction, "**{}** Doesn't have a banner".format(str(user)), ephemeral=True) 
      hexcolor = hex(user.accent_colour.value)
      hex2 = hexcolor.replace("0x", "")
      e = discord.Embed(color=interaction.client.color, title=f"{user.name}'s banner", url=f"https://singlecolorimage.com/get/{hex2}/400x100")
      e.set_image(url=f"https://singlecolorimage.com/get/{hex2}/400x100")
      return await interaction.response.send_message(embed=e)
       
     embed = discord.Embed(color=interaction.client.color, title=f"{user.name}'s banner", url=user.banner.url)
     embed.set_image(url=user.banner.url)
     await interaction.response.send_message(embed=embed)

class confessModal(Modal, title="confess here"):
      name = discord.ui.TextInput(
        label='confession',
        placeholder='the confession is anonymous',
        style=discord.TextStyle.long,
    )

      async def on_submit(self, interaction: discord.Interaction):
       try:
         check = await interaction.client.db.fetchrow("SELECT * FROM confess WHERE guild_id = {}".format(interaction.guild.id)) 
         if check:
          channel = interaction.guild.get_channel(check['channel_id']) 
          count = check['confession']+1
          links = ["https://", "http://", ".com", ".ro", ".gg", ".xyz", ".cf", ".org", ".ru", ".it", ".de"]
          if any(link in self.children[0].value for link in links): return await interaction.client.ext.send_warning(interaction, "i can't send links. those things can be dangerous !!".capitalize(), ephemeral=True)
          embed = discord.Embed(color=interaction.client.color, description=f"{interaction.user.mention}: sent your confession in {channel.mention}")
          await interaction.response.send_message(embed=embed, ephemeral=True)
          e = discord.Embed(color=interaction.client.color, description=f"{self.name.value}", timestamp=datetime.datetime.now())
          e.set_author(name=f"anonymous confession #{count}", url="https://discord.gg/4D5zzsYcUx", icon_url=interaction.guild.icon)
          e.set_footer(text="type /confess to send a confession")            
          await channel.send(embed=e)
          await interaction.client.db.execute("UPDATE confess SET confession = $1 WHERE guild_id = $2", count, interaction.guild.id) 
          await interaction.client.db.execute("INSERT INTO confess_members VALUES ($1,$2,$3)", interaction.guild.id, interaction.user.id, count)
       except Exception as e: return await interaction.client.ext.send_error(interaction, f"Couldn't send your confession - {e}")

class Cog(commands.Cog):
 def __init__(self, bot: commands.AutoShardedBot):
    self.bot = bot
    try:
            self.bot.tree.add_command(user_avatar)
            self.bot.tree.add_command(steal_sticker)
            self.bot.tree.add_command(grab_sticker)
            self.bot.tree.add_command(translate)
            self.bot.tree.add_command(user_banner)
            print("added")
    except:
            self.bot.tree.remove_command("user avatar", type=discord.AppCommandType.message)
            self.bot.tree.remove_command("translate", type=discord.AppCommandType.message)
            self.bot.tree.remove_command("steal sticker", type=discord.AppCommandType.message)
            self.bot.tree.remove_command("grab sticker", type=discord.AppCommandType.message)
            self.bot.tree.remove_command("user banner", type=discord.AppCommandType.user)
            self.bot.tree.add_command(user_avatar)
            self.bot.tree.add_command(steal_sticker)
            self.bot.tree.add_command(grab_sticker)
            self.bot.tree.add_command(translate)
            self.bot.tree.add_command(user_banner)

 @app_commands.command(name="confess", description="anonymously confess your thoughts")
 async def confess(self , ctx: discord.Interaction):
    re = await ctx.client.db.fetchrow("SELECT * FROM confess_mute WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.user.id)
    if re: await ctx.client.ext.send_error(ctx, "You are **muted** from sending confessions in this server", ephemeral=True)
    check = await self.bot.db.fetchrow("SELECT channel_id FROM confess WHERE guild_id = {}".format(ctx.guild.id))
    if check: return await ctx.response.send_modal(confessModal())
    return await self.bot.ext.send_error(ctx, "Confessions aren't enabled in this server", ephemeral=True)

 @app_commands.command(name="poll", description="create a poll")
 async def poll(self, ctx: discord.Interaction, question: str, first: str, second: str):
  embed = discord.Embed(color=ctx.client.color, title=question, description=f"1️⃣ - {first}\n\n2️⃣ - {second}")
  embed.set_footer(text=f"poll created by {ctx.user}")
  channel = self.bot.get_channel(ctx.channel.id)
  await ctx.response.send_message('poll sent', ephemeral=True)
  mes = await channel.send(embed=embed)
  emoji1 = '1️⃣'
  emoji2 = '2️⃣'
  await mes.add_reaction(emoji1)
  await mes.add_reaction(emoji2)    

async def setup(bot) -> None:
    await bot.add_cog(Cog(bot))    