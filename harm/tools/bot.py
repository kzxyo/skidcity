import os
import dotenv
import asyncpg
import discord 
import datetime 
import humanize
import sys

from typing import Optional
from discord.ext import commands 

from tools.help import HarmHelp
from cogs.autopfp import autopfp_loop
from tools.context import HarmContext

dotenv.load_dotenv(verbose=True)

class DiscordBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix = commands.when_mentioned_or(";"),
            intents = discord.Intents.all(),
            owner_ids = [
                1148300105758298123, 
                371224177186963460
            ],
            member_cache = discord.MemberCacheFlags(
                voice=True, 
                joined=True
            ),
            case_insensitive = True, 
            help_command=HarmHelp(),
            allowed_mentions = discord.AllowedMentions(
                everyone=False,
                roles=False,
                replied_user=False 
            )
        )
        
        self.channel_cd = commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.channel)
        self.user_cd = commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.user)
        self.started = datetime.datetime.now()  
        self.color = 0x2f3136
        self.pfps = {
           'male_png': open('./pfps/male_pfps.txt').read().splitlines(),
           'female_png': open("./pfps/female_pfps.txt").read().splitlines(),
           'anime_png': open("./pfps/anime_pfps.txt").read().splitlines(),
           'male_gif': open("./pfps/male_gifs.txt").read().splitlines(),
           'female_gif': open("./pfps/female_gifs.txt").read().splitlines(),
           'anime_gif': open("./pfps/anime_gifs.txt").read().splitlines()
        }

    def __str__(self):
        return f"{self.user} ({self.user.id})"
    
    def run(self):
        return super().run(
            os.environ['token'],
            reconnect=True
        )
    
    def channel_cooldown(self, message: discord.Message) -> Optional[int]:
        bucket = self.channel_cd.get_bucket(message)
        return bucket.update_rate_limit()
    
    def user_cooldown(self, message: discord.Message) -> Optional[int]:
        bucket = self.user_cd.get_bucket(message)
        return bucket.update_rate_limit()

    def cooldown(self, message: discord.Message) -> bool: 
        if self.channel_cooldown(message) or self.user_cooldown(message):
            return True 

        return False

    @property
    def uptime(self):
        """the amount of time the bot has been online for"""
        return humanize.precisedelta(
            self.started, 
            format="%0.0f"
        )

    async def connect_db(self) -> asyncpg.Pool:
        """connect asynchronously to a postgresql database"""
        self.db = await asyncpg.create_pool(
            user="postgres",
            database="postgres",
            password="harmbot",
            port=5432,
            host="localhost"
        )
    
    async def get_context(self, message: discord.Message, cls=HarmContext):
        return await super().get_context(
            message,
            cls=cls
        )

    async def load_cogs(self):
        """loading the bot's cogs""" 
        await self.load_extension("jishaku")
        print("Loaded jishaku") 

        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                try: 
                    await self.load_extension(f"cogs.{file[:-3]}")
                    print(f"Loaded cog {file}")
                except: 
                    print(f"Unable to load {file}")    

    async def setup_hook(self) -> None: 
        await self.connect_db()
        print("Connecting to Discord's API")
        self.invite_url = discord.utils.oauth_url(
            client_id=self.user.id, 
            permissions=discord.Permissions(8)
        )
        await self.load_cogs()
    
    async def on_ready(self):
        autopfp_loop.start(self)
        print(f"Bot is ready as {self}\n{len(self.guilds)} servers & {sum(g.member_count for g in self.guilds):,} users")

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content != after.content: 
            return await self.process_commands(after)

    async def on_message(self, message: discord.Message):
        if not message.author.bot: 
            if message.guild:  
                if not self.cooldown(message): 
                    if not await self.db.fetchrow("SELECT * FROM blacklisted WHERE user_id = $1", message.author.id):   
                        if message.content == self.user.mention: 
                            return await message.reply(embed=discord.Embed(description="> my prefix for this guild is `;`", color= 0x2f3136)) 

                        return await self.process_commands(message)   
                    
    async def on_command_error(
        self,
        ctx: HarmContext,
        error: commands.CommandError
    ):
        to_ignore = [
            commands.NotOwner,
            commands.CommandOnCooldown,
            commands.CommandNotFound
        ]
        if isinstance(error, tuple(to_ignore)):
            return 

        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help(ctx.command)
        
        if isinstance(error, commands.CheckFailure):
            if isinstance(error, commands.MissingPermissions):
                return await ctx.error(f"You need the following permission to use **{ctx.command.qualified_name}**: `{error.missing_permissions[0]}`")

        return await ctx.error(error.args[0])                


async def mobile(self):
    payload = {'op': self.IDENTIFY,'d': {'token': self.token,'properties': {'$os': sys.platform,'$browser': 'Discord iOS','$device': 'discord.py','$referrer': '','$referring_domain': ''},'compress': True,'large_threshold': 250,'v': 3}}
    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]
    state = self._connection
    if state._activity is not None or state._status is not None: 
        payload["d"]["presence"] = {"status": state._status, "game": state._activity, "since": 0, "afk": True}
    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value
    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)
discord.gateway.DiscordWebSocket.identify = mobile