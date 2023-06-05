import discord, time, platform, psutil, datetime
from discord.ext import commands 
from discord.ext.commands import has_permissions
from cogs.events import seconds_to_dhms, blacklist, commandhelp
from utils.classes import Colors, Emojis

my_system = platform.uname()

class info(commands.Cog): 
    def __init__(self, bot: commands.AutoShardedBot): 
      self.bot = bot 
    
    @commands.command(help="check the bot's latency", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def ping(self, ctx: commands.Context): 
        embed = discord.Embed(color=Colors.default, description=f"📡 latency: `{round(self.bot.latency * 1000)}ms`")
        await ctx.reply(embed=embed, mention_author=False)  

    @commands.command(help="check the bot's uptime", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def uptime(self, ctx: commands.Context):  
     uptime = int(time.time() - self.bot.uptime)
     e = discord.Embed(color=Colors.default, description=f":alarm_clock: **{self.bot.user.name}'s** uptime: **{seconds_to_dhms(uptime)}**")
     await ctx.reply(embed=e, mention_author=False) 

    @commands.command(help="check bot's statistics", aliases=["about", "bi", "info"], description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)  
    @blacklist()
    async def botinfo(self, ctx: commands.Context): 
        await ctx.send(f"> Suck My Dick.", mention_author=False)

    @commands.command(help="invite the bot in your server", aliases=["inv"], description="info")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @blacklist()
    async def invite(self, ctx):
        button = discord.ui.Button(label="invite", style=discord.ButtonStyle.url, url=discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions.all()))
        button2 = discord.ui.Button(label="support", style=discord.ButtonStyle.url, url="https://discord.gg/gxGrRvmYWR")
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)
        await ctx.reply(view=view, mention_author=False)

    @commands.command(help="check bot's commands", aliases=["h"], usage="<command name>", description="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def help(self, ctx: commands.Context, *, command=None):
        embed = discord.Embed(title='help',
                              color=0xA480EB,
                              description='for regular commands do ``;help [cmd]`` \nfor subcommands do ``;help [cmd] [subcmd]`` \n \nan asterisk(*) means the command has subcommands')
        config = []
        fun = []
        info = []
        lastfm = []
        moderation = []
        utility = []
        star = ''
        commands = self.client.commands
        for command in commands:
            if command.parent:
                star = '*'
            if command.description == 'fun':
                fun.append(f'`{command.name}`{star}')
            if command.description == 'info':
                info.append(f'`{command.name}`{star}')
            if command.description == 'config':
                config.append(f'`{command.name}`{star}')
            if command.description == 'lastfm':
                lastfm.append(f'`{command.name}`{star}')
            if command.description == 'moderation':
                moderation.append(f'`{command.name}`{star}')
            if command.description == 'utility':
                utility.append(f'`{command.name}`{star}')

        if config == []:
            config = '`none`'
        if fun == []:
            fun = '`none`'
        if info == []:
            info = '`none`'
        if lastfm == []:
            lastfm = '`none`'
        if moderation == []:
            moderation = '`none`'
        if utility == []:
            utility = '`none`'

        embed.add_field(name='configuration', value=f'{config}'.replace("[", '').replace("'", '').replace("]", ''), inline=False)
        embed.add_field(name='fun', value=f'{fun}'.replace("[", '').replace("'", '').replace("]", ''), inline=False)
        embed.add_field(name='info', value=f'{info}'.replace("[", '').replace("'", '').replace("]", ''), inline=False)
        embed.add_field(name='lastfm', value=f'{lastfm}'.replace("[", '').replace("'", '').replace("]", ''), inline=False)
        embed.add_field(name='moderation', value=f'{moderation}'.replace("[", '').replace("'", '').replace("]", ''), inline=False)        
        embed.add_field(name='utility', value=f'{utility}'.replace("[", '').replace("'", '').replace("]", ''), inline=False)

        embed.set_footer(text=f'join

async def setup(bot):
    await bot.add_cog(info(bot))   