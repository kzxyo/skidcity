import inspect
import itertools
import re
import typing

from os import urandom

import dateparser

from discord import ButtonStyle, Guild, Member, TextChannel, VoiceChannel
from discord.ui import Button, View
from discord.utils import utcnow

from helpers import regex
from helpers.models.tagscript import ScriptObject
from helpers.tagscript.classes import ENV, Converter, Node, ParsedTag, Tag
from helpers.utilities import get_color, ordinal


class Parser:
    def __init__(self, env: typing.Optional[dict] = None, *, limit: int = None):
        self.limit = limit
        self.env = env or {}
        self.tags = []
        self._delimiter = r"\:"
        self._argument_delimiter = "&&"
        self._attribute_delimiter = r"\."
        self._escape_character = urandom(32).hex()
        self._start_character = r"\{"
        self._end_character = r"\}"
        self._case_insensitive = True

    @property
    def is_case_insensitive(self):
        return self._case_insensitive

    def update_env(self, new):
        self.env.update(new)

    def get_env(self, var):
        return self.env.get(var)

    @staticmethod
    def _validate_match(pattern, query):
        return re.fullmatch(pattern, query) is not None

    def get_tag(self, name, *, parent=None):
        parent = parent or self
        if self._case_insensitive:
            name = name.lower()

        for tag in parent.tags:
            if tag.name == name or name in tag.aliases:
                return tag
        return None

    def tag(
        self,
        name: str = None,
        *,
        alias: str = None,
        aliases: typing.List[str] = None,
        **attrs,
    ):
        if not aliases:
            aliases = [alias] if alias else []

        if self._case_insensitive:
            aliases = [alias.lower() for alias in aliases]
            if name:
                name = name.lower()

        def decorator(func):
            name_ = name or func.__name__
            tag_ = Tag(
                self,
                func.callback if isinstance(func, Tag) else func,
                name_,
                aliases,
                **attrs,
            )
            self.tags.append(tag_)
            return tag_

        return decorator

    def get_nodes(self, content):
        nodes = []
        buffer = []
        previous = ""

        for i, char in enumerate(content):
            if (
                self._validate_match(self._start_character, char)
                and previous != self._escape_character
            ):
                buffer.append([i])

            if (
                self._validate_match(self._end_character, char)
                and previous != self._escape_character
            ):
                if len(buffer) <= 0:
                    continue
                buffer[-1].append(i)
                nodes.append(Node(*buffer[-1]))
                buffer.pop(-1)
            previous = char

        return nodes

    def _base_argument_conversion(self, argument, converter):
        argument = argument.strip()

        if converter in (str, int, float):
            try:
                return converter(argument)
            except ValueError:
                return None

        if converter is bool:
            if argument.lower() in (
                "enable",
                "true",
                "yes",
                "on",
            ):
                return True

            return False

        if isinstance(converter, Converter):
            try:
                conv = converter.converter
                if len(inspect.signature(conv).parameters.values()) > 1:
                    return conv(self, argument)
                return conv(argument)
            except Exception:
                return None

    def do_argument_conversion(self, argument, converter) -> any:
        try:
            origin = converter.__origin__
        except AttributeError:
            pass
        else:
            if origin is typing.Union:
                type(None)
                for conv in converter.__args__:
                    if res := self._base_argument_conversion(argument, conv):
                        return res
                return None

        return self._base_argument_conversion(argument, converter)

    def parse_single_tag(self, tag) -> typing.Optional[ParsedTag]:
        regex = f"(?<!{re.escape(self._escape_character)})"
        splitted = re.split(regex + self._delimiter, tag, 1)
        if len(splitted) < 2:
            tag_, args = splitted[0], ""
        else:
            tag_, args = splitted[:2]
        tag_body = re.split(regex + self._attribute_delimiter, tag_)

        buffer = self
        for i, iteration in enumerate(tag_body, start=1):
            if got_tag := self.get_tag(iteration, parent=buffer):
                buffer = got_tag
                continue
            return None

        callback_params = list(inspect.signature(buffer.callback).parameters.values())
        if len(callback_params) < 1:
            raise ValueError(
                "Parser callbacks must have at least one parameter (The environment, usually to be named 'env')"
            )
        arguments = re.split(regex + self._argument_delimiter, args)
        parsed_arguments = []

        if args.strip() != "":
            for i, argument in enumerate(arguments):
                try:
                    param = callback_params[i + 1]
                except IndexError:
                    break
                converter = str
                annotation = param.annotation
                if annotation != getattr(inspect, "_empty"):
                    converter = annotation

                kind = param.kind
                if str(kind) == "VAR_POSITIONAL":
                    buf = []
                    for then_arg in arguments[i:]:
                        buf.append(self.do_argument_conversion(then_arg, converter))
                    parsed_arguments += buf
                    continue

                parsed_arguments.append(
                    self.do_argument_conversion(argument, converter)
                )

            args_left = len(callback_params) - len(parsed_arguments) - 1
            if args_left > 0:
                for i in range(len(parsed_arguments), len(callback_params)):
                    try:
                        param = callback_params[i + 1]
                    except IndexError:
                        break
                    default = param.default
                    if default != getattr(inspect, "_empty"):
                        parsed_arguments.append(default)
                        continue
                    parsed_arguments.append(None)

        return ParsedTag(self, tag, tag=buffer, args=parsed_arguments)

    def parse_nodes(self, nodes, content, env, limit):
        final = content
        nodes_parsed = 0

        for i, node in enumerate(nodes):
            string = final[node.coord[0] : node.coord[1] + 1]
            string = string.lstrip(self._start_character)
            string = string.rstrip(self._end_character)
            parsed_tag = self.parse_single_tag(string)
            try:
                value = parsed_tag.tag.callback(env, *parsed_tag.args)
                value = "" if value is None else str(value)
            except (AttributeError, TypeError):
                continue

            start, end = node.coord
            slice_length = (end + 1) - start
            replacement = len(value)
            diff = replacement - slice_length

            final = final[:start] + value + final[end + 1 :]
            nodes_parsed += 1

            if limit and nodes_parsed >= limit:
                break

            for future_node in itertools.islice(nodes, i + 1, None):
                if future_node.coord[0] > start:
                    new_start = future_node.coord[0] + diff
                else:
                    new_start = future_node.coord[0]

                if future_node.coord[1] > start:
                    new_end = future_node.coord[1] + diff
                else:
                    new_end = future_node.coord[1]
                future_node.coord = (new_start, new_end)

        return final

    def parse(self, string, env=None, *, limit=None):
        session_env = self.env
        session_env.update(env or {})
        nodes = self.get_nodes(string)
        return self.parse_nodes(nodes, string, ENV(env), limit)


