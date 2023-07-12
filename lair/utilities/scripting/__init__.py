import datetime
import io
import re

import discord
from aiohttp import ClientSession
from discord.ui import Button, View
from discord.utils import format_dt
from yarl import URL

from utilities.managers.context import Context


def ordinal(n):
    n = int(n)
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10:: 4])

class EmbedBuilder:
    def __init__(self, ctx: Context, user: discord.User | discord.Member):
        self.user = user
        self.ctx = ctx
        self.replacements = {
            "{user}": str(user),
            "{user.mention}": user.mention,
            "{user.name}": user.name,
            "{user.avatar}": user.display_avatar.url,
            "{user.joined_at}": format_dt(user.joined_at, style="R"),
            "{user.created_at}": format_dt(user.created_at, style="R"),
            "{user.discriminator}": user.discriminator,
            "{guild.name}": user.guild.name,
            "{guild.count}": str(user.guild.member_count),
            "{guild.count.format}": ordinal(len(user.guild.members)),
            "{guild.id}": user.guild.id,
            "{guild.created_at}": format_dt(user.guild.created_at, style="R"),
            "{guild.boost_count}": str(user.guild.premium_subscription_count),
            "{guild.booster_count}": str(len(user.guild.premium_subscribers)),
            "{guild.boost_count.format}": ordinal(str(user.guild.premium_subscription_count)),
            "{guild.booster_count.format}": ordinal(str(user.guild.premium_subscription_count)),
            "{guild.boost_tier}": str(user.guild.premium_tier),
            "{guild.icon}": user.guild.icon.url if user.guild.icon else ""
        }

    def is_valid_url(url: str) -> bool:
        regex_pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+/?$'
        return bool(re.match(regex_pattern, url))
    
    async def replace_placeholders(self, params: str) -> str:
        for placeholder, value in self.replacements.items():
            params = params.replace(placeholder, str(value))
        return params
    
    async def build_embed(self, code: str) -> dict:
        replacements = await self.replace_placeholders(code)
        embed = {}
        files = []
        fields = []
        content = None
        delete = None
        view = View()
        client = ClientSession()

        matches = re.findall(r"\$v\{([^{}]+?)\}", replacements)

        for match in matches:
            key_value = match.split(":", 1)
            key = key_value[0].strip()
            value = key_value[1].strip()

            if key == "author":
                author_data = value.split("&&")
                if len(author_data) >= 1:
                    author_name = author_data[0].strip()
                    author_url = None
                    author_icon = None
                    if len(author_name) > 100:
                        raise ValueError(f'Author exceeds character limit of 100.')
                    for data in author_data[1:]:
                        if data.strip().startswith("url:"):
                            author_url = data.strip().replace('url: ', '') or None
                        elif data.strip().startswith("icon:"):
                            author_icon = data.strip().replace('icon: ', '') or None
                    embed['author'] = {'name': author_name}
                    if author_url:
                        if not self.is_valid_url(author_url):
                            raise ValueError(f"Malformed URL in 'author' field: {author_url}")
                        author_url = author_url.replace(' ', '')
                        embed['author']['url'] = author_url
                    if author_icon:
                        if not self.is_valid_url(author_icon):
                            raise ValueError(f"Malformed URL in 'author' field: {author_icon}")
                        author_icon = author_icon.replace(' ', '')
                        embed['author']['icon_url'] = author_icon
            elif key == "title":
                embed['title'] = value
            elif key == "content":
                if len(value) > 2000:
                    raise ValueError("Content exceeds the character limit of 2000")
                content = value
            elif key == "autodelete":
                if value.isdigit():
                    delete = int(value)
            elif key == "file":
                if not self.is_valid_url(value):
                    raise ValueError(f"Malformed URL in 'file' field: {value}")
                files.append(
                    discord.File(
                        io.BytesIO(await client.request(value.strip().replace(' ', '')), URL(value.strip().replace(' ', '')).name)
                    )
                )
            elif key == "url":
                if not self.is_valid_url(value):
                    raise ValueError(f"Malformed URL in 'url' field: {value}")
                embed['url'] = value
            elif key == "description":
                embed['description'] = value
            elif key == "field":
                field_data = value.split("&&")
                field_name = field_data[0].strip()
                field_value = None
                inline = False

                if len(field_data) >= 2:
                    field_value = field_data[1].strip().replace('value: ', '') or None

                if len(field_data) >= 3:
                    inline = bool(field_data[2].strip().replace('inline ', ''))

                fields.append({"name": field_name, "value": field_value, "inline": inline})
            elif key == "image":
                if not self.is_valid_url(value):
                    raise ValueError(f"Malformed URL in 'image' field: {value}")
                embed['image'] = {"url": value}
            elif key == "thumbnail":
                if not self.is_valid_url(value):
                    raise ValueError(f"Malformed URL in 'thumbnail' field: {value}")
                embed['thumbnail'] = {"url": value}
            elif key == "color":
                if value.strip() == "dominant":
                    color = await self.ctx.dominant(self.user.avatar.url)
                    embed['color'] = color
                else:
                    try:
                        embed['color'] = int(value.strip('#'), 16)
                    except ValueError:
                        raise ValueError(f"Invalid color value in 'color' field: {value}")
            elif key == "footer":
                footer_data = value.split("&&")
                if len(footer_data) >= 2:
                    footer_text = footer_data[0].strip()
                    footer_icon = None
                    if len(footer_data) >= 3:
                        footer_icon = footer_data[1].strip().replace('url: ', '')
                    embed['footer'] = {"text": footer_text}
                    if footer_icon:
                        if not self.is_valid_url(footer_icon):
                            raise ValueError(f"Malformed URL in 'footer' field: {footer_icon}")
                        embed['footer']['icon_url'] = footer_icon
                else:
                    embed['footer'] = {"text": footer_data[0].strip()}
            elif key == "timestamp":
                embed['timestamp'] = str(datetime.datetime.now())
            elif key == "button":
                button_data = value.split("&&")
                if len(button_data) >= 2:
                    button_label = button_data[0].strip()
                    _button_url = button_data[1].strip().replace('url: ', '')

                    if not self.is_valid_url(_button_url):
                        raise ValueError(f"Malformed URL in 'button' field: {_button_url}")
                    view.add_item(
                        Button(
                            style=discord.ButtonStyle.link,
                            label=button_label,
                            url=_button_url.replace(' ', '')
                        )
                    )

        if not embed:
            embed = None
        else:
            embed['fields'] = fields
            embed = discord.Embed.from_dict(embed)

        if not replacements.count('{') and not replacements.count('}'):
            content = replacements

        return {'content': content, 'embed': embed, 'view': view, 'delete_after': delete, 'files': files}