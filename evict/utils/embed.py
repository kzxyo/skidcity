import datetime, discord
from dataclasses import dataclass
from typing import List, Optional
from discord.ext import commands

class EmbedFooter():
    text: Optional[str]
    icon_url: Optional[str]

class EmbedField():
    name: Optional[str]
    value: Optional[str]
    inline: bool

class EmbedAuthor():
    name: Optional[str]
    url: Optional[str]
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]
    
class EmbedAuthor():
    name: Optional[str]
    url: Optional[str]
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]  
    
@dataclass
class EmbedAuthor:
    name: str
    icon_url: Optional[str] = None
    url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data['name'], data.get('icon_url'), data.get('url'))
    
    @classmethod
    def from_variable(cls, variables: str):
        variables = variables.split(' && ')
        name = variables[0] if len(variables) > 0 else None
        icon_url = variables[1] if len(variables) > 1 else None
        url = variables[2] if len(variables) > 2 else None
        return cls(name, icon_url, url)
    
    @classmethod
    def to_variable(cls, author: EmbedAuthor):
        return f'author: {author.name} {f"&& {author.icon_url}" if author.icon_url is not None else ""} {f"&& {author.url}" if author.url is not None else ""}'
    
@dataclass
class EmbedField:
    name: str
    value: str
    inline: Optional[bool] = False
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data['name'], data['value'], data['inline'])
    
    @classmethod
    def from_variable(cls, variables: str):
        variables = variables.split(' && ')
        name = variables[0] if len(variables) > 0 else None
        value = variables[1] if len(variables) > 1 else None
        inline = True if 'inline' in variables else False
        return cls(name, value, inline)
    
    @classmethod
    def to_variable(cls, field: EmbedField):
        return f'field: {field.name} && {field.value} {"inline" if field.inline else ""}'
    
@dataclass
class EmbedFooter:
    text: str
    icon_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data['text'], data.get('icon_url'))
    
    @classmethod
    def from_variable(cls, variables: str):
        variables = variables.split(' && ')
        text = variables[0] if len(variables) > 0 else None
        icon_url = variables[1] if len(variables) > 1 else None
        return cls(text, icon_url)
    
    @classmethod
    def to_variable(cls, footer: EmbedFooter):
        return f'footer: {footer.text} {f"&& {footer.icon_url}" if footer.icon_url else ""}'
    
@dataclass
class EmbedButton:
    label: Optional[str] = None
    url: Optional[str] = None
    disabled: Optional[bool] = False
    style: Optional[discord.ButtonStyle] = discord.ButtonStyle.gray
    emoji: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            label=data.get('label'),
            url=data.get('url'),
            disabled=data.get('disabled', False),
            style=discord.ButtonStyle.red if data.get('style') == 'red' else discord.ButtonStyle.green if data.get('style') == 'green' else discord.ButtonStyle.gray if data.get('style') == 'gray' else discord.ButtonStyle.blurple if data.get('style') == 'blue' else discord.ButtonStyle.gray,
            emoji=data.get('emoji')
        )
    
    @classmethod
    def from_variable(cls, variables: str):
        var = variables
        variables = variables.split(' && ')
        label = variables[0] if len(variables) > 0 else var
        emoji = variables[1] if len(variables) > 1 else None
        url = variables[2] if len(variables) > 2 else None
        style = variables[3] if len(variables) > 3 else discord.ButtonStyle.gray
        disabled = True if 'disabled' in variables else False
        return cls(label, url, disabled, style, emoji)
    

