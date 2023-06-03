import discord
from discord.ext import commands
import collections
from utils.paginator import Paginator
import requests

color = 0x2b2d31

def test(self) -> str:
    parts = list()
    CAT = '┌── '
    CMD = '|    ├──  '
    SUB = '|    |   ├── '

    for cog in sorted([self.context.bot.get_cog(cog) for cog in self.context.bot.cogs if self.context.bot.get_cog(cog).get_commands() and self.context.bot.get_cog(cog).qualified_name not in ('Jishaku', 'Developer')], key=lambda c: c.qualified_name[:2]):
        parts.append(f"{CAT}{cog.qualified_name.replace('_', ' ')}")
        for cmd in cog.get_commands():
            parts.append(f"{CMD}{cmd.qualified_name}" + (f"[{'|'.join(cmd.aliases)}]" if cmd.aliases else "") + f": {cmd.description}")
            if hasattr(cmd, 'commands'):
                for c in cmd.walk_commands():
                    parts.append(f"{SUB}{c.qualified_name}" + (f"[{'|'.join(c.aliases)}]" if c.aliases else "") + f": {c.description}")
                    
    return '\n'.join(parts)


class Developer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.mirror=collections.defaultdict(dict)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    async def geninvite(self, guild_id):
        guild=self.bot.get_guild(guild_id)
        for channel in guild.text_channels:
            try:
                invite=await channel.create_invite()
                return invite
            except:
                pass
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if message.guild.id in self.mirror:
            if message.author.bot:
                return
            gchannel=self.mirror[message.guild.id]
            channel=self.bot.get_channel(gchannel)
            e = discord.Embed(
                description=message.content,
                color=color)
            e.set_author(name=f'{message.guild.name}', icon_url=message.guild.icon)
            e.set_footer(text=f'{message.author} ({message.author.id})')
            if message.attachments:
                e.set_image(url=message.attachments[0].proxy_url)
            return await channel.send(embed=e, mention_author=False)

    @commands.command(
        name='load',
        description='Load a bot extension',
        brief='extension',
        usage=
        'Syntax: (extension)\n'
        'Example: LastFM'
    )
    @commands.is_owner()
    async def load(self, ctx, extension):
        await ctx.typing()

        await self.bot.load_extension(f'cogs.{extension}')
        await ctx.success(f'**{extension}** has been loaded')

    @commands.command(
        name='unload',
        description='Unload a bot extension',
        brief='extension',
        usage=
        'Syntax: (extension)\n'
        'Example: Configuration'
    )
    @commands.is_owner()
    async def unload(self, ctx, extension):
        await ctx.typing()

        await self.bot.unload_extension(f'cogs.{extension}')
        await ctx.success(f'**{extension}** has been unloaded')

    @commands.command(
        name='reload',
        description='Reload a bot extension',
        brief='extension',
        usage=
        'Syntax: (extension)\n'
        'Example: Information'
    )
    @commands.is_owner()
    async def reload(self, ctx, extension):
        await ctx.typing()

        await self.bot.reload_extension(f'cogs.{extension}')
        await ctx.success(f'**{extension}** has been reloaded')

    @commands.group(
        invoke_without_command=True,
        name='guild'
    )
    @commands.is_owner()
    async def guild(self, ctx):
        await ctx.send_help(ctx.command)

    @guild.group(
        name='invite',
        description=f'Generate a guild invite',
        brief='id',
        usage=
        'Syntax: (guild id)\n'
        'Example: 980316232341389413',
        aliases=['guildinv']
    )
    @commands.is_owner()
    async def invite(self, ctx, guild:int):
        await ctx.typing()

        invite=await self.geninvite(guild)
        await ctx.success(f'Click **[here]({invite})** to join')
    
    @guild.group(
        name='mirror',
        description='Mirror messages from a guild',
        brief='id',
        usage=
        'Syntax: (guild id)\n'
        'Example: 1075502884352950322',
        aliases=['spy']
    )
    @commands.is_owner()
    async def mirror(self, ctx, guild:int):
        await ctx.typing()
        
        if guild in self.mirror:
            del self.mirror[guild]
            await ctx.success(f'No longer spying on **{guild}**')
        else:
            self.mirror[guild]=ctx.channel.id
            await ctx.success(f'Now spying on **{guild}**')
    
    @guild.group(
        name='unban',
        description='Unban yourself from a guild',
        brief='id',
        usage=
        'Syntax: (guild id)\n'
        'Example: 980316232341389413',
    )
    @commands.is_owner()
    async def unban(self, ctx, guild:int):
        await ctx.typing()

        guild = await self.bot.fetch_guild(guild)
        member = ctx.author
        await guild.unban(member)
        await ctx.send('👍🏾')
    
    @guild.group(
        name='say',
        description='Send a message to a guild with the bot',
        brief='id, message',
        usage=
        'Syntax: (channel id) (message)\n'
        'Example: 1075502884352950322'
    )
    @commands.is_owner()
    async def say(self, ctx, channel_id: int, *, message):
        await ctx.typing()

        channel = self.bot.get_channel(channel_id)
        guild = channel.guild
        await ctx.send(f"Sending message to **{guild}** <#{channel.id}>\n> {message}")
        await channel.send(message)

    @guild.group(
        name='list',
        description='View the servers that the bot is in',
        usage='Syntax: ',
    )
    @commands.is_owner()
    async def guild_list(self, ctx):
        await ctx.typing()

        embeds = []
        ret = []
        num = 0
        pagenum = 0
        for i in sorted(self.bot.guilds, key=lambda x: len(x.members), reverse=True):
            num += 1
            ret.append(f'**{num}.** {i.name} ({i.id}) - {len(i.members)}')
            pages = [p for p in discord.utils.as_chunks(ret, 10)]
        for page in pages:
            pagenum += 1
            embeds.append(discord.Embed(
                color=color,
                title=f'{self.bot.user.name}\'s guilds',
                description="\n".join(page))
                .set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                .set_footer(text=f'Page {pagenum}/{len(pages)}')
                )
        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        else:
            pag = Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            pag.add_button('prev', emoji='<:void_previous:1082283002207424572>')
            pag.add_button('goto', emoji='<:void_goto:1082282999187517490>')
            pag.add_button('next', emoji='<:void_next:1082283004321341511>')
            pag.add_button('delete', emoji='<:void_cross:1082283006649188435>')
            await pag.start()

    @commands.command(
        name='toggle',
        description='Enable or disable a command',
        brief='command',
        usage=
        'Syntax: (command)\n'
        'Example: lastfm'
    )
    @commands.is_owner()
    async def toggle(self, ctx, *, command):
        """Enable or disable a command"""
        await ctx.typing()

        command = self.bot.get_command(command)
        if ctx.command == command:
            await ctx.success(f'You are unable to disable `{ctx.invoked_with}`')
        else:
            command.enabled = not command.enabled
            ternary = "enabled" if command.enabled else "disabled"
            await ctx.success(f'Command `{command.qualified_name}` has been **{ternary}**')

    @guild.group(
        name='leave',
        description='Make void forcefully leave a guild',
        brief='id',
        usage=
        'Syntax: (guild id)\n'
        'Example: 980316232341389413'
    )
    async def leave(self, ctx, guild: int):
        guild = self.bot.get_guild(int(guild))
        await guild.leave()
        await ctx.success(f'`{guild.name}` has been **left**')

    @guild.group(
        invoke_without_command=True,
        name='whitelist',
        description='Authorize/unauthorize a guild for void to join',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: add /voidbot court#9000'
    )
    @commands.is_owner()
    async def whitelist(self, ctx):
        await ctx.send_help(ctx.command)
    
    @whitelist.group(
        name='add',
        description='Authorize a guild for void to join',
        brief='invite, user',
        usage=
        'Syntax: (invite) (user)\n'
        'Example: /voidbot court#9000'
    )
    @commands.is_owner()
    async def whitelist_add(self, ctx, invite: str, owner: discord.Member):
        invite = invite.replace("https://discord.gg/", "").replace("discord.gg/", "")
        r = requests.get(f'https://discord.com/api/v10/invites/{invite}')
        if r.json()['code']:
            guildid = r.json()['guild']['id']
            guildname = r.json()['guild']['name']
            data = await self.bot.db.fetchval('SELECT guild_id FROM whitelist WHERE guild_id = $1', guildid)
            if not data:
                await self.bot.db.execute('INSERT INTO whitelist (guild_id, owner, invite) VALUES($1, $2, $3)', guildid, str(owner.id), invite)
                await ctx.success(f'`{guildname}` has been **whitelisted**, requested by **{owner}**')
            else:
                await ctx.success(f'`{guildname}` is already a **whitelisted** guild')

    @whitelist.group(
        name='remove',
        description='Unauthorize a guild for void to join',
        brief='id',
        usage=
        'Syntax: (guild id)\n'
        'Example: 980316232341389413'
    )
    @commands.is_owner()
    async def whitelist_remove(self, ctx, guild: int):
        data = await self.bot.db.fetchval('SELECT guild_id FROM whitelist WHERE guild_id = $1', str(guild))
        if data:
            await self.bot.db.execute('DELETE FROM whitelist WHERE guild_id = $1', str(guild))
            await ctx.success(f'`{guild}` is no longer an **authorized** guild')
        else:
            await ctx.success(f'`{guild}` is not an **authorized** guild')

async def setup(bot):
    await bot.add_cog(Developer(bot))
