import discord, os, datetime, aiohttp, sys, json
from datetime import datetime, timezone, timedelta
from discord.ext import commands
from modules import utils
from modules import prefix, extensions, logging, watcherr
from io import BytesIO
from pymongo import MongoClient
from data.database import Async


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

with open("db\config.json") as f:
   config = json.load(f)

class miro(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = utils.read_json
        self.db.get = utils.read_json
        self.db.put = utils.write_json
        self.utils = utils
        self.os = os
        self.cluster = MongoClient(config["mongo"])
        self.warning = "<:mirow:1117144157992009728>"
        self.yes = "<:miroapprove:1117144152363245638>"
        self.no = "<:mirodeny:1117144156507209829>"
        self.color = 0x4c5264
        self.done = "<:miroapprove:1117144152363245638>"
        self.fail = "<:mirodeny:1117144156507209829>"
        self.reply = "<:miroreply:1107719722394456065>"
        self.dash = "<:c_dashblue:1107721692568096768>"
        self.logger = logging
        self.owner_ids = [129857040855072768, 892736570602455051]
        self.footerIcon = "https://cdn.discordapp.com/attachments/1116443743831199814/1118245305352200332/Cherry_Blossoms.png"
        self.exact_start = datetime.now()
        self.aiter = self.utils.aiter
        self.global_cd = commands.CooldownMapping.from_cooldown(
            3, 5, commands.BucketType.member
        )
        self.colors = {
            "grey": 30,
            "red": 31,
            "green": 32,
            "yellow": 33,
            "blue": 34,
            "magenta": 35,
            "cyan": 36,
            "white": 37,
        }
        self.send_color = lambda n, m: f"[{self.colors[n]}m{m}[0m"


    async def paginator(self, ctx, pages):
        if len(pages) == 1:
            await ctx.send(embed=pages[0])
            return

        def check(interaction):
            if interaction.user.id != ctx.author.id:
                return False

        class PaginatorView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.bot = ctx.bot
                self.current = 0

            @discord.ui.button(style=discord.ButtonStyle.gray, label="<")
            async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
                if check(interaction) is False:
                    return interaction.response.defer()
                if self.current == 0 or self.current < 0:
                    await interaction.response.defer()
                    return
                try:
                    self.current -= 1
                    await interaction.response.edit_message(embed=pages[self.current])
                except:
                    await interaction.response.defer()

            @discord.ui.button(label=">", style=discord.ButtonStyle.gray)
            async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
                if check(interaction) is False:
                    return interaction.response.defer()
                if self.current == len(pages) - 1:
                    await interaction.response.defer()
                    return
                self.current += 1
                try:
                    await interaction.response.edit_message(embed=pages[self.current])
                except:
                    await interaction.response.defer()

            @discord.ui.button(label="x", style=discord.ButtonStyle.red)
            async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
                if check(interaction) is False:
                    return interaction.response.defer()
                await interaction.response.edit_message(content=":thumbsup_tone2: Stopped interaction", embed=None, view=None)
                self.stop()
                
        paginator = PaginatorView()
        await ctx.send(embed=pages[0], view=paginator)
        await paginator.wait()



    async def setup_hook(self) -> None:
        self.loop.create_task
        self.session = aiohttp.ClientSession(loop=self.loop)

    @property
    def owner(self) -> discord.User:
        return self.get_user(129857040855072768)

    @property
    def user_count(self) -> int:
        return sum(len(g.members) for g in self.guilds)

    @property
    def guild_count(self) -> int:
        return len(self.guilds)

    async def getbyte(self, video: str):
        return BytesIO(await self.session.read(video, proxy=self.proxy_url, ssl=False))


bot = miro(
    command_prefix=prefix.prefix,
    description="multipurpose bot",
    intents=discord.Intents.all(),
    help_command=None,
    activity=discord.Game(name=";help"),
    strip_after_prefix=True,
    allowed_mentions=discord.AllowedMentions(
        everyone=False, replied_user=False, users=True, roles=True
    ),
    max_messages=2000,
)

async def mobile(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": sys.platform,
                "$browser": "Discord iOS",
                "$device": "discord.py",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
            "v": 3,
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
            "afk": True,
        }
    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value
    await self.call_hooks(
        "before_identify", self.shard_id, initial=self._initial_identify
    )
    await self.send_as_json(payload)
discord.gateway.DiscordWebSocket.identify = mobile


@bot.event
async def on_ready():
    await extensions.load(bot)
    bot.uptime = datetime.now()
    watcher1 = watcherr.RebootRunner(bot, path="cogs", preload=False)
    watcher2 = watcherr.RebootRunner(bot, path="events", preload=False)
    watcher3 = watcherr.RebootRunner(bot, path="modules", preload=False)
    await watcher1.start()
    await watcher2.start()
    await watcher3.start()

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    db = bot.db("afk")
    if db.get(str(message.author.id)):
        if db.get(str(message.author.id)).get("lastseen"):
            ls = utils.moment(
                datetime.fromtimestamp(
                    int(db.get(str(message.author.id)).get("lastseen"))
                )
            )
    if db.get(str(message.author.id)):
        context = await bot.get_context(message)
        if not context.invoked_with:
            if db.get(str(message.author.id)).get("guild"):
                if message.guild.id in db.get(str(message.author.id)).get("guild"):
                    db.pop(str(message.author.id))
                    bot.db.put(db, "afk")
                    embed = discord.Embed(
                        color=0x4c5264,
                        description=f":wave: {message.author.mention}**:** welcome back, you were last seen **{ls} ago**",
                    )
                    return await message.reply(embed=embed)

    await bot.process_commands(message)

# checks
@bot.check
async def cooldown_check(ctx):
    bucket = ctx.bot.global_cd.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        raise commands.CommandOnCooldown(
            bucket, retry_after, commands.BucketType.member
        )
    return True

@bot.check
async def disabled_command_check(ctx):
    db = bot.db("disabled")
    if db.get(str(ctx.guild.id)):
        if ctx.command.name in db[str(ctx.guild.id)]:
            return False
    return True


@bot.check
async def ignoredchannel_check(ctx):
    db = ctx.bot.db("ignorechannel")
    if db.get(str(ctx.guild.id)):
        if ctx.channel.id in db[str(ctx.guild.id)]:
            return False
    return True


@bot.check
async def developer_check(ctx):
    if ctx.command.qualified_name in ("jishaku shell", "jishaku debug"):
        if not ctx.author.id == 129857040855072768:
            return False
    if ctx.command.hidden:
        if not await ctx.bot.is_owner(ctx.author):
            return False
    return True


if __name__ == "__main__":
    bot.run(utils.read_json("config")["token"], log_level=20)
