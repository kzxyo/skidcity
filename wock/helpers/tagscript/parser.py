import inspect
import itertools
import re
import typing

from os import urandom

from .classes import Converter, Node, ParsedTag, Tag


class Parser:
    """
    The base parser.
    This class can be subclassed for custom behaviors.
    """

    def __init__(self, limit: int = None, **attrs):
        self._parse_attrs(attrs)
        self.limit = limit
        self.tags = []
        self.setup()

    def _parse_attrs(self, attrs):
        self._delimiter = attrs.pop("delimiter", None) or r"\:"
        self._argument_delimiter = attrs.pop("argument_delimiter", None) or "&&"
        self._attribute_delimiter = attrs.pop("attribute_delimiter", None) or r"\."
        self._escape_character = attrs.pop("escape_character", "\\") or urandom(32).hex()
        self._start_character = attrs.pop("start_character", None) or r"\{"
        self._end_character = attrs.pop("end_character", None) or r"\}"
        self._case_insensitive = attrs.pop("case_insensitive", True)

    @property
    def is_case_insensitive(self):
        return self._case_insensitive

    def setup(self):
        """
        The setup function for when initiating the parser.
        This is to be used by the user.
        """

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

    def method(
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
                parser=self,
                callback=func.callback if isinstance(func, Tag) else func,
                name=name_,
                description=inspect.getdoc(func),
                aliases=aliases,
                **attrs,
            )
            self.tags.append(tag_)
            return tag_

        return decorator

    def get_nodes(self, content):
        """
        Parses the tag nodes from a string.
        :return: List[Node]
        """
        nodes = []
        buffer = []
        previous = ""

        for i, char in enumerate(content):
            if self._validate_match(self._start_character, char) and previous != self._escape_character:
                buffer.append([i])

            if self._validate_match(self._end_character, char) and previous != self._escape_character:
                if len(buffer) <= 0:
                    continue
                buffer[-1].append(i)
                nodes.append(Node(*buffer[-1]))
                buffer.pop(-1)
            previous = char

        return nodes

    def _base_argument_conversion(self, arg, converter):
        arg = str(arg).strip()
        if converter in (str, int, float):
            try:
                return converter(arg)
            except ValueError:
                return None
        if converter is bool:
            lowered = arg.lower()
            if lowered in ("on", "yes", "true", "enable"):
                return True
            elif lowered in ("off", "no", "none", "null", "false", "disable"):
                return False
            return None
        if isinstance(converter, Converter):
            try:
                conv = converter.converter
                if len(inspect.signature(conv).parameters.values()) > 1:
                    return conv(self, arg)
                return conv(arg)
            except Exception:
                return None

    def do_argument_conversion(self, arg, converter) -> any:
        try:
            origin = converter.__origin__
        except AttributeError:
            pass
        else:
            if origin is typing.Union:
                type(None)
                for conv in converter.__args__:
                    if res := self._base_argument_conversion(arg, conv):
                        return res
                return None
        return self._base_argument_conversion(arg, converter)

    def parse_single_tag(self, tag) -> typing.Optional[ParsedTag]:
        """
        Turns a raw string into a `ParsedTag`.
        :param tag: The string to be parsed.
        :return: A `ParsedTag`.
        """
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
            raise ValueError("Parser callbacks must have at least one parameter (The environment, usually to be named 'env')")
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

                parsed_arguments.append(self.do_argument_conversion(argument, converter))

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

    async def parse_nodes(self, nodes, content, limit):
        """
        Parses a list of nodes to it's content.
        :param nodes: A list of `Nodes` to parse.
        :param content: The content associated with the nodes.
        :return str: The parsed string.
        """
        final = content
        nodes_parsed = 0

        for i, node in enumerate(nodes):
            string = final[node.coord[0] : node.coord[1] + 1]
            string = string.lstrip(self._start_character)
            string = string.rstrip(self._end_character) or ""
            parsed_tag = self.parse_single_tag(string)
            try:
                value = await parsed_tag.tag.callback(None, *parsed_tag.args)
                value = "" if value is None else str(value)
            except AttributeError:
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

    async def parse(self, string, *, limit=None):
        nodes = self.get_nodes(string)
        return await self.parse_nodes(nodes, string, limit)
