import discord
from discord.ext import commands
from .utils.util import Emojis, Colors
from .utils.embedparser import to_object
from cogs.utilevents import blacklist

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
  
    @commands.group(aliases=["welc", "wlc"], invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def welcome(self, ctx):
        if ctx.subcommand_passed is not None:
          embed = discord.Embed(color=0xf7f9f8, title="welcome", description="greet your users into your guild")
          embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
          embed.add_field(name="category", value="config")
          embed.add_field(name="commands", value=">>> ,welcome message\n,welcome channel\n,welcome config\n,welcome variables\n,welcome delete\n,welcome test", inline=False)
          embed.add_field(name="usage", value="```,welcome message hello {user}!```", inline=False)
          embed.set_footer(text=f"aliases: welc, wlc")
          embed.set_thumbnail(url=self.bot.user.display_avatar.url)
          embed.set_footer(text="powered by crime")
          await ctx.reply(embed=embed, mention_author=False)
  
  
    @welcome.command(help="configure a welcome message for your server", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def message(self, ctx, *, code=None):
        if not ctx.author.guild_permissions.manage_guild:
            embed = discord.Embed(color=Colors.default, description=f"{Emojis.warn} you are missing permissions **manage_guild**")
            await ctx.reply(embed=embed, mention_author=False)
            return
        embed=discord.Embed(description=f"set welcome message to `{code}`", color=Colors.default)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            if check is None:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("INSERT INTO welcome (guild, message, channel) VALUES (?, ?, ?)", (ctx.guild.id, code, None))
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
            embed = discord.Embed(color=Colors.default, description=f"{Emojis.warn} you are missing permissions **manage_guild**")
            await ctx.reply(embed=embed, mention_author=False)
            return
        embed=discord.Embed(description=f"set welcome channel to {channel.mention}", color=Colors.default)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
            check = await cursor.fetchone()
            if check is None:
                async with self.bot.db.cursor() as cursor:
                    await cursor.execute("INSERT INTO welcome (guild, message, channel) VALUES (?, ?, ?", (ctx.guild.id, None, channel.id))
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
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warn} you are missing permissions **manage_guild**") 
        await ctx.reply(embed=embed, mention_author=False)
        return
        
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("SELECT * FROM welcome WHERE guild = {}".format(ctx.guild.id))
        check = await cursor.fetchone()
        msg = check[1] or "welcome message not set"
        chan = f"<#{check[2]}>" or "welcome channel not set"
        embed=discord.Embed(title="welcome message config", color=Colors.default)
        embed.add_field(name="message", value=f"```{msg}```")
        embed.add_field(name="channel", value=f"{chan.mention}")
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_footer(text="powered by crime")
        await ctx.reply(embed=embed, mention_author=False)

    @welcome.command(help="view the welcome variables", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def variables(self, ctx):   
      embed=discord.Embed(description="here is a list of variables used to greet your members", color=Colors.default)
      embed.add_field(name="member", value=">>> {user}\n{user.name}\n{user.mention}\n{user.avatar}\n{user.discriminator}\n{user.joined_at}")
      embed.add_field(name="guild", value=">>> {guild.name}\n{guild.count}\n{guild.icon}\n{guild.id}")
      embed.set_thumbnail(url=ctx.guild.icon.url)
      embed.set_footer(text="powered by crime")
      await ctx.reply(embed=embed, mention_author=False)

    @welcome.command(help="delete your welcome config", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def delete(self, ctx):   
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warn} you are missing permissions **manage_guild**") 
        await ctx.reply(embed=embed, mention_author=False)
        return
      async with self.bot.db.cursor() as cursor:
        await cursor.execute("DELETE FROM welcome WHERE guild = {}".format(ctx.guild.id))
      await self.bot.db.commit()
      embed=discord.Embed(description=f"{Emojis.check} deleted the welcome config for *{ctx.guild.name}*", color=Colors.default)
      await ctx.reply(embed=embed, mention_author=False)


    @welcome.command(help="tests your welcome message", description="config")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist()
    async def test(self, ctx):   
      if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(color=Colors.default, description=f"{Emojis.warn} you are missing permissions **manage_guild**") 
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
          embed=discord.Embed(description=f"{Emojis.warn} welcome message isnt configured for *{ctx.guild.name}*", color=Colors.default)
          await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(welcome(bot))