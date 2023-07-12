from aiohttp import ClientSession, TCPConnector, ClientTimeout
import socket
import json
from pydantic import create_model, BaseModel
from typing import Dict, List
from discord.gateway import DiscordWebSocket



def Model(data: Dict | List) -> BaseModel:
    if "data" in data:
        data = data["data"]

    raw = json.dumps(data).replace("#text", "text")
    data = json.loads(raw)

    if isinstance(data, dict):
        field_definitions = {}

        for key, value in data.items():
            if isinstance(value, dict):
                field_definitions[key] = (Model(value), ...)

            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    field_definitions[key] = (
                        list[Model(value[0])],
                        ...,
                    )
                else:
                    field_definitions[key] = (list, ...)

            else:
                field_definitions[key] = (value.__class__, ...)

    elif isinstance(data, list):
        definitions = []

        for value in data:
            definitions.append(Model(value))

        return definitions
    else:
        raise TypeError(f"Unexpected type: {type(data)}")

    model = create_model("model", **field_definitions)

    return model(**data)

class ClientSes(ClientSession):
    def __init__(self, *args, **kwargs):
        super().__init__(
            connector=TCPConnector(family=socket.AF_INET),
            timeout=ClientTimeout(total=15),
            raise_for_status=True,
            json_serialize=json.dumps,
        )

    async def request(self, method, url, **kwargs):
        response = await super().request(method, url, **kwargs)

        if response.content_type in ("application/json", "text/javascript"):
            return Model(await response.json(content_type=None))
        elif 'text' in response.content_type:
            return await response.text()
        else:
            return await response.read()



async def identify(self) -> None:
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": "Discord iOS",
                "$browser": "Discord iOS",
                "$device": "iOS",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
        },
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload["d"]["shard"] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload["d"]["presence"] = {
            "status": state._status,
            "game": state._activity,
            "since": 0,
            "afk": False,
        }

    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value

    await self.call_hooks(
        "before_identify", self.shard_id, initial=self._initial_identify
    )
    await self.send_as_json(payload)


DiscordWebSocket.identify = identify