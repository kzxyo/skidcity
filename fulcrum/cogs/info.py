import discord, time, platform 
from discord.ext import commands 
from cogs.events import seconds_to_dhms, blacklist, commandhelp

my_system = platform.uname()

class info(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
      self.bot = bot 
    
    @commands.command(help="check the bot's latency", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def ping(self, ctx: commands.Context): 
      await ctx.reply("...pong 🏓 `{}ms`".format(round(self.bot.latency * 1000)))  

    @commands.command(help="check the bot's uptime", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def uptime(self, ctx: commands.Context):  
     uptime = int(time.time() - self.bot.uptime)
     e = discord.Embed(color=0x2f3136, description=f"⏰ **{self.bot.user.name}'s** uptime: **{seconds_to_dhms(uptime)}**")
     await ctx.reply(embed=e, mention_author=False) 

    @commands.command(help="check bot's statistics", aliases=["about", "bi", "info"], description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def botinfo(self, ctx: commands.Context): 
      lis = []  
      for i in self.bot.owner_ids:
        user = await self.bot.fetch_user(i) 
        lis.append(user.name + "#" + user.discriminator)
      embed = discord.Embed(color=0x2f3136, title="blame | About").set_thumbnail(url=self.bot.user.display_avatar)
      embed.add_field(name="Founder", value=f"`Discord:` `{' '.join(l for l in lis)}`\n`Server:` [here](https://discord.gg/9pVtPjfnb2)", inline=False)
      embed.add_field(name="Stats", value=f"`Users:` `{sum(g.member_count for g in self.bot.guilds)}`\n`Servers:` `{len(self.bot.guilds)}`", inline=False)
      embed.add_field(name="System:", value=f"`Latency:` `{round(self.bot.latency * 1000)}ms`\n`Language`: `Python`\n`System`: `{my_system.system}`", inline=False)   
      await ctx.reply(embed=embed, mention_author=False)
    
    @commands.command(help="invite the bot in your server", aliases=["inv"], description="info")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def invite(self, ctx):
        embed = discord.Embed(color=0x2f3136, description="invite **blame** in your server")
        button = discord.ui.Button(label="invite", style=discord.ButtonStyle.url, url=discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions.all()))
        button2 = discord.ui.Button(label="support", style=discord.ButtonStyle.url, url="https://discord.gg/9pVtPjfnb2")
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @commands.command(help="check bot's commands", aliases=["h"], usage="<command name>", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def help(self, ctx: commands.Context, *, command=None):
        if command is not None: return await commandhelp(self, ctx, command) 
        options = [
            discord.SelectOption(
                label="home",
                description="go back to the home menu",
                emoji="<:icons_generalinfo:1034777879088730152>"
            ),
            discord.SelectOption(
                label="info",
                description="information commands",
                emoji="<:icons_bulb:1034777062625525771>"
            ),
            discord.SelectOption(
              label="lastfm",
              description="last fm commands",
              emoji="<:lastfm:977608782874021888>"
            ),
            discord.SelectOption(
             label="moderation",
             description="moderation commands",
             emoji="<:icons_ban:1038477047372202139>"
            ),
            discord.SelectOption(
              label="config",
              description="config commands",
              emoji="<:icons_richpresence:986220183519657985>"
            ),
            discord.SelectOption(
              label="utility",
              description="utility commands",
              emoji="<:icons_hammer:1046403957414711367>"
            ),
            discord.SelectOption(
              label="emoji",
              description="emoji commands",
              emoji="<:icons_emojiguardian:1040936589183963196>"
            ),
            discord.SelectOption(
                label="antinuke",
                description="antinuke commands",
                emoji="<:icons_roles:1034777937674780743>"
            )
        ]
        embed = discord.Embed(color=0x2f3136, title="help command", description="a compact and minimal antinuke purpose bot").set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url).set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="help", value="use the dropdown menu below to see commands")
        embed.set_footer(text=f"{len(set(self.bot.walk_commands()))} commands")
        select = discord.ui.Select(placeholder="select category", options=options)

        async def select_callback(interaction: discord.Interaction):
          if interaction.user != ctx.author: 
            embed = discord.Embed(color=0x2f3136, description=f"<:Emojis.warninged:1034791706551406592> {interaction.user.mention}: This is not your message")
            await interaction.response.send_message(embed=embed, view=None, ephemeral=True) 
            return 
          if select.values[0] == "home":
            embed = discord.Embed(color=0x2f3136, title="help command", description="a compact and minimal antinuke purpose bot").set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url).set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(name="help", value="use the dropdown menu below to see commands")
            embed.set_footer(text=f"{len(set(self.bot.walk_commands()))} commands")
            await interaction.response.edit_message(embed=embed)   
          else:
            cmds = []
            em = discord.Embed(color=0x2f3136, description=f"{select.values[0]} commands\n<> - optional argument\n[] - required argument").set_thumbnail(url=self.bot.user.display_avatar.url)
            for cmd in set(self.bot.walk_commands()): 
             if cmd.description == select.values[0]: 
              if cmd.parent is not None: cmds.append(str(cmd.parent) + " " + cmd.name)
              else: cmds.append(cmd.name)
            em.add_field(name="commands", value=", ".join(f"`{c}`" for c in cmds) , inline=False) 
            await interaction.response.edit_message(embed=em) 
                        
        select.callback = select_callback 

        view = discord.ui.View()
        view.add_item(select)
        await ctx.reply(embed=embed, view=view)  

async def setup(bot):
    await bot.add_cog(info(bot))      
