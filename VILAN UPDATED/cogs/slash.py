import discord, datetime
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal

class confessModal(Modal, title="confess your thoughts"):
      name = discord.ui.TextInput(
        label='confession',
        placeholder='the confession is anonymous',
        style=discord.TextStyle.long,
        required=True,
    )

      async def on_submit(self, interaction: discord.Interaction):
       try:
         check = await interaction.client.db.fetchrow("SELECT * FROM confess WHERE guild_id = {}".format(interaction.guild.id)) 
         if check:
          channel = interaction.guild.get_channel(check['channel_id']) 
          count = check['confession']+1
          links = ["https://", "http://", ".com", ".ro", ".gg", ".xyz", ".cf", ".org", ".ru", ".it", ".de"]
          if any(link in self.children[0].value for link in links): return await interaction.client.ext.send_warning(interaction, "i cannot send links.".capitalize(), ephemeral=True)
          embed = discord.Embed(color=interaction.client.color, description=f"{interaction.client.yes} {interaction.user.mention}: your confession has been sent in {channel.mention}")
          await interaction.response.send_message(embed=embed, ephemeral=True)
          e = discord.Embed(color=interaction.client.color, description=f"{self.name.value}", timestamp=datetime.datetime.now())
          e.set_author(name=f"anonymous confession #{count}", icon_url=interaction.guild.icon)#,, url="https://discord.gg/kQcYeuDjvN")
          e.set_footer(text="to send a confession, type /confess")           
          await channel.send(embed=e)
          await interaction.client.db.execute("UPDATE confess SET confession = $1 WHERE guild_id = $2", count, interaction.guild.id) 
          await interaction.client.db.execute("INSERT INTO confess_members VALUES ($1,$2,$3)", interaction.guild.id, interaction.user.id, count)
       except Exception as e: return await interaction.client.ext.send_error(interaction, f"Couldn't send your confession - {e}")

class Cog(commands.Cog):
 def __init__(self, bot: commands.AutoShardedBot):
    self.bot = bot
 
 @app_commands.command(name="confess", description="confess your thoughts")
 async def confess(self , ctx: discord.Interaction):
    check = await self.bot.db.fetchrow("SELECT channel_id FROM confess WHERE guild_id = {}".format(ctx.guild.id))
    if check: return await ctx.response.send_modal(confessModal())
    return await self.bot.ext.send_error(ctx, "Confessions are **not** enabled in this server", ephemeral=True)
 
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