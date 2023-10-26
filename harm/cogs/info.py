import discord 
import asyncio
import psutil
import platform
import datetime
from discord.ext import commands 

from tools.bot import DiscordBot
from tools.context import HarmContext

startup_time = datetime.datetime.utcnow()

class Info(commands.Cog):
    def __init__(self, bot: DiscordBot):
      self.bot = bot 



    @commands.hybrid_command(help="get information on harm", description="get information on lavish", usage="[command]", aliases=["boti", "botstats", "stats"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def botinfo(self, ctx: commands.Context):
        loading_embed = discord.Embed(color=0x2f3136, description="<a:harm_loading:1152361161564618782> loading bot info...")
        loading_message = await ctx.reply(embed=loading_embed, mention_author=False)

        await asyncio.sleep(3)

        avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        members = 0
        for guild in self.bot.guilds:
            members += guild.member_count - 1
        self.version = "2.3.2"

        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024
        cpu_usage = psutil.cpu_percent()
        disk_usage = psutil.disk_usage('/').percent
        net_io_counters = psutil.net_io_counters()
        bandwidth_usage = (net_io_counters.bytes_sent + net_io_counters.bytes_recv) / 1024 / 1024
        operating_system = platform.system()

        embed = discord.Embed(
            color=0x2f3136)
        embed.set_thumbnail(url=f'{avatar_url}')
        embed.add_field(
            name="Bot Information",
            value="Servers : " + " ** "
            f"{len(self.bot.guilds)}" + "**\nMembers : " + f"**{members}**\nOwner : <@1148300105758298123> , <@371224177186963460>"
        )
        embed.add_field(
            name="Bot System",
            value="Python version : " + f" **{discord.__version__}**\nPing : " + f"**{round(self.bot.latency * 1000)}ms**\nShard: **{ctx.guild.shard_id + 1}/{self.bot.shard_count}**")
        embed.add_field(
            name="Bot Resources",
            value=f"Cache size: **{len(self.bot.cached_messages)}**\nMemory usage: **{memory_usage:.2f} MB**\nCPU usage: **{cpu_usage}%**\nBandwidth usage: **{bandwidth_usage:.2f} MB**\nDisk usage: **{disk_usage}%**"
    )
        embed.add_field(
            name="Bot Details",
            value=f"Operating system: **{operating_system}**\nBot version: **{self.version}**\nNumber of cogs: **{len(self.bot.cogs)}**\nNumber of commands: **{len(self.bot.commands)}**"
        )
        await loading_message.edit(embed=embed)
    @commands.hybrid_command(help="gets bot ping", description="ping", usage="[command]")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def ping(self, ctx):
        loading_embed = discord.Embed(color=0x2f3136, description="<a:harm_loading:1152361161564618782> loading ping...")
        loading_message = await ctx.reply(embed=loading_embed, mention_author=False)

        await asyncio.sleep(3)
        embed = discord.Embed(color=0x2f3136, description=f"Latency: **{round(self.bot.latency * 1000)}ms**")
        await loading_message.edit(embed=embed)

    @commands.hybrid_command(aliases=['inv'])
    async def invite(self, ctx):
        view = discord.ui.View()
        inv = discord.ui.Button(
        label="Invite",
          url="https://discord.com/api/oauth2/authorize?client_id=624987392494796820&permissions=8&scope=bot"
    )
    

        sup = discord.ui.Button(
        label="Support",
        url="https://discord.gg/abkkQJyUDQ"
       )
    
        view.add_item(inv)
        view.add_item(sup)
    
        await ctx.send(view=view)

    @commands.command(aliases=['creds'])
    async def credits(self, ctx):
      embed = discord.Embed(
        title='dev team:',
        description='<@1148300105758298123> , <@371224177186963460> , <@153643814605553665>',
        color=0x2f3136)


      embed.set_author(
        name='harm credits',
        icon_url='https://images-ext-2.discordapp.net/external/DzSarITZwN7zsEQSXtt38f7svlL-Xzv_URYksTbe_zY/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/624987392494796820/ace504b510f1d0c514aa4199469789ec.png?width=646&height=646'
      )

      await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        current_time = datetime.datetime.utcnow()
        uptime = current_time - startup_time
        await ctx.reply(format_timedelta(uptime), mention_author=False)

def format_timedelta(td):
    seconds = td.total_seconds()
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(days)} day(s), {int(hours)} hour(s), {int(minutes)} minute(s), {int(seconds)} second(s)"

async def setup(bot: DiscordBot) -> None:
   return await bot.add_cog(Info(bot))     
