import discord, os, datetime, aiosqlite, jishaku, random, aiomysql, difflib, aiohttp, json, nacl, traceback, asyncio, sys, textwrap
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from modules import utils
from modules import cache, prefix, extensions, logging, watcherr
from cogs.voice import interfacebuttons
from utils import maria

done = utils.emoji("done")
fail = utils.emoji("fail")
warn = utils.emoji("warn")
reply = utils.emoji("reply")
dash = utils.emoji("dash")
#
success = utils.color("done")
error = utils.color("fail")
warning = utils.color("warn")


class vile(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db2 = maria.MariaDB(self)
        self.db = utils.read_json
        self.db.get = utils.read_json
        self.db.put = utils.write_json
        self.utils = utils
        self.os = os
        self.color = 0xB1AAD8
        self.done = "<:v_done:1010717995099758634>"
        self.fail = "<:v_warn:1010718010828390400>"
        self.reply = "<:vile_reply:997487959093825646>"
        self.dash = "<:vile_dash:998014671107928105>"
        self.removebg_api = [
            "52tiT5sgHQxoVBoQhvXPPaEy",
            "stFyKj4GTUY3CUPFYKWmt57V",
            "nFXg4MpkATXYVHcJM5J9hq1L",
        ]
        self.logger = logging
        self.owner_ids = [
            839221856976109608,
            812126383077457921,
            352190010998390796,
            979978940707930143,
            461914901624127489,
        ]
        self.footerIcon = "https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless"
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
        self.cache = cache.Cache(self)
        self.rival_key = '48108339-2e9e-4bab-bae5-55cf5d63bfec'
        self.rival_api='48108339-2e9e-4bab-bae5-55cf5d63bfec'

    async def setup_hook(self) -> None:
        self.loop.create_task(self.db2.initialize_pool())
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.loop.create_task(self.cache.initialize_settings_cache())
        self.add_view(interfacebuttons())

    async def get_user_data(self, user):

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.rival.rocks/user", headers={'api-key': self.rival_api},
                params={"user_id": user.id},
            ) as resp:
                return self.utils.obj(**(await resp.json())["data"])

    async def find_member(self, guild: discord.Guild, name: str = None):
        members = [m.name.lower() for m in guild.members]
        closest = difflib.get_close_matches(name.lower(), members, n=3, cutoff=0.5)
        if closest:
            for m in guild.members:
                if m.name.lower() == closest[0].lower():
                    member = m

            return member
        else:
            raise commands.MemberNotFound(name)

    @property
    def owner(self) -> discord.User:
        return self.get_user(812126383077457921)

    @property
    def user_count(self) -> int:
        return sum(len(g.members) for g in self.guilds)

    @property
    def guild_count(self) -> int:
        return len(self.guilds)


bot = vile(
    command_prefix=prefix.prefix,
    description="free multipurpose bot",
    intents=discord.Intents.all(),
    help_command=None,
    activity=discord.Streaming(
        name="in discord.gg/heist", url="https://twitch.tv/sosaghostie"
    ),
    strip_after_prefix=True,
    allowed_mentions=discord.AllowedMentions(
        everyone=False, replied_user=False, users=True, roles=True
    ),
    max_messages=500,
)


@bot.event
async def on_ready():

    await extensions.load(bot)
    bot.uptime = datetime.now()
    watcher1 = watcherr.RebootRunner(bot, path='cogs', preload=False)
    watcher2=watcherr.RebootRunner(bot, path='events', preload=False)
    watcher3=watcherr.RebootRunner(bot, path='modules', preload=False)
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
                        color=0x2F3136,
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
async def blacklist_check(ctx):

    db = ctx.bot.db("prefixes")
    if db.get(str(ctx.author.id)):
        x = db[str(ctx.author.id)]["prefix"]
        if x == "…":
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
async def data_check(ctx):

    db = ctx.bot.db("nodata")
    if not db.get(str(ctx.author.id)):

        class bttns(discord.ui.View):
            def __init__(self, invoker: discord.User | discord.Member = None):
                self.invoker = invoker
                super().__init__(timeout=30)

            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=False,
                emoji=utils.emoji("done"),
            )
            async def data_true(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                if interaction.user.id != self.invoker.id:
                    return

                x = interaction.client.db("nodata")
                x[str(interaction.user.id)] = {}
                x[str(interaction.user.id)]["data"] = True
                interaction.client.db.put(x, "nodata")
                await bot.process_commands(ctx.message)
                await interaction.response.edit_message(view=None)
                await interaction.response.send_message(":thumbsup:")

            @discord.ui.button(
                style=discord.ButtonStyle.grey,
                disabled=False,
                emoji=utils.emoji("fail"),
            )
            async def data_false(
                self, interaction: discord.Interaction, button: discord.Button
            ):
                if interaction.user.id != self.invoker.id:
                    return

                x = interaction.client.db("nodata")
                x[str(interaction.user.id)] = {}
                x[str(interaction.user.id)]["data"] = False
                interaction.client.db.put(x, "nodata")
                await interaction.response.edit_message(view=None)
                await interaction.response.send_message(":thumbsup:")

        await ctx.reply(
            embed=discord.Embed(
                color=utils.color("warn"),
                description=f"{utils.emoji('warn')} {ctx.author.mention}**:** do you **agree** to vile's [**privacy policy**](https://tiny.cc/vilebot/privacy-policy)",
            ),
            view=bttns(invoker=ctx.author),
        )
        return False
    else:
        return db[str(ctx.author.id)]["data"] == True


if __name__ == "__main__":
    bot.run(utils.read_json("config")["token"], log_level=20)
