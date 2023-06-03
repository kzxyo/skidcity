import discord, os, sys, asyncio, datetime, humanfriendly, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from discord import app_commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


async def antisetup(ctx: commands.Context):

    data = utils.read_json("antinuke")
    if not discord.utils.get(ctx.guild.text_channels, name="vile-logs"):

        y = await ctx.guild.create_text_channel(name="vile-logs")

    else:

        y = discord.utils.get(ctx.guild.text_channels, name="vile-logs")

    data[str(ctx.guild.id)] = {
        "state": "enabled",
        "logchannel": y.id,
        "whitelisted": [],
        "punishment": "kick",
        "vanity": "on",
        "rolecreate": "on",
        "roledelete": "on",
        "channelcreate": "on",
        "channeldelete": "on",
        "ban": "on",
        "kick": "on",
        "webhook": "on",
        "guild": "on",
        "antibot": "on",
        "owner": ctx.guild.owner.id,
    }
    utils.write_json(data, "antinuke")
    pass


class antinuke(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
        #
        self.done = utils.emoji("done")
        self.fail = utils.emoji("fail")
        self.warn = utils.emoji("warn")
        self.reply = utils.emoji("reply")
        self.dash = utils.emoji("dash")
        #
        self.success = utils.color("done")
        self.error = utils.color("fail")
        self.warning = utils.color("warn")
        #
        self.av = "https://cdn.discordapp.com/attachments/989422588340084757/1008195005317402664/vile.png"

    @commands.hybrid_command()
    @commands.is_owner()
    @commands.has_permissions(administrator=True)
    async def joinlock(self, ctx, stat: str = None):

        try:
            data = utils.read_json("joinlock")[str(ctx.guild.id)]
        except:
            data = utils.read_json("joinlock")
            data[str(ctx.guild.id)] = {"enabled": "no"}
            utils.write_json(data, "joinlock")
        data = utils.read_json("joinlock")[str(ctx.guild.id)]

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="joinlock", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="antinuke",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{utils.read_json('emojis')['reply']} **description:** enable or disable the joinlock module",
            inline=False,
        )
        note.add_field(
            name=f"{self.dash} Usage",
            value=f"{utils.read_json('emojis')['reply']} syntax: ,joinlock <on/off>\n{utils.read_json('emojis')['reply']} example: ,joinlock on",
            inline=False,
        )
        if not stat:
            return await ctx.reply(embed=note)

        if stat == "on":

            data = utils.read_json("joinlock")
            data[str(ctx.guild.id)] = {"enabled": "yes"}
            utils.write_json(data, "joinlock")
            try:
                x = data
            except:
                pass

            await ctx.reply(
                embed=discord.Embed(
                    color=self.success,
                    description=f"{self.done} {ctx.author.mention}**:**  join lock module has been **enabled**",
                )
            )

        if stat == "off":

            data = utils.read_json("joinlock")
            data[str(ctx.guild.id)] = {"enabled": "no"}

            await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** join lock module has been **disabled**",
                )
            )

    @commands.hybrid_group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def antialt(
        self,
        ctx,
        stat: str = None,
        channel: discord.TextChannel = None,
        days: int = None,
    ):

        try:
            data = utils.read_json("antialt")[str(ctx.guild.id)]
        except:
            data = utils.read_json("antialt")
            data[str(ctx.guild.id)] = {"enabled": "no", "channel": None, "days": 0}
            utils.write_json(data, "antialt")
        data = utils.read_json("antialt")[str(ctx.guild.id)]

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="antialt", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="antinuke",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** enable or disable the antialt module\n{self.reply} **sub commands:** status, channel, age",
            inline=False,
        )
        note.add_field(
            name=f"{self.dash} Usage",
            value=f"{self.reply} syntax: ,antialt <on/off> <log channel> <min age in days>\n{utils.read_json('emojis')['reply']} example: ,antialt on #logs 7",
            inline=False,
        )
        if not stat:
            return await ctx.reply(embed=note)

        if stat == "on":

            if not channel:
                return await ctx.reply(embed=note)

            if not days:
                return await ctx.reply(embed=note)

            data[str(ctx.guild.id)] = {
                "enabled": "on",
                "channel": channel.id,
                "days": days,
            }
            utils.write_json(data, "antialt")

            await ctx.reply(
                embed=discord.Embed(
                    color=self.success,
                    description=f"{self.done} {ctx.author.mention}**:**  anti alt module has been **enabled**",
                )
            )

        if stat == "off":

            data[str(ctx.guild.id)] = {"enabled": "off", "channel": None, "days": 0}
            utils.write_json(data, "antialt")

            await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** anti alt module has been **disabled**",
                )
            )

    @antialt.command()
    async def status(self, ctx):

        try:
            stat = utils.read_json("antialt")[str(ctx.guild.id)]["enabled"]
        except:
            data = utils.read_json("antialt")
            data[str(ctx.guild.id)] = {"enabled": "no", "channel": None, "days": 0}
            utils.write_json(data, "antialt")
        stat = utils.read_json("antialt")[str(ctx.guild.id)]["enabled"]
        await ctx.reply(
            f"antialt is **{'enabled' if stat == 'yes' else 'disabled'}** for **{ctx.guild.name}**"
        )

    @antialt.command()
    async def channel(self, ctx):

        try:
            stat = utils.read_json("antialt")[str(ctx.guild.id)]["enabled"]
            ch = utils.read_json("antialt")[str(ctx.guild.id)]["channel"]
        except:
            data = utils.read_json("antialt")
            data[str(ctx.guild.id)] = {"enabled": "no", "channel": None, "days": 0}
            utils.write_json(data, "antialt")
        stat = utils.read_json("antialt")[str(ctx.guild.id)]["enabled"]
        ch = utils.read_json("antialt")[str(ctx.guild.id)]["channel"]
        await ctx.reply(
            f"antialt logs are currently **{f'binded to <#{ch}> for **{ctx.guild.name}**' if stat == 'yes' else 'not binded to any channel'}**"
        )

    @antialt.command()
    async def age(self, ctx):

        try:
            stat = utils.read_json("antialt")[str(ctx.guild.id)]["enabled"]
            age = utils.read_json("antialt")[str(ctx.guild.id)]["days"]
        except:
            data = utils.read_json("antialt")
            data[str(ctx.guild.id)] = {"enabled": "no", "channel": None, "days": 0}
            utils.write_json(data, "antialt")
        stat = utils.read_json("antialt")[str(ctx.guild.id)]["enabled"]
        age = utils.read_json("antialt")[str(ctx.guild.id)]["days"]
        await ctx.reply(
            f"antialt minimum age is currently **{f'set to **{age} days** for **{ctx.guild.name}**' if stat == 'yes' else 'not set'}**"
        )

    @commands.hybrid_command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(administrator=True)
    async def massunban(self, ctx):

        unbanned = 0
        banned = 0
        invoker = ctx.author.id
        channel = ctx.channel
        async for entry in ctx.guild.bans():
            banned += 1
        embed = discord.Embed(
            color=self.warning,
            description=f"{utils.read_json('emojis')['warn']} {ctx.author.mention}**:** are you sure you want to unban {banned} users?",
        )
        cancelembed = discord.Embed(
            color=self.success,
            description=f"{utils.read_json('emojis')['done']} {ctx.author.mention}**:** massunban has been cancelled",
        )
        doneembed = discord.Embed(
            color=self.success,
            description=f"{utils.read_json('emojis')['done']} {ctx.author.mention}**:** successfully unbanned **{banned}**/**{banned}** members from **{ctx.guild.name}**.",
        )
        failembed = discord.Embed(
            color=self.error,
            description=f"{utils.read_json('emojis')['fail']} {ctx.author.mention}**:** cannot find any **banned** users in **{ctx.guild.name}**",
        )

        class disabledbuttons(discord.ui.View):
            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=True,
                emoji=utils.read_json("emojis")["done"],
            )
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != invoker:
                    return
                await channel.delete()
                ch = await interaction.channel.clone(
                    name=interaction.channel.name,
                    reason=f"original channel nuked by {invoker}",
                )
                ch = await interaction.guild.fetch_channel(ch.id)
                await ch.send(f"<@{invoker}>: channel has been nuked successfully")

            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=True,
                emoji=utils.read_json("emojis")["fail"],
            )
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                await interaction.response.edit_message(
                    content="are you sure you want to nuke this channel?", view=None
                )
                await interaction.channel.send(
                    f"<@{interaction.user.id}>: channel nuke has been cancelled"
                )

        class buttons(discord.ui.View):
            @discord.ui.button(
                style=discord.ButtonStyle.grey, emoji=utils.read_json("emojis")["done"]
            )
            async def confirm(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                if interaction.user.id != invoker:
                    return
                if banned != 0:
                    async with ctx.channel.typing():
                        [
                            await ctx.guild.unban(
                                user=entry.user,
                                reason=f"massunban: used by {ctx.author}",
                            )
                            async for entry in ctx.guild.bans()
                        ]

                    await interaction.message.reply(embed=doneembed)
                else:
                    await interaction.message.reply(embed=failembed)

            @discord.ui.button(
                style=discord.ButtonStyle.grey, emoji=utils.read_json("emojis")["fail"]
            )
            async def cancel(
                self, interaction: discord.Interaction, button: discord.Button
            ):

                await interaction.response.edit_message(
                    embed=embed, view=disabledbuttons()
                )
                await interaction.message.reply(embed=cancelembed)

        await ctx.reply(embed=embed, view=buttons())

    @commands.hybrid_group(aliases=["an", "antiskid"], invoke_without_command=True)
    @commands.bot_has_permissions(administrator=True)
    async def antinuke(self, ctx, module: str = None, state: str = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        antistate = anti["state"]
        logs = anti["logchannel"]
        pment = anti["punishment"]
        owner = anti["owner"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        se = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        se.set_author(name="antinuke", icon_url=self.bot.user.avatar)
        se.set_footer(
            text="antinuke",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        se.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up antinuke configs for the guild\n{self.reply} **sub commands:** setup, on/off, punishment, antinuke modules\n{self.reply} **whitelisting system:** ,whitelist <user>, ,unwhitelist <user>, ,whitelisted",
            inline=False,
        )
        se.add_field(
            name=f"{self.dash} Custom Setup",
            value=f"{self.reply} syntax: ,antinuke <module> <state:bool>\n{self.reply} example: ,antinuke ban on",
            inline=False,
        )
        se.add_field(
            name=f"{self.dash} Auto Setup", value=f"{self.reply} ,antinuke setup"
        )

        # notenabledembed = discord.Embed(color=self.warning, description=f"{self.warn} {ctx.author.mention}**:** anti nuke module is **disabled** for **{ctx.guild.name}**")
        if antistate == "disabled":
            return await ctx.reply(embed=se)
        # elif antistate == 'enabled': await ctx.reply(embed=se)

        if not module or not state:
            return await ctx.reply(embed=se)
        states = ["on", "off"]
        modules = [
            "vanity",
            "rolecreate",
            "roledelete",
            "channelcreate",
            "channeldelete",
            "ban",
            "kick",
            "webhook",
            "guild",
        ]
        if module not in modules:
            return await ctx.reply(embed=se)
        if state not in states:
            return await ctx.reply(embed=se)
        db = utils.read_json("antinuke")
        db[str(ctx.guild.id)][str(module)] = str(state)
        utils.write_json(db, "antinuke")
        await ctx.reply(":thumbsup:")

    @antinuke.command()
    @commands.bot_has_permissions(administrator=True)
    async def setup(self, ctx):

        await antisetup(ctx)
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        antistate = anti["state"]
        logs = anti["logchannel"]
        pment = anti["punishment"]
        owner = anti["owner"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        se = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        se.set_author(name="antinuke", icon_url=self.bot.user.avatar)
        se.set_footer(
            text="antinuke",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        se.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** set up antinuke configs for the guild\n{self.reply} **sub commands:** setup, on/off, punishment, antinuke modules\n{self.reply} **whitelisting system:** ,whitelist <user>, ,unwhitelist <user>, ,whitelisted",
            inline=False,
        )
        se.add_field(
            name=f"{self.dash} Custom Setup",
            value=f"{self.reply} syxtax: ,antinuke <module> <state:bool>\n{self.reply} example: ,antinuke ban on",
        )
        notenabledembed = discord.Embed(
            color=self.warning,
            description=f"{self.warn} {ctx.author.mention}**:** anti nuke module is **disabled** for **{ctx.guild.name}**",
        )
        if antistate == "disabled":
            return await ctx.reply(embed=notenabledembed)
        await ctx.reply(
            embed=discord.Embed(
                color=self.success,
                description=f"{self.done} {ctx.author.mention}**:** set up the default **antinuke** configurations, use `,an settings` to view them",
            )
        )

    @antinuke.command(aliases=["info", "modules"])
    async def settings(self, ctx):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        state = anti["state"]
        logs = anti["logchannel"]
        pment = anti["punishment"]
        owner = anti["owner"]

        notenabledembed = discord.Embed(
            color=self.warning,
            description=f"{self.warn} {ctx.author.mention}**:** anti nuke module is **disabled** for **{ctx.guild.name}**",
        )
        if state == "disabled":
            return await ctx.reply(embed=notenabledembed)

        try:
            antialt = utils.read_json("antialt")[str(ctx.guild.id)]
        except:
            antialt = utils.read_json("antialt")
            antialt[str(ctx.guild.id)] = {"enabled": "no", "channel": None, "days": 0}
            utils.write_json(antialt, "antialt")
            pass
        antialt = utils.read_json("antialt")[str(ctx.guild.id)]

        try:
            joinlock = utils.read_json("joinlock")[str(ctx.guild.id)]
        except:
            joinlock = utils.read_json("joinlock")
            joinlock[str(ctx.guild.id)] = {"enabled": "no"}
            utils.write_json(joinlock, "joinlock")
            pass

        try:
            antibot = anti["antibot"]
        except:
            x = anti
            x["antibot"] = "off"
            utils.write_json(x, "joinlock")
            pass

        joinlock = utils.read_json("joinlock")[str(ctx.guild.id)]

        joinlock = utils.read_json("joinlock")[str(ctx.guild.id)]["enabled"]
        antialt = utils.read_json("antialt")[str(ctx.guild.id)]["enabled"]
        logschannel = anti["logchannel"]

        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        try:
            x = await ctx.guild.fetch_channel(logs)
            x = x.mention
        except:
            try:
                x = discord.utils.get(ctx.guild.text_channels, name="vile-logs")
                x = x.mention
            except:
                x = await ctx.guild.create_text_channel(name="vile-logs")
                x = x.mention

        try:
            v = ctx.guild.vanity_url_code
            vanity = "on"
        except:
            vanity = "off"
            v = None

        vanity = anti["vanity"]
        rolecreate = anti["rolecreate"]
        roledelete = anti["roledelete"]
        channelcreate = anti["channelcreate"]
        channeldelete = anti["channeldelete"]
        ban = anti["ban"]
        kick = anti["kick"]
        webhook = anti["webhook"]
        guild = anti["guild"]

        se = discord.Embed(color=0x2F3136)
        se.set_thumbnail(url=self.bot.user.avatar)
        se.description = f"```           Vile Anti-Nuke Settings     ```"
        # antievents = ['Ban', 'Kick', 'Channel Create', 'Channel Delete', 'Role Create', 'Role Delete', 'Emoji Create', 'Emoji Delete', 'Anti Invite', 'Guild Update', 'Webhook Spam']
        # for event in antievents: se.add_field(name=f"{event}", value=f"{self.reply} enabled")
        se.add_field(
            name=f"Anti Vanity",
            value=f"{self.reply} **vanity:** **`{'N/A' if not v else f'gg/{v}'}`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if vanity == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Role Create",
            value=f"{self.reply} **limits:** **`N/A`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if rolecreate == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Role Delete",
            value=f"{self.reply} **limits:** **`N/A`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if roledelete == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Logs Channel",
            value=f"{self.reply} **channel:** {'null' if not x else x}\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if x != None else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Channel Create",
            value=f"{self.reply} **limits:** **`N/A`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if channelcreate == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Channel Create",
            value=f"{self.reply} **limits:** **`N/A`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if channeldelete == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Member Ban",
            value=f"{self.reply} **limits:** **`N/A`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if ban == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Member Kick",
            value=f"{self.reply} **limits:** **`N/A`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if kick == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Webhook Spam",
            value=f"{self.reply} **limits:** **`N/A`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if webhook == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Guild Update",
            value=f"{self.reply} **limits:** **`N/A`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if guild == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Alt",
            value=f"{self.reply} **limits:** **`N/A`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if antialt == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )
        se.add_field(
            name=f"Anti Bot Add",
            value=f"{self.reply} **function:** **`{'true' if antibot == 'on' else 'false'}`**\n{self.reply} status: {'<:vile_enabled:1007168449958658068>' if antibot == 'on' else '<:vile_disabled:1007168484159008848>'}",
        )

        await ctx.reply(embed=se)

    @antinuke.command(aliases=["enable"])
    async def on(self, ctx, channel: discord.TextChannel = None):

        try:
            try:
                anti = utils.read_json("antinuke")[str(ctx.guild.id)]
            except:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                    )
                )
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
            whitelisted = anti["whitelisted"]
            notwhitelistedembed = discord.Embed(
                color=self.error,
                description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
            )
            if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
                return await ctx.reply(embed=notwhitelistedembed)
            if not channel:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{self.fail} {ctx.author.mention}**:** please provide a **valid** logs channel",
                    )
                )

            data = utils.read_json("antinuke")
            data[str(ctx.guild.id)]["state"] = "enabled"
            data[str(ctx.guild.id)]["logchannel"] = channel.id
            utils.write_json(data, "antinuke")
            await self.bot.get_channel(data[str(ctx.guild.id)]["logchannel"]).send(
                embed=discord.Embed(
                    color=self.success,
                    description=f"{self.done} {ctx.author.mention}**:** all **antinuke** actions will be logged in this channel",
                )
            )
            await ctx.reply(
                embed=discord.Embed(
                    color=self.success,
                    description=f"{self.done} {ctx.author.mention}**:** enabled **antinuke** for the guild",
                )
            )
        except:
            pass

    @antinuke.command(aliases=["disable"])
    async def off(self, ctx):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        data = utils.read_json("antinuke")
        data[str(ctx.guild.id)]["state"] = "disabled"
        utils.write_json(data, "antinuke")
        await ctx.reply(
            embed=discord.Embed(
                color=self.success,
                description=f"{self.done} {ctx.author.mention}**:** disabled **antinuke** for the guild",
            )
        )

    @antinuke.command(aliases=["pment"])
    async def punishment(self, ctx, pun: str = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        e1 = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        e1.set_author(name="punishment", icon_url=self.bot.user.avatar)
        e1.add_field(
            name=f"{utils.read_json('emojis')['dash']} Info",
            value=f"{self.reply} **description:** select the punishment for antinuke events\n{self.reply} **aliases:** punishment, pment, pun\n{self.reply} **sub commands:** all, bots, humans, withrole",
            inline=False,
        )
        e1.add_field(
            name=f"{utils.read_json('emojis')['dash']} Punishments",
            value=f"```YAML\nban - bans the user\nkick - kicks the suer\nstrip - strips the user of their roles\njail - strips and jails the user```",
            inline=False,
        )
        e1.set_footer(
            text="moderation",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        if not pun:
            return await ctx.reply(embed=e1)
        punishments = ["ban", "kick", "strip", "jail"]
        if pun not in punishments:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** please provide a **valid** punishment",
                )
            )
        data = utils.read_json("antinuke")
        data[str(ctx.guild.id)]["punishment"] = pun
        utils.write_json(data, "antinuke")
        await ctx.reply(
            embed=discord.Embed(
                color=self.success,
                description=f"{self.done} {ctx.author.mention}**:** set the **antinuke** punishment as `{pun}`",
            )
        )

    @commands.hybrid_command(aliases=["wl"])
    async def whitelist(self, ctx, user: discord.Member = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)
        if not user:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** please provide a **valid** username",
                )
            )

        data = utils.read_json("antinuke")
        data[str(ctx.guild.id)]["whitelisted"].append(user.id)
        utils.write_json(data, "antinuke")
        await ctx.reply(":thumbsup:")

    @commands.hybrid_command(aliases=["uwl"])
    async def unwhitelist(self, ctx, user: discord.Member = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)
        if not user:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** please provide a **valid** username",
                )
            )

        data = utils.read_json("antinuke")
        data[str(ctx.guild.id)]["whitelisted"].remove(user.id)
        utils.write_json(data, "antinuke")
        await ctx.reply(":thumbsup:")

    @antinuke.command(aliases=["logs", "logchannel"])
    async def logschannel(self, ctx, channel: discord.TextChannel = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)
        if not channel:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** please provide a **valid** logs channel",
                )
            )

        data = utils.read_json("antinuke")
        data[str(ctx.guild.id)]["logchannel"] = channel.id
        utils.write_json(data, "antinuke")
        await self.bot.get_channel(data[str(ctx.guild.id)]["logchannel"]).send(
            embed=discord.Embed(
                color=self.success,
                description=f"{self.done} {ctx.author.mention}**:** all **antinuke** actions will be logged in this channel",
            )
        )
        await ctx.reply(":thumbsup:")

    @commands.hybrid_command()
    async def whitelisted(self, ctx):

        try:
            try:
                anti = utils.read_json("antinuke")[str(ctx.guild.id)]
            except:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                    )
                )
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
            whitelisted = anti["whitelisted"]
            notwhitelistedembed = discord.Embed(
                color=self.error,
                description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
            )
            if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
                return await ctx.reply(embed=notwhitelistedembed)

            ret = []
            num = 0
            wlmembers = []
            async for m in utils.aiter(whitelisted):
                try:
                    x = await ctx.guild.fetch_member(m)

                    num += 1
                    ret.append(f"**`{num}`** <@{x.id}>: **{x}** ( `{x.id}` )\n")
                    embed = discord.Embed(
                        color=0x2F3136,
                        description=" ".join(ret),
                        title=f"whitelisted members",
                        timestamp=datetime.now(),
                    )
                    embed.set_footer(text=f"1/1 ({num} entries)")
                    fakeembed = discord.Embed(
                        color=0x2F3136,
                        description="undefined",
                        title=f"whitelisted members",
                        timestamp=datetime.now(),
                    )
                    fake1 = fakeembed.set_footer(
                        text=f"2/1 ({num} entries)",
                        icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
                    )
                except:
                    pass
            from modules import paginator as pg

            paginator = pg.Paginator(self.bot, [embed, fake1], ctx, invoker=None)
            paginator.add_button("prev", emoji=utils.emoji("prevpage"))
            paginator.add_button("end", emoji=utils.read_json("emojis")["fail"])
            paginator.add_button("next", emoji=utils.emoji("nextpage"))
            await paginator.start()
        except:
            pass

    @commands.hybrid_command(aliases=["ab"])
    @commands.bot_has_permissions(administrator=True)
    async def antibot(
        self,
        ctx,
        stat: str = None,
        channel: discord.TextChannel = None,
        days: int = None,
    ):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        note = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        note.set_author(name="antinuke", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="antinuke",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** enable or disable the antibot module\n{self.reply} **aliases:** antibot, ab",
            inline=False,
        )
        note.add_field(
            name=f"{self.dash} Usage",
            value=f"{self.reply} syntax: ,antialt <on/off>\n{utils.read_json('emojis')['reply']} example: ,antibot on",
            inline=False,
        )
        if not stat:
            return await ctx.reply(embed=note)

        if stat == "on":

            data = utils.read_json("antinuke")
            data[str(ctx.guild.id)]["antibot"] = "on"
            utils.write_json(data, "antinuke")
            try:
                x = data[str(ctx.guild.id)]
            except:
                pass

            await ctx.reply(
                embed=discord.Embed(
                    color=self.success,
                    description=f"{self.done} {ctx.author.mention}**:**  anti bot module has been **enabled**",
                )
            )

        if stat == "off":

            data = utils.read_json("antinuke")
            data[str(ctx.guild.id)]["antibot"] = "off"
            utils.write_json(data, "antinuke")

            await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** anti bot module has been **disabled**",
                )
            )

    @commands.hybrid_group(aliases=["raid"], invoke_without_command=True)
    async def antiraid(self, ctx):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        se = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        se.set_author(name="antiraid", icon_url=self.bot.user.avatar)
        se.set_footer(
            text="antinuke",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        se.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** view information about the antiraid module\n{self.reply} **sub commands:** ban, jail",
            inline=False,
        )
        await ctx.reply(embed=se)

    @antiraid.command(name="ban")
    @commands.bot_has_permissions(ban_members=True)
    async def antiraid_ban(self, ctx, time: str = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        await ctx.message.add_reaction("👍")
        async for member in aiter(ctx.guild.members):
            d = datetime.now().astimezone() - member.joined_at
            if d.total_seconds() < humanfriendly.parse_timespan(time):
                await member.ban(reason=f"antiraid ban: used by {ctx.author}")

        await ctx.message.clear_reaction("👍")
        await ctx.reply(":thumbsup:")

    @antiraid.command(name="jail")
    @commands.bot_has_permissions(ban_members=True)
    async def antiraid_jail(self, ctx, time: str = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{self.fail} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{self.fail} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        await ctx.message.add_reaction("👍")
        async for member in utils.aiter(ctx.guild.members):
            d = datetime.now().astimezone() - member.joined_at
            if d.total_seconds() < humanfriendly.parse_timespan(time):
                await ctx.invoke(self.bot.get_command("jail"), member)

        await ctx.message.clear_reaction("👍")
        await ctx.reply(":thumbsup:")


async def setup(bot):
    await bot.add_cog(antinuke(bot))
