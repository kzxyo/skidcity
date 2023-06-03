import asyncio
import os
import discord
from discord.ext import commands
import asyncpg
import traceback
import dotenv
import os
import datetime
import secrets
import jishaku
from session import Http

dotenv.load_dotenv()

intents = discord.Intents.all()

async def get_prefix(bot, message):
    default_prefix = [";"]
    if not message.guild:
        return commands.when_mentioned_or(*default_prefix)(bot, message)

    db_prefixes = await bot.db.fetchrow("SELECT * FROM guild_prefixes WHERE guild_id = $1", message.guild.id)
    if db_prefixes:
        prefixes = db_prefixes["prefixes"]
        return commands.when_mentioned(*prefixes)(bot, message)
    else:
        return commands.when_mentioned_or(*default_prefix)(bot, message)

class pretend(commands.AutoShardedBot):
    emojis=None
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True, replied_user=False),
            intents=intents,
            help_command=None,
            owner_ids=[
                1078962964662591528, # marian
                1071108000317714452, # hammer <3
                1006275329217794068 # skill
            ],
            activity=discord.Activity(
               type=discord.ActivityType.competing, name=";help"
            ),
            status=discord.Status.dnd,
        )
        self.color = 0x6d827d
        self.session = Http() 

    async def load_cogs(self):
        await self.load_extension("jishaku")
        for category in os.listdir('cogs'):
            if category == "__pycache__": continue
            for file in os.listdir(f"cogs/{category}"):
                if file.endswith(".py") and not file.startswith("_"):
                    try: await self.load_extension(f"cogs.{category}.{file[:-3]}")
                    except Exception as e: print(f"Failed to load cog: {category}/{file[:-3]}: {e}")

    async def setup_hook(self):
        
        self.db = await asyncpg.create_pool(
            database=os.getenv('database'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            host=os.getenv('host'),
        )
        self.emojis = {
            "stop": "<:stop:1103620492285456444>"
        }
        with open("tables.sql", "r") as f:
            await self.db.execute(f.read())

        await self.load_cogs()

    async def on_ready(self):
        print(f"Running on {len(self.guilds)} guild(s) and {len(self.users)} user(s)!")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CheckFailure):
            return await ctx.reply(f"{error}")
        if isinstance(error, commands.CommandNotFound):
            return await ctx.message.add_reaction(self.emojis["stop"])
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply(embed=discord.Embed(description="You are missing the following permissions: " + ", ".join(error.missing_permissions), color=self.color))
        if isinstance(error, commands.BotMissingPermissions):
            return await ctx.reply(embed=discord.Embed(description="I am missing the following permissions: " + ", ".join(error.missing_perms), color=self.color))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description=f"Missing required argument `<{error.param.name}>`", color=self.color)
            if ctx.command.usage:
                embed.add_field(name="Usage", value=f"```bf\n{ctx.command.usage}```")
            return await ctx.reply(embed=embed)
        if isinstance(error, commands.BadArgument):
            em = discord.Embed(description=f"Bad argument `<{error.param.name}>`", color=self.color)
            em.description = f"{error}"
            if ctx.command.usage:
                em.add_field(name="Usage", value=f"```bf\n{ctx.command.usage}```")
            return await ctx.reply(embed=em)
        if isinstance(error, commands.CommandError):
            if "403 Forbidden" in str(error):
                await ctx.reply(embed=discord.Embed(description=f"I am missing permissions to execute **{f'{ctx.parent} ' if ctx.parent else ''}{ctx.command.name}**", color=self.color))
                return
            rns = secrets.token_hex(5)
            em = discord.Embed(description=f"{self.emojis['stop']} An error occured. Please report this to the developer with the error code `{rns}`\n{error}", color=self.color)
            await ctx.reply(embed=em)
            async with self.db.acquire() as conn:
                await conn.execute(
                    "INSERT INTO errors (error, command, message_url, user_id, time, id) VALUES ($1, $2, $3, $4, $5, $6)",
                    str(error)[29:],
                    ctx.command.name,
                    ctx.message.jump_url,
                    ctx.author.id,
                    datetime.datetime.now(),
                    rns
                )
            traceback.print_exception(type(error), error, error.__traceback__)
            return

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
                await interaction.response.edit_message(content=":thumbsup_tone5: Stopped interaction", embed=None, view=None)
                self.stop()
                
        paginator = PaginatorView()
        await ctx.send(embed=pages[0], view=paginator)
        await paginator.wait()

    async def prefix(self, message):
        default_prefix = [";"]
        if not message.guild:
            return default_prefix
        return await client.db.fetchval("SELECT prefixes FROM guild_prefixes WHERE guild_id = $1", message.guild.id) or default_prefix

client = pretend()
client.run(os.getenv("token"))