parser = Parser()


@parser.tag("message", alias="content")
def message(self, value: str) -> None:
    self.model.content = value


@parser.tag("color")
def color(self, color: str) -> None:
    self.model.embed.color = get_color(color)


@parser.tag("author")
def author(self, name: str, icon_url: str = None, external_url: str = None) -> None:
    if icon_url and regex.IMAGE_URL.match(icon_url):
        pass

    elif icon_url and (match := regex.URL.match(icon_url)):
        icon_url = None
        external_url = match.group()

    self.model.embed.set_author(
        name=name,
        icon_url=icon_url,
        url=external_url,
    )


@parser.tag("url")
def url(self, external_url: str) -> None:
    self.model.embed.url = external_url


@parser.tag("title")
def title(self, value: str) -> None:
    self.model.embed.title = value


@parser.tag("description")
def description(self, value: str) -> None:
    self.model.embed.description = value


@parser.tag("image")
def image(self, image_url: str) -> None:
    self.model.embed.set_image(
        url=image_url,
    )


@parser.tag("thumbnail")
def thumbnail(self, image_url: str) -> None:
    self.model.embed.set_thumbnail(
        url=image_url,
    )


@parser.tag("field")
def field(self, name: str, value: str, inline: str = False) -> None:
    self.model.embed.add_field(
        name=name,
        value=value,
        inline=bool(inline),
    )


@parser.tag("footer")
def footer(self, text: str, icon_url: str = None) -> None:
    self.model.embed.set_footer(
        text=text,
        icon_url=icon_url,
    )


@parser.tag("timestamp")
def timestamp(self, value: str = None) -> None:
    self.model.embed.timestamp = utcnow() if not value else dateparser.parse(value)


@parser.tag("button")
def button(
    self, option: str, label: str, emoji: str = None, disabled: str = False
) -> None:
    if emoji == "disabled":
        emoji = None
        disabled = True

    if (match := regex.URL.match(option)) or (option == "url" and (match := option)):
        self.model.view.add_item(
            Button(
                label=label,
                emoji=emoji,
                url=match.group(),
                disabled=bool(disabled),
            )
        )
    else:
        self.model.view.add_item(
            Button(
                style=getattr(ButtonStyle, option, None),
                label=label,
                emoji=emoji,
                disabled=bool(disabled),
            )
        )


