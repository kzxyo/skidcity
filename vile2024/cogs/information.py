from asyncio import (
    gather,
    sleep
)

from typing import (
    Any,
    Optional,
    Literal,
    Union
)

from typing_extensions import NoReturn
from datetime import datetime as Date
from humanize import ordinal
from io import BytesIO
from pydantic import ValidationError

from discord import (
    ButtonStyle,
    Color as BaseColor,
    Embed,
    File,
    Guild,
    Interaction,
    Invite,
    Member as BaseMember,
    User as BaseUser,
    utils
)

from discord.ext.commands import (
    Author,
    BucketType,
    bot_has_permissions,
    Cog,
    command as Command,
    CommandError,
    CurrentGuild,
    Greedy,
    group as Group,
    max_concurrency,
    parameter
)

from discord.ui import (
    Button,
    View
)

from discord.utils import format_dt
from munch import Munch

from random import (
    shuffle,
)

from utilities.vile import (
    Attachment,
    Color,
    Context,
    DataProcessing,
    dominant_color,
    ImageGenerator,
    Member,
    MinecraftUser,
    Role,
    strip_flags,
    User,
    VileBot
)

from contextlib import suppress
from xxhash import xxh3_64_hexdigest as hash

import arrow

TUPLE = ()


class Information(Cog):
    def __init__(self: "Information", bot: VileBot) -> NoReturn:
        self.bot = bot
    
    @Command(
        name="generate",
        aliases=("gen",),
        usage="<prompt>",
        example="generate cats",
    )
    @max_concurrency(1, BucketType.channel, wait=False)
    async def generate(
        self: "Information", 
        ctx: Context, 
        *, 
        prompt: str
    ):
        """Generate an image based on a prompt"""
        
        if not ctx.channel.nsfw:
            raise CommandError("Due to reported issues with our content moderation system, this command is temporarily restricted to NSFW channels.")
        
        if not (image_buffer := self.bot.cache.get(f"bytes:dalle:{hash(prompt)}")):
            try:
                data = await (await self.bot.rival.request(
                    method="GET", 
                    endpoint="/image/generation", 
                    params = {
                        "prompt": prompt
                    }
                )).json()

                self.bot.cache.set(
                    f"bytes:dalle:{hash(prompt)}", 
                    image_buffer := await self.bot.session.read(data["url"])
                )
            
            except Exception: 
                raise CommandError("I couldn't generate the requested image.")
        
        explicit_report = await self.bot.data_processing.determine_explicit(image_buffer)

        if (explicit_report.nudity and not ctx.channel.nsfw) or explicit_report.gore:
            raise CommandError("I couldn't display this image; it contains explicit content.")
        
        return await ctx.reply(file=File(
            fp=BytesIO(image_buffer),
            filename=f"{self.bot.user.name.title()} DALL-E.png"
        ))
        
    
    @Group(
        name="minecraft",
        aliases=("mcraft",),
        usage="<sub command>",
        example="avatar onlinv",
        invoke_without_command=True
    )
    async def minecraft(self: "Information", ctx: Context):
        """
        View information on a Minecraft user
        """

        return await ctx.send_help(ctx.command.qualified_name)
    

    @minecraft.command(
        name="user",
        aliases=("information", "info"),
        usage="<user name/uuid>",
        example="onlinv"
    )
    async def minecraft_user(
        self: "Information", 
        ctx: Context, 
        user: MinecraftUser
    ):
        """
        View a Minecraft user's information
        """

        return await ctx.reply(
            embed=(
                Embed(color=await dominant_color(user.body))
                .set_author(
                    name=user.username,
                    icon_url=user.avatar
                )
                .set_thumbnail(url=user.avatar)
                .set_image(url=user.body)
                .set_footer(text=f"UUID: {user.id}")
                .add_field(
                    name="Previous Names",
                    value=f"> {'N/A' if not user.name_history else ', '.join(user.name_history)}"
                )
            ),
            view=View().add_items((
                Button(
                    style=ButtonStyle.link,
                    label="Avatar",
                    url=user.body
                ),
                Button(
                    style=ButtonStyle.link,
                    label="Head",
                    url=user.avatar
                )
            ))
        )
    

    @minecraft.command(
        name="avatar",
        aliases=("av",),
        usage="<user name/uuid>",
        example="onlinv"
    )
    async def minecraft_avatar(
        self: "Information", 
        ctx: Context, 
        user: MinecraftUser
    ):
        """
        View a Minecraft user's avatar
        """

        return await ctx.reply(file=File(
            BytesIO(await self.bot.session.read(user.body)),
            "avatar.png"
        ))
    

    @minecraft.command(
        name="head",
        usage="<user name/uuid>",
        example="onlinv"
    )
    async def minecraft_head(
        self: "Information", 
        ctx: Context, 
        user: MinecraftUser
    ):
        """
        View a Minecraft user's head
        """

        return await ctx.reply(file=File(
            BytesIO(await self.bot.session.read(user.avatar)),
            "head.png"
        ))
    

    @Group(
        name="boosters",
        usage="<sub command>",
        example="lost",
        invoke_without_command=True
    )
    async def boosters(self: "Information", ctx: Context):
        """
        View the server's boosters
        """

        if not (boosters := tuple(
            m for m in ctx.guild.members 
            if m.premium_since
        )):
            raise CommandError("There aren't any boosters in this server.")
        
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Boosters in '{ctx.guild.name}'"
        )

        for booster in boosters:
            rows.append(f"{booster} - {format_dt(booster.premium_since, style='D')}")

        return await ctx.paginate((embed, rows))
    
    
    @boosters.command(
        name="lost",
        aliases=("l",)
    )
    async def boosters_lost(self: "Information", ctx: Context):
        """
        View the members who have stopped boosting
        """

        if not (boosters_lost := await self.bot.db.execute(
            "SELECT user_id, expired FROM boosters_lost WHERE guild_id = %s;",
            ctx.guild.id
        )):
            raise CommandError("There are no lost boosters in this server.")
        
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Boosters Lost in '{ctx.guild.name}'"
        )

        for user_id, expired in boosters_lost:
            if user := self.bot.get_user(user_id):
                rows.append(f"{user} - {format_dt(expired, style='D')}")

        return await ctx.paginate((embed, rows))
    

    @Command(
        name="ping",
        aliases=("latency",)
    )
    async def ping(self: "Information", ctx: Context):
        """
        View the bot's WebSocket and edit latency
        """
        return await ctx.success(f"WebSocket latency: `{round(self.bot.latency*1000, 2)}ms`")
    

    @Command(
        name="membercount",
        aliases=("mc",),
        usage="[server invite]",
        example="/vilebot"
    )
    async def membercount(
        self: "Information", 
        ctx: Context, 
        *, 
        server: Union[ Invite, Guild ] = CurrentGuild
    ):
        """
        View the server's member count
        """

        if isinstance(server, Invite) and not isinstance(server.guild, Guild):
            invite = server
            server = invite.guild

            return await ctx.reply(
                embed=(
                    Embed(
                        color=self.bot.color,
                        timestamp=Date.now()
                    )
                    .set_author(
                        name=f"{server.name}'s member count",
                        icon_url=server.icon
                    )
                    .add_field(
                        name="Members (+0)",
                        value=f"{invite.approximate_member_count:,}"
                    )
                    .add_field(
                        name="Humans (0.00%)",
                        value="N/A"
                    )
                    .add_field(
                        name="Bots (0.00%)",
                        value="N/A"
                    )
                )
            )
        
        if isinstance(server, Invite):
            server = server.guild

        members = [member async for member in server.fetch_members()] if server.id != ctx.guild.id else ctx.guild.members

        humans = len(tuple(
            m for m in members 
            if not m.bot
        ))

        bots = len(tuple(
            m for m in members 
            if m.bot
        ))

        joins = len(sorted(
            (
                m for m in members
                if Date.now().timestamp() - m.joined_at.timestamp() < 86400
            ),
            key=lambda m: m.joined_at
        ))

        return await ctx.reply(
            embed=(
                Embed(
                    color=self.bot.color,
                    timestamp=Date.now()
                )
                .set_author(
                    name=f"{server.name}'s member count",
                    icon_url=server.icon
                )
                .add_field(
                    name=f"Members (+{joins})",
                    value=f"{server.member_count:,}"
                )
                .add_field(
                    name=f"Humans ({round((humans / server.member_count) * 100, 2)}%)",
                    value=f"{humans:,}"
                )
                .add_field(
                    name=f"Bots ({round((bots / server.member_count) * 100, 2)}%)",
                    value=f"{bots:,}"
                )
            )
        )
    

    @Command(
        name="recentjoins",
        aliases=("rj", "newmembers", "recentmembers")
    )
    async def recentjoins(
        self: "Information",
        ctx: Context, 
        count: Optional[int] = 5
    ):
        """
        View recently joined members
        """

        if count > 100:
            raise CommandError("I can only display up to **100 users**.")
        
        embed = Embed(
            color=self.bot.color,
            title=f"Recent Joins in '{ctx.guild.name}'"
        )

        rows = [
            f"{member} - {format_dt(member.joined_at, style='R' if (Date.now().astimezone()-member.joined_at).total_seconds() < 86400 else 'D')}"
            for member in sorted(
                ctx.guild.members,
                key=lambda member: member.joined_at,
                reverse=True,
            )[:count]
        ]

        return await ctx.paginate((embed, rows))
    

    @Command(
        name="image",
        aliases=("img", "images"),
        usage="<query>",
        example="black people"
    )
    async def image(
        self: "Information", 
        ctx: Context, 
        *, 
        query: str
    ):
        """
        View image results for your query
        """

        safe = not ctx.channel.nsfw
        embeds = [ ]
            
        data = await self.bot.data_processing.google_images(
            query, 
            safe
        )

        if not data and safe:
            raise CommandError("I couldn't find any image results; safe search is enabled.")
            
        if not data:
            raise CommandError("I couldn't find any image results.")
                
        shuffle(data)
        
        for index, result in enumerate(data[:100], start=1):
            embeds.append((
                Embed(
                    color=result["color"],
                    title=f"{result['title']} ({result['domain']})",
                    url=result["url"]
                )
                .set_author(
                    name=ctx.author,
                    icon_url=ctx.author.display_avatar
                )
                .set_image(url=result["url"])
                .set_footer(
                    text=f"Page {index} / {len(data[:100])} (Safe Search: FAILED)",
                    icon_url="https://cdn.discordapp.com/emojis/1131689476394065950.webp?size=160&quality=lossless"
                )
            ))

        #async def execute_upon_switch(paginator: "Paginator", interaction: Interaction):
            #data[paginator.page]["color"] = await get_image_color(data[paginator.page]["url"])
            #paginator.embeds[paginator.page].color = data[paginator.page]["color"]

        return await ctx.paginate(embeds, )#execute=(execute_upon_switch,))
            

    @Command(
        name="google",
        aliases=("g", "gsearch"),
        usage="<query>",
        example="discord"
    )
    async def google(
        self: "Information", 
        ctx: Context, 
        *, 
        query: str
    ):
        """
        View google search results for your query
        """

        safe = not ctx.channel.nsfw
        fields = [ ]
        embed = (
            Embed(
                color=self.bot.color,
                title=f"Search results for '{query}'",
                url=f"https://google.com/search?q={query.replace(' ', '%20')}"
            )
            .set_author(
                name=ctx.author,
                icon_url=ctx.author.display_avatar
            )
        )

        data = await self.bot.data_processing.google_search(
            query, 
            safe
        )

        if not data and safe:
            raise CommandError("I couldn't find any search results; safe search is enabled.")
        
        if not data:
            raise CommandError("I couldn't find any search results.")
        
        shuffle(data)
        
        for result in data[:100]:
            result = Munch(result)

            fields.append(dict(
                name=f"{result.title[:1900]} ({result.domain})",
                value=result.description,
                inline=False
            ))

        return await ctx.paginate_fields(
            embed,
            fields,
            footer=dict(
                text=f"Page {{index}} / {{total}} (Safe Search: {'enabled' if not ctx.channel.nsfw else 'disabled'})",
                icon_url="https://cdn.discordapp.com/emojis/1131689476394065950.webp?size=160&quality=lossless"
            ),
            per_page=5
        )
    

    @Command(
        name="color",
        aliases=("hex",),
        usage="<images or colors>",
        example="#ffffff #000000"
    )
    async def color(
        self: "Information", 
        ctx: Context, 
        sources: Greedy[Union[ Color, Member, Role ]] = TUPLE
    ):
        """
        Show information on the provided colors
        """

        if not sources and not ctx.message.attachments:
            return await ctx.send_help(ctx.command.qualified_name)
        
        colors = [
            (str(source).lstrip("#") if isinstance(source, BaseColor) else str(source.color).lstrip("#"))
            for source in sources
        ] + [
            str(BaseColor(color)).lstrip("#")
            for color in await gather(*(
                dominant_color(attachment.url)
                for attachment in (
                    ctx.message.reference.resolved.attachments 
                    if ctx.message.reference 
                    else ctx.message.attachments
                )
            ))
        ]

        embeds = [ ]

        color_data = await gather(*(
            self.bot.proxied_session.get(f"https://api.alexflipnote.dev/colour/{color}")
            for color in colors[:10]
        ))

        for data in color_data:
            if data.get("code"):
                continue
            
            embeds.append((
                Embed(color=data["int"])
                .set_thumbnail(url=data["images"]["square"])
                .set_image(url=data["images"]["gradient"])
                .set_author(
                    name=data["name"], 
                    icon_url=data["images"]["square"]
                )
                .set_footer(text=f"Page {color_data.index(data)+1} / {len(tuple(data for data in color_data if data.get('code') is None))}")
                .add_field(
                    name="RGB", 
                    value=data["rgb"]["string"]
                )
                .add_field(
                    name="Hex", 
                    value=data["hex"]["string"]
                )
                .add_field(
                    name="Brightness", 
                    value=data["brightness"]
                )
                .add_field(
                    name="Shades", 
                    value=f"```{', '.join(data['shade'][:4])}```"
                )
            ))

        return await ctx.paginate(embeds)
    

    @Command(
        name="define",
        usage="<word>",
        example="kiss"
    )
    async def define(
        self: "Information", 
        ctx: Context, 
        word: str
    ):
        """
        Get the definition of a word
        """

        if (data := await self.bot.data_processing.definition(word)).valid is False:
            raise CommandError("I couldn't find a definition for that word.")

        embed = ctx.default_embed
        embed.title = f"Definition for '{word}'"
        embed.description = "> " + data.definition.split("\n")[0]

        return await ctx.reply(embed=embed)
    

    @Command(
        name="urbandictionary",
        aliases=("urban", "ud"),
        usage="<term>",
        example="weirdo"
    )
    async def urbandictionary(
        self: "Information", 
        ctx: Context, 
        term: str
    ):
        """
        Get the urban definition of a term
        """

        if not (data := await self.bot.data_processing.urban_definition(term)):
            raise CommandError("I couldn't find a definition for that word.")

        embeds = [ ]

        for index, record in enumerate(sorted(
            data[:3],
            key=lambda record: record.thumbs_up,
            reverse=True
        ), start=1):
            embeds.append(
                ctx.default_embed
                .add_field(
                    name=f"Urban Definition for '{term}'",
                    value=f"> {(record.definition[:650] + ('...' if len(record.definition) > 650 else '')).replace('[', '').replace(']', '')}"
                )
                .add_field(
                    name="Example",
                    value=f"> {(record.example[:650] + ('...' if len(record.example) > 650 else '')).replace('[', '').replace(']', '')}",
                    inline=False
                )
                .set_footer(text=f"Page {index} / {len(data[:3])} | 👍 {record.thumbs_up} 👎 {record.thumbs_down}")
            )

        return await ctx.paginate(embeds)
    

    @Group(
        name="detect",
        aliases=("find",),
        usage="<sub command>",
        example="objects ...",
        invoke_without_command=True
    )
    async def detect(self: "Information", ctx: Context):
        """
        Utilities for detecting (x) in images
        """
        
        return await ctx.send_help(ctx.command.qualified_name)
    

    @detect.command(
        name="objects",
        usage="[image]",
        example="..."
    )
    async def detect_objects(
        self: "Information", 
        ctx: Context, 
        image: Attachment = parameter(
            converter=Attachment,
            default=Attachment.search
        )
    ):
        """
        Detect objects in an image
        """

        if not (data := await self.bot.data_processing.detect_objects(await self.bot.proxied_session.read(image))):
            raise CommandError("I couldn't find any objects in that image.")
        
        if len(data) > 2:
            lastk, lastv = tuple(data.items())[-1]
            fmt = "{}, and {}".format(
                ", ".join(f"{'a' if v == 1 else v} {k.replace('person', 'people') + ('s' if (v > 1 and k != 'person') else '')}" for k, v in tuple(data.items())[:-1]), 
                f"{'a' if lastv == 1 else lastv} {lastk.replace('person', 'people') + ('s' if (lastv > 1 and lastk != 'person') else '')}"
            )

        else:
            fmt = " and ".join(f"{'a' if v == 1 else v} {(k.replace('person', 'people') if v > 1 else k) + ('s' if (v > 1 and k != 'person') else '')}" for k, v in data.items())

        return await ctx.success(f"I found [{fmt}]({image}).")
    

    @detect.command(
        name="text",
        usage="[image]",
        example="..."
    )
    async def detect_text(
        self: "Information", 
        ctx: Context, 
        image: Attachment = parameter(
            converter=Attachment,
            default=Attachment.search
        )
    ):
        """
        Detect text in an image
        """

        if not (data := await self.bot.data_processing.detect_text(await self.bot.proxied_session.read(image))):
            raise CommandError("I couldn't find any text in that image.")
        
        return await ctx.reply(f"```{data}```")
    

    @Command(
        name="inflation",
        usage="[type <CPI/HICP>] <country>",
        example="CPI United States"
    )
    async def inflation(
        self: "Information",
        ctx: Context,
        _type: Optional[Literal[ "CPI", "HICP", "cpi", "hicp" ]],
        *,
        country: str
    ):
        """
        Get the inflation rates for a country
        """


        if not (data := await self.bot.data_processing.inflation(_type or "CPI", country)):
            raise CommandError("I couldn't find that country.")

        return await ctx.reply(embed=(
            ctx.default_embed
            .set_title(f"{_type or 'CPI'} inflation rates for '{data['country']}'")
            .set_timestamp(Date.now())
            .add_field(
                name="Monthly Rate",
                value=f"{data['monthly_rate_pct']:.2f}%",
            )
            .add_field(
                name="Annual Rate",
                value=f"{data['yearly_rate_pct']:.2f}%",
            )
        ))
    

    @Command(
        name="sentiment",
        aliases=("tone",),
        usage="<text>",
        example="I'm loving it!"
    )
    async def sentiment(
        self: "Information", 
        ctx: Context, 
        *, 
        text: str
    ):
        """
        Get the sentiment for the given text
        """

        if not any(char.isalpha() for char in text):
            raise CommandError("Please provide **valid** text.")
        
        data = await self.bot.data_processing.text_sentiment(text)
        return await ctx.success(f"The **sentiment** for the text `{data.text}` is **{data.sentiment.lower()}** with a score of `{data.score}`.")
    

    @Command(
        name="similarity",
        aliases=("textsimilarity",),
        usage="<text1> || <text2>",
        example="Hello || Hi"
    )
    async def similarity(
        self: "Information", 
        ctx: Context, 
        *, 
        text: str
    ):
        """
        Get the similarity between two given texts
        """

        if len(sliced := text.split("||")) != 2:
            raise CommandError("Please provide **valid** texts separated by '||'.")
        
        data = await self.bot.data_processing.text_similarity(*(item.strip() for item in sliced))
        return await ctx.success(f"The similarity between the two given texts is `{(data['similarity'] * 100):.2f}%`.")
    

    @Command(
        name="userinfo",
        aliases=("uinfo", "u", "i", "ui"),
        usage="[user]",
        example="@mewa"
    )
    async def userinfo(
        self: "Information", 
        ctx: Context, 
        *, 
        user: Union[ Member, User ] = Author
    ):
        """View information about the mentioned user"""

        # Dates
        joined = "N/A"
        boosted = "N/A"
        created = utils.format_dt(user.created_at, style='R')

        if isinstance(user, BaseMember):
            joined = utils.format_dt(user.joined_at, style="R")

            if user.premium_since is not None:
                boosted = utils.format_dt(user.premium_since, style="R")

        # Roles
        roles = ""

        if isinstance(user, BaseMember) and user.roles:
            if len(user.roles) > 5:
                roles = ", ".join(role.mention for role in tuple(reversed(user.roles[1:]))[:5]) + f" and {len(user.roles)-5} more"
           
            else:
                roles = ", ".join([role.mention for role in tuple(reversed(user.roles[1:]))] + [ "@everyone" ])

        # Permissions
        permissions = ""

        if isinstance(user, BaseMember):
            permissions = (
                "Administrator"
                if user.guild_permissions.administrator
                else "Create Invite" 
                if user.guild_permissions.create_instant_invite
                else "No Permissions"
            )

        # Join Position
        join_position = ""
        if isinstance(user, BaseMember):
            joinpos = ordinal(
                sorted(ctx.guild.members, key=lambda m: m.joined_at)
                .index(user) + 1
            )
            join_position = f"Join position: {joinpos}"
        
        # badges
        ui = None # await utils.get_user(user.id)
        badges = [ ]
        flags = user.public_flags

        emojis = Munch({
            "nitro": "<:vile_nitro:1022941557541847101>",
            "hypesquad_brilliance": "<:vile_hsbrilliance:1022941561392209991>",
            "hypesquad_bravery": "<:vile_hsbravery:1022941564349194240>",
            "hypesquad_balance": "<:vile_hsbalance:1022941567318765619>",
            "bug_hunter": "<:vile_bhunter:991776532227969085>",
            "bug_hunter_level_2": "<:vile_bhunterplus:991776477278388386>",
            "discord_certified_moderator": "<:vile_cmoderator:1022943277340692521>",
            "early_supporter": "<:vile_esupporter:1022943630945685514>",
            "verified_bot_developer": "<:vile_dev:1042082778629537832>",
            "partner": "<:vile_partner:1022944710895075389>",
            "staff": "<:vile_dstaff:1022944972858720327>",
            "verified_bot": "<:vile_vbot:1022945560094834728>",
            "server_boost": "<:vile_sboost:1022950372576342146>",
            "active_developer": "<:vile_activedev:1043160384124751962>",
            "pomelo": "<:pomelo:1122143950719954964>"
        })
        
        for flag in (
            "bug_hunter",
            "bug_hunter_level_2",
            "discord_certified_moderator",
            "hypesquad_balance",
            "hypesquad_bravery",
            "hypesquad_brilliance",
            "active_developer",
            "early_supporter",
            "partner",
            "staff",
            "verified_bot",
            "verified_bot_developer"
        ):
            if getattr(flags, flag, False) is True:
                badges.append(emojis[flag])
        
        if ctx.is_boosting(user) is True:
            badges.extend((
                emojis.nitro,
                emojis.server_boost
            ))

        if user.discriminator == "0":
            badges.append(emojis.pomelo)
        
        # Mutuals
        mutual_guilds = (
            "No mutual guilds" 
            if not user.mutual_guilds 
            else f"{len(user.mutual_guilds)} mutual guild{'' if len(user.mutual_guilds) == 1 else 's'}"
        )
        
        # Buttons
        user2 = await self.bot.fetch_user(user.id)
        banner = user2.banner and user2.banner.url or "https://none.none"
        
        view = (
            View()
            .add_item(
                Button(
                    style=ButtonStyle.link, 
                    label="Avatar", 
                    url=user.display_avatar.url, 
                    disabled=False
                )
            )
            .add_item(
                Button(
                    style=ButtonStyle.link, 
                    label="Banner", 
                    url=banner, 
                    disabled=True if banner == "https://none.none" else False
                )
            )
        )
        
        # Embed
        footer = (
            "" 
            if not isinstance(user, BaseMember) 
            else f"{permissions}   \u2022   {join_position}   \u2022   "
        )

        embed = (
            Embed(
                color=await dominant_color(user.display_avatar),
                title=f"{user}  \u2022  {' '.join(badges)}"
            )
            .set_author(
                name=f"{user.name} ( {user.id} )", 
                icon_url=user.display_avatar
            )
            .set_footer(text=f"{footer}{mutual_guilds}")
            .set_thumbnail(url=user.display_avatar)
            .add_field(
                name="Created", 
                value=created
            )
            .add_field(
                name="Joined", 
                value=joined
            )
            .add_field(
                name="Boosted", 
                value=boosted
            )
        )

        if roles:
            embed.add_field(
                name=f"Roles [{len(user.roles)}]", 
                value=roles, 
                inline=False
            )
        
        return await ctx.reply(
            embed=embed, 
            view=view
        )
        

    @Command(
        name="avatar",
        aliases=("av",),
        usage="[user] [type global/server]",
        example="@mewa global"
    )
    async def avatar(
        self: "Information",
        ctx: Context,
        user: Optional[Union[ Member, User ]] = Author,
        _type: Literal[ "global", "server" ] = "global"
    ):
        """View the mentioned user's avatar"""

        if _type == "server":
            if isinstance(user, BaseUser):
                raise CommandError("I can't show the **server avatar** of a non-server member.")
            
            if (avatar := user.guild_avatar) is None:
                raise CommandError("That member doesn't have a **server avatar**.")

        else:
            avatar = user.display_avatar
        
        embed = (
            ctx.default_embed
            .set_color(await dominant_color(avatar))
            .set_title(f"{user.name}'s {'server ' if _type == 'server' else ''}avatar")
            .set_url(avatar.url)
            .set_image(url=avatar)
        )

        view = (
            View()
            .add_item(Button(
                style=ButtonStyle.link, 
                label="WEBP", 
                url=avatar.replace(size=4096, format="webp").url
            ))
            .add_item(Button(
                style=ButtonStyle.link, 
                label="PNG", 
                url=avatar.replace(size=4096, format="png").url
            ))
            .add_item(Button(
                style=ButtonStyle.link, 
                label="JPG", 
                url=avatar.replace(size=4096, format="jpg").url
            ))
        )

        return await ctx.reply(
            embed=embed,
            view=view
        )
    

    @Command(
        name="youngest",
        usage="[count]",
        example="15"
    )
    async def youngest(
        self: "Information", 
        ctx: Context, 
        count: Optional[int] = 5
    ):
        """View the youngest users in the server"""

        if count > 100:
            raise CommandError("I can only display up to **100 users**.")

        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Youngest Users in '{ctx.guild.name}'"
        )

        for member in sorted(ctx.guild.members, key=lambda m: m.created_at, reverse=True)[:count]:
            rows.append(f"{member} - {format_dt(member.created_at, style='R' if (Date.now().astimezone()-member.created_at).total_seconds() < 86400 else 'D')}")

        return await ctx.paginate((embed, rows))
    

    @Command(
        name="oldest",
        usage="[count]",
        example="15"
    )
    async def oldest(self: "Information", ctx: Context, count: Optional[int] = 5):
        """View the oldest users in the server"""

        if count > 100:
            raise CommandError("I can only display up to **100 users**.")

        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Oldest Users in '{ctx.guild.name}'"
        )

        for member in sorted(ctx.guild.members, key=lambda m: m.created_at)[:count]:
            rows.append(f"{member} - {format_dt(member.created_at, style='R' if (Date.now().astimezone()-member.created_at).total_seconds() < 86400 else 'D')}")

        return await ctx.paginate((embed, rows))
        
        
    @Command(
        name="roleinfo",
        aliases=("rinfo", "ri"),
        usage="<role>",
        example="@Member"
    )
    async def roleinfo(
        self: "Information",
        ctx: Context,
        *,
        role: Role
    ):
        """
        Get information on a role
        """
        
        embed = (
            ctx.default_embed
            .set_color(color := BaseColor(role.color.value or 0xb9bbbe))
            .set_title(f"{role.name} ({role.id})")
            .set_thumbnail(url="attachment://square.png")
            .add_field(
                name="Created",
                value=format_dt(role.created_at, style='R' if (Date.now().astimezone()-role.created_at).total_seconds() < 86400 else 'D')
            )
            .add_field(
                name="Members",
                value=len(role.members)
            )
            .add_field(
                name="Hoist",
                value=role.hoist
            )
            .add_field(
                name="Color",
                value=str(color)
            )
            .add_field(
                name="Mentionable",
                value=role.mentionable
            )
            .add_field(
                name="Managed",
                value=role.managed
            )
            .set_footer(text=f"{'Administrator' if role.permissions.administrator else 'Create Invite' if role.permissions.create_instant_invite else 'No Permissions'}   \u2022   Position: {role.position}   \u2022   Dangerous: {ctx.is_dangerous(role)}")
        )
        
        return await ctx.reply(
            embed=embed,
            file=File(
                ImageGenerator().single_color(color=color.to_rgb()),
                "square.png"
            )
        )
    

    @Command(
        name="screenshot",
        aliases=("ss",),
        usage="<website url>",
        example="https://discord.com",
        parameters={
            "sleep": {
                "converter": int,
                "description": "Time to wait before taking the screenshot",
                "aliases": [
                    "s",
                    "wait",
                    "delay"
                ]
            }
        }
    )
    async def screenshot(
        self: "Information",
        ctx: Context,
        url: str
    ):
        """
        Get an image of a website
        """
        
        screenshot_bytes = await self.bot.browser.screenshot(
            url, 
            not ctx.channel.nsfw,
            ctx.parameters.get("sleep")
        )
        
        with suppress(Exception):
            explicit_report = await self.bot.data_processing.determine_explicit(screenshot_bytes.read())
            screenshot_bytes.seek(0)

            if (explicit_report.nudity and not ctx.channel.nsfw) or explicit_report.gore:
                raise CommandError("I couldn't display this page; it contains explicit content.")
            
        return await ctx.send(file=File(
            screenshot_bytes, 
            f"{self.bot.user.name.title()} Screenshot.png"
        ))

    
    @Command(
        name="translate",
        aliases=("tr",),
        usage="<text>",
        example="english hola",
        parameters={
            "from": {
                "converter": str,
                "description": "Language to translate the text from",
                "aliases": [
                    "source",
                    "sl",
                ]
            },
            "to": {
                "converter": str,
                "description": "Language to translate the text to",
                "aliases": [
                    "target",
                    "tl",
                ]
            }
        }
    )
    async def translate(
        self: "Information",
        ctx: Context,
        *,
        text: str
    ):
        """
        Translate text to another language
        """

        try:
            return await ctx.reply(
                await self.bot.data_processing.translate_text(
                    text=strip_flags(text, ctx),
                    source_language=ctx.parameters.get("from") or "auto",
                    target_language=ctx.parameters.get("to") or "english"
                )
            )

        except Exception:
            raise CommandError("I couldn't translate the provided text.")
            
            
    @Group(
        name="server",
        usage="[sub command]",
        example="information",
        invoke_without_command=True
    )
    async def server(self: "Information", ctx: Context):
        """
        Commands related to the current server
        """
        
        return await ctx.invoke(self.bot.get_command("server information"))
        
        
    @server.command(
        name="information",
        aliases=("info", "i")
    )
    @bot_has_permissions(manage_guild=True)
    async def server_information(self: "Information", ctx: Context):
        """
        View information about the server
        """
        
        embed = Embed(
            color=await dominant_color(ctx.guild.icon),
            title=ctx.guild.name
        ).set_thumbnail(url=ctx.guild.icon
        ).set_footer(text=f"Server ID: {ctx.guild.id}   \u2022   Server created {arrow.get(ctx.guild.created_at).humanize()}")
        
        embed.add_field(
            name="Owner",
            value=f"> {ctx.guild.owner} ({ctx.guild.owner.mention})\n> ID: {ctx.guild.owner_id}"
        )
        
        humans = sum(
            1 for m in ctx.guild.members 
            if not m.bot
        )
        
        embed.add_field(
            name="Members",
            value=f"> Total: {ctx.guild.member_count}\n> Humans: {humans}\n> Bots: {ctx.guild.member_count-humans}"
        )
        
        embed.add_field(
            name="General",
            value=f"> Verification: {ctx.guild.verification_level.name.title()}\n> Level: {ctx.guild.premium_tier}/{ctx.guild.premium_subscription_count}\n> Large: {ctx.guild.large}"
        )
        
        embed.add_field(
            name=f"Channels ({len(ctx.guild.channels)})",
            value=f"> Category Channels: {len(ctx.guild.categories)}\n> Text Channels: {len(ctx.guild.text_channels)}\n> Voice Channels: {len(ctx.guild.voice_channels)}"
        )
        
        embed.add_field(
            name="Counts",
            value=f"> Boosters: {len(ctx.guild.premium_subscribers)}\n> Emojis: {len(ctx.guild.emojis)}\n> Roles: {len(ctx.guild.roles)}"
        )
        
        uses = 0
        vanity_code = None
        
        with suppress(Exception):
            vanity_invite = await ctx.guild.vanity_invite()
            vanity_code = ctx.guild.vanity_url_code
            uses = vanity_invite.uses
        
        embed.add_field(
            name="Invites",
            value=f"> Invites: {len(await ctx.guild.invites())}\n> Vanity Invite: {vanity_code}\n> Vanity Joins: {uses}"
        )
        
        icon = ctx.guild.icon and ctx.guild.icon.url or "https://none.none"
        banner = ctx.guild.banner and ctx.guild.banner.url or "https://none.none"
        
        view = (
            View()
            .add_item(
                Button(
                    style=ButtonStyle.link, 
                    label="Icon", 
                    url=icon, 
                    disabled=True if icon == "https://none.none" else False
                )
            )
            .add_item(
                Button(
                    style=ButtonStyle.link, 
                    label="Banner", 
                    url=banner, 
                    disabled=True if banner == "https://none.none" else False
                )
            )
        )
        
        return await ctx.reply(
            embed=embed,
            view=view
        )
        
        
    @server.command(
        name="icon",
        aliases=("image",)
    )
    async def server_icon(self: "Information", ctx: Context):
        """
        View the server's icon
        """
        
        if ctx.guild.icon is None:
            raise CommandError("This server doesn't have an icon.")
        
        embed = (
            ctx.default_embed
            .set_color(await dominant_color(ctx.guild.icon))
            .set_title(f"{ctx.guild.name}'s server icon")
            .set_url(ctx.guild.icon.url)
            .set_image(url=ctx.guild.icon.url)
        )

        view = (
            View()
            .add_item(Button(
                style=ButtonStyle.link, 
                label="WEBP", 
                url=ctx.guild.icon.replace(size=4096, format="webp").url
            ))
            .add_item(Button(
                style=ButtonStyle.link, 
                label="PNG", 
                url=ctx.guild.icon.replace(size=4096, format="png").url
            ))
            .add_item(Button(
                style=ButtonStyle.link, 
                label="JPG", 
                url=ctx.guild.icon.replace(size=4096, format="jpg").url
            ))
        )

        return await ctx.reply(
            embed=embed,
            view=view
        )
        
        
    @server.command(name="banner")
    async def server_banner(self: "Information", ctx: Context):
        """
        View the server's banner
        """
        
        if ctx.guild.banner is None:
            raise CommandError("This server doesn't have a banner.")
        
        embed = (
            ctx.default_embed
            .set_color(await dominant_color(ctx.guild.banner))
            .set_title(f"{ctx.guild.name}'s server banner")
            .set_url(ctx.guild.banner.url)
            .set_image(url=ctx.guild.banner.url)
        )

        view = (
            View()
            .add_item(Button(
                style=ButtonStyle.link, 
                label="WEBP", 
                url=ctx.guild.banner.replace(size=4096, format="webp").url
            ))
            .add_item(Button(
                style=ButtonStyle.link, 
                label="PNG", 
                url=ctx.guild.banner.replace(size=4096, format="png").url
            ))
            .add_item(Button(
                style=ButtonStyle.link, 
                label="JPG", 
                url=ctx.guild.banner.replace(size=4096, format="jpg").url
            ))
        )

        return await ctx.reply(
            embed=embed,
            view=view
        )
        
        
    @Command(
        name="avatarhistory",
        aliases=("avh", "ah", "avatars"),
        usage="[user]",
        example="@mewa"
    )
    async def avatarhistory(
        self: "Information",
        ctx: Context,
        user: Optional[User] = Author
    ):
        """View avatar history"""
        
        if (history_data := await self.bot.session.get(f"https://api.rival.rocks/avatars/{user.id}?format=json", headers={"api-key": "adminrivalkey999"})) is None:
            raise CommandError("Couldn't find any avatar history for that user.")
        
        return await ctx.success(f"Click [**here**](https://vile.bot/avatars/{user.id}) to view **{len(history_data['avatars'])}** avatars.")

    
    @Command(
        name="wolfram",
        aliases=("w", "wolframalpha"),
        usage="<query>",
        example="5 minutes -> hours"
    )
    async def wolfram(
        self: "Information",
        ctx: Context,
        *,
        query: str
    ):
        """Gets basic information about a query, like Google search"""

        data = (await self.bot.data_processing.wolfram(query))["queryresult"]

        if "pods" not in data:
            raise CommandError("I couldn't find any results.")
        
        embed = (
            ctx.default_embed
            .set_title("Wolfram Alpha")
            .set_url(f"https://www.wolframalpha.com/input/?i={'+'.join(query.split())}")
            .set_thumbnail(url="https://www.wolfram.com/homepage/img/carousel-wolfram-alpha.png")
        )

        for pod in data["pods"][:4]:
            await sleep(1e-3)

            embed.add_field(
                name=pod["title"],
                value=pod["subpods"][0]["plaintext"]
            )

        return await ctx.reply(embed=embed)
    

    @Command(
        "ipinfo",
        aliases=("ipaddr", "geoip", "addrinfo", "ip"),
        usage="<address>",
        example="127.0.0.1"
    )
    async def ipinfo(
        self: "Information",
        ctx: Context,
        address: str
    ):
        """Get information on an IP address"""

        try:
            data = await self.bot.data_processing.address_info(address)

        except (AssertionError, ValidationError):
            raise CommandError("I couldn't retrieve information on that address.")
        
        except Exception as exception:
            if str(exception).startswith("The IP address is a bogon IP."):
                return await ctx.reply(f"**This is a bogon address.**\n> Some IP addresses and IP ranges are reserved for special use, such as for local or private networks, and should not appear on the public internet. These reserved ranges, along with other IP ranges that haven't yet been allocated and therefore also shouldn't appear on the public internet are sometimes known as bogons.")

            if str(exception).startswith("You entered a value that does not appear to be a valid IP address."):
                return await ctx.reply(f"Please provide a **valid** IP address.")
        
            raise
        
        return await ctx.reply(embeds=[
            (
                ctx.default_embed
                .set_title("General Information")
                .add_field(name="IP Address", value=data.ip, inline=False)
                .add_field(name="City", value=data.location.city, inline=True)
                .add_field(name="Region", value=data.location.region, inline=True)
                .add_field(name="Country", value=data.location.country.name, inline=True)
                .add_field(name="Organization", value=data.company.name, inline=False)
                .add_field(name="Postal Code", value=data.location.postal, inline=True)
                .add_field(name="Timezone", value=data.time_zone.name, inline=True)
            ),
            (
                ctx.default_embed
                .set_title("ASN Information")
                .add_field(name="ASN", value=f"{data.connection.asn} {data.connection.organization}", inline=False)
                .add_field(name="ASN Domain", value=data.connection.domain, inline=True)
                .add_field(name="ASN Route", value=data.connection.route, inline=True)
                .add_field(name="ASN Type", value=data.connection.type, inline=True)
            ),
            (
                ctx.default_embed
                .set_title("Carrier Information")
                .add_field(name="Carrier Name", value=data.carrier.name or "N/A", inline=False)
                .add_field(name="MCC", value=data.carrier.mcc or "N/A", inline=True)
                .add_field(name="MNC", value=data.carrier.mnc or "N/A", inline=True)
            ),
            (
                ctx.default_embed
                .set_title("Currency Information")
                .add_field(name="Currency Code", value=data.currency.code, inline=False)
                .add_field(name="Currency Name", value=data.currency.name, inline=True)
                .add_field(name="Currency Symbol", value=data.currency.symbol, inline=True)
            ),
            (
                ctx.default_embed
                .set_title("Location Information")
                .add_field(name="Continent", value=data.location.continent.name, inline=False)
                .add_field(name="Country", value=data.location.country.name, inline=True)
                .add_field(name="Region", value=data.location.region.name, inline=True)
                .add_field(name="City", value=data.location.city, inline=True)
                .add_field(name="Postal Code", value=data.location.postal, inline=True)
            ),
            (
                ctx.default_embed
                .set_title("Security Information")
                .add_field(name="Is Abuser", value="Yes" if data.security.is_abuser else "No", inline=True)
                .add_field(name="Is Attacker", value="Yes" if data.security.is_attacker else "No", inline=True)
                .add_field(name="Is Bogon", value="Yes" if data.security.is_bogon else "No", inline=True)
                .add_field(name="Is Cloud Provider", value="Yes" if data.security.is_cloud_provider else "No", inline=True)
                .add_field(name="Is Proxy", value="Yes" if data.security.is_proxy else "No", inline=True)
                .add_field(name="Is Relay", value="Yes" if data.security.is_relay else "No", inline=True)
                .add_field(name="Is TOR", value="Yes" if data.security.is_tor else "No", inline=True)
                .add_field(name="Is TOR Exit", value="Yes" if data.security.is_tor_exit else "No", inline=True)
                .add_field(name="Is VPN", value="Yes" if data.security.is_vpn else "No", inline=True)
                .add_field(name="Is Anonymous", value="Yes" if data.security.is_anonymous else "No", inline=True)
                .add_field(name="Is Threat", value="Yes" if data.security.is_threat else "No", inline=True)
            ),
            (
                ctx.default_embed
                .set_title("Timezone Information")
                .add_field(name="Timezone ID", value=data.time_zone.id, inline=False)
                .add_field(name="Timezone Abbreviation", value=data.time_zone.abbreviation, inline=True)
                .add_field(name="Current Time", value=data.time_zone.current_time, inline=True)
                .add_field(name="Timezone Name", value=data.time_zone.name, inline=True)
                .add_field(name="Offset", value=data.time_zone.offset, inline=True)
                .add_field(name="In Daylight Saving", value="Yes" if data.time_zone.in_daylight_saving else "No", inline=True)
            )
        ])


async def setup(bot: "VileBot") -> NoReturn:
    """
    Add the Information cog to the bot.

    Parameters:
        bot (VileBot): An instance of the VileBot class.
    """

    await bot.add_cog(Information(bot))
