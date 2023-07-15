import discord, datetime 
from discord.ext import commands 

async def noperms(self, ctx, permission):
    e = discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.author.mention}: you are missing permission `{permission}`")
    await sendmsg(self, ctx, None, e, None, None, None)

def blacklist(): 
        async def predicate(ctx): 
            if ctx.guild is None:
             return False
            async with ctx.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(ctx.author.id))
                check = await cursor.fetchone()
                if check is not None: 
                   await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.author.mention}: You are blacklisted."), mention_author=False)
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

       embed = discord.Embed(
                title=f"command: {command.name}", description=command.help or "N/A", color=self.bot.color)
       embed.add_field(name="Aliases", value="" +
                                ", ".join(command.aliases) + "")
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="command usage", value=f"```;{cmd} {usage}```", inline=False)
       embed.set_thumbnail(url=self.bot.user.display_avatar.url)
       await ctx.reply(embed=embed, mention_author=False)
    except:
       await ctx.reply(f"command `{cmd}` not found", mention_author=False)

class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): 
       if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description=f"Missing required argument `<{error.param.name}>`", color=self.bot.color)
            
       if isinstance(error, commands.CommandNotFound): return
       elif isinstance(error, commands.CheckFailure): return 
       else:   
        try:
         e = discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.author.mention}: {error}")
         await ctx.reply(embed=e, mention_author=False)
        except: 
            pass
          
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
      channel = self.bot.get_channel(1100437555519963186) 
      embed = discord.Embed(color=colors.default, description=f"joined **{guild.name}** (`{guild.id}`) owned by {guild.owner} ({guild.member_count})")
      await channel.send(embed=embed)             

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
      channel = self.bot.get_channel(1100437555519963186) 
      embed = discord.Embed(color=colors.default, description=f"left **{guild.name}** (`{guild.id}`) owned by {guild.owner} ({guild.member_count})")
      await channel.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_message_edit(self, before, after): 
        await self.bot.process_commands(after)


async def setup(bot):
    await bot.add_cog(Events(bot))      