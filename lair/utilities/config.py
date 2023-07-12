import os
import re
from typing import List

owner_ids: List[int] = [1105178083977334864, 1093956521332838453, 461914901624127489, 384905496819138561]
default_prefix: str = ","
tokens: str = ["MTAzNzM3OTQ5ODA5MTQ5OTU3MA.GHYKVm.trC3xsXu1lv1LN3vZRSRi5WTXCjIzRuipsEebQ"]
redis: str = "redis://:KdUq58aASsRss5955T93qsrdx8HhYaBRNbf731zLJRdEvpeSGSCdGGCcY8SZeXGBDiWmrLLHz118np6T@127.0.0.1:6379"
IMAGE_URL = re.compile(r"(?:http\:|https\:)?\/\/.*\.(?P<mime>png|jpg|jpeg|webp|gif)")
worker_tokens = ['MTA5Mzk1NjUyMTMzMjgzODQ1Mw.Gg3Cal.zdu_duZ6fcZFDSs1uL8a4Ds7YL5v28pQ38Qt7E']
URL = re.compile(r"(?:http\:|https\:)?\/\/[^\s]*")
LairAPIKey: str = "tuuid:L5DYOiOFDjI2lqDY"

class Proxy:
    http: str = "http://qintykci-rotate:nxd3doqn8svz@p.webshare.io:80/"
    https: str = "http://qintykci-rotate:nxd3doqn8svz@p.webshare.io:80/"
    LA: str = "http://qintykci:nxd3doqn8svz@2.56.119.93:5074/"
    spain: List[str] = ["http://qintykci:nxd3doqn8svz@185.199.228.220:7300/", "http://qintykci:nxd3doqn8svz@185.199.229.156:7492/", "http://qintykci:nxd3doqn8svz@185.199.231.45:8382/", "http://qintykci:nxd3doqn8svz@154.95.36.199:6893/"]
    italy: List[str] = ["http://qintykci:nxd3doqn8svz@188.74.210.207:6286/", "http://qintykci:nxd3doqn8svz@188.74.183.10:8279/", "http://qintykci:nxd3doqn8svz@188.74.210.21:6100/"]
    netherlands: List[str] = ["http://qintykci:nxd3doqn8svz@45.155.68.129:8133/", "http://qintykci:nxd3doqn8svz@154.95.36.199:6893/"]


class Database:
    name: str = "lair"
    user: str = "postgres"
    host: str = "localhost"
    port: int = 5432
    password: str = "lair"


class Color:
    done: int = 0xACD8A7
    main: int = 2829617
    error: int = 0xFAA61A
    warning: int = 16414073
    music: int = 7384037


class Emoji:
    done: str = "<:tick:1120738414292119713>"
    error: str = "<:emoji_7:1067186202626768957>"
    warning: str = "<:x_:1104809324108337193>"
    goto: str = "<:goto:1117780969886326834>"
    previous: str = "<:prev:1117780989989621760>"
    next: str = "<:next:1117781087670763640>"
    stop: str = "<:xxx:1119232897124143174>"
    first: str = "<:first:1117781040296112188>"
    last: str = "<:last:1117781139743068210>"
    on: str = "<:enabled:1096523187468107807>"
    off: str = "<:disabled:1096523240303759462>"
    music: str = "🎵"
    loading: str = '🔃'


class Start:
    async def load(self):
        try:
            for file in os.listdir("events"):
                if file.endswith(".py"):
                    try:
                        await self.load_extension(f"events.{file[:-3]}")
                    except Exception as e:
                        raise e
            for file in os.listdir("cogs"):
                if file.endswith(".py"):
                    try:
                        await self.load_extension(f"cogs.{file[:-3]}")
                    except Exception as e:
                        raise e
            for file in os.listdir('utilities/webserver'):
                if file.endswith('.py'):
                    try:
                        await self.load_extension(f"utilities.webserver.{file[:-3]}")
                    except Exception:
                        raise
        except Exception as error:
            raise error