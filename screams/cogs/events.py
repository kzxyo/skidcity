import discord, re, datetime
from discord.ext import commands 
from utils.classes import colors, emojis
from discord.ui import Button, View

async def noperms(self, ctx, permission):
    e = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permission `{permission}`")
    await sendmsg(self, ctx, None, e, None, None, None)

def blacklist(): 
        async def predicate(ctx): 
            if ctx.guild is None:
             return False
            async with ctx.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(ctx.author.id))
                check = await cursor.fetchone()
                return check is None
        return commands.check(predicate)

async def sendmsg(self, ctx, content, embed, view, file, allowed_mentions): 
    if ctx.guild is None: return
    try:
       await ctx.reply(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions, mention_author=False)
    except:
        await ctx.send(content=content, embed=embed, view=view, file=file, allowed_mentions=allowed_mentions)

async def commandhelp(self, ctx, cmd):
    try:
       command = self.bot.get_command(cmd)
       if command.usage is None:
        usage = ""
       else:
        usage = command.usage 
       embed = discord.Embed(color=colors.default, title=command, description=command.help)
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="category", value=command.description)
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
        if f"<@{self.bot.user.id}>" in message.content:
           await message.reply(f"prefix: `!`")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
     if message.guild:
      if not message.author.guild_permissions.manage_guild:
        result = re.search("(?P<url>https?:\/\/[^\s]+)", message.content)
        if result:
          await message.delete()
          await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=300), reason="Antinuke: sending links")
        else: return

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM whitelisted WHERE guild = {}".format(guild.id))
        check = await cursor.fetchone()     
        if check is None:
          await guild.leave()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): 
       if isinstance(error, commands.CommandNotFound): return
       elif isinstance(error, commands.CheckFailure): return 
       else:   
        try:
         e = discord.Embed(color=colors.default, description=f"{emojis.bigwarn} {ctx.author.mention} {error}")
         await ctx.reply(embed=e, mention_author=False)
        except: 
            pass         
 
async def setup(bot):
    await bot.add_cog(events(bot))         
