import discord 
from discord.ext import commands 

owners = [371224177186963460, 911351586398294037]
wrong = "<:x_denied:1030181108916174848>"

async def commandhelp(self, ctx, cmd):
    try:
       command = self.bot.get_command(cmd)
       if command.usage is None:
        usage = ""
       else:
        usage = command.usage 
       embed = discord.Embed(color=0x2f3136, title=command, description=command.help)
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="category", value=command.cog_name)
       embed.add_field(name="permissions", value=command.description or "any")
       if command.brief:
        embed.add_field(name="commands", value=command.brief, inline=False)
       embed.add_field(name="usage", value=f"```{cmd} {usage}```", inline=False)
       embed.add_field(name="aliases", value=", ".join(map(str, command.aliases)) or "none")
       embed.set_thumbnail(url=self.bot.user.avatar.url)
       await ctx.reply(embed=embed, mention_author=False)
    except:
       await ctx.reply(f"command `{cmd}` not found", mention_author=False)

class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.content == f"<@{self.bot.user.id}>":
            await message.reply(f"prefix: `,`")

    @commands.Cog.listener() 
    async def on_guild_join(self, guild: discord.Guild):
     async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
      mem = entry.user
      if entry.target.id == self.bot.user.id:
       if guild.member_count < 20:
        if not mem.id in owners: 
          await guild.leave()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): 
       if isinstance(error, commands.CommandNotFound):
        return 
       else:   
        e = discord.Embed(color=0xff0000, description=f"{wrong} {ctx.author.mention} {error}")
        await ctx.reply(embed=e, mention_author=False)            



  
async def setup(bot):
    await bot.add_cog(events(bot))         
