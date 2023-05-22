import discord, json, datetime, typing, aiohttp, difflib, asyncio, sys, io, os, humanize, pathlib, importlib, inspect
from pathlib import Path
from datetime import datetime, timezone, timedelta
from .paginator import Paginator
from discord.ext import commands
from threading import Thread
import requests, random, yarl

paginator = Paginator


class ArgError(Exception):

    """Exception that's thrown when
    an argument is invalid in some
    way or not given inside a function"""

    pass


class UnexpectedError(Exception):

    """Exception that's thrown when
    an argument is unexpected inside a function"""

    pass


def intword(num: int):

    """Get the string
    version of an
    integer"""

    if not num:
        raise ArgError("missing required arguments")
        return
    else:
        return humanize.intword(num).replace(".0", "")


class Database:
    def get(self, filename: str = None):

        with open(f"{sys.path[0]}/db/{filename}.json", "r") as file:
            data = json.load(file)
        file.close()
        return data

    def put(self, data, filename: str = None):

        with open(f"{sys.path[0]}/db/{filename}.json", "w") as file:
            json.dump(data, file, indent=4)
        file.close()
        return


def read_json(filename: str):
    return Database().get(filename)


def write_json(data, filename: str):
    return Database().put(data, filename)


# def moment(time):
#
#   """Get the
#  .fromNow() from
# a datetime.datetime"""
#
# if not time: raise ArgError('missing required arguments') ; return
# from datetime import timedelta
# created = time
# now = datetime.now().astimezone()
# delta = (now - created)
# minutes = timedelta(days=delta.days, seconds=int(delta.seconds)) / timedelta(minutes=1)
# days = delta.days
# hours = delta / timedelta(hours=1)
# seconds = delta.total_seconds()
# years = delta / timedelta(days=365)
# weeks = delta / timedelta(days=7)
# months = delta / timedelta(days=30)
# if seconds <= 60:
#   ret = "a few seconds ago"
# elif int(minutes) <= 60:
#   ret = f"{int(minutes)} minute{'s' if int(minutes) != 1 else ''} ago"
# elif hours <= 24:
#   ret = f"{int(hours)} hour{'s' if int(hours) != 1 else ''} ago"
# elif days <= 30:
#   ret = f"{int(days)} day{'s' if int(days) != 1 else ''} ago"
# elif months >= 1 and months < 12:
#   ret = f"{int(months)} month{'s' if int(months) != 1 else ''} ago"
# else:
#   ret = f"{int(years)} year{'s' if int(years) != 1 else ''} ago"
#
# return ret


def color(clr: str):

    """Get the color for
    your desired emoji"""

    if not clr:
        raise ArgError("missing required arguments")
        return
    if clr == "main":
        return eval(f"0x{read_json('colors')['main']}")
    elif clr == "done":
        return eval(f"0x{read_json('colors')['done']}")
    elif clr == "warn":
        return eval(f"0x{read_json('colors')['warn']}")
    elif clr == "fail":
        return eval(f"0x{read_json('colors')['fail']}")
    else:
        raise UnexpectedError("unexpected argument")
        return


def emoji(em: str):

    """Get the desired emoji"""

    if not em:
        raise ArgError("missing required arguments")
        return
    return read_json("emojis")[em]


def moment(t: datetime, accuracy=1, separator: str = ", "):
    """
    :param t : Time in seconds
    :returns : Formatted string
    """

    t = datetime.now().timestamp() - t.timestamp()
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    y, d = divmod(d, 365)

    components = []
    if y > 0:
        components.append(f"{int(y)} year" + ("s" if y != 1 else ""))
    if d > 0:
        components.append(f"{int(d)} day" + ("s" if d != 1 else ""))
    if h > 0:
        components.append(f"{int(h)} hour" + ("s" if h != 1 else ""))
    if m > 0:
        components.append(f"{int(m)} minute" + ("s" if m != 1 else ""))
    if s > 0:
        components.append(f"{int(s)} second" + ("s" if s != 1 else ""))

    return ", ".join(components[:accuracy])


import psutil
import math


