import discord, datetime, humanfriendly
from discord.ext import commands
from datetime import datetime
from .modules import utils
from .utils.util import Emojis
from cogs.utilevents import blacklist
async def antisetup(ctx: commands.Context):

    data = utils.read_json("antinuke")
    if not discord.utils.get(ctx.guild.text_channels, name="crime-logs"):

        y = await ctx.guild.create_text_channel(name="crime-logs")

    else:

        y = discord.utils.get(ctx.guild.text_channels, name="crime-logs")

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
        self.done = Emojis.check
        self.fail = Emojis.deny
        self.warn = Emojis.warn
        #
        self.success = 0x2f3136
        self.error = 0x2f3136
        self.warning = 0x2f3136

    @commands.command()
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

        note = discord.Embed(color=0xf7f9f8, timestamp=datetime.now())
        note.set_author(name="joinlock", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="powered by crime",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"Info",
            value=f"> **description:** enable or disable the joinlock module",
            inline=False,
        )
        note.add_field(
            name=f"Usage",
            value=f"> syntax: ,joinlock <on/off>\n> example: ,joinlock on",
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
                    description=f"{Emojis.deny} {ctx.author.mention}**:** join lock module has been **disabled**",
                )
            )

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @blacklist()

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

        note = discord.Embed(color=0xf7f9f8, timestamp=datetime.now())
        note.set_author(name="antialt", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="powered by crime",
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        note.add_field(
            name=f"Info",
            value=f"> **description:** enable or disable the antialt module\n> **sub commands:** status, channel, age",
            inline=False,
        )
        note.add_field(
            name=f"Usage",
            value=f"> syntax: ,antialt <on/off> <log channel> <min age in days>\n> example: ,antialt on #logs 7",
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
                    description=f"{Emojis.deny} {ctx.author.mention}**:** anti alt module has been **disabled**",
                )
            )

    @antialt.command()
    @blacklist()
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
    @blacklist()

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
    @blacklist()
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

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(administrator=True)
    @blacklist()
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

    @commands.group(aliases=["an", "antiskid"], invoke_without_command=True)
    @commands.bot_has_permissions(administrator=True)
    @blacklist()
    async def antinuke(self, ctx, module: str = None, state: str = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
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
            description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        se = discord.Embed(color=0x2f3136, title="group command: antinuke", description="protect your server against nukes and raids")
        se.set_thumbnail(url=self.bot.user.display_avatar.url)
        se.add_field(name="commands", value=">>> antinuke settings - returns stats of server's antinuke\nantinuke vanity - toggle anti vanity change module\nantinuke ban - toggle anti ban module\nantinuke kick - toggle anti kick module\nantinuke channeldelete - toggle anti channel delete antinuke\nantinuke channelcreate - toggle anti channel create module\n antinuke roledelete - toggle anti role delete module\nantinuke rolecreate - toggle anti role create module\nantinuke webhook - toggles the webhook spam module\nantinuke botadd - toggles the botadd module\nantinuke alt - toggles the alt module\nantinuke guildupdate - toggles the guildupdate module", inline=False)
        se.add_field(name="punishments", value=">>> ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action\njail - jails the unauthorized member after an action ", inline=False)
        se.add_field(name="usage", value="```,antinuke ban on\nantinuke pment jail```", inline=False)
        se.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        se.set_footer(text="aliases: an")

        if antistate == "disabled":
            return await ctx.reply(embed=se)

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
    @blacklist()
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
            description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        e1 = discord.Embed(color=0x2f3136, title="group command: antinuke", description="protect your server against nukes and raids")
        e1.set_thumbnail(url=self.bot.user.display_avatar.url)
        e1.add_field(name="commands", value=">>> antinuke settings - returns stats of server's antinuke\nantinuke vanity - toggle anti vanity change module\nantinuke ban - toggle anti ban module\nantinuke kick - toggle anti kick module\nantinuke channeldelete - toggle anti channel delete antinuke\nantinuke channelcreate - toggle anti channel create module\n antinuke roledelete - toggle anti role delete module\nantinuke rolecreate - toggle anti role create module\nantinuke webhook - toggles the webhook spam module\nantinuke botadd - toggles the botadd module\nantinuke alt - toggles the alt module\nantinuke guildupdate - toggles the guildupdate module", inline=False)
        e1.add_field(name="punishments", value=">>> ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action\njail - jails the unauthorized member after an action ", inline=False)
        e1.add_field(name="usage", value="```,antinuke ban on\nantinuke pment jail```", inline=False)
        e1.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        e1.set_footer(text="aliases: an")
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
    @blacklist()
    async def settings(self, ctx):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
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
            description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        try:
            x = await ctx.guild.fetch_channel(logs)
            x = x.mention
        except:
            try:
                x = discord.utils.get(ctx.guild.text_channels, name="crime-logs")
                x = x.mention
            except:
                x = await ctx.guild.create_text_channel(name="crime-logs")
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

        se = discord.Embed(color=0xf7f9f8)
        se.set_thumbnail(url=self.bot.user.avatar)
        se.description = f""
        se.add_field(
            name=f"Vanity Change",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if vanity == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Role Create",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if rolecreate == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Role Delete",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if roledelete == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Logs Channel",
            value=f"> {'null' if not x else x}",
        )
        se.add_field(
            name=f"Channel Create",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if channelcreate == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Channel Create",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if channeldelete == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Member Ban",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if ban == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Member Kick",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if kick == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Webhook Spam",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if webhook == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Guild Update",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if guild == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Alt Join",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if antialt == 'on' else '<:crimeoff:1082126192099995718>'}",
        )
        se.add_field(
            name=f"Bot Add",
            value=f"> **status:** {'<:crimeon:1082126198601171025>' if antibot == 'on' else '<:crimeoff:1082126192099995718>'}",
        )

        await ctx.reply(embed=se)

    @antinuke.command(aliases=["enable"])
    @blacklist()
    async def on(self, ctx, channel: discord.TextChannel = None):

        try:
            try:
                anti = utils.read_json("antinuke")[str(ctx.guild.id)]
            except:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                    )
                )
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
            whitelisted = anti["whitelisted"]
            notwhitelistedembed = discord.Embed(
                color=self.error,
                description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
            )
            if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
                return await ctx.reply(embed=notwhitelistedembed)
            if not channel:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{Emojis.deny} {ctx.author.mention}**:** please provide a **valid** logs channel",
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
    @blacklist()
    async def off(self, ctx):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
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
    @blacklist()
    async def punishment(self, ctx, pun: str = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        e1 = discord.Embed(color=0x2f3136, title="group command: antinuke", description="protect your server against nukes and raids")
        e1.set_thumbnail(url=self.bot.user.display_avatar.url)
        e1.add_field(name="commands", value=">>> antinuke settings - returns stats of server's antinuke\nantinuke vanity - toggle anti vanity change module\nantinuke ban - toggle anti ban module\nantinuke kick - toggle anti kick module\nantinuke channeldelete - toggle anti channel delete antinuke\nantinuke channelcreate - toggle anti channel create module\n antinuke roledelete - toggle anti role delete module\nantinuke rolecreate - toggle anti role create module\nantinuke webhook - toggles the webhook spam module\nantinuke botadd - toggles the botadd module\nantinuke alt - toggles the alt module\nantinuke guildupdate - toggles the guildupdate module", inline=False)
        e1.add_field(name="punishments", value=">>> ban - bans the unauthorized member after an action\nkick - kicks the unauthorized member after an action\nstrip - removes all staff roles from the unauthorized member after an action\njail - jails the unauthorized member after an action ", inline=False)
        e1.add_field(name="usage", value="```,antinuke ban on\nantinuke pment jail```", inline=False)
        e1.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        e1.set_footer(text="aliases: an")
        if not pun:
            return await ctx.reply(embed=e1)
        punishments = ["ban", "kick", "strip", "jail"]
        if pun not in punishments:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** please provide a **valid** punishment",
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

    @commands.command(aliases=["wl"])
    @blacklist()
    async def whitelist(self, ctx, user: discord.Member = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)
        if not user:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** please provide a **valid** username",
                )
            )

        data = utils.read_json("antinuke")
        data[str(ctx.guild.id)]["whitelisted"].append(user.id)
        utils.write_json(data, "antinuke")
        await ctx.reply(":thumbsup:")

    @commands.command(aliases=["uwl"])
    @blacklist()
    async def unwhitelist(self, ctx, user: discord.Member = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)
        if not user:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** please provide a **valid** username",
                )
            )

        data = utils.read_json("antinuke")
        data[str(ctx.guild.id)]["whitelisted"].remove(user.id)
        utils.write_json(data, "antinuke")
        return await ctx.reply(
        embed=discord.Embed(
            color=self.error,
            description=f"{self.done} {ctx.author.mention}**:** user has been unwhitelisted",
        )
    )
    @antinuke.command(aliases=["logs", "logchannel"])
    @blacklist()
    async def logschannel(self, ctx, channel: discord.TextChannel = None):

        try:
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        except:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)
        if not channel:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.error,
                    description=f"{Emojis.deny} {ctx.author.mention}**:** please provide a **valid** logs channel",
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
        return await ctx.reply(
        embed=discord.Embed(
            color=self.error,
            description=f"{self.done} {ctx.author.mention}**:** logs channel has been set",
        )
    )
    @commands.command()
    @blacklist()
    async def whitelisted(self, ctx):

        try:
            try:
                anti = utils.read_json("antinuke")[str(ctx.guild.id)]
            except:
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.error,
                        description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                    )
                )
            anti = utils.read_json("antinuke")[str(ctx.guild.id)]
            whitelisted = anti["whitelisted"]
            notwhitelistedembed = discord.Embed(
                color=self.error,
                description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
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
                        color=0xf7f9f8,
                        description=" ".join(ret),
                        title=f"whitelisted members",
                        timestamp=datetime.now(),
                    )
                    embed.set_footer(text=f"1/1 ({num} entries)")
                    fakeembed = discord.Embed(
                        color=0xf7f9f8,
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

    @commands.command(aliases=["ab"])
    @blacklist()
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
                    description=f"{Emojis.deny} {ctx.author.mention}**:** antinuke isn't **set up**, use `,an setup` to start",
                )
            )
        anti = utils.read_json("antinuke")[str(ctx.guild.id)]
        whitelisted = anti["whitelisted"]
        notwhitelistedembed = discord.Embed(
            color=self.error,
            description=f"{Emojis.deny} {ctx.author.mention}**:** command restricted to **server owners** & **whitelisted** users",
        )
        if ctx.author.id != ctx.guild.owner.id and ctx.author.id not in whitelisted:
            return await ctx.reply(embed=notwhitelistedembed)

        note = discord.Embed(title="antibot", description="toggles the antibot module", color=0xf7f9f8, timestamp=datetime.now())
        note.set_author(name="antinuke", icon_url=self.bot.user.avatar)
        note.set_footer(
            text="powered by crime",
        )
        note.add_field(
            name=f"category",
            value=f"antinuke",
            inline=False,
        )
        note.add_field(
            name=f"commands",
            value=f",antibot on\n,antibot off",
            inline=False,
        )
        note.add_field(
            name=f"usage",
            value=f"```,antibot <on/off>```",
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
                    description=f"{Emojis.deny} {ctx.author.mention}**:** anti bot module has been **disabled**",
                )
            )

async def setup(bot):
    await bot.add_cog(antinuke(bot))