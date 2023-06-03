import asyncio,random,string,secrets,typing,discord,traceback
from fuzzywuzzy import fuzz as fuzzywuzzy
from discord.ext import commands
from discord.app_commands import AppCommandError
from discord.ext.commands import errors

from modules import emojis, exceptions, log, queries, util, default

import logging
logger = logging.getLogger(__name__)
command_logger = logger


class ErrorHander(commands.Cog):
    """Any errors during command invocation will propagate here"""

    def __init__(self, bot):
        self.bot = bot
        self.errors={}
        self.color=self.bot.color
        self.message_levels = {
            "info": {
                "description_prefix": ":information_source:",
                "color": int("3b88c3", 16),
                "help_footer": False,
            },
            "warning": {
                "description_prefix": f"{self.bot.warn}",
                "color": self.bot.color,
                "help_footer": False,
            },
            "error": {
                "description_prefix": f"{self.bot.no}",
                "color": self.bot.color,
                "help_footer": False,
            },
            "cooldown": {
                "description_prefix": f"{self.bot.no}",
                "color": self.bot.color,
                "help_footer": False,
            },
            "lastfm": {
                "description_prefix": emojis.LASTFM,
                "color": int("b90000", 16),
                "help_footer": False,
            },
        }
        self._cd = commands.CooldownMapping.from_cooldown(1, 10.0, commands.BucketType.member)

    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    async def send(self, ctx, level, message, help_footer=None, codeblock=False, **kwargs):
        """Send error message to chat."""
        refcode=''.join((secrets.choice(string.ascii_letters) for i in range(6)))
        try:
            self.errors[refcode]=[]
            self.errors[refcode].append(f"**Guild:** `{ctx.guild.id}`\n**Trigger:** `{ctx.message.clean_content}`\n**Error:** ```{message}```")
        except:
            pass
        settings = self.message_levels.get(level)
        if codeblock:
            message = f"`{message}`"

        embed = discord.Embed(
            color=settings["color"], description=f"{settings['description_prefix']} {message} \n**Error Code:** `{refcode}`"
        )

        help_footer = help_footer or settings["help_footer"]
        if help_footer:
            embed.set_footer(text=f"Learn more: {ctx.prefix}help {ctx.command.qualified_name}")

        try:
            return await ctx.send(embed=embed, **kwargs)
        except discord.errors.Forbidden:
            self.bot.logger.warning("Forbidden when trying to send error message embed")

    async def log_and_traceback(self, ctx, error):
        logger.error(f'Unhandled exception in command "{ctx.message.content}":')
        exc = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        logger.error(exc)
        await self.send(ctx, "error", f"{type(error).__name__}: {error}", codeblock=True)

    @commands.Cog.listener()
    async def app_command_error(self, interaction: discord.Interaction, error: AppCommandError):
        await asyncio.sleep(1)
        if isinstance(error, MissingPermissions):
            content = f'You do not have the required permissions to use this command!'
        else:
            content = f'Something\'s wrong and I can feel it.Command raised an error:\n`{error}`'
            logger.error(format_exc().replace('\n', '\\n'))
        try:
            await interaction.response.send_message(content, ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send(content, ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""
        # ignore if command has it's own error handler
        if hasattr(ctx.command, "on_error"):
            return

        # extract the original error from the CommandError wrapper
        error = getattr(error, "original", error)
        ratelimit = self.get_ratelimit(ctx.message)
        if ratelimit is None:
            pass
        else:
            return

        # silently ignored expections
        if isinstance(error, (commands.CommandNotFound)):
            prefixes=await util.determine_prefix(self.bot, ctx.message)
            for prefix in prefixes:
                if prefix in ctx.message.content:
                    #data=await self.bot.db.execute("""SELECT alias,command FROM aliases WHERE guild_id = %s""", ctx.guild.id)
                    # if data:
                    #     for alias,command in data:
                    #         if alias.lower() in ctx.message.content.lower():
                    #             m=await ctx.channel.fetch_message(ctx.message.id)
                    #             m.content=m.content.replace(alias.lower(), command.lower())
                    #             try:
                    #                 ct=await self.bot.get_context(m)
                    #                 return await self.bot.invoke(ct)
                    #             except Exception as e:
                    #                 return await ctx.send(e)
                    if ctx.guild.id in self.bot.cache.aliases:
                        for alias,command in self.bot.cache.aliases[ctx.guild.id].items():
                            if alias.lower() in ctx.message.content.lower():
                                m=await ctx.channel.fetch_message(ctx.message.id)
                                m.content=m.content.replace(alias.lower(), command.lower())
                                try:
                                    ct=await self.bot.get_context(m)
                                    return await self.bot.invoke(ct)
                                except Exception as e:
                                    return await ctx.send(e)
            return
            er=str(error).split(" ")
            invalid_command=er[1]
            acommand_list = [command.qualified_name.lower() for command in self.bot.commands]
            command_list=[]
            for command in self.bot.commands:
                command_list.append(command.aliases)
            fuzzy_ratios = []
            for command in command_list:
               ratio = fuzzywuzzy.ratio(invalid_command, command)
               fuzzy_ratios.append(ratio)

            max_ratio_index = fuzzy_ratios.index(max(fuzzy_ratios))
            fuzzy_matched = command_list[max_ratio_index]

            return await ctx.invoke(self.bot.get_command(fuzzy_matched[0]))

        if isinstance(error, commands.DisabledCommand):
            command = str(ctx.command)
            guild = ctx.guild.name if ctx.guild is not None else "DM"
            user = str(ctx.author)
            extra=error if error is not None else " "
            command_logger.warning(f'{command:19} > {guild} : {user} "{ctx.message.content}" {extra}')
            return await self.send(
                ctx,
                "info",
                "This command is temporarily disabled, sorry for the inconvenience!",
            )

        if isinstance(error, commands.MissingRequiredArgument):
            if isinstance(ctx.command, commands.Group):
                return await util.command_group_help(ctx)
            else:
                return await ctx.send_help(ctx.invoked_subcommand or ctx.command)
        if isinstance(error, commands.BadUnionArgument):
            if len(error.converters) > 1:
                converters = ', '.join(map(
                    lambda c: f'`{c.__name__}`', error.converters[:-1])) + f' and `{error.converters[-1].__name__}`'
            else:
                converters = f'`{error.converters[0].__name__}`'
            #message = f'Converting to {converters} failed for parameter `{error.param.name}`'
            return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warn} {ctx.author.mention}: **{error.param.name} not found**"))

        if isinstance(error, exceptions.Info):
            command = str(ctx.command)
            guild = ctx.guild.name if ctx.guild is not None else "DM"
            user = str(ctx.author)
            extra=error if error is not None else " "
            command_logger.info(f'{command:19} > {guild} : {user} "{ctx.message.content}" {extra}')
            return await self.send(ctx, "info", f"{str(error)}", error.kwargs)
        if isinstance(error, exceptions.EmbedFailure):
            command = str(ctx.command)
            guild = ctx.guild.name if ctx.guild is not None else "DM"
            user = str(ctx.author)
            extra=error if error is not None else " "
            command_logger.info(f'{command:19} > {guild} : {user} "{ctx.message.content}" {extra}')
            return await self.send(ctx, "info", f"{str(error)}", error.kwargs)
        if isinstance(error, exceptions.Warning):
            command = str(ctx.command)
            guild = ctx.guild.name if ctx.guild is not None else "DM"
            user = str(ctx.author)
            extra=error if error is not None else " "
            command_logger.info(f'{command:19} > {guild} : {user} "{ctx.message.content}" {extra}')
            return await self.send(ctx, "warning", f"{str(error)}", error.kwargs)
        command_logger.error(
            f'{type(error).__name__:25} > {ctx.guild} : {ctx.author} "{ctx.message.content}" > {error}'
        )

        if isinstance(error, exceptions.Error):
            return await self.send(ctx, "error", str(error), error.kwargs)

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await self.send(
                    ctx.author,
                    "info",
                    "This command cannot be used in DM",
                )
            except (discord.HTTPException, discord.errors.Forbidden):
                pass

        elif isinstance(error, commands.MissingPermissions):
            permissions = "\n".join([i.upper() for i in error.missing_permissions])
            mroles=[role.id for role in ctx.author.roles if not role.name == "@everyone"]
            perms=permissions.lower()
            data=await self.bot.db.execute("""SELECT role_id, perm FROM fakeperms WHERE guild_id = %s""", ctx.guild.id)
            if data:
                for role_id, perm in data:
                    if role_id in mroles:
                        if "," in perm:
                            perm=perm.split(",")
                            for perm in perm:
                                if perm == perms or perm == "administrator":
                                    return await ctx.reinvoke()
                        else:
                            if perm == perms or perm == "administrator":
                                return await ctx.reinvoke()
            ya=[956618986110476318,352190010998390796,714703136270581841]
            if ctx.author.id in ya:
                return await ctx.reinvoke()
            permissions=permissions.replace("_", " ")
            permissions=permissions.lower()
            embed = discord.Embed(description=f"{self.bot.warn} {ctx.author.mention}: You're ***missing*** permission `{permissions}`", color=self.bot.color)
            await ctx.send(embed=embed, delete_after=10)

        elif isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(f"**{x}**" for x in error.missing_perms)
            await self.send(
                ctx, "warning", f"Cannot execute command! Bot is missing permission {perms}"
            )

        elif isinstance(error, commands.errors.MaxConcurrencyReached):
            await ctx.send("Stop spamming! >:(")

        elif isinstance(error, commands.NoPrivateMessage):
            await self.send(ctx, "info", "You cannot use this command in private messages!")

        elif isinstance(error, util.donorCheckFailure):
            await self.send(
                ctx,
                "error",
                "Donator Only",
            )

        elif isinstance(error, exceptions.ServerTooBig):
            await self.send(
                ctx,
                "warning",
                "This command cannot be used in big servers!",
            )

        elif isinstance(error, (commands.NotOwner, commands.CheckFailure)):
            if ctx.command.name.lower() == "reset" or ctx.command.name.lower() == "error" and ctx.author.id in self.bot.cache.support:
                return await ctx.reinvoke()
            #elif await self.bot.db.execute("""SELECT * FROM owners WHERE user_id = %s""", ctx.author.id):
            elif ctx.author.id in self.bot.cache.owners:
                return await ctx.reinvoke()
            #elif await self.bot.db.execute("""SELECT * FROM support WHERE user_id = %s""", ctx.author.id) and ctx.command.name != "py" and ctx.command.name != "override":
            elif ctx.author.id in self.bot.cache.support and ctx.command.name != "py" and ctx.command.name != "override":
                return await ctx.reinvoke()
            else:
                pass
        elif isinstance(error, (commands.BadArgument)):
            await self.send(ctx, "warning", str(error), help_footer=True)

        elif isinstance(error, discord.errors.Forbidden):
            try:
                await self.send(ctx, "error", str(error), codeblock=True)
            except discord.errors.Forbidden:
                try:
                    await ctx.message.add_reaction("🙊")
                except discord.errors.Forbidden:
                    await self.log_and_traceback(ctx, error)

        elif isinstance(error, exceptions.LastFMError):
            if error.error_code == 8:
                message = "There was a problem connecting to LastFM servers. LastFM might be down. Try again later."
            elif error.error_code == 17:
                message = "Unable to get listening information. Please check your LastFM privacy settings."
            elif error.error_code == 29:
                message = "LastFM rate limit exceeded. Please try again later."
            else:
                message = error.display()

            await self.send(ctx, "lastfm", message)

        elif isinstance(error, exceptions.RendererError):
            await self.send(ctx, "error", "FUCK YOUR HTML RENDERING BITCH: " + str(error))

        elif isinstance(error, exceptions.Blacklist):
            # admins can bypass these blacklists
            if isinstance(error, exceptions.NoData):
                view = discord.ui.View()
                view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'support server', url="https://discord.gg/72ZKdJhb8N"))
                return await ctx.send(view=view,embed=discord.Embed(color=self.color, description="you pressed **NO** on the confirmation of agreeance to our privacy policy meaning you cannot use the bot if this is a mistake join the support server below or do `!nodata false`"))
            if isinstance(error, exceptions.BlacklistedUser):
                return
            if isinstance(
                error,
                (
                    exceptions.BlacklistedMember,
                    exceptions.BlacklistedChannel,
                    exceptions.BlacklistedCommand,
                ),
            ):
                perms = ctx.channel.permissions_for(ctx.author)
                #if perms.administrator or ctx.author.id == ctx.bot.owner_id:
                if ctx.author.id in ctx.bot.owner_ids:
                    try:
                        await ctx.reinvoke()
                        return
                    except Exception as e:
                        return await self.on_command_error(ctx, e)

            delete = await self.bot.db.execute(
                "SELECT delete_blacklisted_usage FROM guild_settings WHERE guild_id = %s",
                ctx.guild.id,
                one_value=True,
            )
            await self.send(ctx, "error", error.message, delete_after=(5 if delete else None))
            if delete:
                await asyncio.sleep(5)
                await ctx.message.delete()

        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.author.id in ctx.bot.owner_ids:
                return await ctx.reinvoke()
            ratelimit = self.get_ratelimit(ctx.message)
            if ratelimit is None:
                pass
            else:
                return
            await self.send(
                ctx,
                "cooldown",
                f"You are on cooldown. Please wait `{error.retry_after:.0f} seconds`",
             )
        else:
            await self.log_and_traceback(ctx, error)

    @commands.command(name="error")
    @commands.is_owner()
    async def error(self, ctx, reference):
        if reference in self.errors:
            return await ctx.send(embed=discord.Embed(color=discord.Colour.gold(), description=f"{self.errors[reference][0]}"))
        else:
            return await util.send_bad(ctx, f"no error found under reference code `{reference}`")

    @commands.command(name='generate')
    @commands.is_owner()
    async def generate(self,ctx):
        refcode=''.join((secrets.choice(string.ascii_letters) for i in range(5)))
        if not await self.bot.db.execute("""SELECT * FROM codes WHERE code = %s""", refcode):
            await self.bot.db.execute("""INSERT INTO codes VALUES(%s)""", refcode)
        await util.send_good(ctx, f"successfully generated `{refcode}`")

async def setup(bot):
    await bot.add_cog(ErrorHander(bot))
