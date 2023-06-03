import discord, time, datetime, platform 
from discord.ext import commands
from cogs.events import commandhelp
from utils.classes import colors, emojis
from cogs.events import blacklist
from discord.ui import Button, View

global startTime
my_system = platform.uname()

class info(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
    
    @commands.Cog.listener()
    async def on_connect(self):
        global startTime
        startTime = time.time()

    @commands.command(help="shows bot's uptime", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def uptime(self, ctx):
     uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
     e = discord.Embed(color=0x2f3136, description=f"**{self.bot.user.name}'s** uptime: **{uptime}**")
     await ctx.reply(embed=e, mention_author=False)
    
    @commands.command(help="shows bot's latency", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user) 
    @blacklist()
    async def ping(self, ctx):
        await ctx.reply(f"...pong :ping_pong: `{round(self.bot.latency * 1000)}ms`", mention_author=False)
           
    @commands.command(help="check bot's statistics", aliases=["about", "bi", "info"], description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def botinfo(self, ctx: commands.Context): 
      lis = []  
      for i in self.bot.owner_ids:
        user = await self.bot.fetch_user(i) 
        lis.append(user.name + "#" + user.discriminator)
      embed = discord.Embed(color=0x2f3136).set_thumbnail(url=self.bot.user.display_avatar)
      embed.add_field(name="Founder", value=f"`Discord:` `{' '.join(l for l in lis)}`\n`Server:` [here](https://discord.gg/screams)", inline=False)
      embed.add_field(name="Stats", value=f"`Users:` `{sum(g.member_count for g in self.bot.guilds)}`\n`Servers:` `{len(self.bot.guilds)}`", inline=False)
      embed.add_field(name="System:", value=f"`Latency:` `{round(self.bot.latency * 1000)}ms`\n`Language`: `Python`\n`System`: `{my_system.system}`", inline=False)   
      await ctx.reply(embed=embed, mention_author=False)
                         

    @commands.command(aliases=["h"])

    async def help(self, ctx: commands.Context, *, command=None):
        if command is not None: return await commandhelp(self, ctx, command) 
        options = [
            discord.SelectOption(label="home", description="go back to the home menu"),
            discord.SelectOption(label="info", description="info commands"),
            discord.SelectOption(label="autopfp", description="autopfp commands"),
            discord.SelectOption(label="roleplay", description="roleplay commands"),
            discord.SelectOption(label="config", description="config commands"),
            discord.SelectOption(label="moderation", description="moderation commands"),
            discord.SelectOption(label="emoji", description="emoji commands")
        ]
        embed = discord.Embed(color=colors.default, description=f"{self.bot.user.name} is a multi-purpose bot with a lot of useful features lol").set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url).set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="contact", value="if you need support you can contact us in the **[support server](https://discord.gg/screams)**")
        select = discord.ui.Select(placeholder="select category...", options=options)

        async def select_callback(interaction: discord.Interaction):
          if interaction.user != ctx.author: 
            embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {interaction.user.mention} this is not your embed")
            await interaction.response.send_message(embed=embed, view=None, ephemeral=True) 
            return 
          cmds = []
          for cmd in set(self.bot.walk_commands()): 
           if cmd.description == select.values[0]: 
            if cmd.parent is not None: cmds.append(str(cmd.parent) + " " + cmd.name)
            else: cmds.append(cmd.name)
          if select.values[0] == "home":
            embed = discord.Embed(color=colors.default, description=f"{self.bot.user.name} is a multi-purpose bot with a lot of useful features lol").set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url).set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(name="contact", value="if you need support you can contact us in the **[support server](https://discord.gg/arrest)**")
            embed.set_footer(text=f"{len(self.bot.commands)} commands")
            await interaction.response.edit_message(embed=embed)  
          elif select.values[0] == "nsfw":
            if not ctx.channel.is_nsfw():
              embed = discord.Embed(color=colors.default, description=f"{emojis.warn} {interaction.user.mention} this channel must be age resteicted")
              await interaction.response.send_message(embed=embed, view=None, ephemeral=True) 
            else:
              em = discord.Embed(color=colors.default).set_author(name=select.values[0], icon_url=self.bot.user.display_avatar.url).set_footer(text=f"{len(set(self.bot.walk_commands()))} commands") 
              em.add_field(name="commands", value=", ".join(f"`{c}`" for c in cmds))
              await interaction.response.edit_message(embed=em)  
          else:
            em = discord.Embed(color=colors.default).set_author(name=select.values[0], icon_url=self.bot.user.display_avatar.url).set_footer(text=f"{len(set(self.bot.walk_commands()))} commands") 
            em.add_field(name="commands", value=", ".join(f"`{c}`" for c in cmds))
            await interaction.response.edit_message(embed=em) 
                        
        select.callback = select_callback 
        button1 = Button(label=f"invite {self.bot.user.name}", url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot")
        button2 = Button(label=f"support", url="https://discord.gg/screams")
      
        view = discord.ui.View()
        view.add_item(select)
        view.add_item(button1)
        view.add_item(button2)
        await ctx.reply(embed=embed, mention_author=False, view=view)   

    @commands.command(description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def invite(self, ctx: commands.Context):
      button1 = Button(label=f"invite {self.bot.user.name}", url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot")
      button2 = Button(label=f"buy", url=f"https://discord.gg/screams")
      view = View()
      view.add_item(button1)
      view.add_item(button2)
      await ctx.reply(view=view, mention_author=False)

    @commands.command(description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def buy(self, ctx: commands.Context):
      button1 = Button(label=f"buy", url=f"https://discord.gg/screams")
      view = View()
      view.add_item(button1)
      await ctx.reply(view=view, mention_author=False)

async def setup(bot):
    await bot.add_cog(info(bot))