def compile(
    script: str,
    **vars,
) -> str:
    user: Member
    guild: Guild
    channel: TextChannel | VoiceChannel

    if user := vars.get("user"):
        guild = user.guild

        script = (
            script.replace("{user}", str(user))
            .replace("{user.name}", user.name)
            .replace("{user.display_name}", user.display_name)
            .replace("{user.mention}", user.mention)
            .replace("{user.id}", str(user.id))
            .replace("{user.tag}", user.discriminator)
            .replace("{user.bot}", ("Yes" if user.bot else "No"))
            .replace("{user.badges}", ("".join(user.badges()) or "N/A"))
            .replace("{user.avatar}", str(user.display_avatar))
            .replace("{user.guild_avatar}", str(user.display_avatar))
            .replace("{user.display_avatar}", str(user.display_avatar))
            .replace("{user.joined_at}", user.joined_at.strftime("%m/%d/%Y, %I:%M %p"))
            .replace("{user.joined_at_timestamp}", str(int(user.joined_at.timestamp())))
            .replace(
                "{user.created_at}", user.created_at.strftime("%m/%d/%Y, %I:%M %p")
            )
            .replace(
                "{user.created_at_timestamp}", str(int(user.created_at.timestamp()))
            )
            .replace("{user.boost}", ("Yes" if user.premium_since else "No"))
            .replace(
                "{user.boost_since}",
                (
                    user.premium_since.strftime("%m/%d/%Y, %I:%M %p")
                    if user.premium_since
                    else "N/A"
                ),
            )
            .replace(
                "{user.boost_since_timestamp}",
                (
                    str(int(user.premium_since.timestamp()))
                    if user.premium_since
                    else "N/A"
                ),
            )
            .replace("{user.color}", str(user.color))
            .replace(
                "{user.top_role}",
                (user.top_role.name if user.top_role != guild.default_role else "N/A"),
            )
            .replace(
                "{user.role_list}",
                (
                    ", ".join(
                        reversed(
                            [
                                role.mention
                                for role in user.roles
                                if not role.is_default()
                            ]
                        )
                    )
                    if user.roles[1:]
                    else "N/A"
                ),
            )
            .replace(
                "{user.role_text_list}",
                (
                    ", ".join(
                        reversed(
                            [role.name for role in user.roles if not role.is_default()]
                        )
                    )
                    if user.roles[1:]
                    else "N/A"
                ),
            )
            .replace("{user.join_position}", str(user.join_position))
            .replace("{user.join_position_suffix}", ordinal(user.join_position))
        )

    if guild := vars.get("guild", guild):
        script = (
            script.replace("{guild}", str(guild))
            .replace("{guild.name}", guild.name)
            .replace("{guild.id}", str(guild.id))
            .replace("{guild.icon}", str(guild.icon or "N/A"))
            .replace("{guild.banner}", str(guild.banner or "N/A"))
            .replace("{guild.splash}", str(guild.splash or "N/A"))
            .replace("{guild.discovery}", str(guild.discovery_splash or "N/A"))
            .replace("{guild.shard}", str(guild.shard_id))
            .replace("{guild.owner_id}", str(guild.owner_id))
            .replace("{guild.preferred_locale}", guild.preferred_locale.value)
            .replace(
                "{guild.key_features}",
                (
                    ", ".join(
                        [
                            feature.replace("_", " ").title()
                            for feature in guild.features
                        ]
                    )
                    or "N/A"
                ),
            )
            .replace("{guild.count}", f"{guild.member_count:,}")
            .replace("{guild.emoji_count}", f"{len(guild.emojis):,}")
            .replace("{guild.role_count}", f"{len(guild.roles):,}")
            .replace("{guild.boost_count}", f"{guild.premium_subscription_count:,}")
            .replace("{guild.boost_tier}", str(guild.premium_tier or "No Level"))
            .replace("{guild.max_presences}", f"{(guild.max_presences or 0):,}")
            .replace("{guild.max_members}", f"{guild.max_members:,}")
            .replace(
                "{guild.max_video_channel_users}", f"{guild.max_video_channel_users:,}"
            )
            .replace("{guild.afk_timeout}", f"{guild.afk_timeout:,}")
            .replace(
                "{guild.afk_channel}",
                (guild.afk_channel.mention if guild.afk_channel else "N/A"),
            )
            .replace(
                "{guild.channels}",
                (", ".join([channel.name for channel in guild.channels]) or "N/A"),
            )
            .replace("{guild.channels_count}", f"{len(guild.channels):,}")
            .replace(
                "{guild.text_channels}",
                (", ".join([channel.name for channel in guild.text_channels]) or "N/A"),
            )
            .replace("{guild.text_channels_count}", f"{len(guild.text_channels):,}")
            .replace(
                "{guild.voice_channels}",
                (
                    ", ".join([channel.name for channel in guild.voice_channels])
                    or "N/A"
                ),
            )
            .replace("{guild.voice_channels_count}", f"{len(guild.voice_channels):,}")
            .replace(
                "{guild.category_channels}",
                (", ".join([channel.name for channel in guild.categories]) or "N/A"),
            )
            .replace("{guild.category_channels_count}", f"{len(guild.categories):,}")
        )

    if (channel := vars.get("channel")) and isinstance(channel, TextChannel):
        script = (
            script.replace("{channel}", str(channel))
            .replace("{channel.name}", channel.name)
            .replace("{channel.mention}", channel.mention)
            .replace("{channel.id}", str(channel.id))
            .replace("{channel.topic}", str(channel.topic or "N/A"))
            .replace("{channel.type}", channel.type.name)
            .replace(
                "{channel.category}",
                str(channel.category.name if channel.category else "N/A"),
            )
            .replace(
                "{channel.category_name}",
                str(channel.category.name if channel.category else "N/A"),
            )
            .replace(
                "{channel.category_id}",
                str(channel.category.id if channel.category else "N/A"),
            )
            .replace("{channel.position}", str(channel.position))
            .replace("{channel.slowmode_delay}", str(channel.slowmode_delay))
        )

    return script


def parse(
    script: str,
    **vars,
) -> ScriptObject:
    model = ScriptObject(
        script,
        view=View(),
    )

    compiled = compile(script, **vars)
    parser.parse(
        compiled,
        env={
            "model": model,
        },
    )

    if not model:
        model.content = compiled

    return model