def size(size_in_bytes: int) -> str:
    """
    Converts a number of bytes to an appropriately-scaled unit
    E.g.:
        1024 -> 1.00 KiB
        12345678 -> 11.77 MiB
    """
    units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    power = int(math.log(max(abs(size_in_bytes), 1), 1024))

    return (
        f"{size_in_bytes / (1024 ** power):.2f}{units[power]}".replace("KiB", "KB")
        .replace("MiB", "MB")
        .replace("GiB", "GB")
        .replace("TiB", "TB")
        .replace("PiB", "PB")
        .replace("ZiB", "ZB")
        .replace("YiB", "YB")
    )


def restart():
    os.execv(sys.executable, ["python"] + sys.argv)


async def help(ctx):

    cmd = ctx.bot.get_command(str(ctx.invoked_with))

    embed = discord.Embed(color=color("main"))
    embed.set_author(name=f"Command: {cmd.name}", icon_url=ctx.bot.user.display_avatar)
    embed.set_footer(text=f"Module: {cmd.cog_name}")
    embed.set_thumbnail(url="attachment://vile.png")

    embed.add_field(
        name="Description", value=f"{'N/A' if not cmd.description else cmd.description}"
    )

    embed.add_field(
        name="Aliases",
        value=f"{'N/A' if not cmd.aliases else cmd.aliases}",
        inline=True,
    )

    embed.add_field(
        name="Usage",
        value=f"""```{'N/A' if not cmd.brief or not cmd.usage else f'''{cmd.usage}
{cmd.brief}'''}```""",
        inline=False,
    )

    await ctx.reply(embed=embed, file=discord.File("vile.png"))


def perms(perm: str = None):
    async def predicate(ctx):
        num = 0
        currentperms = ctx.author.guild_permissions
        fakeperms = read_json("fakepermissions")
        try:
            torun = eval(f"currentperms.{perm}")
            if torun == True:
                num += 1
        except:
            pass
        try:
            async for role in aiter(ctx.author.roles):
                try:
                    if perm in fakeperms[str(ctx.guild.id)][str(role.id)]:
                        num += 1
                except:
                    pass
        except:
            pass
        if num != 0:
            return True

        raise discord.ext.commands.MissingPermissions([perm])

    return discord.ext.commands.check(predicate)


async def file(url: str, fn: str = None, filename: str = None):

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.read()

    fileName = ""
    if not fn and not filename:
        fileName = "image.png"
    elif not fn and filename:
        fileName = filename
    elif not filename and fn:
        fileName = fn
    elif filename and fn:
        return

    return discord.File(io.BytesIO(data), filename=fileName)


async def send_pages(
    ctx: discord.ext.commands.Context, embed: discord.Embed, rows: list
):

    embeds = []
    pages = [p async for p in aiter(discord.utils.as_chunks(rows, 10))]
    for page in pages:
        em = embed
        em.description = "\n".join(pages)
        embeds.append(em)
    paginator = Paginator(ctx.bot, embeds, ctx, invoker=None, timeout=30)
    paginator.add_button("prev", emoji=emoji("prevpage"))
    paginator.add_button("goto", emoji=emoji("choosepage"))
    paginator.add_button("next", emoji=emoji("nextpage"))
    await paginator.start()


def query_roles(guild: discord.Guild, query: str = None, limit: int = 1):

    roles = []

    rs = [role.name.lower() for role in guild.roles if role.is_assignable()]
    closest = difflib.get_close_matches(query.lower(), rs, n=3, cutoff=0.5)
    if closest:
        for r in guild.roles:
            if r.name.lower() == closest[0].lower():
                roles.append(r)

    return roles[:limit]


def query_members(guild: discord.Guild, query: str = None, limit: int = 1):

    members = []

    ms = [member.name.lower() for member in guild.members]
    closest = difflib.get_close_matches(query.lower(), ms, n=3, cutoff=0.5)
    if closest:
        for r in guild.members:
            if r.name.lower() == closest[0].lower():
                members.append(r)

    return members[:limit]


