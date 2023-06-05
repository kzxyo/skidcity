import discord, aiohttp, asyncio, datetime, io, yarl
from discord.ui import Button, View
from io import BytesIO

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

    for part in get_parts(params):

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
            label='no label'
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