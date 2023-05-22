import discord, sys, importlib, time, copy, traceback, asyncio, subprocess, random, tuuid
from typing import Callable, Any, Union
from utilities import utils, advancedutils
from utilities.baseclass import Vile
from utilities.advancedutils import AsyncCodeExecutor, AsyncSender, ReplResponseReactor, ShellReader
from utilities.context import Context
from utilities.tasks import submit
from discord.ext import commands
from javascript import console, require


class Developer(commands.Cog):
    def __init__(self, bot: Vile) -> None:
        self.bot = bot

    @commands.command(name="auth")
    @commands.is_owner()
    async def auth(self,ctx:Context,guild:int):
        if not await self.bot.db.execute(f"""SELECT * FROM authorization WHERE guild_id = {guild}"""):
            await self.bot.db.execute(f"""INSERT INTO authorization(guild_id) VALUES({guild})""")
            return await ctx.send("authorized")
        else:
            await self.bot.db.execute(f"""DELETE FROM authorized WHERE guild_id = {guild}""")
            return await ctx.send("unauthorized")

    @commands.command(
        name='sql',
        description='execute a sql query',
        syntax='sql <query>',
        example='sql SELECT count(*) FROM DUAL',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def sql(self, ctx: Context, *, query: str):
        
        parts = query.split(' | ')
        query = parts[0]
        args = list()
        if len(parts) == 2:
            args = parts[1].split()
            
        one_value = False
        one_row = False
        as_list = False
        for arg in args:
            if arg == 'value':
                one_value = True
            elif arg == 'row':
                one_row = True
            elif arg == 'list':
                as_list = True

        async with ReplResponseReactor(ctx.message):
            ret = await self.bot.db.execute(f'''{query}''', one_value=one_value, one_row=one_row, as_list=as_list)

        return await ctx.reply(ret)
        

    @commands.command(
        name='eval',
        aliases=['py', 'evaluate', 'exec'],
        description='execute python code through discord',
        brief='eval <code>',
        help="eval 'hi'",
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def _eval(self, ctx: Context, *, code: str):
        
        code = code.strip('```')  
        env = {
            'author': ctx.author,
            'bot': ctx.bot,
            'channel': ctx.channel,
            'ctx': ctx,
            'guild': ctx.guild,
            'me': ctx.me,
            'message': ctx.message,
            'msg': ctx.message,
            'utils': utils,
            'source': utils.source,
            'src': utils.source,
            'autils': advancedutils,
            'console': console,
            'require': require
        }

        with submit(ctx):
            async with ReplResponseReactor(ctx.message):
                execute = AsyncCodeExecutor(code, arg_dict=env)
                async for send, result in AsyncSender(execute):

                    if result is None:
                        continue
                        
                    send(await utils.handle_result(ctx, result))


    @commands.command(
        name='reloadutils',
        aliases=['ru'],
        description='reload all the files in the modules folder',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def reloadutils(self, ctx: Context):

        modules = [
            k for k, v in sys.modules.items() 
            if k.startswith('utilities.')
        ]

        async with ctx.handle_response():
            for module in modules:
                try:
                    importlib.reload(sys.modules[module])
                except:
                    await ctx.reply(f"Couldn't reload {module}\n\n{traceback.format_exc()}")
                    continue
        
        return await ctx.send_success('successfully **reloaded** all modules')


    @commands.command(
        name='debug',
        aliases=['dbg'],
        description='run a command and return the error, if any',
        brief='debug <command>',
        help='debug ban',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def debug(self, ctx: Context, *, command: str):

        alt_message = copy.copy(ctx.message)
        alt_message.content = ctx.prefix + command
        alt_ctx = await self.bot.get_context(alt_message)

        if alt_ctx.command is None:
            return await ctx.send_error(f'command **{alt_ctx.invoked_with}** not found')

        start = time.perf_counter()

        async with ReplResponseReactor(ctx.message):
            await alt_ctx.command.invoke(alt_ctx)

        end = time.perf_counter()
        return await ctx.send_success(f'command **{alt_ctx.command.qualified_name}** finished in `{end-start:.3f}s`')


    @commands.group(
        name='blacklist',
        aliases=['bl'],
        description='blacklist/unblacklist a user or guild from using the bot',
        brief='blacklist <sub command>',
        help='blacklist add user @glory#0007',
        extras={'permissions': 'developer'},
        invoke_without_command=True
    )
    @commands.is_owner()
    async def blacklist(self, ctx: Context):
        return await ctx.send_help()

    
    @blacklist.group(
        name='add',
        description='blacklist a user or guild from using the bot',
        brief='blacklist add <sub command>',
        help='blacklist add user @glory#0007',
        extras={'permissions': 'developer'},
        invoke_without_command=True
    )
    @commands.is_owner()
    async def blacklist_add(self, ctx: Context):
        return await ctx.send_help()

    
    @blacklist_add.command(
        name='user',
        description='blacklist a user from using the bot',
        brief='blacklist add user <user>',
        help='blacklist add user @glory#0007',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def blacklist_add_user(self, ctx: Context, user: int):

        await self.bot.db.execute('INSERT INTO blacklisted_users (user_id) VALUES (%s)', user)
        self.bot.cache.global_bl['users'].add(user)
        return await ctx.send_success(f"{self.bot.get_user(user) or 'null'} has been **permanently blacklisted** from vile")


    @blacklist_add.command(
        name='guild',
        description='blacklist a guild from using the bot',
        brief='blacklist add guild <guild>',
        help='blacklist add guild 1054447513794515146',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def blacklist_add_guild(self, ctx: Context, guild: int):

        await self.bot.db.execute('INSERT INTO blacklisted_guilds (guild_id) VALUES (%s)', guild)
        self.bot.cache.global_bl['guilds'].add(guild)
        await ctx.send_success(f"{self.bot.get_guild(guild) or 'null'} has been **permanently blacklisted** from vile")
        if self.bot.get_guild(guild) is not None:
            await self.bot.get_guild(guild).leave()


    @blacklist.group(
        name='remove',
        description='unblacklist a user or guild from using the bot',
        brief='blacklist remove <sub command>',
        help='blacklist remove user @glory#0007',
        extras={'permissions': 'developer'},
        invoke_without_command=True
    )
    @commands.is_owner()
    async def blacklist_remove(self, ctx: Context):
        return await ctx.send_help()


    @blacklist_remove.command(
        name='user',
        description='unblacklist a user from using the bot',
        brief='blacklist remove user <user>',
        help='blacklist remove user @glory#0007',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def blacklist_remove_user(self, ctx: Context, user: int):

        await self.bot.db.execute('DELETE FROM blacklisted_users WHERE user_id = %s', user)
        self.bot.cache.global_bl['users'].discard(user)
        return await ctx.send_error(f"{self.bot.get_user(user) or 'null'} has been **unblacklisted** from vile")


    @blacklist_remove.command(
        name='guild',
        description='unblacklist a guild from using the bot',
        brief='blacklist remove guild <guild>',
        help='blacklist remove guild 1054447513794515146',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def blacklist_remove_guild(self, ctx: Context, guild: int):

        await self.bot.db.execute('DELETE FROM blacklisted_guilds WHERE guild_id = %s', guild)
        self.bot.cache.global_bl['guilds'].discard(guild)
        return await ctx.send_error(f"{self.bot.get_guild(guild) or 'null'} has been **unblacklisted** from vile")


    @commands.command(
        name='reset',
        description="reset a user's data collection setting",
        brief='reset <user>',
        help='reset @glory#0007',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def reset(self, ctx: Context, user: Union[discord.Member, discord.User]):

        await self.bot.db.execute('DELETE FROM nodata WHERE user_id = %s', user.id)
        self.bot.cache.nodata.pop(user.id)

        return await ctx.send_success(f"successfully **reset** {user.mention}'s data collection setting")


    @commands.command(
        name='commands',
        description='see how many commands a user has ran',
        brief='commands <user>',
        help='commands @glory#0007',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def _commands(self, ctx: Context, user: Union[discord.Member, discord.User]):

        commands_ran = await self.bot.db.fetchval('SELECT count FROM user_commands WHERE user_id = %s', user.id) or 0
        return await ctx.send_success(f"{user.name} has ran **{commands_ran:,}** command{'' if commands_ran == 1 else 's'}")


    @commands.command(
        name='sudo',
        description='execute commands with full permissions',
        brief='sudo <command>',
        help='sudo ban @glory#0007',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def sudo(self, ctx: Context, *, command_string: str):

        message = copy.copy(ctx.message)
        message.author = ctx.guild.owner
        message.content = (self.bot.cache.customprefixes.get(ctx.guild.owner.id) or self.bot.cache.guildprefixes.get(ctx.guild.id) or self.bot.prefix) + command_string

        return await self.bot.process_commands(message)
            
            
    @commands.command(
        name='pull',
        description='incorporate changes from a remote repository into the current branch',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def pull(self, ctx: Context):
        
        async with ctx.handle_response():
            with ShellReader('git pull origin master', escape_ansi=False) as reader:
                ret = list()
                async for line in reader:
                    ret.append(line)
                
                if len(ret) > 1:
                    ret = ret[4:]
                        
                ret = '\n'.join(ret)
                return await ctx.reply(f"```{ret}```")


    @commands.command(
        name='portal',
        aliases=['getinv'],
        description='create an invite in a server',
        brief='portal <server>',
        help='portal 1001013236986019901',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def portal(self, ctx: Context, *, guild: discord.Guild):

        if guild.vanity_url_code:
            return await ctx.reply(f'https://discord.gg/{guild.vanity_url_code}')

        if guild.me.guild_permissions.create_instant_invite is False:
            return await ctx.send_error("can't create an **invite** in that server")

        if not guild.text_channels and not guild.voice_channels:
            return await ctx.send_error("cannot create invite; server has no channels")

        return await ctx.reply(await random.choice(guild.text_channels + guild.voice_channels).create_invite(max_uses=1))


    @commands.command(
        name='traceback',
        aliases=['trace'],
        description='get information on an unknown exception',
        brief='traceback <error code>',
        help='traceback ERyE4wZKN997v',
        extras={'permissions': 'developer'}
    )
    @commands.is_owner()
    async def _traceback(self, ctx: Context, code: str):

        if self.bot.cache.errors.get(code) is None:
            return await ctx.send_error("couldn't find an **error** with that code")

        error = self.bot.cache.errors[code]
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f"{error['command'].qualified_name} @ {code}",
            description=f"{self.bot.reply} **guild:** {error['guild'].name} ( `{error['guild'].id}` )\n{self.bot.reply} **user:** {error['user']} ( `{error['user'].id}` )\n{self.bot.reply} **timestamp:** {discord.utils.format_dt(tuuid.decode(code), style='f')}"
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
        embed.add_field(name='', value=f"```py\n{type(error['error']).__name__}: {error['error']}```")

        return await ctx.reply(embed=embed)


async def setup(bot: Vile):
    await bot.add_cog(Developer(bot))
