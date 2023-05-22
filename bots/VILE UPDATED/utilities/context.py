import discord, difflib, asyncio, subprocess, sys, traceback, typing
from .paginator import Paginator
from typing import Optional, Union, Iterable, Iterator, Any, Awaitable, Callable, Type
from typing_extensions import Self
from types import TracebackType
from datetime import datetime
from discord.ext import commands


def as_chunks(iterator: Iterable[Any], max_size: int) -> Iterator[Any]:
    ret = list()
    n = 0
    for item in iterator:
        ret.append(item)
        n += 1
        if n == max_size:
            yield ret
            ret = list()
            n = 0
    if ret:
        yield ret


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    
    async def send_success(self, message: str, delete_after: Optional[int] = None) -> discord.Message:

        try:
            return await self.reply(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.bot.done} {self.author.mention}**:** {message}'
                ),
                delete_after=delete_after
            )
        except:
            return await self.send(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.bot.done} {self.author.mention}**:** {message}'
                ),
                delete_after=delete_after
            )


    async def send_error(self, message: str, delete_after: Optional[int] = None) -> discord.Message:

        try:
            return await self.reply(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.bot.fail} {self.author.mention}**:** {message}'
                ),
                delete_after=delete_after
            )
        except:
            return await self.send(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f'{self.bot.fail} {self.author.mention}**:** {message}'
                ),
                delete_after=delete_after
            )


    async def send_help(self) -> discord.Message:

        command = self.command
        bot = self.bot
        done = bot.done
        fail = bot.fail
        warn = bot.fail
        reply = bot.reply
        dash = bot.dash
        success = bot.color
        error = bot.color
        warning = bot.color
        nl = '\n'

        if not hasattr(command, 'commands'):
            cmd = command
            name = cmd.qualified_name
            desc = cmd.description or 'none'
            aliases = ', '.join(cmd.aliases)
            permissions = None if cmd.extras.get('permissions') is None else cmd.extras['permissions']
            syntax = cmd.brief or 'none'
            example = cmd.help or 'none'
            
            embed=discord.Embed(
                color=bot.color, 
                timestamp=datetime.now()
            )
            embed.set_author(
                name=name,
                icon_url=self.bot.user.display_avatar
            )
            embed.add_field(
                name=f'{dash} Information',
                value=f"{reply} **description:** {desc}{nl+f'{reply} **permissions:** {permissions}' if permissions else ''}{nl+f'{reply} **aliases:** {aliases}' if aliases else ''}",
                inline=False
            )
            embed.add_field(
                name=f'{dash} Usage',
                value=f'{reply} **syntax:** {self.prefix if syntax != "none" else ""}{syntax}\n{reply} **example:** {self.prefix if example != "none" else ""}{example}',
                inline=False
            )
            embed.set_footer(
                text=cmd.cog_name.replace('_', ' ')
            )
            return await self.reply(embed=embed)
            
        if hasattr(command, 'commands'):
            embeds = list()
            aliases = ', '.join(command.aliases)
            permissions = None if command.extras.get('permissions') is None else command.extras['permissions']
            num = 1
            embed=discord.Embed(
                color=bot.color, 
                timestamp=datetime.now()
            )
            embed.set_author(
                name=self.command.qualified_name,
                icon_url=self.bot.user.display_avatar
            )
            embed.add_field(
                name=f'{dash} Information',
                value=f"{reply} **description:** {command.description or 'none'}{nl+f'{reply} **permissions:** {permissions}' if permissions else ''}{nl+f'{reply} **aliases:** {aliases}' if aliases else ''}",
                inline=False
            )
            embed.add_field(
                name=f'{dash} Usage',
                value=f'{reply} **syntax:** {self.prefix if command.brief else ""}{command.brief or "none"}\n{reply} **example:** {self.prefix if command.help else ""}{command.help or "none"}',
                inline=True
            )
            embed.set_footer(
                text=f"{command.cog_name.replace('_', ' ')}   \u2022   Page {num} / {len(set(self.command.walk_commands()))+1}"
            )
            embeds.append(embed)
            
            for command in set(command.walk_commands()):
                num += 1
                aliases = ', '.join(getattr(command, 'aliases', list()))
                permissions = None if command.extras.get('permissions') is None else command.extras['permissions']
                embed = discord.Embed(
                    color=bot.color, 
                    timestamp=datetime.now()
                )
                embed.set_author(
                    name=command.qualified_name,
                    icon_url=bot.user.display_avatar
                )
                embed.add_field(
                    name=f'{dash} Information',
                    value=f"{reply} **description:** {getattr(command, 'description', None) or 'none'}{nl+f'{reply} **permissions:** {permissions}' if permissions else ''}{nl+f'{reply} **aliases:** {aliases}' if aliases else ''}",
                    inline=False
                )
                embed.add_field(
                    name=f'{dash} Usage',
                    value=f"{reply} **syntax:** {self.prefix if getattr(command, 'brief', None) else ''}{getattr(command, 'help', None) or 'none'}\n{reply} **example:** {self.prefix if getattr(command, 'brief', None) else ''}{getattr(command, 'help', None) or 'none'}",
                    inline=True
                )
                embed.set_footer(
                    text=f"{command.cog_name.replace('_', ' ')}   \u2022   Page {num} / {len(set(self.command.walk_commands()))+1}"
                )
                embeds.append(embed)
                
            return await self.paginate(embeds)



    async def paginate(self, to_paginate: Union[discord.Embed, list]) -> Optional[discord.Message]:

        if isinstance(to_paginate, discord.Embed):
            embed = to_paginate
            if not embed.description:
                return

            if not isinstance(embed.description, list):
                return

            if len(embed.description) == 0:
                return await self.send_error('no entries found')
                

            embeds = list()
            num = 0
            rows = [
                f'`{index}` {row}'
                for index, row in enumerate(embed.description, start=1)
            ]

            for page in as_chunks(rows, 10):
                num += 1
                embeds.append(
                    discord.Embed(
                        color=embed.color or self.bot.colo,
                        title=embed.title,
                        description='\n'.join(page),
                        timestamp=embed.timestamp
                    )
                    .set_footer(text=f'Page {num} / {len(list(as_chunks(rows, 10)))}  ({len(rows)} entries)')
                    .set_author(name=self.author, icon_url=self.author.display_avatar)
                )

            if self.should_paginate(embeds) is False:
                return await self.reply(embed=embeds[0])

            interface = Paginator(self.bot, embeds, self, invoker=self.author.id, timeout=30)
            interface.default_pagination()
            return await interface.start()

        elif isinstance(to_paginate, list):
            
            embeds = to_paginate
            
            if len(embeds) == 0:
                return await self.send_error('no entries found')

            if self.should_paginate(embeds) is False:
                return await self.reply(embed=embeds[0])

            interface = Paginator(self.bot, embeds, self, invoker=self.author.id, timeout=30)
            interface.default_pagination()
            return await interface.start()


    def find_member(self, name: str) -> Optional[discord.Member]:
        
        members = [m.name.lower() for m in self.guild.members]
        closest = difflib.get_close_matches(name.lower(), members, n=3, cutoff=0.5)
        if closest:
            for m in self.guild.members:
                if m.name.lower() == closest[0].lower():
                    return m
        return None


    def find_role(self, name: str) -> Optional[discord.Role]:
        
        roles = [r.name.lower() for r in self.guild.roles]
        closest = difflib.get_close_matches(name.lower(), roles, n=3, cutoff=0.5)
        if closest:
            for r in self.guild.roles:
                if r.name.lower() == closest[0].lower():
                    return r
        return None


    async def can_moderate(self, user: Union[discord.Member, discord.User], action: str = 'moderate') -> Optional[discord.Message]:

        if user == self.author:
            return await self.send_error(f"you can't **{action}** yourself")
        
        if isinstance(user, discord.Member) and (user.top_role.position >= self.author.top_role.position and self.author.id != self.guild.owner_id) or user.id == self.guild.owner_id:
            return await self.send_error(f"you can't **{action}** that {'member' if isinstance(user, discord.Member) else 'user'}")
            
        if self.bot.get_user(user.id) == self.bot.get_user(self.bot.user.id):
            return await self.send_error(f"you can't **{action}** that {'member' if isinstance(user, discord.Member) else 'user'}")
            
        if isinstance(user, discord.Member) and (user.top_role.position >= self.guild.me.top_role.position and self.author.id != self.guild.owner_id):
            return await self.send_error(f"i can't **{action}** that {'member' if isinstance(user, discord.Member) else 'user'}")

        return None


    async def dm(self, user: Union[discord.Member, discord.User], *args, **kwargs) -> Optional[discord.Message]:

        if 15 <= self.bot.cache.limits['dms'].setdefault(self.guild.id, 0):
            return None

        try:
            await user.send(*args, **kwargs)
            self.bot.cache.limits['dms'][self.guild.id] += 1
        except:
            return None
        
        return None


    def should_paginate(self, _list: list) -> bool:
        return len(_list) > 1


    def is_dangerous(self, role: discord.Role) -> bool:

        permissions = role.permissions
        return any([
            permissions.kick_members, permissions.ban_members,
            permissions.administrator, permissions.manage_channels,
            permissions.manage_guild,
            permissions.manage_roles, permissions.manage_webhooks,
            permissions.manage_emojis_and_stickers, permissions.manage_threads,
            permissions.mention_everyone
        ])


    def is_boosting(self, user: Union[discord.Member, discord.User]) -> bool:

        for guild in user.mutual_guilds:
            if guild.get_member(user.id).premium_since is not None:
                return True

        return False

    
    def convert_emoji(self, emoji: Union[discord.PartialEmoji, discord.Emoji]) -> str:

        if isinstance(emoji, discord.PartialEmoji):
            return f':{emoji.name}:'

        return f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>"


    async def await_response(self) -> Optional[str]:

        try:
            message = await self.bot.wait_for(
                'message', check=lambda m: m.author.id == self.author.id and m.channel.id == self.channel.id, timeout=30
            )
        except asyncio.TimeoutError:
            return None
        else:
            return message.content


    def handle_response(self):

        if self.interaction:
            return self.channel.typing()
        return DelayedResponseReactor(self)


class DelayedResponseReactor:
    def __init__(self, context: Context) -> None:
        self.context = context
        self.loop = context.bot.loop
        self.handle = None


    async def __aenter__(self) -> Self:
        self.handle = self.loop.create_task(self.delay_action(2, self.add_reaction, '<a:vile_loading:1003252144377446510>'))
        return self


    async def __aexit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> Optional[discord.Reaction]:
        
        if self.handle:
            self.handle.cancel()

        if not exc_val:
            return await self.add_reaction('<:v_done:1067033981452828692>')

        return await self.add_reaction('<:v_warn:1067034029569888266>')


    async def delay_action(self, delay: Union[float, int], coro: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        await asyncio.sleep(delay)
        return await coro(*args, **kwargs)


    async def add_reaction(self, reaction: Union[str, discord.Emoji]) -> Optional[discord.Reaction]:
        try:
            return await self.context.message.add_reaction(reaction)
        except discord.HTTPException:
            return None
