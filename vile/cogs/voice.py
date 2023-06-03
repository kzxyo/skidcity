import discord, os, sys, asyncio, aiohttp, datetime, sqlite3, textwrap, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils


class limit_modal(discord.ui.Modal, title="vile voicemaster"):
    def __init__(self, button):
        super().__init__()
        self.button = button
        self.limit = discord.ui.TextInput(
            label="vc limit",
            placeholder=f"type a number to change the channel's user limit",
            style=discord.TextStyle.short,
            required=True,
        )
        self.add_item(self.page_num)

    async def on_submit(self, interaction: discord.Interaction):
        try:

            num = int(self.limit.value) - 1

            if num in range(50):
                conn = sqlite3.connect("voice.db")
                c = conn.cursor()
                id = interaction.user.id
                c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
                voice = c.fetchone()
                if voice is None:
                    await interaction.response.send_message(
                        f"you don't own a channel", ephemeral=True
                    )
                else:

                    channelID = voice[0]
                    channel = interaction.client.get_channel(channelID)
                    await channel.edit(user_limit=self.limit)
                    await interaction.response.send_message(
                        ":thumbsup:", ephemeral=True
                    )
                    c.execute(
                        "SELECT channelName FROM userSettings WHERE userID = ?", (id,)
                    )
                    voice = c.fetchone()
                    if voice is None:
                        c.execute(
                            "INSERT INTO userSettings VALUES (?, ?, ?)",
                            (id, f"{interaction.user.name}", self.limit),
                        )
                    else:
                        c.execute(
                            "UPDATE userSettings SET channelLimit = ? WHERE userID = ?",
                            (self.limit, id),
                        )
                conn.commit()
                conn.close()

            else:
                return await interaction.followup.send(
                    content="Invalid number: aborting", ephemeral=True
                )

        except ValueError:
            return await interaction.response.send_message(
                content="That's not a number", ephemeral=True
            )


class interfacebuttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # @discord.ui.button(style=discord.ButtonStyle.grey, label='setup')
    # async def bsetup(self, interaction: discord.Interaction, button: discord.Button):

    # if interaction.user.id != invoker: return
    # conn = sqlite3.connect('voice.db')
    # c = conn.cursor()
    # guildID = interaction.guild.id
    # id = invoker
    # await interaction.response.send_message('what should the category be called? (e.g join 2 create)', ephemeral=True)
    # try:
    #   category = await interaction.client.wait_for('message', check=lambda m: m.author.id == invoker, timeout = 30.0)
    # except asyncio.TimeoutError:
    #   await interaction.response.send_message('you took too long to answer', ephemeral=True)
    # else:
    #   new_cat = await interaction.guild.create_category_channel(category.content)
    #  await interaction.response.send_message('what should the voice channel be called? (e.g j2c)', ephemeral=True)
    # try:
    #    channel = await interaction.client.wait_for('message', check=lambda m: m.author.id == invoker, timeout = 30.0)
    # except asyncio.TimeoutError:
    #    await interaction.response.send_message('you took too long to answer', ephemeral=True)
    # else:
    #    try:
    #        channel = await interaction.guild.create_voice_channel(channel.content, category=new_cat)
    #        c.execute("SELECT * FROM guild WHERE guildID = ? AND ownerID=?", (guildID, id))
    #        voice=c.fetchone()
    #        if voice is None:
    #            c.execute ("INSERT INTO guild VALUES (?, ?, ?, ?)",(guildID,id,channel.id,new_cat.id))
    #        else:
    #            c.execute ("UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?",(guildID,id,channel.id,new_cat.id, guildID))
    #        await interaction.response.send_message(":thumbsup:", ephemeral=True)
    #    except:
    #        await interaction.response.send_message("you didn't enter the names properly, try again", ephemeral=True)
    # conn.commit()
    # conn.close()

    @discord.ui.button(
        style=discord.ButtonStyle.grey, label="lock", custom_id="persistent_view:lock"
    )
    async def block(self, interaction: discord.Interaction, button: discord.Button):

        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = interaction.user.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await interaction.response.send_message(
                f"you don't own a channel", ephemeral=True
            )
        else:
            channelID = voice[0]
            role = interaction.guild.default_role
            channel = interaction.client.get_channel(channelID)
            await channel.set_permissions(role, connect=False)
            await interaction.response.send_message(f":thumbsup:", ephemeral=True)
        conn.commit()
        conn.close()
        await interaction.defer()

    @discord.ui.button(
        style=discord.ButtonStyle.grey,
        label="unlock",
        custom_id="persistent_view:unlock",
    )
    async def bunlock(self, interaction: discord.Interaction, button: discord.Button):

        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = interaction.user.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await interaction.response.send_message(
                f"you don't own a channel", ephemeral=True
            )
        else:
            channelID = voice[0]
            role = interaction.guild.default_role
            channel = interaction.client.get_channel(channelID)
            await channel.set_permissions(role, connect=True)
            await interaction.response.send_message(f":thumbsup:", ephemeral=True)
        conn.commit()
        conn.close()

    @discord.ui.button(
        style=discord.ButtonStyle.grey, label="limit", custom_id="persistent_view:limit"
    )
    async def blimit(self, interaction: discord.Interaction, button: discord.Button):

        # return await interaction.response.send_modal(limit_modal(self))
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = interaction.user.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await interaction.response.send_message(
                f"you don't own a channel", ephemeral=True
            )
        else:

            await interaction.response.send_message(
                "what should the voice channel's limit be?", ephemeral=True
            )
            try:
                limit = await interaction.client.wait_for("message", timeout=30.0)
            except asyncio.TimeoutError:
                await interaction.response.send_message(
                    "you took too long to answer", ephemeral=True
                )
            else:
                channelID = voice[0]
                channel = interaction.client.get_channel(channelID)
                await channel.edit(user_limit=limit.content)
                await interaction.response.send_message(":thumbsup:", ephemeral=True)
                c.execute(
                    "SELECT channelName FROM userSettings WHERE userID = ?", (id,)
                )
                voice = c.fetchone()
                if voice is None:
                    c.execute(
                        "INSERT INTO userSettings VALUES (?, ?, ?)",
                        (id, f"{interaction.user.name}", limit),
                    )
                else:
                    c.execute(
                        "UPDATE userSettings SET channelLimit = ? WHERE userID = ?",
                        (limit, id),
                    )
        conn.commit()
        conn.close()

    @discord.ui.button(
        style=discord.ButtonStyle.grey, label="name", custom_id="persistent_view:name"
    )
    async def bname(self, interaction: discord.Interaction, button: discord.Button):

        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = interaction.user.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await interaction.response.send_message(
                f"you don't own a channel", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "what should the voice channel's name be?", ephemeral=True
            )
            try:
                name = await interaction.client.wait_for("message", timeout=30.0)
            except asyncio.TimeoutError:
                await interaction.response.send_message(
                    "you took too long to answer", ephemeral=True
                )
            else:
                channelID = voice[0]
                channel = interaction.client.get_channel(channelID)
                await channel.edit(name=name.content)
                await interaction.response.send_message(f":thumbsup:", ephemeral=True)
                c.execute(
                    "SELECT channelName FROM userSettings WHERE userID = ?", (id,)
                )
                voice = c.fetchone()
                if voice is None:
                    c.execute(
                        "INSERT INTO userSettings VALUES (?, ?, ?)", (id, name, 0)
                    )
                else:
                    c.execute(
                        "UPDATE userSettings SET channelName = ? WHERE userID = ?",
                        (name, id),
                    )
        conn.commit()
        conn.close()

    @discord.ui.button(
        style=discord.ButtonStyle.grey, label="claim", custom_id="persistent_view:claim"
    )
    async def bclaim(self, interaction: discord.Interaction, button: discord.Button):

        x = False
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        channel = interaction.user.voice.channel
        if channel == None:
            await interaction.response.send_message(
                f"you're not in a voice channel", ephemeral=True
            )
        else:
            id = interaction.user.id
            c.execute(
                "SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,)
            )
            voice = c.fetchone()
            if voice is None:
                await interaction.response.send_message(
                    f"you can't own that channel", ephemeral=True
                )
            else:
                async for data in utils.aiter(channel.members):
                    if data.id == voice[0]:
                        owner = interaction.guild.get_member(voice[0])
                        await interaction.response.send_message(
                            f"this channel is already owned by {owner.mention}",
                            ephemeral=True,
                        )
                        x = True
                if x == False:
                    await interaction.response.send_message(f":thumbsup:")
                    c.execute(
                        "UPDATE voiceChannel SET userID = ? WHERE voiceID = ?",
                        (id, channel.id),
                    )
            conn.commit()
            conn.close()


