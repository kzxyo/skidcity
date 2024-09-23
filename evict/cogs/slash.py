import discord, datetime, aiohttp, io
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, View
from deep_translator import GoogleTranslator

@app_commands.context_menu(name="translate")
async def translate(interaction: discord.Interaction, message: discord.Message): 
  if not message.content: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description="{} {}: there is no message to translate".format(interaction.client.warning, interaction.user.mention)), ephemeral=True)
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
  select = discord.ui.Select(options=options, placeholder="select a language")
  embed = discord.Embed(color=interaction.client.color, description="🔍 {}: select the language you want to translate `{}` in".format(interaction.user.mention, message.content))

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

@app_commands.context_menu(name="steal emoji")
async def steal_emoji(interaction: discord.Interaction, message: discord.Message): 
  if not interaction.user.guild_permissions.manage_emojis_and_stickers: return await interaction.response.send_message(embed=discord.Embed(description=f"{interaction.client.warning} {interaction.user.mention}: you are missing permission `manage_emojis_and_stickers`"), ephemeral=True)
  try:
        if message.stickers:
            emojis = message.stickers
        added_emojis = []
        emojis = list(dict.fromkeys(emojis))
        async with aiohttp.ClientSession() as session:
            for emoji in interaction.guild.emojis:
                if added_emojis:
                        return await interaction.edit_original_response(content='added emojis')
                try:
                    async with session.get(emoji.url) as resp:
                        image = io.BytesIO(await resp.read()).read()
                    added = await interaction.guild.create_custom_emoji(name=emoji.name, image=image)
                except Exception as error:
                    embed = discord.Embed(color=interaction.client.color, description=f"{interaction.client.no} {interaction.user.mention}: unable to add emojis - {error}")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    if added_emojis:
                      return await interaction.edit_original_response(content='added emojis')
                added_emojis.append(added)
        
        response = ' '.join([str(e) for e in added_emojis])
        await interaction.edit_original_response(content=response)
  except Exception as error:
       embed = discord.Embed(color=interaction.client.color, description=f"{interaction.client.no} {interaction.user.mention}: unable to add emojis - {error}")
       await interaction.response.send_message(embed=embed, ephemeral=True)

@app_commands.context_menu(name="steal sticker")
async def steal_sticker(interaction: discord.Interaction, message: discord.Message): 
  if not interaction.user.guild_permissions.manage_emojis_and_stickers: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.warning} {interaction.user.mention}: you are missing permission `manage_expressions`"), ephemeral=True)
  if not message.stickers: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.no} {interaction.user.mention}: this message doesnt have any sticker"), ephemeral=True)
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
  if not message.stickers: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.no} {interaction.user.mention}: this message doesn't have any sticker"), ephemeral=True)
  options = []
  for g in interaction.user.mutual_guilds:
    if g.get_member(interaction.user.id).guild_permissions.manage_emojis_and_stickers and len(g.stickers) < g.sticker_limit: options.append(discord.SelectOption(label=g.name, value=str(g.id), description=g.description))
  
  if len(options) == 0: return await interaction.response.send_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.no} {interaction.user.mention}: you cant add this sticker anywhere"), ephemeral=True)
  embed = discord.Embed(color=interaction.client.color, description=f"🔍 where should `{message.stickers[0].name}` be added?") 
  select = discord.ui.Select(options=options, placeholder="select a server", max_values=len(options))

  async def select_callback(inte: discord.Interaction): 
    sticker = message.stickers[0]
    url = sticker.url
    name = sticker.name
    for value in select.values: 
         file = discord.File(fp=await interaction.client.ext.getbyte(url))
         sticker = await inte.client.get_guild(int(value)).create_sticker(name=name, description=name, emoji="skull", file=file, reason=f"sticker created by {interaction.user}")
    
    await inte.response.edit_message(embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.yes} {inte.user.mention}: added `{sticker.name}` in **{len(select.values)}** servers"), view=None)

  select.callback = select_callback
  view = discord.ui.View()
  view.add_item(select)
  await interaction.response.send_message(embed=embed, view=view, ephemeral=True) 


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
          if any(link in self.children[0].value for link in links): return await interaction.client.ext.warning(interaction, "i can't send links. those things can be dangerous !!".capitalize(), ephemeral=True)
          embed = discord.Embed(color=interaction.client.color, description=f"{interaction.user.mention}: sent your confession in {channel.mention}")
          await interaction.response.send_message(embed=embed, ephemeral=True)
          e = discord.Embed(color=interaction.client.color, description=f"{self.name.value}", timestamp=datetime.datetime.now())
          e.set_author(name=f"anonymous confession #{count}", url="https://discord.gg/evict", icon_url=interaction.guild.icon)
          e.set_footer(text="type /confess to send a confession")            
          await channel.send(embed=e)
          await interaction.client.db.execute("UPDATE confess SET confession = $1 WHERE guild_id = $2", count, interaction.guild.id) 
          await interaction.client.db.execute("INSERT INTO confess_members VALUES ($1,$2,$3)", interaction.guild.id, interaction.user.id, count)
       except Exception as e: return await interaction.client.ext.error(interaction, f"Couldn't send your confession - {e}")

class Cog(commands.Cog):
 def __init__(self, bot: commands.Bot):
    self.bot = bot
    try:
            self.bot.tree.add_command(steal_sticker)
            self.bot.tree.add_command(grab_sticker)
            self.bot.tree.add_command(translate)
            self.bot.tree.add_command(steal_emoji)
            print("added")
    except:
            self.bot.tree.remove_command("translate", type=discord.AppCommandType.message)
            self.bot.tree.remove_command("steal sticker", type=discord.AppCommandType.message)
            self.bot.tree.remove_command("grab sticker", type=discord.AppCommandType.message)
            self.bot.tree.remove_command("steal emoji", type=discord.AppCommandType.message)
            self.bot.tree.add_command(steal_sticker)
            self.bot.tree.add_command(grab_sticker)
            self.bot.tree.add_command(translate)
            self.bot.tree.add_command(steal_emoji)

 @app_commands.command(name="confess", description="anonymously confess your thoughts")
 async def confess(self , ctx: discord.Interaction):
    re = await ctx.client.db.fetchrow("SELECT * FROM confess_mute WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.user.id)
    if re: await ctx.client.ext.error(ctx, "you are **muted** from sending confessions in this server", ephemeral=True)
    check = await self.bot.db.fetchrow("SELECT channel_id FROM confess WHERE guild_id = {}".format(ctx.guild.id))
    if check: return await ctx.response.send_modal(confessModal())
    return await self.bot.ext.error(ctx, "confessions aren't enabled in this server", ephemeral=True)   

async def setup(bot) -> None:
    await bot.add_cog(Cog(bot))    