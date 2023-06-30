from json import dumps, loads

import aiohttp

from bs4 import BeautifulSoup
from discord.ext.commands import CommandError
from pydantic import BaseModel, create_model
from yarl import URL

import config


def create_model_from_dict(data: dict | list) -> BaseModel:
    if "data" in data:
        data = data["data"]

    raw = dumps(data).replace("#text", "text")
    data = loads(raw)

    if isinstance(data, dict):
        field_definitions = {}

        for key, value in data.items():
            if isinstance(value, dict):
                field_definitions[key] = (create_model_from_dict(value), ...)

            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    field_definitions[key] = (
                        list[create_model_from_dict(value[0])],
                        ...,
                    )
                else:
                    field_definitions[key] = (list, ...)

            else:
                field_definitions[key] = (value.__class__, ...)

    elif isinstance(data, list):
        definitions = []

        for value in data:
            definitions.append(create_model_from_dict(value))

        return definitions
    else:
        raise TypeError(f"Unexpected type: {type(data)}")

    model = create_model("ResponseModel", **field_definitions)

    return model(**data)


class ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            timeout=aiohttp.ClientTimeout(total=15),
            raise_for_status=True,
        )

    async def request(self, *args, **kwargs) -> aiohttp.ClientResponse | dict:
        args = list(args)
        args[1] = URL(args[1])
        raise_for = kwargs.pop("raise_for", {})
        if kwargs.pop("proxy", False):
            kwargs["params"] = {"url": str(args[1]), **kwargs.get("params", {})}
            args[1] = URL(config.proxy_url)

        args = tuple(args)

        try:
            response = await super().request(*args, **kwargs)
        except aiohttp.ClientResponseError as e:
            if error_message := raise_for.get(e.status):
                raise CommandError(error_message)

            raise

        if response.content_type == "text/html":
            return BeautifulSoup(await response.text(), "html.parser")

        elif response.content_type in ("application/json", "text/javascript"):
            return create_model_from_dict(await response.json(content_type=None))

        elif response.content_type.startswith(("image/", "video/", "audio/")):
            return await response.read()

        return response
