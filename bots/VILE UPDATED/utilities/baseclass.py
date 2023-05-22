import discord, difflib, os, jishaku, arrow, pathlib, random
from aiohttp import BasicAuth
from utilities import DL, utils, confirmation, models, config
from utilities.redis import VileRedis
from utilities.cache import VileCache

from utilities.context import Context
from utilities.vileapi import VileAPI
from utilities.maria import MariaDB
from typing import Optional, Union, Any
from datetime import datetime, timedelta
from discord.ext import commands, tasks


class Vile(commands.AutoShardedBot):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.color = self.config.colors.main
        self.done = self.config.emojis.done
        self.fail = self.config.emojis.fail
        self.reply = self.config.emojis.reply
        self.dash = self.config.emojis.dash
        self.afk = self.config.emojis.afk
        self.enabled = self.config.emojis.enabled
        self.disabled = self.config.emojis.disabled
        self.db = MariaDB()
        self.cache = VileCache(self)
        self.session = DL
        self.prefix = self.config.bot.prefix
        self.version = self.config.bot.version
        self.invite = self.config.bot.invite
        self.privacy_policy = self.config.bot.privacy_policy
        self.terms_of_service = self.config.bot.terms_of_service
        self.owner_ids = self.config.bot.owner_ids
        self.snipes = dict()
        self.editsnipes = dict()
        self.reactionsnipes = dict()
        self.uptime = datetime.now()
        self.tasks = dict()
        self.rival_api = self.config.authorization.rival_api
        self.vile_api = VileAPI(self.config.authorization.vile_api)
        self.chatgpt_api = self.config.authorization.chatgpt_api
        self.spam_cd = commands.CooldownMapping.from_cooldown(15, 30, commands.BucketType.member)
        self.global_cd = commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.member)
        

    async def on_message(self, message):
        if not bot.is_ready() or message.guild is None:
            return  
        await super().on_message(message)

        
    async def setup_hook(self) -> None:
        self.redis = await VileRedis.from_url()
        self.loop.create_task(self.db.initialize_pool())
        self.loop.create_task(self.cache.initialize_settings_cache())


    async def get_context(self, origin: Union[discord.Interaction, discord.Message], cls: Any = Context) -> Context:
        return await super().get_context(origin, cls=cls)


    @property
    def owner(self) -> Optional[discord.User]:
        return self.get_user(812126383077457921)


    @property
    def user_count(self) -> int:
        return sum([g.member_count for g in self.guilds])


    @property
    def guild_count(self) -> int:
        return len(self.guilds)

    @property
    def command_count(self) -> int:
        return len(list(self.walk_commands()))

    
    @property
    def line_count(self) -> int:
        return sum(
            [
                len(f.open('r').readlines()) for f in [
                    f for f in pathlib.Path('./').glob('**/*.py') 
                    if f.is_file()
                ]
            ]
        )


    @property
    def coroutine_count(self) -> int:
        return sum(
            [
                len([l for l in f.open('r').readlines() if l.strip().startswith('async def ')]) for f in [
                    f for f in pathlib.Path('./').glob('**/*.py') 
                    if f.is_file()
                ]
            ]
        )


    @property
    def class_count(self) -> int:
        return sum(
            [
                len([l for l in f.open('r').readlines() if l.strip().startswith('class ')]) for f in [
                    f for f in pathlib.Path('./').glob('**/*.py') 
                    if f.is_file()
                ]
            ]
        )
        

    @property
    def function_count(self) -> int:
        return sum(
            [
                len([l for l in f.open('r').readlines() if l.strip().startswith('def ')]) for f in [
                    f for f in pathlib.Path('./').glob('**/*.py') 
                    if f.is_file()
                ]
            ]
        )


    @property
    def import_count(self) -> int:
        return sum(
            [
                len([l for l in f.open('r').readlines() if l.strip().startswith('import ') or l.strip().startswith('from  ') and ' import ' in l.strip()]) for f in [
                    f for f in pathlib.Path('./').glob('**/*.py') 
                    if f.is_file()
                ]
            ]
        )


    @property
    def file_count(self) -> int:
        return len([f for f in pathlib.Path('./').glob('**/*.py') if f.is_file()])


    async def load_extensions(self) -> None:
        if self.cogs:
            for cog in self.cogs:
                try:
                    await self.unload_extension(cog.__module__)
                except:
                    continue

        await self.load_extension('jishaku')
        for folder in ['cogs', 'events']:
            for extension in os.listdir(folder):
                if 'pycache' not in extension:
                    try:
                        await self.load_extension(f'{folder}.{extension[:-3]}')
                        print(f"loaded {extension[:-3]}")
                    except Exception as e:
                        print(f"error loading {extension[:-3]} - {e}")
        print('loaded all extensions')
