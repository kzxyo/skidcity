import discord, os, sys, asyncio, aiohttp, subprocess, datetime, textwrap, copy, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils, paginator as pg
from discord import app_commands
from jishaku.codeblocks import codeblock_converter

import collections
import typing


class owner(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
        #
        self.done = utils.emoji("done")
        self.fail = utils.emoji("fail")
        self.warn = utils.emoji("warn")
        self.reply = utils.emoji("reply")
        self.dash = utils.emoji("dash")
        #
        self.success = utils.color("done")
        self.error = utils.color("fail")
        self.warning = utils.color("warn")
        #
        self.av = "https://cdn.discordapp.com/attachments/989422588340084757/1008195005317402664/vile.png"

    # @commands.command()
    # @commands.is_owner()
    # async def eval(self, ctx, *, code: str):
    #
    #    code = code.replace('self.', '')
    #    args = {
    #        "discord": discord,
    #        "sys": sys,
    #        "os": os,
    #        "bot": self.bot,
    #        "ctx": ctx,
    #        "channel": ctx.channel,
    #        "guild": ctx.guild,
    #        "datetime": datetime,
    #        "time": time,
    #        "random": random,
    #        "json": json,
    #        #"uptime": sorrow_uptime,
    #        "asyncio": asyncio,
    #        "author": ctx.author,
    #        "traceback": traceback,
    #        "read_json": utils.read_json,
    #       "write_json": utils.write_json,
    #        "true": True,
    #        "false": False,
    #        "ret": ctx.send,
    #        "message": discord.Message,
    #        "color": utils.color,
    #        "utils": utils,
    #        "moment": utils.moment,
    #        "done": self.done,
    #        "warn": self.warn,
    #        "fail": self.fail,
    #        "reply": self.reply,
    #        "dash": self.dash,
    #        "warning": self.warning,
    #        "success": self.success,
    #        "error": self.error
    #

    #    try:
    #        exec(f"async def func():\n{textwrap.indent(code, '  ')}", args)
    #        response = await eval('func()', args)
    #        if (response is None) or isinstance(response, discord.Message):
    #            del args, code
    #            return
    #    except Exception as e:
    #        embed = discord.Embed(color=0x2f3136, description=f'```py\n{traceback.format_exc()}\n\n```')
    #        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
    #        await ctx.reply(embed=embed) # f"Error occurred:```YAML\n\n{type(e).__name__}: {str(e)}```"
    #
    #    del args, code

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *ext):

        if not ext:
            raise utils.ArgError("missing required argument")
            return

        reloaded = []
        try:
            async for ext in utils.aiter(ext):
                try:
                    await self.bot.reload_extension(f'{ext.split("/")[0]}')
                    reloaded.append(ext)
                except:
                    pass

            await ctx.reply(f'reloaded {", ".join(reloaded)}')
        except Exception as e:
            embed = discord.Embed(color=0x2F3136)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            embed.description = f"```py\n{e}\n\n```"
            await ctx.reply(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):

        await ctx.message.add_reaction("⌛")
        await ctx.bot.tree.sync()
        await ctx.message.clear_reactions()
        return await ctx.reply(":thumbsup:")

    @commands.group(name="blacklist", invoke_without_command=False)
    @commands.is_owner()
    async def blacklist(self, ctx):
        ...

    @blacklist.group(name="add", invoke_without_command=False)
    @commands.is_owner()
    async def blacklist_add(self, ctx):
        ...

    @blacklist_add.command(name="guild")
    async def blacklist_add_guild(self, ctx, *, guild: int):

        db = utils.read_json("blacklisted")
        db["servers"].append(guild)
        utils.write_json(db, "blacklisted")
        await ctx.reply(":thumbsup:")
        try:
            x = await self.bot.fetch_guild(guild)
            await x.leave()
        except:
            pass

    @blacklist_add.command(name="user")
    async def blacklist_add_user(self, ctx, *, user: int):

        data = utils.read_json("prefixes")
        data[str(user)] = {"prefix": "…"}
        utils.write_json(data, "prefixes")
        await ctx.reply(":thumbsup:")

    @blacklist.group(name="remove", invoke_without_command=False)
    @commands.is_owner()
    async def blacklist_remove(self, ctx):
        ...

    @blacklist_remove.command(name="guild")
    async def blacklist_remove_guild(self, ctx, *, guild: int):

        db = utils.read_json("blacklisted")
        db["servers"].remove(guild)
        utils.write_json(db, "blacklisted")
        await ctx.reply(":thumbsup:")

    @blacklist_remove.command(name="user")
    async def blacklist_remove_user(self, ctx, *, user: int):

        data = utils.read_json("prefixes")
        data.pop(str(user))
        utils.write_json(data, "prefixes")
        await ctx.reply(":thumbsup:")

    @commands.command(aliases=["portal", "getinv"])
    @commands.is_owner()
    async def getinvite(self, ctx, gid: int = None):

        guild = discord.utils.get(self.bot.guilds, id=gid)
        channel = guild.text_channels[0]
        inv = await channel.create_invite(max_age=86400)
        await ctx.send(inv)

    @commands.command(aliases=["src"])
    @commands.is_owner()
    async def source(self, ctx, *, cmd: str = None):

        x = self.bot.get_command(cmd)
        import inspect

        with open(f"./source.txt", "w", encoding="utf-8") as f:
            x, _ = inspect.getsourcelines(x.callback)
            x = "".join(x)
            f.writelines(x)

        await ctx.send(file=discord.File("./source.txt"))
        os.remove("./source.txt")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def emojipost(self, ctx):
        """Fancy post the emoji lists"""
        emojis = sorted(
            [
                e
                async for e in utils.aiter(ctx.guild.emojis)
                if len(e.roles) == 0 and e.available
            ],
            key=lambda e: e.name.lower(),
        )
        paginator = commands.Paginator(suffix="", prefix="")
        paginator.max_size = 150
        channel: Optional[discord.TextChannel] = ctx.guild.get_channel(ctx.channel.id)  # type: ignore

        if channel is None:
            return

        async for emoji in utils.aiter(emojis):
            paginator.add_line(f"{emoji} -- `{emoji}`")

        # await channel.purge()
        async for page in utils.aiter(paginator.pages):
            await channel.send(page)

        await ctx.send()

    async def run_process(self, command: str) -> list[str]:
        try:
            process = await asyncio.create_subprocess_shell(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    @commands.command()
    @commands.is_owner()
    async def sh(self, ctx, *, command: str):
        """Runs a shell command."""
        # from modules import rdanny

        async with ctx.typing():
            stdout, stderr = await self.run_process(command)

        if stderr:
            text = f"stdout:\n{stdout}\nstderr:\n{stderr}"
        else:
            text = stdout

        # pages = rdanny.RoboPages(rdanny.TextPageSource(text), ctx=ctx)
        await ctx.send(text)

    @commands.command()
    @commands.is_owner()
    async def pip(self, ctx, *, argument: str):

        await ctx.invoke(self.bot.get_command("sh"), command=f"pip3 {argument}")

    @commands.command()
    @commands.is_owner()
    async def bash(self, ctx, *, argument: codeblock_converter):
        await ctx.invoke(self.bot.get_command("jsk bash"), argument=argument)

    @commands.group(name="guilds")
    @commands.is_owner()
    async def guilds(self, ctx):
        ...

    @guilds.command(name="filter")
    @commands.is_owner()
    async def guilds_filter(self, ctx, minimum: int = None):
        
        num=0
        embed=discord.Embed(
            color=self.bot.color,
            description=f'{self.bot.fail} {ctx.author.mention}**:** are you **sure** you want to leave guilds with less than **{minimum}** members?\nthis action is **irreversible**'
        )
        
        from modules.confirmation import confirm
        
        sentmsg=await ctx.reply(embed=embed)
        conf=await confirm(
            self=self, 
            ctx=ctx, 
            msg=sentmsg
        )
        
        if conf:
            await ctx.typing()
            for guild in self.bot.guilds:
                if len(guild.members) < minimum:
                    await guild.leave()
                    num+=1
            embed=discord.Embed(
                color=self.bot.color,
                description=f'{self.bot.done} {ctx.author.mention}**:** left {num} **guilds** under {minimum} **members**'
            )
            await sentmsg.delete()
            await ctx.reply(embed=embed)
            
        else:
            await sentmsg.delete()
    @guilds.command(name="leave")
    @commands.is_owner()
    async def guilds_leave(self, ctx, guild: discord.Guild):

        await guild.leave()
        await ctx.reply(f"left {guild.name} :thumbsup:")

    @commands.command()
    @utils.perms("manage_guild")
    async def test(self, ctx):
        await ctx.reply(ctx.author.name)

    @commands.command()
    @commands.is_owner()
    async def sendas(
        self,
        ctx,
        who: typing.Optional[discord.Member | discord.User] = commands.Author,
        *,
        content: str,
    ):

        msg = copy.copy(ctx.message)
        msg.author = who
        msg.content = content
        self.bot.dispatch("message", msg)

    @commands.command()
    @commands.is_owner()
    async def getinfo(
        self,
        ctx,
        user: typing.Optional[discord.User | discord.Member] = commands.Author,
        extra: str = "",
    ):

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://api.rival.rocks/user",
                headers={
                    "api-key": self.bot.rival_api,
                    "content-type": "application/json",
                },
                params={"user_id": user.id},
            ) as resp:
                return await ctx.reply(
                    json.dumps((await resp.json())["data"], indent=4)
                )

    @commands.command()
    @commands.is_owner()
    async def reloadutils(self, ctx):

        import importlib
        from modules import utils, paginator

        importlib.reload(utils)
        importlib.reload(paginator)
        await ctx.reply(":thumbsup:")

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, argument: codeblock_converter):
        await ctx.invoke(self.bot.get_command("jishaku py"), argument=argument)

    @commands.command()
    async def restart(self, ctx):

        if ctx.author.id == self.bot.owner.id:
            await ctx.reply(":thumbsup:")
            os.execv(sys.executable, ["python3.10"] + sys.argv)

    @commands.command()
    @commands.is_owner()
    async def selfunban(self, ctx, guild: int):
        guild = await self.bot.fetch_guild(guild)
        member = 812126383077457921
        await guild.unban(discord.Object(id=member))
        await ctx.reply(":thumbsup:")

    @commands.command(
        name='sql',
        description='execute a sql query',
        syntax=',sql (query)',
        example=',sql SELECT count(*) FROM test'
    )
    @commands.is_owner()
    async def sql(self, ctx, *, query: str):
        
        from jishaku.codeblocks import codeblock_converter as cc
        
        parts=query.split(' | ')
        query=parts[0]
        args=[]
        if len(parts) == 2:
            args=parts[1].split()
            
        one_value=False
        one_row=False
        as_list=False
        for arg in args:
            if 'value' in arg:
                one_value=True
            elif 'row' in arg:
                one_row=True
            elif 'list' in arg:
                as_list=True
        
        
        
        await ctx.invoke(self.bot.get_command('eval'), argument=cc(f'''await bot.db2.execute(f'{query.split(' || ')[0]}', one_value={one_value}, one_row={one_row}, as_list={as_list})'''))

async def setup(bot):

    await bot.add_cog(owner(bot))
