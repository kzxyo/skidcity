import aiohttp
from discord.ext import commands
import discord
import yarl
from io import BytesIO
import datetime
import pytz
from typing import Union

async def async_dl(url, headers=None, params=None, ssl=None):
    total_size=0
    data=b''
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params, ssl=ssl) as response:
            assert response.status == 200
            while True:
                chunk=await response.content.read(4*1024)
                data += chunk
                total_size += len(chunk)
                if not chunk:
                    break
                if total_size > 500000000:
                    return None
    return data

async def async_read(url, headers=None, params=None, ssl=None):
    return await async_dl(url, headers, params, ssl)
    
read = async_read

def get_parts(code: str):
    """
    :param code : Embed code using custom format
    :returns  : A list of parts
    """
    
    params = code.replace('{embed}', '')
    return [p[1:][:-1] for p in params.split('$v')]

async def to_object(code: str):
    """
    :param code : Embed code using custom format
    :returns  : A dict meant to be used with `ctx.send` and/or `ctx.reply`
    """
    
    embed = {}
    fields = []
    content = None
    timestamp = None
    files = []
    delete=None
    view = discord.ui.View()

    for part in get_parts(code):

        if part.startswith('content:'):
            content = part[len('content:'):]

        if part.startswith('url:'):
            embed['url'] = part[len('url:'):]

        if part.startswith('title:'):
            embed['title'] = part[len('title:'):]

        if part.startswith('delete:'):
            if part[len('delete:'):].strip().isdigit():
                delete=int(part[len('delete:'):].strip())

        if part.startswith('description:'):
            embed['description'] = part[len('description:'):]

        if part.startswith('footer:'):
            embed['footer'] = part[len('footer:'):]

        if part.startswith('color:'):
            try:
                embed['color'] = int(part[len('color:'):].strip().strip('#'), 16)
            except:
                embed['color'] = 0x2f3136

        if part.startswith('image:'):
            embed['image'] = {'url': part[len('description:'):]}

        if part.startswith("thumbnail:"):
            embed['thumbnail'] = {'url': part[len('thumbnail:'):]}

        if part.startswith('attach:'):
            files.append(
                discord.File(
                    BytesIO(await read(part[len('attach:'):].replace(' ', ''))), yarl.URL(part[len('attach:') :].replace(' ', '')).name)
            )

        if part.startswith('author:'):
            z = part[len('author:'):].split(' && ')
            icon_url = None
            url = None
            for p in z[1:]:
                if p.startswith('icon:'):
                    p = p[len('icon:') :]
                    icon_url = p.replace(' ', '')
                elif p.startswith('url:'):
                    p = p[len('url:'):]
                    url = p.replace(' ', '')
            try:
                name = z[0] if z[0] else None
            except:
                name = None
            
            embed['author'] = {'name': name}
            if icon_url:
                embed['author']['icon_url'] = icon_url
            if url:
                embed['author']['url'] = url

        if part.startswith('field:'):
            z = part[len('field:'):].split(' && ')
            value = None
            inline='true'
            for p in z[1:]:
                if p.startswith('value:'):
                    p = p[len('value:'):]
                    value = p
                elif p.startswith('inline:'):
                    p = p[len('inline:'):]
                    inline = p.replace(' ', '')
            try:
                name = z[0] if z[0] else None
            except:
                name = None
            
            if isinstance(inline, str):
                if inline == 'true':
                    inline = True

                elif inline == 'false':
                    inline = False

            fields.append({'name': name, 'value': value, 'inline': inline})

        if part.startswith('footer:'):
            z = part[len('footer:'):].split(' && ')
            text = None
            icon_url = None
            for p in z[1:]:
                if p.startswith('icon:'):
                    p = p[len('icon:'):]
                    icon_url = p.replace(' ', '')
            try:
                text = z[0] if z[0] else None
            except:
                pass
                
            embed['footer'] = {'text': text}
            if icon_url:
                embed['footer']['icon_url'] = icon_url

        if part.startswith('label:'):
            z = part[len('label:'):].split(' && ')
            label = 'no label'
            url = None
            for p in z[1:]:
                if p.startswith('url:'):
                    p = p[len('url:'):]
                    url = p.replace(' ', '')
                    
            try:
                label = z[0] if z[0] else None
            except:
                pass
                

            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link, 
                    label=label, 
                    url=url
                )
            )
            
        if part.startswith('image:'):
            z = part[len('image:'):]
            embed['image'] = {'url': z}
            
        if part.startswith('timestamp:'):
            z = part[len('timestamp:'):].replace(' ', '')
            if z == 'true':
                timestamp = True
                
    if not embed:
        embed = None
    else:
        embed['fields'] = fields
        embed = discord.Embed.from_dict(embed)

    if not code.count('{') and not code.count('}'):
        content = code
        
    if timestamp:
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/London'))

    return {'content': content, 'embed': embed, 'files': files, 'view': view, 'delete_after': delete}