class voice(commands.Cog):
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

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        guildID = member.guild.id
        c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
        voice = c.fetchone()
        if voice is None:
            pass
        else:
            voiceID = voice[0]
            try:
                if after.channel.id == voiceID:
                    c.execute(
                        "SELECT * FROM voiceChannel WHERE userID = ?", (member.id,)
                    )
                    cooldown = c.fetchone()
                    if cooldown is None:
                        pass
                    else:
                        # await member.send("stop trying to rate limit me lol")
                        # await asyncio.sleep(15)
                        pass
                    c.execute(
                        "SELECT voiceCategoryID FROM guild WHERE guildID = ?",
                        (guildID,),
                    )
                    voice = c.fetchone()
                    c.execute(
                        "SELECT channelName, channelLimit FROM userSettings WHERE userID = ?",
                        (member.id,),
                    )
                    setting = c.fetchone()
                    c.execute(
                        "SELECT channelLimit FROM guildSettings WHERE guildID = ?",
                        (guildID,),
                    )
                    guildSetting = c.fetchone()
                    if setting is None:
                        name = f"{member.name}'s channel"
                        if guildSetting is None:
                            limit = 0
                        else:
                            limit = guildSetting[0]
                    else:
                        if guildSetting is None:
                            name = setting[0]
                            limit = setting[1]
                        elif guildSetting is not None and setting[1] == 0:
                            name = setting[0]
                            limit = guildSetting[0]
                        else:
                            name = setting[0]
                            limit = setting[1]
                    categoryID = voice[0]
                    id = member.id
                    category = self.bot.get_channel(categoryID)
                    channel2 = await member.guild.create_voice_channel(
                        name, category=category
                    )
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(
                        self.bot.user, connect=True, read_messages=True
                    )
                    await channel2.edit(name=name, user_limit=limit)
                    c.execute("INSERT INTO voiceChannel VALUES (?, ?)", (id, channelID))
                    conn.commit()

                    def check(a, b, c):
                        return len(channel2.members) == 0

                    await self.bot.wait_for("voice_state_update", check=check)
                    await channel2.delete()
                    await asyncio.sleep(3)
                    c.execute("DELETE FROM voiceChannel WHERE userID=?", (id,))
            except:
                pass
        conn.commit()
        conn.close()

    @commands.hybrid_group(aliases=["vm", "voicemaster", "vc"])
    async def voice(self, ctx):

        ex = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        ex.set_author(name="voice", icon_url=self.bot.user.display_avatar)
        ex.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** manage the voicemaster module\n{self.reply} **aliases:** vm, voicemaster",
        )
        ex.add_field(
            name=f"{self.dash} Sub Cmds",
            value="```,voice setup - set up the voicemaster module\n,voice lock - lock the channel\n,voice unlock - unlock the channel\n,voice name - change yout channel name\n,voice limit - change your channel limit\n,voice permit (user) - give user's perms to join\n,voice claim - claim ownership of the channel\n,voice reject - remove user's perms to join\n\n```",
            inline=False,
        )
        ex.set_footer(
            text=f"voice",
            icon_url=None,
        )
        await ctx.reply(embed=ex)

    @voice.command()
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx):

        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        guildID = ctx.guild.id
        id = ctx.author.id
        await ctx.reply("what should the category be called?")
        try:
            category = await self.bot.wait_for(
                "message", check=lambda m: m.author.id == ctx.author.id, timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.reply("you took too long to answer")
        else:
            new_cat = await ctx.guild.create_category_channel(category.content)
            await ctx.reply("what should the voice channel be called?")
            try:
                channel = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author.id == ctx.author.id,
                    timeout=30.0,
                )
            except asyncio.TimeoutError:
                await ctx.channel.send("you took too long to answer")
            else:
                try:
                    channel = await ctx.guild.create_voice_channel(
                        channel.content, category=new_cat
                    )
                    overwrites = {
                        ctx.guild.default_role: discord.PermissionOverwrite(
                            read_messages=True, send_messages=False
                        ),
                        ctx.guild.me: discord.PermissionOverwrite(
                            read_messages=True, send_messages=True
                        ),
                    }
                    interface = await ctx.guild.create_text_channel(
                        "vile-interface", category=new_cat, overwrites=overwrites
                    )
                    ex = discord.Embed(color=0x2F3136, timestamp=datetime.now())
                    ex.set_author(
                        name="vile interface", icon_url=self.bot.user.display_avatar
                    )
                    ex.add_field(
                        name=f"{self.dash} Info",
                        value=f"{self.reply} **description:** vile's voicemaster interface\n{self.reply} **aliases:** if, inter, iface\n{utils.read_json('emojis')['dash']} **functions:** lock, unlock, limit, name, claim",
                    )
                    ex.add_field(
                        name=f"{self.dash} Sub Cmds",
                        value="```YAML\nlock - lock the channel\nunlock - unlock the channel\nname - change yout channel name\nlimit - change your channel limit\nclaim - claim ownership of the channel\n\n```",
                        inline=False,
                    )
                    ex.set_footer(
                        text="voice",
                        icon_url=None,
                    )
                    await interface.send(embed=ex, view=interfacebuttons())

                    c.execute(
                        "SELECT * FROM guild WHERE guildID = ? AND ownerID=?",
                        (guildID, id),
                    )
                    voice = c.fetchone()
                    if voice is None:
                        c.execute(
                            "INSERT INTO guild VALUES (?, ?, ?, ?)",
                            (guildID, id, channel.id, new_cat.id),
                        )
                    else:
                        c.execute(
                            "UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?",
                            (guildID, id, channel.id, new_cat.id, guildID),
                        )
                    await ctx.reply(":thumbsup:")
                except:
                    await ctx.reply(traceback.format_exc())
        conn.commit()
        conn.close()

    @voice.command(aliases=["if", "inter", "iface"])
    async def interface(self, ctx):

        invoker = ctx.author.id

        ex = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        ex.set_author(name="vile interface", icon_url=self.bot.user.display_avatar)
        ex.add_field(
            name=f"{self.dash} Info",
            value=f"{self.reply} **description:** vile's voicemaster interface\n{self.reply} **aliases:** if, inter, iface\n{utils.read_json('emojis')['dash']} **functions:** lock, unlock, limit, name, claim",
        )
        ex.add_field(
            name=f"{self.dash} Sub Cmds",
            value="```YAML\nlock - lock the channel\nunlock - unlock the channel\nname - change yout channel name\nlimit - change your channel limit\nclaim - claim ownership of the channel\n\n```",
            inline=False,
        )
        ex.set_footer(
            text="voice",
            icon_url=None,
        )
        ex = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        ex.set_author(name="vile interface", icon_url=self.bot.user.display_avatar)
        ex.add_field(name=f"Description", value="vile's voicemaster interface")
        ex.add_field(name="Aliases", value="vm, voicemaster", inline=False)
        ex.add_field(
            name=f"Sub Cmds",
            value="```lock - lock the channel\nunlock - unlock the channel\nname - change yout channel name\nlimit - change your channel limit\nclaim - claim ownership of the channel```",
            inline=False,
        )
        ex.set_footer(
            text=f"Module: {ctx.command.cog_name}",
            icon_url=None,
        )
        await ctx.reply(embed=ex, view=interfacebuttons())

    @commands.hybrid_command()
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(manage_guild=True)
    async def setlimit(self, ctx, num):

        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        c.execute("SELECT * FROM guildSettings WHERE guildID = ?", (ctx.guild.id,))
        voice = c.fetchone()
        if voice is None:
            c.execute(
                "INSERT INTO guildSettings VALUES (?, ?, ?)",
                (ctx.guild.id, f"{ctx.author.name}'s channel", num),
            )
        else:
            c.execute(
                "UPDATE guildSettings SET channelLimit = ? WHERE guildID = ?",
                (num, ctx.guild.id),
            )
        await ctx.reply(":thumbsup:")

        conn.commit()
        conn.close()

    @voice.command(name="lock")
    async def voice_lock(self, ctx):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.reply(f"you don't own a channel")
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False)
            await ctx.reply(f":thumbsup:")
        conn.commit()
        conn.close()

    @voice.command(name="unlock")
    async def voice_unlock(self, ctx):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.reply(f"you don't own a channel")
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True)
            await ctx.reply(f":thumbsup:")
        conn.commit()
        conn.close()

    @voice.command(aliases=["allow"])
    async def permit(self, ctx, member: discord.Member):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.reply(f"you don't own a channel")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)
            await ctx.reply(
                embed=discord.Embed(
                    color=self.success,
                    description=f"{self.done} {ctx.author.mention}**:** {member.name} now has **access** to the channel",
                )
            )
        conn.commit()
        conn.close()

    @voice.command(aliases=["deny"])
    async def reject(self, ctx, member: discord.Member):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = ctx.author.id
        guildID = ctx.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.reply(f"you don't own a channel")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            async for members in utils.aiter(channel.members):
                if members.id == member.id:
                    c.execute(
                        "SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,)
                    )
                    voice = c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False, read_messages=True)
            await ctx.reply(
                embed=discord.Embed(
                    color=self.success,
                    description=f"{self.done} {ctx.author.mention}**:** {member.name} no longer has **access** to the channel",
                )
            )
        conn.commit()
        conn.close()

    @voice.command()
    async def limit(self, ctx, limit):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.reply(f"you don't own a channel")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit=limit)
            await ctx.reply(":thumbsup:")
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice = c.fetchone()
            if voice is None:
                c.execute(
                    "INSERT INTO userSettings VALUES (?, ?, ?)",
                    (id, f"{ctx.author.name}", limit),
                )
            else:
                c.execute(
                    "UPDATE userSettings SET channelLimit = ? WHERE userID = ?",
                    (limit, id),
                )
        conn.commit()
        conn.close()

    @voice.command()
    async def name(self, ctx, *, name):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.reply(f"you don't own a channel")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name=name)
            await ctx.reply(f":thumbsup:")
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice = c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id, name, 0))
            else:
                c.execute(
                    "UPDATE userSettings SET channelName = ? WHERE userID = ?",
                    (name, id),
                )
        conn.commit()
        conn.close()

    @voice.command()
    async def claim(self, ctx):
        x = False
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        channel = ctx.author.voice.channel
        if channel == None:
            await ctx.reply(f"you're not in a voice channel")
        else:
            id = ctx.author.id
            c.execute(
                "SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,)
            )
            voice = c.fetchone()
            if voice is None:
                await ctx.reply(f"you can't own that channel")
            else:
                async for data in utils.aiter(channel.members):
                    if data.id == voice[0]:
                        owner = ctx.guild.get_member(voice[0])
                        await ctx.reply(
                            f"this channel is already owned by {owner.mention}"
                        )
                        x = True
                if x == False:
                    await ctx.reply(f":thumbsup:")
                    c.execute(
                        "UPDATE voiceChannel SET userID = ? WHERE voiceID = ?",
                        (id, channel.id),
                    )
            conn.commit()
            conn.close()


async def setup(bot):
    await bot.add_cog(voice(bot))