def query_guilds(bot, query: str = None, limit: int = 1):

    guilds = []

    gs = [guild.name.lower() for guild in bot.guilds]
    closest = difflib.get_close_matches(query.lower(), gs, n=3, cutoff=0.5)
    if closest:
        for g in bot.guilds:
            if g.name.lower() == closest[0].lower():
                guilds.append(g)

    return guilds[:limit]


def query_channels(guild: discord.Guild, query: str = None, limit: int = 1):

    channels = []

    ms = [channel.name.lower() for channel in guild.channels]
    closest = difflib.get_close_matches(query.lower(), ms, n=3, cutoff=0.5)
    if closest:
        for c in guild.channels:
            if c.name.lower() == closest[0].lower():
                channels.append(c)

    return channels[:limit]


async def query_bans(guild: discord.Guild, query: str = None, limit: int = 1):

    bans = []

    bs = [ban.user.name.lower() async for ban in guild.bans()]
    closest = difflib.get_close_matches(query.lower(), bs, n=3, cutoff=0.5)
    if closest:
        for b in [ban async for ban in guild.bans()]:
            if b.user.name.lower() == closest[0].lower():
                bans.append(b)

    return bans[:limit]


def ordinal(n):

    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4])


async def getwhi(query):

    url = f"https://weheartit.com/search/entries?query={query.replace(' ', '+')}"
    from bs4 import BeautifulSoup

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as x:
            soup = BeautifulSoup(await x.text(), features="html.parser")
            divs = str(soup.find_all("div", class_="entry grid-item"))
            soup2 = BeautifulSoup(divs, features="html.parser")
            badge = soup2.find_all(class_="entry-badge")
            images = soup2.find_all("img")
            links = []
            async for image in aiter(images):
                if "data.whicdn.com/images/" in str(image):
                    links.append(image["src"])
    return links


async def getwhiuser(query):

    url = f"https://weheartit.com/{query.replace(' ', '+')}"
    from bs4 import BeautifulSoup

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as x:
            soup = BeautifulSoup(await x.text(), features="html.parser")
            divs = str(soup.find_all("div", class_="entry grid-item"))
            soup2 = BeautifulSoup(divs, features="html.parser")
            badge = soup2.find_all(class_="entry-badge")
            images = soup2.find_all("img")
            links = []
            async for image in aiter(images):
                if "data.whicdn.com/images/" in str(image):
                    links.append(image["src"])
    return links


def get_xp(level):
    return math.ceil(math.pow((level - 1) / (0.05 * (1 + math.sqrt(5))), 2))


def get_level(xp):
    return math.floor(0.05 * (1 + math.sqrt(5)) * math.sqrt(xp)) + 1


def xp_to_next_level(level):
    return get_xp(level + 1) - get_xp(level)


def xp_from_message(message: discord.Message):
    words = message.content.split(" ")
    eligible_words = 0
    for x in words:
        if len(x) > 1:
            eligible_words += 1
    xp = eligible_words + (10 * len(message.attachments))
    if xp == 0:
        xp = 1

    return min(xp, 50)


def get_parts(params):
    params = params.replace("{embed}", "")
    return [p[1:][:-1] for p in params.split("$v")]


