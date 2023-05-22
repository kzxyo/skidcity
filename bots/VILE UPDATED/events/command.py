import discord, difflib, copy, asyncio, tuuid
from typing import Any
from utilities import utils
from utilities.baseclass import Vile
from utilities.context import Context
from discord.ext import commands


class CommandEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot
        

    @commands.Cog.listener()
    async def on_command(self, ctx: Context):

        await self.bot.db.execute('UPDATE commands SET count = count+1')
        await self.bot.db.execute(
            'INSERT INTO user_commands (user_id, count) VALUES (%s, 1) ON DUPLICATE KEY UPDATE count = count+1',
            ctx.author.id
        )

        await self.bot.get_channel(1039918538934190221).send(
            f'{ctx.author} in #{ctx.channel.name} ({ctx.guild.name}): **{ctx.message.content}**',
            allowed_mentions=discord.AllowedMentions.none()
        )

    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: Any):
        
        if ctx.channel.permissions_for(ctx.guild.me).send_messages is False:
            return
        
        if type(error) in (commands.NotOwner, commands.CheckFailure):
            return

        if isinstance(error, asyncio.CancelledError):
            return await ctx.send_error('this task was **manually cancelled**')

        if isinstance(error, commands.CommandNotFound):
            if self.bot.cache.aliases.get(ctx.guild.id) is not None:
                aliases = self.bot.cache.aliases[ctx.guild.id]
                
                if ctx.invoked_with in aliases:
                    message = copy.copy(ctx.message)
                    message.content = message.content.replace(ctx.invoked_with, aliases[ctx.invoked_with], 1)
                    
                    return await self.bot.process_commands(message)

        if isinstance(error, commands.BotMissingPermissions):
            permission = error.missing_permissions[0].lower().replace('_', ' ')
            return await ctx.send_error(f"i'm missing the **{permission}** permission")

        if isinstance(error, commands.MissingPermissions):
            permission = error.missing_permissions[0].lower().replace('_', ' ')
            return await ctx.send_error(f"you're missing the **{permission}** permission")

        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send_error(
                f"you're on a **[cooldown](https://discord.com/developers/docs/topics/rate-limits)** & cannot use `{ctx.invoked_with}` for another **{error.retry_after:.2f}** second(s)",
                error.retry_after
            )

        if isinstance(error, commands.MemberNotFound):
            return await ctx.send_error('please provide a **valid** member')

        if isinstance(error, commands.UserNotFound):
            return await ctx.send_error('please provide a **valid** user')

        if isinstance(error, commands.ChannelNotFound):
            return await ctx.send_error('please provide a **valid** channel')

        if isinstance(error, commands.RoleNotFound):
            return await ctx.send_error('please provide a **valid** role')

        if isinstance(error, commands.EmojiNotFound):
            return await ctx.send_error('please provide a **valid** emoji')

        if isinstance(error, commands.GuildNotFound):
            return await ctx.send_error('please provide a **valid** guild')

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.BadInviteArgument):
            return await ctx.send_error('please provide a **valid** invite')

        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help()

        if isinstance(error, commands.BadArgument):
            return await ctx.send_error(
                utils.multi_replace(
                    error.args[0].lower(), {'"': '**', 'int': 'number', 'str': 'text'}
                )[:-1]
            )

        if isinstance(error, commands.BadUnionArgument):
            return await ctx.send_error(
                utils.multi_replace(
                    error.args[0].lower(), {'"': '**', 'into': 'into a', 'member': '**member**', 'user': '**user**'}
                )[:-1]
            )

        else:
            error_code = tuuid.tuuid()
            self.bot.cache.errors[error_code] = {
                'guild': ctx.guild,
                'command': ctx.command,
                'user': ctx.author,
                'error': error
            }
            
            return await ctx.send_error(f'**{ctx.command.qualified_name}** raised an unexpected error (`{error_code}`)')


async def setup(bot: Vile):
    await bot.add_cog(CommandEvents(bot))
