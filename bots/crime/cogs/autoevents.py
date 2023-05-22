import discord ; from discord.ext import commands
from cogs.utils.util import Emojis

class autoevents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


@commands.Cog.listener()
async def on_ready(self):
    async with self.bot.db.cursor() as cursor: 
        await cursor.execute("CREATE TABLE IF NOT EXISTS autoresponder (trigger TEXT, response TEXT, guild_id INTEGER)")
    await self.bot.db.commit()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message): 
       if not message.guild: return  
       if message.author.bot: return
       if message.attachments: return 
       if message.stickers: return
       if message.type != discord.MessageType.default and message.type != discord.MessageType.reply: return
       me = message.content.lower().split()
       async with self.bot.db.cursor() as cursor:
        await cursor.execute(f"SELECT * FROM autoresponder WHERE guild_id = {message.guild.id}") 
        results = await cursor.fetchall()
        if results is not None: 
          for result in results: 
            if result[0] in me:
              retry_after = self.get_ratelimit(message)
              if retry_after is not None: return
              return await message.channel.send(result[1], allowed_mentions=discord.AllowedMentions(users=True))
            

async def setup(bot):
    await bot.add_cog(autoevents(bot))