async def to_object(params):

    x = {}
    fields = []
    content = None
    timestamp=None
    files = []
    view = discord.ui.View()

    async for part in aiter(get_parts(params)):

        if part.startswith("content:"):
            content = part[len("content:") :]

        if part.startswith("url:"):
            x["url"] = part[len("url:") :]

        if part.startswith("title:"):
            x["title"] = part[len("title:") :]

        if part.startswith("description:"):
            x["description"] = part[len("description:") :]

        if part.startswith("footer:"):
            x["footer"] = part[len("footer:") :]

        if part.startswith("color:"):
            try:
                x["color"] = int(part[len("color:") :].replace(' ', '').replace('#', ''), 16)
            except:
                x["color"] = 0x2F3136

        if part.startswith("image:"):
            x["image"] = {"url": part[len("description:") :]}

        if part.startswith("thumbnail:"):
            x["thumbnail"] = {"url": part[len("thumbnail:") :]}

        if part.startswith("attach:"):
            async with aiohttp.ClientSession() as session:
                async with session.get(part[len("attach:") :].replace(' ', '')) as resp:
                    balls = await resp.read()
            files.append(
                discord.File(io.BytesIO(balls), yarl.URL(part[len("attach:") :].replace(' ', '')).name)
            )

        if part.startswith("author:"):
            z = part[len("author:") :].split(" && ")
            icon_url=None
            url=None
            for p in z[1:]:
                if p.startswith('icon:'):
                    p=p[len('icon:') :]
                    icon_url=p.replace(' ', '')
                elif p.startswith('url:'):
                    p=p[len('url:') :]
                    url=p.replace(' ', '')
            try:
                name = z[0] if z[0] else None
            except:
                name = None

            x["author"] = {"name": name}
            if icon_url:
                x["author"]["icon_url"] = icon_url
            if url:
                x["author"]["url"] = url

        if part.startswith("field:"):
            z = part[len("field:") :].split(" && ")
            value=None
            inline='true'
            for p in z[1:]:
                if p.startswith('value:'):
                    p=p[len('value:') :]
                    value=p
                elif p.startswith('inline:'):
                    p=p[len('inline:') :]
                    inline=p.replace(' ', '')
            try:
                name = z[0] if z[0] else None
            except:
                name = None
            
            if isinstance(inline, str):
                if inline == "true":
                    inline = True

                elif inline == "false":
                    inline = False

            fields.append({"name": name, "value": value, "inline": inline})

        if part.startswith("footer:"):
            z = part[len("footer:") :].split(" && ")
            text=None
            icon_url=None
            for p in z[1:]:
                if p.startswith('icon:'):
                    p=p[len('icon:') :]
                    icon_url=p.replace(' ', '')
            try:
                text = z[0] if z[0] else None
            except:
                pass
                
            x["footer"] = {"text": text}
            if icon_url:
                x["footer"]["icon_url"] = icon_url

        if part.startswith("label:"):
            z = part[len("label:") :].split(" && ")
            labrl='no label'
            url=None
            for p in z[1:]:
                if p.startswith('link:'):
                    p=p[len('link:') :]
                    url=p.replace(' ', '')
                    
            try:
                label = z[0] if z[0] else None
            except:
                pass
                

            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link, label=label, url=url
                )
            )
            
        if part.startswith('image:'):
            z=part[len('image:') :]
            x['image']={'url': z}
            
        if part.startswith('timestamp:'):
            z=part[len('timestamp:') :].replace(' ', '')
            if z == 'true':
                timestamp=True
                
    if not x:
        embed = None
    else:
        x["fields"] = fields
        embed = discord.Embed.from_dict(x)

    if not params.count("{") and not params.count("}"):
        content = params
        
    if timestamp:
        embed.timestamp=datetime.now(__import__('pytz').timezone('America/New_York'))

    return {"content": content, "embed": embed, "files": files, "view": view}


def get_partss(params):
    x = {}
    notembed, embed = params.split("{extra}")[0].split("{embed}")
    x["notembed"] = [p[1:][:-1] for p in notembed.split("$v")]
    x["embed"] = [p[1:][:-1] for p in embed.split("$v")]
    x["extra"] = [p for p in params.split("{extra}")[1].split()]
    return x


