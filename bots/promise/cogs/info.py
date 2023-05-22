import discord, time, datetime, psutil
from discord.ext import commands
from discord.ui import View, Button, Select
from core.utils.classes import Colors, Emojis, Func

global start

class info(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_connect(self):
        global start
        start = time.time()

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def uptime(self, ctx):
        uptime = str(
            datetime.timedelta(seconds=int(round(time.time() - start))))
        e = discord.Embed(
            color=Colors.green,
            description=f"**@promise** start **{uptime}** ago")
        await ctx.reply(embed=e, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def ping(self, ctx):
        e = discord.Embed(
            color=Colors.green,
            description=f"Took **{round(self.bot.latency * 1000)}ms** To Call A Hot Asian")
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(aliases=["bi"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def botinfo(self, ctx):
        uptime = str
        avatar_url = self.bot.user.avatar.url
        members = 0
        for guild in self.bot.guilds:
            members += guild.member_count - 1

        embed = discord.Embed(
            color=Colors.green,
            title="‎ ",
            description=
            "**This bot was made on <t:1675980000:D>**\n‎ ")
        embed.set_thumbnail(url=f'{avatar_url}')
        embed.add_field(
            name="bot",
            value="servers : " + " ** "
            f"{len(self.bot.guilds)}" + "**\nmembers : " + f"**{members}**\nowner : **devx#0001**"
        )
        embed.add_field(
            name="system",
            value="python version : " + f" **{discord.__version__}**\nping : " + f"**{round(self.bot.latency * 1000)}ms**" + "\nlines : **1583**"
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["inv"])
    async def invite(self, ctx):
        embed = discord.Embed(
            color=Colors.green,
            description="**@promise** Invitation Link Below")
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar.url)
        button1 = Button(label="Server", url="https://discord.gg/mcKpbra79z")
        button2 = Button(
            label="invite",
            url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
        )
        view = View()
        view.add_item(button1)
        view.add_item(button2)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @commands.command(aliases=["h"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def help(self, ctx):
        embed = discord.Embed(color=Colors.green, description="")
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_author(name="@promise", icon_url=self.bot.user.avatar.url)
        embed.set_footer(text=f"{len(set(self.bot.walk_commands()))} commands")
        embed.add_field(name="‎ ",
                        value="**Press Dropdown for category commands\n‎ **",
                        inline=False)
        button1 = Button(label="server", url="https://discord.gg/mcKpbra79z")
        button2 = Button(
            label="invite",
            url=
            f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
        )
        select = Select(
            placeholder="Select The Category Command",
            options=[
                discord.SelectOption(
                label="home",
                description="home page",
                emoji="<:0_bf3:1061276144999088158>"
            ),
                discord.SelectOption(
                label="info",
                description="information commands",
                emoji="<:0_heart2:1061276184706560020>"
            ),
                discord.SelectOption(
                label="utility",
                description="useful commands",
                emoji="<:0_key:1061276218344874064>"
            ),
                discord.SelectOption(
                label="moderation",
                description="admin commands",
                emoji="<:1D_folder:1074749588797411468>"
            ),
                discord.SelectOption(
                label="config",
                description="server config commands",
                emoji="<:1D_star:1074749584598904893>"
            ),
                discord.SelectOption(
                label="lastfm",
                description="lastfm interface",
                emoji="<:1woostargrey:1074749582673723524>"
            ),
                discord.SelectOption(
                label="updates",
                description="promise updates",
                emoji="<:3_stargrey:1074749573299450008>"
            )
            ])

        async def select_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                em = discord.Embed(
                    color=Colors.green,
                    description=
                    f"**Sorry but you can't interact with this message!**"
                )
                await interaction.response.send_message(embed=em, ephemeral=True)
                return

            if select.values[0] == "home":
                await interaction.response.edit_message(embed=embed)
            elif select.values[0] == "info":
                e = discord.Embed(color=Colors.green, title="‎ ")
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="‎ ",
                            value="**botinfo , invite , help , ping , uptime, userinfo**\n**‎ **",
                            inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "utility":
                e = discord.Embed(color=Colors.green,
                                  title="‎ ")
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="‎ ",
                            value="**profileicon , ben , spotify, avatar , banner , sicon , sbanner , splash , addmultiple , addemoji , emojilist , enlarge , getbotinvite , boosters , webshot , tiktok , translate , server , afk , pastusernames , blacktea**\n**‎ **",
                            inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "updates":
                e = discord.Embed(color=Colors.green,
                                  title="‎ ")
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="‎ ",
                            value="**Added lastfm interface and more moderation commands**\n**‎ **",
                            inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "moderation":
                e = discord.Embed(color=Colors.green, title="‎ ")
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="‎ ", value="**role , lock , unlock , untimeout , ban , unban , kick , slowmode**\n**‎ **", inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "config":
                e = discord.Embed(color=Colors.green, title="‎ ")
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="‎ ", value="**autoresponder , jail , roleall**\n**‎ **", inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "lastfm":
                e = discord.Embed(color=Colors.green,
                                  title="‎ ")
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="‎ ",
                            value="**lastfm , nowplaying , lastfm customcommand , topartists , topalbums , globalwhoknows , whoknows , lastfm remove**\n**‎ **",
                            inline=False)
                await interaction.response.edit_message(embed=e)

        select.callback = select_callback 

        view = View()
        view.add_item(select)
        view.add_item(button1)
        view.add_item(button2)      

        await ctx.reply(embed=embed, view=view, mention_author=False)  


async def setup(bot) -> None:
    await bot.add_cog(info(bot))
