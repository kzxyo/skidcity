import asyncio
import datetime
import time
import json
import logging
import asyncio
import random
import matplotlib.pyplot as plt
import io
from discord.ext.commands import Group
from aiohttp import web
from ..managers import Wrench
from typing import List

_log = logging.getLogger(__name__)


class event_loop_manager:
    def __init__(self):
        self.loop = None

    async def __aenter__(self):
        self.loop = asyncio.get_event_loop()
        return self.loop

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self.loop.is_closed():
            self.loop.stop()
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

class WebServer(Wrench):
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.app.router.add_get('/users', self.users)
        self.app.router.add_get('/guilds', self.guilds)
        self.app.router.add_get('/keys', self.api_keys)
        self.app.router.add_get('/commands', self.commandz)
        self.app.router.add_get('/shards', self.shards)
        self.app.router.add_get('/avatars', self.avatarz)

    async def cog_load(self):
        self.bot.loop.create_task(self.run())

    async def avatarz(self, request: web.Request) -> web.Response:
        user_id = request.headers.get('user_id')
        avatars = await self.bot.db.fetch('SELECT * FROM avatars WHERE user_id = $1 ORDER BY time DESC', int(user_id))
        if not avatars:
            return web.Response(status=404)
        out: dict = {
            "user_id": avatars[0]['user_id'],
            "username": avatars[0]['username'],
            "avatar": []
        }
        for i in avatars:
            out['avatar'].append(i['avatar'])
        print(out)
        return web.Response(text=json.dumps(out), content_type='application/json')

    async def users(self, request: web.Request) -> web.Response:
        info: int = len(self.bot.users)
        return web.Response(text=str(info))
    
    async def guilds(self, request: web.Request) -> web.Response:
        info: int = len(self.bot.guilds)
        return web.Response(text=str(info))

    async def api_keys(self, request: web.Request) -> web.Response:
        api_keys = await self.bot.db.fetchdict('SELECT api_key FROM api_keys')
        api_keys = [i['api_key'] for i in api_keys]
        json_data = json.dumps(api_keys)
        return web.Response(text=json_data, content_type='application/json')

    async def shards(self, request: web.Request) -> web.Response:
        shards = []
        for k, v in self.bot.shards.items():
            shard_id = k
            is_connected = True if not v.is_closed() else False
            servers = len([guild for guild in self.bot.guilds if guild.shard_id == k])
            users = sum(len(guild.members) for guild in self.bot.guilds if guild.shard_id == k)
            latency = round(v.latency * 1000, 1)

            shards.append({
                "shard_id": shard_id,
                "is_connected": is_connected,
                "servers": servers,
                "users": users,
                "latency": latency,
                "updated": time.time()
            })

        return web.Response(text=json.dumps(shards), content_type="application/json")
    
    async def commandz(self, req: web.Request) -> web.Response:
        output = ''
        for name, cog in sorted(self.bot.cogs.items(), key=lambda cog: cog[0].lower()):
            if name.lower() in ("jishaku", "developer"):
                continue

            _commands = list()
            for command in cog.walk_commands():
                if command.hidden:
                    continue

                usage = " " + command.usage if command.usage else ""
                aliases = "(" + ", ".join(command.aliases) + ")" if command.aliases else ""
                if isinstance(command, Group) and not command.root_parent:
                    _commands.append(f"|    ├── {command.name}{aliases}: {command.brief or 'No description'}")
                elif not isinstance(command, Group) and command.root_parent:
                    _commands.append(f"|    |   ├── {command.qualified_name}{aliases}{usage}: {command.brief or 'No description'}")
                elif isinstance(command, Group) and command.root_parent:
                    _commands.append(f"|    |   ├── {command.qualified_name}{aliases}: {command.brief or 'No description'}")
                else:
                    _commands.append(f"|    ├── {command.qualified_name}{aliases}{usage}: {command.brief or 'No description'}")

            if _commands:
                output += f"┌── {name}\n" + "\n".join(_commands) + "\n"

        out = json.dumps(output)
        return web.Response(text=out, content_type="application/json")

    
    async def commands(self, request: web.Request) -> web.Response:
        data = []
        for name, cog in sorted(self.bot.cogs.items(), key=lambda cog: cog[0].lower()):
            if name.lower() in ('jishaku', 'developer'):
                continue

            commands = []
            for command in cog.walk_commands():
                usage = command.usage or 0
                description = command.brief or "No Description"
                aliases = "(" + ", ".join(command.aliases) + ")"
                permissions = command.perms or 0

                commands.append({
                    "name": command.qualified_name,
                    "aliases": aliases,
                    "usage": usage,
                    "description": description,
                    "permissions": permissions
                })
            
            if commands:
                data.append({
                    "name": name,
                    "commands": commands
                })
        
        out = json.dumps(data)
        return web.Response(text=out, content_type="application/json")

    async def run(self, host='127.0.0.1', port=1337):
        await web._run_app(self.app, host=host, port=port, print=None)

    def __repr__(self) -> str:
        return "<Webserver host=127.0.0.1 port=1337>"

async def setup(bot) -> None:
    await bot.add_cog(WebServer(bot))