async def to_objectt(params):

    x = {}
    parts = get_partss(params)
    fields = []
    content = None
    files = []
    view = discord.ui.View()

    for part in parts["notembed"]:

        if part.startswith("content:"):
            content = part[len("content:") :]

        if part.startswith("button:"):
            z = part[len("button:") :].split(" && ")
            try:
                label = z[0] if z[0] else None
            except:
                label = "no label"
            try:
                url = z[1] if z[1] else None
            except:
                url = "https://none.none"
            try:
                emoji = z[2] if z[2] else None
            except:
                emoji = None

            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link, label=label, url=url, emoji=emoji
                )
            )

    for part in parts["embed"]:

        if part.startswith("url:"):
            x["url"] = part[len("url:") :]

        if part.startswith("title:"):
            x["title"] = part[len("title:") :]

        if part.startswith("description:"):
            x["description"] = part[len("description:") :]

        if part.startswith("footer:"):
            x["footer"] = part[len("footer:") :]

        if part.startswith("color:"):
            try:
                x["color"] = int(part[len("color:") :].strip("#").strip(), 16)
            except:
                x["color"] = 0x2F3136

        if part.startswith("image:"):
            x["image"] = {"url": part[len("description:") :]}

        if part.startswith("thumbnail:"):
            x["thumbnail"] = {"url": part[len("thumbnail:") :]}

        if part.startswith("attach:"):
            async with aiohttp.ClientSession() as session:
                async with session.get(part[len("attach:") :]) as resp:
                    balls = await resp.read()
            files.append(
                discord.File(io.BytesIO(balls), yarl.URL(part[len("attach:") :]).name)
            )

        if part.startswith("author:"):
            z = part[len("author:") :].split(" && ")
            try:
                name = z[0] if z[0] else None
            except:
                name = None
            try:
                icon_url = z[1] if z[1] else None
            except:
                icon_url = None
            try:
                url = z[2] if z[2] else None
            except:
                url = None

            x["author"] = {"name": name}
            if icon_url:
                x["author"]["icon_url"] = icon_url
            if url:
                x["author"]["url"] = url

        if part.startswith("field:"):
            z = part[len("field:") :].split(" && ")
            try:
                name = z[0] if z[0] else None
            except:
                name = None
            try:
                value = z[1] if z[1] else None
            except:
                value = None
            try:
                inline = z[2] if z[2] else True
            except:
                inline = True

            if isinstance(inline, str):
                if inline == "true":
                    inline = True

                elif inline == "false":
                    inline = False

            fields.append({"name": name, "value": value, "inline": inline})

        if part.startswith("footer:"):
            z = part[len("footer:") :].split(" && ")
            try:
                text = z[0] if z[0] else None
            except:
                text = None
            try:
                icon_url = z[1] if z[1] else None
            except:
                icon_url = None
            x["footer"] = {"text": text}
            if icon_url:
                x["footer"]["icon_url"] = icon_url

    if not x:
        embed = None
    else:
        x["fields"] = fields
        embed = discord.Embed.from_dict(x)

    if not params.count("{") and not params.count("}"):
        content = params

    return (
        {"content": content, "embed": embed, "files": files, "view": view},
        parts["extra"],
    )


async def embed_replacement(user, params):

    if "{user}" in params:
        params = params.replace("{user}", user)
    if "{user.mention}" in params:
        params = params.replace("{user.mention}", user.mention)
    if "{user.name}" in params:
        params = params.replace("{user.name}", user.name)
    if "{user.avatar}" in params:
        params = params.replace("{user.avatar}", user.display_avatar.url)
    if "{user.joined_at}" in params:
        params = params.replace(
            "{user.joined_at}", discord.utils.format_dt(user.joined_at, style="R")
        )
    if "{user.created_at}" in params:
        params = params.replace(
            "{user.created_at}", discord.utils.format_dt(user.created_at, style="R")
        )
    if "{user.discriminator}" in params:
        params = params.replace("{user.discriminator}", user.discriminator)
    if "{guild.name}" in params:
        params = params.replace("{guild.name}", user.guild.name)
    if "{guild.count}" in params:
        params = params.replace("{guild.count}", str(user.guild.member_count))
    if "{guild.count.format}" in params:
        params = params.replace(
            "{guild.count.format}", ordinal(len(user.guild.members))
        )
    if "{guild.id}" in params:
        params = params.replace("{guild.id}", user.guild.id)
    if "{guild.created_at}" in params:
        params = params.replace(
            "{guild.created_at}",
            discord.utils.format_dt(user.guild.created_at, style="R"),
        )
    if "{guild.boost_count}" in params:
        params = params.replace(
            "{guild.boost_count}", str(user.guild.premium_subscription_count)
        )
    if "{guild.booster_count}" in params:
        params = params.replace(
            "{guild.booster_count}", str(len(user.guild.premium_subscribers))
        )
    if "{guild.boost_count.format}" in params:
        params = params.replace(
            "{guild.boost_count.format}",
            ordinal(str(len(user.guild.premium_subscriber_count))),
        )
    if "{guild.booster_count.format}" in params:
        params = params.replace(
            "{guild.booster_count.format}",
            ordinal(str(len(user.guild.premium_subscriber_count))),
        )
    if "{guild.boost_tier}" in params:
        params = params.replace("{guild.boost_tier}", str(user.guild.premium_tier))
    if "{guild.icon}" in params:
        if user.guild.icon:
            params = params.replace("{guild.icon}", user.guild.icon.url)
        else:
            params = params.replace("{guild.icon}", "")
    return params


