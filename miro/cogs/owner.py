import discord, os, sys, asyncio, subprocess, copy, typing
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path
from modules import utils, paginator as pg
from jishaku.codeblocks import codeblock_converter


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
        self.av = "https://cdn.discordapp.com/attachments/1116443743831199814/1118245305352200332/Cherry_Blossoms.png"

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
            embed = discord.Embed(color=0x4c5264)
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


    @commands.command(aliases=["portal", "getinv"])
    @commands.is_owner()
    async def getinvite(self, ctx, gid: int = None):
        guild = discord.utils.get(self.bot.guilds, id=gid)
        channel = guild.text_channels[0]
        inv = await channel.create_invite(max_age=86400)
        await ctx.send(inv)

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
        await ctx.send(text)

    @commands.command()
    @commands.is_owner()
    async def pip(self, ctx, *, argument: str):
        await ctx.invoke(self.bot.get_command("sh"), command=f"pip3 {argument}")

    @commands.command()
    @commands.is_owner()
    async def bash(self, ctx, *, argument: codeblock_converter):
        await ctx.invoke(self.bot.get_command("jsk bash"), argument=argument)

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
        member = 129857040855072768
        await guild.unban(discord.Object(id=member))
        await ctx.reply(":thumbsup:")

    @commands.command(
        name="sql",
        description="execute a sql query",
        syntax=";sql (query)",
        example=";sql SELECT count(*) FROM test",
    )
    @commands.is_owner()
    async def sql(self, ctx, *, query: str):
        from jishaku.codeblocks import codeblock_converter as cc

        parts = query.split(" | ")
        query = parts[0]
        args = []
        if len(parts) == 2:
            args = parts[1].split()

        one_value = False
        one_row = False
        as_list = False
        for arg in args:
            if "value" in arg:
                one_value = True
            elif "row" in arg:
                one_row = True
            elif "list" in arg:
                as_list = True

        await ctx.invoke(
            self.bot.get_command("eval"),
            argument=cc(
                f"""await bot.db2.execute(f'{query.split(' || ')[0]}', one_value={one_value}, one_row={one_row}, as_list={as_list})"""
            ),
        )

    @commands.command()
    @commands.is_owner()
    async def mirror(self, ctx, guild: int):
        await ctx.typing()

        if guild in self.mirror:
            del self.mirror[guild]
            await ctx.success(f"No longer spying on **{guild}**")
        else:
            self.mirror[guild] = ctx.channel.id
            await ctx.success(f"Now spying on **{guild}**")



    @commands.command()
    @commands.is_owner()
    async def say(self, ctx, channel_id: int, *, message):
        await ctx.typing()

        channel = self.bot.get_channel(channel_id)
        guild = channel.guild
        await ctx.send(f"Sending message to **{guild}** <#{channel.id}>\n> {message}")
        await channel.send(message)

    @commands.command(aliases=['guildlists'])
    @commands.is_owner()
    async def guild_list(self, ctx):
        await ctx.typing()

        embeds = []
        ret = []
        num = 0
        pagenum = 0
        for i in sorted(self.bot.guilds, key=lambda x: len(x.members), reverse=True):
            num += 1
            ret.append(f"**{num}.** {i.name} ({i.id}) - {len(i.members)}")
            pages = [p for p in discord.utils.as_chunks(ret, 10)]
        for page in pages:
            pagenum += 1
            embeds.append(
                discord.Embed(
                    color=0x4c5264,
                    title=f"{self.bot.user.name}'s guilds",
                    description="\n".join(page),
                )
                .set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.display_avatar
                )
                .set_footer(text=f"Page {pagenum}/{len(pages)}")
            )
        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        else:
            paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            paginator.add_button("prev", emoji="<:left:1107307769582850079>")
            paginator.add_button("goto", emoji="<:filter:1113850464832868433>")
            paginator.add_button("next", emoji="<:right:1107307767041105920>")
            paginator.add_button("delete", emoji="<:page_cancel:1121826948520362045>")
            await paginator.start()


    @commands.command()
    async def leaveg(self, ctx, guild: int):
        guild = self.bot.get_guild(int(guild))
        await guild.leave()
        await ctx.success(f"`{guild.name}` has been **left**")

async def setup(bot):
    await bot.add_cog(owner(bot))
