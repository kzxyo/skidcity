import discord, aiohttp, io
from io import BytesIO

def get_parts(params):
    params=params.replace('{embed}', '')
    return [p[1:][:-1] for p in params.split('$v')]

async def to_object(params):

    x={}
    fields=[]
    content=None
    view=discord.ui.View()

    for part in get_parts(params):
        if part.startswith('attach:'):
            async with aiohttp.ClientSession() as session:
                async with session.get(file) as resp:
                    object = io.BytesIO(await resp.read())
            file= discord.File(object, filename="wonder.png")

        if part.startswith('content:'):
            content=part[len('content:'):]
            
        if part.startswith('title:'):
            x['title']=part[len('title:'):]
        
        if part.startswith('description:'):
            x['description']=part[len('description:'):]

        if part.startswith('footer:'):
            x['footer']=part[len('footer:'):]

        if part.startswith('color:'):
            try:
                x['color']=int(part[len('color:'):].strip('#').strip(), 16)
            except:
                x['color']=0x2f3136

        if part.startswith('image:'):
            x['image']={'url': part[len('image:'):]}

        if part.startswith('thumbnail:'):
            x['thumbnail']={'url': part[len('thumbnail:'):]}
        
        if part.startswith('author:'):
            z=part[len('author:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            try:
                url=z[2] if z[2] else None
            except:
                url=None

            x['author']={'name': name}
            if icon_url:
                x['author']['icon_url']=icon_url
            if url:
                x['author']['url']=url

        if part.startswith('field:'):
            z=part[len('field:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                value=z[1] if z[1] else None
            except:
                value=None
            try:
                inline=z[2] if z[2] else True
            except:
                inline=True

            if isinstance(inline, str):
                if inline == 'true':
                    inline=True

                elif inline == 'false':
                    inline=False

            fields.append({'name': name, 'value': value, 'inline': inline})

        if part.startswith('footer:'):
            z=part[len('footer:'):].split(' && ')
            try:
                text=z[0] if z[0] else None
            except:
                text=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            x['footer']={'text': text}
            if icon_url:
                x['footer']['icon_url']=icon_url
                
        if part.startswith('button:'):
            z=part[len('button:'):].split(' && ')
            try:
                label=z[0] if z[0] else None
            except:
                label='no label'
            try:
                url=z[1] if z[1] else None
            except:
                url='https://none.none'
            try:
                emoji=z[2] if z[2] else None
            except:
                emoji=None
                
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=label, url=url, emoji=emoji))


    if not x: embed=None
    else:
        x['fields']=fields
        embed=discord.Embed.from_dict(x)
    return content, embed, view


async def embed_replacement(user, params):

    if '{user}' in params:
        params=params.replace('{user}', user)
    if '{user.mention}' in params:
        params=params.replace('{user.mention}', user.mention)
    if '{user.name}' in params:
        params=params.replace('{user.name}', user.name)
    if '{user.avatar}' in params:
        params=params.replace('{user.avatar}', user.display_avatar.url)
    if '{user.joined_at}' in params:
        params=params.replace('{user.joined_at}', discord.utils.format_dt(user.joined_at, style='R'))
    if '{user.created_at}' in params:
        params=params.replace('{user.created_at}', discord.utils.format_dt(user.created_at, style='R'))
    if '{user.discriminator}' in params:
        params=params.replace('{user.discriminator}', user.discriminator)
    if '{guild.name}' in params:
        params=params.replace('{guild.name}', user.guild.name)
    if '{guild.count}' in params:
        params=params.replace('{guild.count}', str(user.guild.member_count))
    if '{guild.count.format}' in params:
        params=params.replace('{guild.count.format}', ordinal(len(user.guild.members)))
    if '{guild.id}' in params:
        params=params.replace('{guild.id}', user.guild.id)
    if '{guild.created_at}' in params:
        params=params.replace('{guild.created_at}', discord.utils.format_dt(user.guild.created_at, style='R'))
    if '{guild.boost_count}' in params:
        params=params.replace('{guild.boost_count}', str(user.guild.premium_subscription_count))
    if '{guild.booster_count}' in params:
        params=params.replace('{guild.booster_count}', str(len(user.guild.premium_subscribers)))
    if '{guild.boost_count.format}' in params:
        params=params.replace('{guild.boost_count.format}', ordinal(str(len(user.guild.premium_subscriber_count))))
    if '{guild.booster_count.format}' in params:
        params=params.replace('{guild.booster_count.format}', ordinal(str(len(user.guild.premium_subscriber_count))))
    if '{guild.boost_tier}' in params:
        params=params.replace('{guild.boost_tier}', str(user.guild.premium_tier))
    if '{guild.icon}' in params:
        if user.guild.icon:
            params=params.replace('{guild.icon}', user.guild.icon.url)
        else:
            params=params.replace('{guild.icon}', '')
    return params

async def get_user_info(user: str):
    async with aiohttp.ClientSession() as cs:
     async with cs.get(f"https://ws.audioscrobbler.com/2.0/?method=user.getInfo&user={user}&api_key=e739760b740efae08aeef62f0e15d7b7&format=json") as response:
       z = await response.json()
       return z

def Sort_Tuple(tup):
    return(reversed(sorted(tup, key = lambda x: x[1])))


async def file(url: str, fn: str=None, filename: str=None):

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                data=await r.read()

        fileName=''
        if not fn and not filename:
            fileName='image.png'
        elif not fn and filename:
            fileName=filename
        elif not filename and fn:
            fileName=fn
        elif filename and fn:
            return

        return discord.File(io.BytesIO(data), filename=fileName)