async def too_objectt(user, params):
    params = params.replace("{embed}", "")
    em = discord.Embed()
    if not params.count("}"):
        if not params.count("{"):
            em.description = params


async def send_help(ctx):

    done = emoji("done")
    fail = emoji("fail")
    warn = emoji("warn")
    reply = emoji("reply")
    dash = emoji("dash")
    success = color("done")
    error = color("fail")
    warning = color("warn")

    if isinstance(ctx.command, commands.Command):
        embed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
        embed.set_footer(
            text=ctx.command.cog_name,
            icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
        )
        embed.set_author(
            name=f'{" ".join([p.name async for p in aiter(ctx.command.parents)])} {ctx.command.name}',
            icon_url=ctx.bot.user.display_avatar,
        )
        embed.add_field(
            name=f"{dash} Info",
            value=f"{reply} **description:** {ctx.command.description if ctx.command.description else 'none'}\n{reply} **aliases:** {', '.join(ctx.command.aliases) if ctx.command.aliases else 'none'}",
            inline=False,
        )
        embed.add_field(
            name=f"{dash} Usage",
            value=f"{reply} syntax: {ctx.prefix if ctx.command.brief else ''}{ctx.command.brief if ctx.command.brief else 'none'}\n{reply} example: {ctx.prefix if ctx.command.help else ''}{ctx.command.help if ctx.command.help else 'none'}",
            inline=False,
        )
        return await ctx.reply(embed=embed)

    elif isinstance(ctx.command, commands.Group) or isinstance(
        ctx.command, commands.HybridGroup
    ):

        embeds = []
        async for cmd in aiter(ctx.command.commands):
            embed = discord.Embed(color=0x2F3136, timestamp=datetime.now())
            embed.set_footer(
                text=ctx.command.cog_name,
                icon_url="https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless",
            )
            embed.set_author(
                name=f"{cmd.full_parent_name} {cmd.name}",
                icon_url=ctx.bot.user.display_avatar,
            )
            embed.add_field(
                name=f"{dash} Info",
                value=f"{reply} **description:** {cmd.description if cmd.description else 'none'}\n{reply} **aliases:** {', '.join(ctx.command.aliases) if ctx.command.aliases else 'none'}",
                inline=False,
            )
            embed.add_field(
                name=f"{dash} Usage",
                value=f"{reply} syntax: {ctx.prefix if cmd.brief else ''}{cmd.brief if cmd.brief else 'none'}\n{reply} example: {ctx.prefix if cmd.help else ''}{cmd.help if cmd.help else 'none'}",
                inline=False,
            )
            embeds.append(embed)

        paginator = paginator(ctx.bot, embeds, ctx, timeout=30, invoker=None)
        paginator.add_button("first", emoji=emoji("firstpage"))
        paginator.add_button("prev", emoji=emoji("prevpage"))
        paginator.add_button("next", emoji=emoji("nextpage"))
        paginator.add_button("last", emoji=emoji("lastpage"))
        paginator.add_button("goto", emoji=emoji("choosepage"))
        return await paginator.start()


async def aiter(
    iterable: typing.Iterator[typing.Any],
) -> typing.AsyncIterator[typing.Any]:
    for i in iterable:
        yield i


async def source(objectt: object):

    x, _ = inspect.getsourcelines(objectt)
    return "".join(x)


