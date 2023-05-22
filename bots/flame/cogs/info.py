import discord, time, button_paginator as pg
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown, Bot as AB
from discord.ui import Button, View
import datetime
start_time = time.time()
now = datetime.datetime.now()

def seconds_to_dhms(time):
    seconds_to_minute   = 60
    seconds_to_hour     = 60 * seconds_to_minute
    seconds_to_day      = 24 * seconds_to_hour

    days    =   time // seconds_to_day
    time    %=  seconds_to_day

    hours   =   time // seconds_to_hour
    time    %=  seconds_to_hour

    minutes =   time // seconds_to_minute
    time    %=  seconds_to_minute

    seconds = time
    return ("%d days, %d hours, %d minutes, %d seconds" % (days, hours, minutes, seconds))

class info(commands.Cog):
   def __init__(self, bot: AB):
        self.bot = bot

   @commands.command(help="check how long the bot has been online for", description="info")
   @cooldown(1, 4, BucketType.user)
   async def uptime(self, ctx):
     uptime = int(time.time() - self.bot.uptime)
     e = discord.Embed(color=0xffffff, description=f"⏰ **{self.bot.user.name}'s** uptime: **{seconds_to_dhms(uptime)}**")
     await ctx.reply(embed=e, mention_author=False)

   @commands.command(help="check bot connection", description="info")
   @cooldown(1, 4, BucketType.user)
   async def ping(self, ctx):
        mf = f"`{round(self.bot.latency * 1000)}ms`"
        await ctx.reply(content=f"....pong 🏓 {mf}", mention_author=False)

   @commands.command(aliases = ['h'])
   @commands.cooldown(1, 3, commands.BucketType.user)
   async def help(self, ctx):
        try:
            dev = self.bot.get_user(605366345902587921)
            embed = discord.Embed(color = 0xffffff).set_footer(text="1/6", icon_url = "https://cdn.discordapp.com/attachments/1022196816063770774/1024294648564424775/2421_butterflywings.gif").set_thumbnail(url = self.bot.user.avatar).set_author(name= self.bot.user.name, icon_url = self.bot.user.avatar).add_field(name = "**Looking for help?**", value = f"""An asterisk (*) means the command has sub commands
For sub commands do `,command`""", inline = False).add_field(name = f"**Are you in need of help with {self.bot.user.name}?**", value = f"""Contact `{dev.name}#{dev.discriminator}` or **join the support server**""", inline = False)
            embed.add_field(name = "**Useful links**", value = f"[Support](https://discord.gg/mJzM4Bzf8Y) — [Invite](https://discord.com/api/oauth2/authorize?client_id=912344349470244975&permissions=8&scope=bot) — [Docs](https://github.com/tbpn/wonder-bot)", inline = False)
            embed2 = discord.Embed(description = f"""``​`autoreact*, autoresponder*, chatfilter*, starboard*, clownboard*, welcome*, goodbye*, lastfm*, autorole*, prefix``​`""", color = 0xffffff).set_footer(text = "2/6", icon_url = "https://cdn.discordapp.com/attachments/1022196816063770774/1024294648564424775/2421_butterflywings.gif").set_author(name= "configuration", icon_url = self.bot.user.avatar)
            embed3 = discord.Embed(description = f"""``​`hack, bite, bitches, horny, tickle, cry, iq, howfunny, fatrate, coolrate, cuterate, gayrate, sus, roast, 8ball, punch, slap, kiss``​`""", color = 0xffffff).set_footer(text = "3/6", icon_url = "https://cdn.discordapp.com/attachments/1022196816063770774/1024294648564424775/2421_butterflywings.gif").set_author(name= "fun", icon_url = self.bot.user.avatar)
            embed4 = discord.Embed(description = f"""``​`ban, unban, clear, botclear, mute. unmute, kick, warn, warns, clearwarns, changenickname, addrole``​`""", color = 0xffffff).set_footer(text = "4/6", icon_url = "https://cdn.discordapp.com/attachments/1022196816063770774/1024294648564424775/2421_butterflywings.gif").set_author(name= "moderation", icon_url = self.bot.user.avatar)
            embed5 = discord.Embed(description = f"""``​`ipinfo, inrole, anime, aninews, youtube, image, reverse, passwordgenerator, crypto, covid, urban, pastusernames. pastavatars, tags, nodata``​`""", color = 0xffffff).set_footer(text = "5/6", icon_url = "https://cdn.discordapp.com/attachments/1022196816063770774/1024294648564424775/2421_butterflywings.gif").set_author(name= "tools", icon_url = self.bot.user.avatar)
            embed6 = discord.Embed(description = f"""``​`spotify, emojify, coinflip, boosterlist, roleperms, roleinfo, fancify, christmas, addemoji, deleteemoji, avatar, serveravatar, banner, serverbanner, servericon, botinfo, userinfo, serverinfo, ping, donate, invite, membercount``​`""", color = 0xffffff).set_footer(text = "6/6", icon_url = "https://cdn.discordapp.com/attachments/1022196816063770774/1024294648564424775/2421_butterflywings.gif").set_author(name = "utility", icon_url = self.bot.user.avatar)
            embeds = (embed, embed2, embed3, embed4, embed5, embed6)
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button('prev', emoji= "<:left:1030762618635423824>")
            paginator.add_button('next', emoji="<:right:1030762620032131142>")
            paginator.add_button('delete', emoji = "<:stop:1030762621613391872>")
            paginator.add_button('goto', emoji = "<:skip:1030767781483909170>")
            await paginator.start() 
        except Exception as e:
            print(e)

   @commands.command(aliases = ['info'], description = "Shows some information about the bot", usage = ",botinfo")
   async def botinfo(self, ctx):
        try:
            dev = self.bot.get_user(605366345902587921)
            uptime = int(time.time() - self.bot.uptime)
            button = Button(label="Invite", url = "https://discord.com/api/oauth2/authorize?client_id=912344349470244975&permissions=8&scope=bot")
            current_time = time.time()
            difference = int(round(current_time - start_time))
            view = View()
            view.add_item(button)
            embed = discord.Embed(timestamp=ctx.message.created_at, colour=0xffffff)
            embed.add_field(name = f"**{self.bot.user.name}'s statistics**", value = f"""`{len(self.bot.guilds)}` guilds
`{sum(g.member_count for g in self.bot.guilds)}` users""", inline = False)
            embed.add_field(name = "**client**", value = f"""`{len(self.bot.commands)}` commands
websocket latency: `{round(self.bot.latency * 1000)}` ms
uptime: `{seconds_to_dhms(uptime)}`""", inline = False)
            embed.set_author(name = self.bot.user.display_name, icon_url = self.bot.user.avatar)
            embed.set_thumbnail(url = self.bot.user.avatar)
            await ctx.reply(embed=embed, view=view)
        except Exception as e:
            print(e) 

   @commands.command(aliases = ['gc'], description="info", usage = ",guildcount")
   async def guildcount(self, ctx):
    embed = discord.Embed(color=0xffffff, description=f"{self.bot.user.name} is in {len(self.bot.guilds)} guilds caching {len(self.bot.users)} members", author=f"{self.bot.user.display_name} {self.bot.user.avatar}")
    await ctx.reply(embed=embed, mention_author=False)

   @commands.command(aliases = ['inv'], help="invite link for bot", description="info")
   async def invite(self, ctx):
        try:
            dev = self.bot.get_user(605366345902587921)
            button = Button(label="Invite", url = "https://discord.com/api/oauth2/authorize?client_id=912344349470244975&permissions=8&scope=bot")
            button2 = Button(label="Support", url = "https://discord.gg/mJzM4Bzf8Y")
            view = View()
            view.add_item(button)
            view.add_item(button2)
            embed = discord.Embed(name =f"{self.bot.user.name}, {self.bot.user.avatar.url}", color=0xffffff, description=f"Invite **{self.bot.user.display_name}** [here](https://discord.com/api/oauth2/authorize?client_id=912344349470244975&permissions=8&scope=bot)")
            await ctx.reply(embed=embed, view=view)
        except Exception as e:
            print(e) 

async def setup(bot) -> None:
    await bot.add_cog(info(bot))  