async def embed_replacement(user: discord.Member, params):
    if "{user}" in params:
        params = params.replace("{user}", str(user))
    if "{user.id}" in params:
        params = params.replace("{user.id}", str(user.id))
    if "{user.mention}" in params: 
        params = params.replace("{user.mention}", str(user.mention))
    if "{user.name}" in params: 
        params = params.replace("{user.name}", str(user.name))
    if "{user.tag}" in params: 
        params = params.replace("{user.tag}", str(user.discriminator))
    if "{user.avatar}" in params:
         params = params.replace("{user.avatar}", str(user.display_avatar.url))
    if "{user.color}" in params:
         params = params.replace("{user.color}", str(user.top_role.color))
    if "{user.display_name}" in params:
         params = params.replace("{user.display_name}", str(user.nick))
    if "{user.bot}" in params:
        params = params.replace("{user.bot}", "Yes" if user.bot else "No")
    if "{user.created_at}" in params:
         params = params.replace("{user.created_at}", str(user.created_at.strftime("%d/%m/%Y %H:%M")))
    if "{unix(user.created_at}" in params:
         params = params.replace("{unix(user.created_at}", str(round(user.created_at.timestamp())))
    if "{guild}" in params:
        params = params.replace("{guild}", str(user.guild))
    if "{guild.name}" in params:
        params = params.replace("{guild.name}", str(user.guild.name))
    if "{guild.id}" in params:
        params = params.replace("{guild.id}", str(user.guild.id))
    if "{guild.owner_id}" in params:
        params = params.replace("{guild.owner_id}", str(user.guild.owner_id))
    if "{guild.icon}" in params:
        params = params.replace("{guild.icon}", str(user.guild.icon.url) if user.guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png")
    if "{guild.banner}" in params:
        params = params.replace("{guild.banner}", str(user.guild.banner.url) if user.guild.banner else "https://cdn.discordapp.com/embed/avatars/0.png")
    if "{guild.splash}" in params:
        params = params.replace("{guild.splash}", str(user.guild.splash.url) if user.guild.splash else "https://cdn.discordapp.com/embed/avatars/0.png")
    if "{guild.discovery}" in params:
        params = params.replace("{guild.discovery}", "Yes" if user.guild.discovery_splash else "https://cdn.discordapp.com/embed/avatars/0.png")
    if "{guild.created_at}" in params:
        params = params.replace("{guild.created_at}", str(user.guild.created_at.strftime("%d/%m/%Y %H:%M")))
    if "{unix(guild.created_at}" in params:
        params = params.replace("{unix(guild.created_at}", str(round(user.guild.created_at.timestamp())))
    if "{guild.count}" in params:
        params = params.replace("{guild.count}", str(user.guild.member_count))
    if "{guild.boost_count}" in params:
        params = params.replace("{guild.boost_count}", str(user.guild.premium_subscription_count))
    else:
        pass
    return params