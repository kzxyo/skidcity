import discord, time, datetime, psutil
from discord.ext import commands
from discord.ui import View, Button, Select

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
            color=0x2f3136,
            description=f"**My uptime: {uptime}**")
        await ctx.reply(embed=e, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        e = discord.Embed(
            color=0x2f3136,
            description=f"My latency is`{round(self.bot.latency * 1000)}ms`")
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(aliases = ['bi'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botinfo(self, ctx):
        avatar_url = self.bot.user.avatar.url
        uptime = str(
            datetime.timedelta(seconds=int(round(time.time() - start))))
        members = 0
        for guild in self.bot.guilds:
            members += guild.member_count - 1

        embed = discord.Embed(
            color=0x2f3136,
            title=self.bot.user.name,
            description=
            "[Axie a multipurpose discord bot](https://discord.gg/DXRKFyefnq)")
        embed.set_thumbnail(url=f'{avatar_url}')
        embed.add_field(
            name="**Statistics**",
            value=f"> Guilds: " + " ** "
            f"{len(self.bot.guilds)}" + "**\n> Users: " + f"**{members}" +
            " ** \n> Discord.py Version: " + f" **{discord.__version__}**\n> Ping: " +
            f"**{round(self.bot.latency * 1000)}ms**\n" +
            f"> Uptime: **{uptime}**\n> Ram Usage: **{psutil.virtual_memory()[2]}%**"
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        embed = discord.Embed(
            color=0x2f3136,
            description="> Axie Invite : __Click on the buttons__")
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar.url)
        button1 = Button(label="Contact", url="https://discord.gg/t39bJJvDje")
        button2 = Button(
            label="Axie",
            url=
            f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
        )
        view = View()
        view.add_item(button1)
        view.add_item(button2)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def help(self, ctx):
        embed = discord.Embed(color=0x2f3136, description="")
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_author(name="help panel", icon_url=self.bot.user.avatar.url)
        embed.add_field(name="> Axie Commands List ",
                        value="**For the Commands Check The Dropdown**",
                        inline=False)
        embed.add_field(
            name="> __Axie Support__",
            value=
            "**If you have problems with bot just join in our ** [support server](https://discord.gg/t39bJJvDje)"
        )
        button1 = Button(label="Contact", url="https://discord.gg/t39bJJvDje")
        button2 = Button(
            label="Axie",
            url=
            f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
        )
        select = Select(
            placeholder="select category",
            options=[
                discord.SelectOption(label="home"),
                discord.SelectOption(label="config"),
                discord.SelectOption(label="info"),
                discord.SelectOption(label="utility"),
                discord.SelectOption(label="moderation"),
                discord.SelectOption(label="roleplay"),
                discord.SelectOption(label="lastfm"),
                discord.SelectOption(label="emoji"),
                discord.SelectOption(label="countdowns")
                
            ])

        async def select_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                em = discord.Embed(
                    color=0xffff00,
                    description=f"<:emoji_7:1048996990706524322> {interaction.user.mention} you are not the author of this message"
                )
                await interaction.response.send_message(embed=em, ephemeral=True)
                return
           

            if select.values[0] == "home":
                await interaction.response.edit_message(embed=embed)
            elif select.values[0] == "info":
                e = discord.Embed(color=0x2f3136)
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="info",
                            value="`botinfo , ping , uptime`",
                            inline=False)   
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "utility":
                e = discord.Embed(color=0x2f3136)
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="utility",
                            value="`userinfo, mods , vanity , voicecount , server splash , server banner , server , tags , boostcount , invites , webshot , clear`",
                            inline=False) 
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "moderation":
                e = discord.Embed(color=0x2f3136)
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="moderation", value="`kick , ban , unban`", inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "roleplay":
                e = discord.Embed(color=0x2f3136)
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="roleplay",
                            value="`kiss , hug , slap , cuddle , pat , cry , marry , laugh , marriage , divorce`",
                            inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "lastfm":
                e = discord.Embed(color=0x2f3136)
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="lastfm",
                            value="`soon...`",
                            inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "countdowns":
                e = discord.Embed(color=0x2f3136)
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="countdowns", value="> ` xmas , summer , newyear`", inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "emoji":
                e = discord.Embed(color=0x2f3136)
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="emoji", value="> `steal`", inline=False)
                await interaction.response.edit_message(embed=e)
            elif select.values[0] == "config":
                e = discord.Embed(color=0x2f3136)
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="config", value="> `autorole , voicemaster , autoresponder`", inline=False)
                await interaction.response.edit_message(embed=e)

        select.callback = select_callback 

        view = View()
        view.add_item(select)
        view.add_item(button1)
        view.add_item(button2)
        

        await ctx.reply(embed=embed, view=view, mention_author=False)  
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def template(self, ctx):
        embed = discord.Embed(color=0x2f3136, description="")
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_author(name="Template Selecter", icon_url=self.bot.user.avatar.url)
        embed.add_field(name="Choose",
                        value="**Use the dropdown menu below to choose a template to copy**",
                        inline=False)
        embed.add_field(
            name="info",
            value=
            "**The bot recomande you a template the bot will dont load a template/save**"
        )
        button4 = Button(label="support", url="https://discord.gg/xE2aFkj2cD")
        button3 = Button(
            label="invite",
            url=
            f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
        )
        select = Select(
            placeholder="select category",
            options=[
                discord.SelectOption(label="home"),
                discord.SelectOption(label="community")
                
            ])

        async def select_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                em = discord.Embed(
                    color=0xffff00,
                    description=
                    f"<:emoji_7:1048996990706524322> {interaction.user.mention} you are not the author of this message"
                )
                await interaction.response.send_message(embed=em, ephemeral=True)
                return
           

            if select.values[0] == "home":
                await interaction.response.edit_message(embed=embed)
            elif select.values[0] == "community":
                e = discord.Embed(color=0x2f3136,
                                  title="Community Templates")
                e.set_thumbnail(url=self.bot.user.avatar.url)
                e.add_field(name="Delta",
                            value="**<:1_vcy:1030446438645235752> : https://discord.new/KH5dDkawVTaA**\n**<:2_1:1030446441522532362> : https://discord.new/YWqCyacWn5AK **",
                            inline=False) 
                await interaction.response.edit_message(embed=e)
            
        select.callback = select_callback 

        view = View()
        view.add_item(select)
        view.add_item(button4)
        view.add_item(button3)
        

        await ctx.reply(embed=embed, view=view, mention_author=False)

async def setup(bot) -> None:
    await bot.add_cog(info(bot))
