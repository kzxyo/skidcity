import discord, datetime, time
from discord.ext import commands
from discord.ui import Button, View
from utils.classes import emojis, colors
from utils.embedparser import to_object
from cogs.events import blacklist, commandhelp


global startTime

class welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS welcome (guild INTEGER, message TEXT, channel INTEGER);") 
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(member.guild.id))
        check = await cursor.fetchone()
        if check is not None:
          msg = check[1]
          chan = check[2]
          channel = self.bot.get_channel(chan)
          user = member
          guild = member.guild
          z = msg.replace('{user}', f'{user}').replace('{user.name}', f'{user.name}').replace('{user.mention}', f'{user.mention}').replace('{user.avatar}', user.avatar.url).replace('{user.joined_at}', f'<t:{int(user.created_at.timestamp())}:R>').replace('{user.discriminator}', f'{user.discriminator}').replace('{guild.name}', f'{guild.name}').replace('{guild.count}', f'{guild.member_count}').replace('{guild.icon}', guild.icon.url).replace('{guild.id}', f'{guild.id}')
          x = await to_object(z)
          await channel.send(**x)
  
    @commands.group(aliases=["welc"], invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def welcome(self, ctx):
      embed=discord.Embed(description="configure a welcome message for your server - `$embedbuilder` for info on making a embed", color=colors.default)
      embed.add_field(name="commands", value=">>> welcome message - configure a welcome message\nwelcome channel - configure the welcome channel\nwelcome config - check the welcome settings\nwelcome variables - check the variables\nwelcome delete - deletes welcome message\nwelcome test - test your welcome channel")
      await ctx.reply(embed=embed, mention_author=False)

  
    @welcome.command(help="configure a welcome message for your server", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def message(self, ctx, *, code=None):   
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return
      embed=discord.Embed(description=f"{emojis.approve} {ctx.author.mention} set welcome message to ```{code}```", color=colors.default)
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
          async with self.bot.db.cursor() as cursor:
            await cursor.execute("INSERT INTO welcome VALUES (?, ?, ?)", (ctx.guild.id, code, None))
          await self.bot.db.commit()
          await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
          async with self.bot.db.cursor() as cursor:
            await cursor.execute("UPDATE welcome SET message = ? WHERE guild = ?", (code, ctx.guild.id))
          await self.bot.db.commit()
          await ctx.reply(embed=embed, mention_author=False)

    @welcome.command(help="configure a welcome channel for your server", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def channel(self, ctx, channel: discord.TextChannel=None):  
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return
      embed=discord.Embed(description=f"{emojis.approve} {ctx.author.mention} set welcome channel to {channel.mention}", color=colors.default)
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is None:
          async with self.bot.db.cursor() as cursor:
            await cursor.execute("INSERT INTO welcome VALUES (?, ?, ?)", (ctx.guild.id, None, channel.id))
          await self.bot.db.commit()
          await ctx.reply(embed=embed, mention_author=False)
        elif check is not None:
          async with self.bot.db.cursor() as cursor:
            await cursor.execute("UPDATE welcome SET channel = ? WHERE guild = ?", (channel.id, ctx.guild.id))
          await self.bot.db.commit()
          await ctx.reply(embed=embed, mention_author=False)

    @welcome.command(help="check your welcome settings for your server", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def config(self, ctx):   
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return
        
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        msg = check[1] or "welcome message not set"
        chan = f"<#{check[2]}>" or "`welcome channel not set`"
        embed=discord.Embed(title="welcome message config", color=colors.default)
        embed.add_field(name="message", value=f"```{msg}```")
        embed.add_field(name="channel", value=f"{chan}")
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_author(name=f"{ctx.author.mention}", icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

    @welcome.command(help="veiw welcome variables", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def variables(self, ctx):   
      embed=discord.Embed(description="use the welome variables for your welcome message/embed", color=colors.default)
      embed.add_field(name="user related", value=">>> {user} - returns user full name\n{user.name} return user's username\n{user.mention} - mention user\n{user.avatar} - return user's avatar\n{user.discriminator}- return user's discriminator\n{user.joined_at} - returns the  relative time user joined the server")
      embed.add_field(name="guild related", value=">>>{guild.name} - return server's name\n{guild.count} - return server's member count\n{guild.icon} - returns server's icon\n{guild.id} - returns server's id")
      embed.set_thumbnail(url=ctx.guild.icon.url)
      embed.set_author(name=f"{ctx.author.mention}", icon_url=ctx.author.avatar.url)
      await ctx.reply(embed=embed, mention_author=False)

    @welcome.command(help="delete your welcome message", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def delete(self, ctx):   
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("DELETE FROM welcome WHERE guild = {}".format(ctx.guild.id))
      await self.bot.db.commit()
      embed=discord.Embed(description=f"{emojis.approve} {ctx.author.mention} deleted the welcome message for `{ctx.guild.name}`", color=colors.default)
      await ctx.reply(embed=embed, mention_author=False)

    @welcome.command(help="delete your welcome message", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def test(self, ctx):   
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {ctx.author.mention} you are missing permissions `manage_guild`") 
        await ctx.reply(embed=embed, mention_author=False)
        return
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        if check is not None:
          msg = check[1]
          chan = check[2]
          channel = self.bot.get_channel(chan)
          user = ctx.author
          guild = ctx.guild
          z = msg.replace('{user}', f'{user}').replace('{user.name}', f'{user.name}').replace('{user.mention}', f'{user.mention}').replace('{user.avatar}', user.avatar.url).replace('{user.joined_at}', f'<t:{int(user.created_at.timestamp())}:R>').replace('{user.discriminator}', f'{user.discriminator}').replace('{guild.name}', f'{guild.name}').replace('{guild.count}', f'{guild.member_count}').replace('{guild.icon}', guild.icon.url).replace('{guild.id}', f'{guild.id}')
          x = await to_object(z)
          await channel.send(**x)
          await ctx.reply(f"<#{chan}>", mention_author=False)
        elif check is None:
          embed=discord.Embed(description=f"{emojis.warn} {ctx.author.mention} welcome message isnt configured for `{ctx.guild.name}`", color=colors.default)
          await ctx.reply(embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(welcome(bot))