async def reload(files: list):

    async for file in aiter(files):
        importlib.reload(file)

    return


async def send2(ctx, content: str, limit: int = 5):

    x = f"https://discord.com/api/v10/channels/{ctx.channel.id}/messages"

    def pp():
        requests.post(
            x,
            data={"content": content},
            headers={"Authorization": f"Bot {read_json('config')['token']}"},
        )

    async for i in aiter(range(5)):
        Thread(target=pp).start()


async def pack(ctx, packs, user, limit: int = 5):

    x = f"https://discord.com/api/v10/channels/{ctx.channel.id}/messages"

    def pp():
        requests.post(
            x,
            data={"content": f"{random.choice(packs)} {user.mention}"},
            headers={"Authorization": f"Bot {read_json('config')['token']}"},
        )

    async for i in aiter(range(limit)):
        Thread(target=pp).start()


class obj(object):
    def __init__(self, *args, **kwargs):
        for arg in args:
            self.__dict__.update(arg)

        self.__dict__.update(kwargs)

    def __getitem__(self, name):
        return self.__dict__.get(name, None)

    def __setitem__(self, name, val):
        return self.__dict__.__setitem__(name, val)

    def __delitem__(self, name):
        if self.__dict__.has_key(name):
            del self.__dict__[name]

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __setattr__(self, name, val):
        return self.__setitem__(name, val)

    def __delattr__(self, name):
        return self.__delitem__(name)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __repr__(self):
        return self.__dict__.__repr__()

    def __str__(self):
        return self.__dict__.__str__()

async def domcolor(url: str):
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            'https://api.rival.rocks/media/color',
            headers={
                'api-key': '48108339-2e9e-4bab-bae5-55cf5d63bfec'
            },
            params={
                'url': url
            }
        ) as resp:
            return int(eval(await resp.text()), 16)

class MessageSnipe:
    
    def __init__(self, bot=None, author: discord.Member=None, msg: discord.Message=None, timestamp=None):
        
        self._author_color=0x2f3136 if not author.color else author.color
        self._sender=msg.author
        self._content=msg.clean_content
        self._guild_id=msg.guild.id
        self._channel_id=msg.channel.id
        self._message_id=msg.id
        self._reference=msg.reference
        self._attachments=msg.attachments
        self._embeds=msg.embeds
        self._timestamp=moment(msg.created_at if not timestamp else timestamp)
        self._bot=bot
        
    @property
    def sender(self):
        return self._sender
    
    @property
    def user(self):
        return self.sender
        
    @property
    def content(self) -> str:
        return discord.utils.remove_markdown(self._content)
        
    @property
    def timestamp(self) -> float:
        return self._timestamp
        
    @property
    def bot(self):
        return self._bot
        
    @property
    def guild_id(self) -> int:
        return self._guild_id
        
    @property
    def channel_id(self) -> int:
        return self._channel_id
    
    @property
    def reference(self) -> typing.Optional[discord.MessageReference]:
        return self._reference
        
    @property
    def reference_url(self) -> typing.Optional[str]:
        if self.reference:
            return self.reference.jump_url
            
    @property
    def attachments(self) -> list[discord.Attachment]:
        return self._attachments
        
    @property
    def embeds(self) -> list[discord.Embed]:
        return self._embeds
        
    @property
    def has_embeds(self) -> bool:
        return len(self.embeds) > 0
        
    @property
    def has_attachments(self) -> bool:
        return len(self.attachments) > 0
        
    @property
    def embed(self) -> discord.Embed:
        
        embed=discord.Embed(
            color=self._author_color, 
            description=self.content
        )
        embed.set_author(
            name=self.sender.display_name,
            icon_url=self.sender.display_avatar.url
        )
        embed.set_footer(
            text=f'deleted {self.timestamp} ago',
            icon_url=self.bot.footerIcon
        )
        
        if self.has_attachments:
            
            embed.description+='\n\n'
            for attachment in self.attachments:
                embed.description+=attachment.url 
            
            for attachment in self.attachments:
                embed.set_image(url=attachment.proxy_url)
                break
        
        return embed