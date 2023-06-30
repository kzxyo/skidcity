import typing


class Node:
    __slots__ = ("start", "end", "range", "coord")

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.range = abs(end - start)
        self.coord = (start, end)


class Tag:
    def __init__(self, parser, callback, name, aliases, *, parent=None, **attrs):
        self._tags = []
        self._parser = parser
        self.callback = callback
        self.name = name
        self.aliases = aliases
        self.parent = parent

        for attr, value in attrs.items():
            if attr not in (
                "callback",
                "name",
                "aliases",
                "parent",
                "tag",
                "parser",
                "tags",
            ) and not attr.startswith("_"):
                setattr(self, attr, value)  # Allows things like descriptions

    @property
    def parser(self):
        return self._parser

    @property
    def tags(self):
        return self._tags

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

    def tag(
        self,
        name: str = None,
        *,
        alias: str = None,
        aliases: typing.List[str] = None,
        **attrs
    ):
        if not aliases:
            aliases = [alias] if alias else []

        if self.parser.is_case_insensitive:
            aliases = [alias.lower() for alias in aliases]
            if name:
                name = name.lower()

        def decorator(func):
            name_ = name or func.__name__
            tag_ = Tag(
                self.parser,
                func.callback if isinstance(func, Tag) else func,
                name_,
                aliases,
                parent=self,
                **attrs
            )
            self._tags.append(tag_)
            return tag_

        return decorator


class ParsedTag:
    __slots__ = ("_parser", "_raw", "_tag", "_parent", "_args")

    def __init__(self, parent_parser, raw, *, tag, args):
        self._parser = parent_parser
        self._raw = raw

        self._tag = tag
        self._args = []
        if args:
            self._args = args

    @property
    def tag(self):
        return self._tag

    @property
    def args(self):
        return self._args

    @property
    def parser(self):
        return self._parser

    @property
    def raw(self):
        return self._raw


class Converter:
    __slots__ = ("converter",)

    def __init__(self, converter):
        self.converter = converter

    def __call__(self, *args, **kwargs):
        return self.converter(*args, **kwargs)


class ENV(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