@dataclass
class Embed:
    content: str
    title: str
    description: str
    color: int
    timestamp: Optional[datetime.datetime] = None
    image: Optional[str] = None
    thumbnail: Optional[str] = None
    author: Optional[EmbedAuthor] = None
    footer: Optional[EmbedFooter] = None
    fields: List[EmbedField] = None
    buttons: List[EmbedButton] = None
    only_content: bool = False
    
    def replace(code: str, member: discord.Member, target: discord.Member):
        code = code.replace("{server}", member.guild.name)
        code = code.replace("{server.name}", member.guild.name)
        code = code.replace("{server.id}", str(member.guild.id))
        code = code.replace("{server.owner}", member.guild.owner.name)
        code = code.replace("{server.owner.id}", str(member.guild.owner.id))
        code = code.replace("{server.owner.mention}", member.guild.owner.mention)
        code = code.replace("{server.owner.avatar}", member.guild.owner.display_avatar.url)
        if member.guild.banner is not None: code = code.replace("{server.banner}", member.guild.banner.url)
        code = code.replace("{server.region}", 'I dont know')
        code = code.replace("{server.member_count}", str(member.guild.member_count))
        code = code.replace("{server.boost_count}", str(member.guild.premium_subscription_count))
        code = code.replace("{server.boost_tier}", str(member.guild.premium_tier))
        code = code.replace("{server.created_at}", discord.utils.format_dt(member.guild.created_at, style='R'))
        code = code.replace("{server.vanity}", "/" + (member.guild.vanity_url_code or "none"))
        code = code.replace("{guild}", member.guild.name)
        code = code.replace("{guild.name}", member.guild.name)
        code = code.replace("{guild.id}", str(member.guild.id))
        code = code.replace("{guild.owner}", member.guild.owner.name)
        code = code.replace("{guild.owner.id}", str(member.guild.owner.id))
        code = code.replace("{guild.owner.mention}", member.guild.owner.mention)
        code = code.replace("{guild.owner.avatar}", member.guild.owner.display_avatar.url)
        if member.guild.banner is not None: code = code.replace("{guild.banner}", member.guild.banner.url)
        code = code.replace("{guild.region}", 'I dont know')
        code = code.replace("{guild.member_count}", str(member.guild.member_count))
        code = code.replace("{guild.boost_count}", str(member.guild.premium_subscription_count))
        code = code.replace("{guild.boost_tier}", str(member.guild.premium_tier))
        code = code.replace("{guild.created_at}", discord.utils.format_dt(member.guild.created_at, style='R'))
        code = code.replace("{guild.vanity}", "/" + (member.guild.vanity_url_code or "none"))
        code = code.replace("{user}", member.mention)
        code = code.replace("{user.mention}", member.mention)
        code = code.replace("{user.name}", member.name)
        code = code.replace("{user.id}", str(member.id))
        code = code.replace("{user.avatar}", member.display_avatar.url)
        code = code.replace("{user.joined_at}", discord.utils.format_dt(member.joined_at, style='R'))
        code = code.replace("{user.created_at}", discord.utils.format_dt(member.created_at, style='R'))
        code = code.replace("{target}", target.mention)
        code = code.replace("{target.mention}", target.mention)
        code = code.replace("{target.name}", target.name)
        code = code.replace("{target.id}", str(target.id))
        code = code.replace("{target.avatar}", target.display_avatar.url)
        code = code.replace("{target.joined_at}", discord.utils.format_dt(target.joined_at, style='R'))
        code = code.replace("{target.created_at}", discord.utils.format_dt(target.created_at, style='R'))
        return code
    
    @classmethod
    def from_dict(cls, data: dict, member: discord.Member, target: discord.Member=None):
        if target is None: target = member
        return cls(
            content=Embed.replace(data.get('content'), member, target),
            title=Embed.replace(data.get('title'), member, target),
            description=Embed.replace(data.get('description'), member, target),
            color=data.get('color'),
            timestamp=data.get('timestamp'),
            image=Embed.replace(data.get('image'), member, target),
            thumbnail=Embed.replace(data.get('thumbnail'), member, target),
            author=Embed.replace(EmbedAuthor.from_dict(data.get('author'), member, target)),
            footer=EmbedFooter.from_dict(Embed.replace(data.get('footer'), member, target)),
            fields=[EmbedField.from_dict(field) for field in Embed.replace(data.get('fields', []), member, target)],
            buttons=[EmbedButton.from_dict(button) for button in Embed.replace(data.get('buttons', []), member, target)]
        )
        
    @classmethod
    def from_variable(cls, variables: str, member: discord.Member, target: discord.Member=None):
        if target is None: target = member
        content, title, color, description, image, thumbnail, author, footer, timestamp, fields, buttons = None, None, None, None, None, None, None, None, None, [], []
        variables = Embed.replace(variables, member, target)
        variables = variables.replace('$v', '').split('{')
        if len(variables) == 1 and '{embed}' not in variables: return cls(content=variables[0], title=title, color=color, description=description, image=image, thumbnail=thumbnail, author=author, footer=footer, fields=fields, buttons=buttons, only_content=True)
        variables = [variable[1:-1] if '{' in variable else variable[:-1] for variable in variables]
        for variable in variables:
            if variable.startswith('content:'): content = variable[len('content:'):]
            if variable.startswith('title:'): title = variable[len('title:'):]
            if variable.startswith('description:'): description = variable[len('description:'):]
            if variable.startswith('color:'): color = int(variable[len('color:'):].replace("#", ""), 16)
            if variable.startswith('image:'): image = variable[len('image:'):]
            if variable.startswith('thumbnail:'): thumbnail = variable[len('thumbnail:'):]
            if variable.startswith('author:'): author = EmbedAuthor.from_variable(variable[len('author:'):])
            if variable.startswith('footer:'): footer = EmbedFooter.from_variable(variable[len('footer:'):])
            if variable.startswith('field:'): fields.append(EmbedField.from_variable(variable[len('field:'):]))
            if variable.startswith('button:'): buttons.append(EmbedButton.from_variable(variable[len('button:'):]))
            if variable.startswith('timestamp'): timestamp = datetime.datetime.now()     
                   
        return cls(
            content=content,
            title=title,
            description=description,
            color=color,
            timestamp=timestamp,
            image=image,
            thumbnail=thumbnail,
            author=author,
            footer=footer,
            fields=fields,
            buttons=buttons,
            only_content=False
        )
        
    def to_embed(self) -> discord.Embed:
        if self.only_content: return None
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color,
            timestamp=self.timestamp
        )
        if self.image: embed.set_image(url=self.image)
        if self.thumbnail: embed.set_thumbnail(url=self.thumbnail)
        if self.author: embed.set_author(name=self.author.name, icon_url=self.author.icon_url, url=self.author.url)
        if self.footer: embed.set_footer(text=self.footer.text, icon_url=self.footer.icon_url)
        if self.fields: 
            for field in self.fields:
                embed.add_field(name=field.name, value=field.value, inline=field.inline)
        return embed
    
    def to_view(self) -> discord.ui.View:
        view = discord.ui.View()
        for button in self.buttons:
            view.add_item(discord.ui.Button(label=button.label, style=button.style, disabled=button.disabled, emoji=button.emoji, url=button.url))
        return view

    def to_variables(message: discord.Message) -> str:
        variables = []
        embed = message.embeds[0] if len(message.embeds) > 0 else None
        if message.content: variables.append(f"content:{message.content}")
        if embed is None: return "{" + "}{".join(variables) + "}"
        if embed.title: variables.append(f"title:{embed.title}")
        if embed.description: variables.append(f"description:{embed.description}")
        if embed.color: variables.append(f"color:{embed.color}")
        if embed.image: variables.append(f"image:{embed.image}")
        if embed.thumbnail: variables.append(f"thumbnail:{embed.thumbnail.url}")
        if embed.author:
            author_variables = EmbedAuthor.to_variable(embed.author)
            variables.append(f"{author_variables}")
        if embed.footer:
            footer_variables = EmbedFooter.to_variable(embed.footer)
            variables.append(f"{footer_variables}")
        if embed.fields:
            for field in embed.fields:
                field_variables = EmbedField.to_variable(field)
                variables.append(f"{field_variables}")
        if embed.timestamp:
            variables.append("timestamp")
        
        return "{" + "}{".join(variables) + "}"
        
class EmbedConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> Embed:
        argument = argument.replace("{embed}", "")
        return Embed.from_variable(argument, ctx.author)