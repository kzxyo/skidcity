from discord.ext import commands  # For Discord
import discord
from utils.embed import to_object, embed_replacement
import re

color = 0x2b2d31


class Servers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.group(
        invoke_without_command=True,
        name='prefix',
        description='View the server prefix',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: set !',
    )
    async def prefix(self, ctx):
        data = await self.bot.db.fetchval('SELECT prefix FROM prefix WHERE guild_id = $1', ctx.guild.id)
        if not data:
            data = ','
        await ctx.success(f'Prefix: `{data}`')

    @prefix.group(
        name='set',
        description='Change the server prefix',
        brief='prefix',
        usage=
        'Syntax: (new prefix)\n'
        'Example: !',
        aliases=['setprefix', 'changeprefix'],
        extras={'perms': 'Administrator'}
    )
    @commands.has_permissions(administrator=True)
    async def prefix_set(self, ctx, prefix: str):
        await self.bot.db.execute('INSERT INTO prefix (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = EXCLUDED.prefix', ctx.guild.id, prefix)
        await ctx.success(f'The **prefix** has been changed to `{prefix}`')

    @commands.group(
        invoke_without_command=True,
        name='selfprefix',
        description='View the custom prefix for yourself',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: set !'
    )
    async def selfprefix(self, ctx):
        data = await self.bot.db.fetchval('SELECT prefix FROM selfprefix WHERE user_id = $1', ctx.author.id)
        if data is None:
            data = ','
        await ctx.success(f'Selfprefix: `{data}`')

    @selfprefix.group(
        name='set',
        description='Set a custom prefix for yourself',
        brief='prefix',
        usage=
        'Syntax: (new prefix)\n'
        'Example: !'
    )
    async def selfprefix_set(self, ctx, prefix: str):
        await self.bot.db.execute('INSERT INTO selfprefix (user_id, prefix) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET prefix = EXCLUDED.prefix', ctx.author.id, prefix)
        await ctx.success(f'The **self prefix** has been changed to `{prefix}`')

    @commands.group(
        invoke_without_command=True,
        name='welcome',
        description='Setup a welcome message for new members',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: add #general Welcome {user.mention}',
        extras={'perms': 'Manage Guild'}
    )
    async def welcome(self, ctx):
        await ctx.send_help(ctx.command)

    @welcome.group(
        name='add',
        description='Set a welcome message',
        brief='channel, message',
        usage=
        'Syntax: (channel) (message)\n'
        'Example: {content: #general Welcome {user.mention}!}',
        aliases=['set'],
        extras={'perms': 'Manage Guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_add(self, ctx, channel: discord.TextChannel, *, text):
        data = await self.bot.db.fetchval('SELECT channel_id, message FROM welcome WHERE guild_id = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO welcome (guild_id, channel_id, message) VALUES ($1, $2, $3)', ctx.guild.id, channel.id, text)
            await ctx.success(f'**Welcome message** has been setup')
        if data:
            await self.bot.db.execute('UPDATE welcome SET channel_id = $1, message = $2 WHERE guild_id = $3', channel.id, text, ctx.guild.id)
            await ctx.success(f'**Welcome message** has been updated')


    @welcome.group(
        name='remove',
        description='Remove a welcome message from a channel',
        brief='channel',
        usage=
        'Syntax: (channel)\n'
        'Example: #general',
        aliases=['delete'],
        extras={'perms': 'Manage Guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_remove(self, ctx, channel: discord.TextChannel):
        data = await self.bot.db.fetchval('SELECT channel_id, message FROM welcome WHERE guild_id = $1', ctx.guild.id)
        if data:
            await self.bot.db.execute('DELETE FROM welcome WHERE channel_id = $1', channel.id)
            await ctx.success(f'**Welcome message** has been removed')

    @welcome.group(
        name='clear',
        description='Remove all welcome messages',
        usage='Syntax: ',
        aliases=['purge'],
        extras={'perms': 'Manage Guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_clear(self, ctx):
        data = await self.bot.db.fetchval('SELECT channel_id, message FROM welcome WHERE guild_id = $1', ctx.guild.id)
        if data:
            await self.bot.db.execute('DELETE FROM welcome WHERE guild_id = $1', ctx.guild.id)
            await ctx.success(f'**Welcome messages** has been cleared')

    @welcome.group(
        name='test',
        description='Test all welcome messages',
        usage='Syntax: ',
        aliases=['check'],
        extras={'perms': 'Manage Guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_test(self, ctx):
        data = await self.bot.db.fetchval('SELECT message FROM welcome WHERE guild_id = $1', ctx.guild.id)
        if data:
            result = await to_object(data)
            embed = result['embed']
            if embed:
                if embed.title:
                    embed.title = await embed_replacement(ctx.author, embed.title)
                if embed.description:
                    embed.description = await embed_replacement(ctx.author, embed.description)
                if embed.footer:
                    if embed.footer.text and embed.footer.icon_url:
                        embed.set_footer(text=await embed_replacement(ctx.author, embed.footer.text), icon_url=await embed_replacement(ctx.author, embed.footer.icon_url))
                    elif embed.footer.text:
                        embed.set_footer(text=await embed_replacement(ctx.author, embed.footer.text))
                    elif embed.footer.icon_url:
                        embed.set_footer(icon_url=await embed_replacement(ctx.author, embed.footer.icon_url))
                if embed.author:
                    if embed.author.name and embed.author.icon_url:
                        embed.set_author(name=await embed_replacement(ctx.author, embed.author.name), icon_url=await embed_replacement(ctx.author, embed.author.icon_url))
                    elif embed.author.name:
                        embed.set_author(name=await embed_replacement(ctx.author, embed.author.name))
                    elif embed.author.icon_url:
                        embed.set_author(icon_url=await embed_replacement(ctx.author, embed.author.icon_url))
                if embed.fields:
                    for field in embed.fields:
                        if field.name:
                            embed.set_field_at(index=embed.fields.index(field), name=await embed_replacement(ctx.author, field.name), value=await embed_replacement(ctx.author, field.value), inline=field.inline)
                if embed.image:
                    embed.set_image(url=await embed_replacement(ctx.author, embed.image.url))
                if embed.thumbnail:
                    embed.set_thumbnail(url=await embed_replacement(ctx.author, embed.thumbnail.url))
            content = result['content']
            if content:
                content = await embed_replacement(ctx.author, content)
            msg = await ctx.send(content=content, embed=embed, view=result['view'], files=result['files'], delete_after=result['delete_after'], allowed_mentions=discord.AllowedMentions(users=True, everyone=False))
            for reaction in result['reactions']:
                regex = re.search("<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>", reaction)
                if regex:
                    get_only_id = regex.group("id")
                    emoji = self.bot.get_emoji(int(get_only_id))
                    if emoji:
                        await msg.add_reaction(emoji)
                    else:
                        return await ctx.reply(embed=discord.Embed(ctx, "I can't find that emoji!"), mention_author=False)
                else:
                    import emoji
                    w = emoji.emojize(reaction)
                    if w:
                        await msg.add_reaction(w.replace(" ", ""))
                    else:
                        return await ctx.reply(embed=discord.Embed(ctx, "I can't find that emoji!"), mention_author=False)
    
    @commands.group(
        invoke_without_command=True,
        name='goodbye',
        description='Setup a goodbye message for old members',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: add #general Goodbye {mention}',
        aliases=['bye'],
        extras={'perms': 'Manage Guild'}
    )
    async def goodbye(self, ctx):
        await ctx.send_help(ctx.command)

    @goodbye.group(
        name='add',
        description='Add a goodbye message to a channel',
        brief='channel',
        usage=
        'Syntax: (channel)\n'
        'Example: {content: #general Goodbye {user.mention}!}',
        aliases=['set', 'create'],
        extras={'perms': 'Manage Guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_add(self, ctx, channel: discord.TextChannel, *, text):
        data = await self.bot.db.fetchval('SELECT channel_id, message FROM goodbye WHERE guild_id = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO goodbye (guild_id, channel_id, message) VALUES ($1, $2, $3)', ctx.guild.id, channel.id, text)
            await ctx.success(f'**Goodbye message** has been setup')
        if data:
            await self.bot.db.execute('UPDATE goodbye SET channel_id = $1, message = $2 WHERE guild_id = $3', channel.id, text, ctx.guild.id)
            await ctx.success(f'**Goodbye message** has been updated')

    @goodbye.group(
        name='remove',
        description='Remove a goodbye message from a channel',
        brief='channel',
        usage=
        'Syntax: (channel)\n'
        'Example: #general',
        aliases=['delete'],
        extras={'perms': 'Manage Guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_remove(self, ctx, channel: discord.TextChannel):
        data = await self.bot.db.fetchval('SELECT channel_id, message FROM goodbye WHERE guild_id = $1', ctx.guild.id)
        if data:
            await self.bot.db.execute('DELETE FROM goodbye WHERE channel_id = $1', channel.id)
            await ctx.success(f'**Goodbye message** has been removed')

    @goodbye.group(
        name='clear',
        description='Remove all goodbye messages',
        usage='Syntax: ',
        aliases=['purge'],
        extras={'perms': 'Manage Guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_clear(self, ctx):
        data = await self.bot.db.fetchval('SELECT channel_id, message FROM goodbye WHERE guild_id = $1', ctx.guild.id)
        if data:
            await self.bot.db.execute('DELETE FROM goodbye WHERE guild_id = $1', ctx.guild.id)
            await ctx.success(f'**Goodbye messages** has been cleared')

    @goodbye.group(
        name='test',
        description='Test all goodbye messages',
        usage='Syntax: ',
        aliases=['check'],
        extras={'perms': 'Manage Guild'}
    )
    @commands.has_permissions(manage_guild=True)
    async def goodbye_test(self, ctx):
        data = await self.bot.db.fetchval('SELECT message FROM goodbye WHERE guild_id = $1', ctx.guild.id)
        if data:
            result = await to_object(data)
            embed = result['embed']
            if embed:
                if embed.title:
                    embed.title = await embed_replacement(ctx.author, embed.title)
                if embed.description:
                    embed.description = await embed_replacement(ctx.author, embed.description)
                if embed.footer:
                    if embed.footer.text and embed.footer.icon_url:
                        embed.set_footer(text=await embed_replacement(ctx.author, embed.footer.text), icon_url=await embed_replacement(ctx.author, embed.footer.icon_url))
                    elif embed.footer.text:
                        embed.set_footer(text=await embed_replacement(ctx.author, embed.footer.text))
                    elif embed.footer.icon_url:
                        embed.set_footer(icon_url=await embed_replacement(ctx.author, embed.footer.icon_url))
                if embed.author:
                    if embed.author.name and embed.author.icon_url:
                        embed.set_author(name=await embed_replacement(ctx.author, embed.author.name), icon_url=await embed_replacement(ctx.author, embed.author.icon_url))
                    elif embed.author.name:
                        embed.set_author(name=await embed_replacement(ctx.author, embed.author.name))
                    elif embed.author.icon_url:
                        embed.set_author(icon_url=await embed_replacement(ctx.author, embed.author.icon_url))
                if embed.fields:
                    for field in embed.fields:
                        if field.name:
                            embed.set_field_at(index=embed.fields.index(field), name=await embed_replacement(ctx.author, field.name), value=await embed_replacement(ctx.author, field.value), inline=field.inline)
                if embed.image:
                    embed.set_image(url=await embed_replacement(ctx.author, embed.image.url))
                if embed.thumbnail:
                    embed.set_thumbnail(url=await embed_replacement(ctx.author, embed.thumbnail.url))
            content = result['content']
            if content:
                content = await embed_replacement(ctx.author, content)
            msg = await ctx.send(content=content, embed=embed, view=result['view'], files=result['files'], delete_after=result['delete_after'], allowed_mentions=discord.AllowedMentions(users=True, everyone=False))
            for reaction in result['reactions']:
                regex = re.search("<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>", reaction)
                if regex:
                    get_only_id = regex.group("id")
                    emoji = self.bot.get_emoji(int(get_only_id))
                    if emoji:
                        await msg.add_reaction(emoji)
                    else:
                        return await ctx.reply(embed=discord.Embed(ctx, "I can't find that emoji!"), mention_author=False)
                else:
                    import emoji
                    w = emoji.emojize(reaction)
                    if w:
                        await msg.add_reaction(w.replace(" ", ""))
                    else:
                        return await ctx.reply(embed=discord.Embed(ctx, "I can't find that emoji!"), mention_author=False)
    
    @commands.group(
        invoke_without_command=True,
        name='reactionrole',
        description='Create self-assignable roles using reactions',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: add https://discord.com/../ 🤍 White',
        aliases=['rr'],
        extras={'perms': 'Manage Roles'}
    )
    async def reactionrole(self, ctx):
        await ctx.send_help(ctx.command)

    @reactionrole.group(
        name='add',
        description='Add a reaction role to a message',
        brief='message, emote, role',
        usage=
        'Syntax: (message link) (emote) (role)\n'
        'Example: https://discord.com/../ 🤍 White',
        aliases=['create'],
        extras={'perms':'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, message_link: str, emote: str, role: discord.Role):
            message = message_link.strip("/").split("/")[-1]
            await self.bot.db.execute('INSERT INTO reactionroles (message, role, emote, guild) VALUES ($1, $2, $3, $4)', message, str(role.id), emote, ctx.guild.id)
            message = await ctx.channel.fetch_message(message)
            await message.add_reaction(emote)
            await ctx.success("You now successfully added a reaction role")

    @reactionrole.group(
        invoke_without_command=True,
        name='remove',
        description='Remove a reaction role from a message',
        brief='message, emote',
        usage=
        'Syntax: (message link) (emote)\n'
        'Example: https://discord.com/../ 🤍',
        aliases=['delete', 'del'],
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx, message_link: str, emote: str):
            message = message_link.strip("/").split("/")[-1]
            data = await self.bot.db.fetch('SELECT * FROM reactionroles WHERE message = $1 AND emote = $2 AND guild = $3',  message, emote, ctx.guild.id)
            if data:
                await self.bot.db.execute('DELETE FROM reactionroles WHERE message = $1 AND emote = $2 AND guild = $3', message, emote, ctx.guild.id)
                message = await ctx.channel.fetch_message(message)
                await message.clear_reaction(emote)
                await ctx.success("You now successfully removed a reaction role")

    @remove.group(
        name='all',
        description='Remove all reaction roles from a message',
        brief='message',
        usage=
        'Syntax: (message link)\n'
        'Example: https://discord.com/../',
        extras={'perms': 'Manage Roles'}
    )
    @commands.has_permissions(manage_roles=True)
    async def remove_all(self, ctx, message_link: str):
        message = message_link.strip("/").split("/")[-1]
        data = await self.bot.db.fetchval('SELECT message FROM reactionroles WHERE guild = $1', ctx.guild.id)
        if data:
            await self.bot.db.execute('DELETE FROM reactionroles WHERE message = $1', message)
            emotes = await message.fetch_emojis()
            message = await ctx.channel.fetch_message(message)
            await message.clear_reaction(emotes)
            await ctx.send('deleted all the rrs')

    @commands.group(
        invoke_without_command=True,
        name='response',
        description='Set up automatic trigger responses',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: add Hey!, How are you? --strict',
        aliases=['ar'],
        extras={'perms': 'Manage Messages'}
    )
    async def response(self, ctx):
        await ctx.send_help(ctx.command)

    @response.group(
        name='add',
        description='Add a response trigger',
        brief='trigger, response',
        usage=
        'Syntax: (trigger), (response)\n'
        'Example: Hey!, How are you? --strict',
        aliases=['create'],
        extras={'perms':'Manage Message'}
    )
    @commands.has_permissions(manage_messages=True)
    async def response_add(self, ctx, *, args):
        await ctx.typing()

        trigger, response = map(str.strip, args.split(","))
        await self.bot.db.execute("INSERT INTO response (guild_id, trigger, response) VALUES ($1, $2, $3)", ctx.guild.id, trigger, response)
        await ctx.success(f"Created a **response trigger** for `{trigger}`")

    @response.group(
        name='remove',
        description='Remove a response trigger',
        brief='trigger',
        usage=
        'Syntax: (trigger)\n'
        'Example: Hey!',
        aliases=['delete'],
        extras={'perms':'Manage Message'}
    )
    @commands.has_permissions(manage_messages=True)
    async def response_remove(self, ctx, trigger):
        await ctx.typing()

        await self.bot.db.execute("DELETE FROM response WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, trigger)
        await ctx.success(f"Removed **response trigger** for `{trigger}`")

    @commands.group(
        invoke_without_command=True,
        name='tracker',
        description='Track #0001 discriminator changes',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: add #tags',
        aliases=['track'],
        extras={'perms': 'Manage Channels'}
    )
    @commands.has_permissions(manage_channels=True)
    async def tracker(self, ctx):
        await ctx.typing()

        await ctx.send_help(ctx.command)

    @tracker.group(
        name='add',
        description='Add a channel to track discriminator changes',
        brief='channel',
        usage=
        'Syntax: <channel>\n'
        'Example: #tags',
        aliases=['create'],
        extras={'perms': 'Manage Channels'}
    )
    @commands.has_permissions(manage_channels=True)
    async def tracker_add(self, ctx, channel: discord.TextChannel):
        await ctx.typing()

        data = await self.bot.db.fetch(f"SELECT * FROM tracker WHERE guild_id = $1 AND channel = $2", ctx.guild.id, channel.id)
        if not data:
            await self.bot.db.execute("INSERT INTO tracker VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET channel = EXCLUDED.channel", ctx.guild.id, channel.id)
            await ctx.success(f'{channel.mention} is now **tracking** discriminators')
        else:
            await ctx.success(f'Tracker already bount to {channel.mention}')

    @tracker.group(
        name='remove',
        description='Remove a channel from tracking discriminator changes',
        brief='channel',
        usage=
        'Syntax: (channel)\n'
        'Example: #tags',
        aliases=['delete', 'del'],
        extras={'perms': 'Manage Channels'}
    )
    @commands.has_permissions(manage_channels=True)
    async def tracker_delete(self, ctx, channel: discord.TextChannel):
        await ctx.typing()

        data = await self.bot.db.fetch('SELECT channel FROM tracker WHERE guild_id = $1', ctx.guild.id)
        if data:
            await ctx.success(f'**{channel.mention}** is no longer **tracking** discriminators')
            await self.bot.db.execute("DELETE FROM tracker WHERE guild_id = $1", ctx.guild.id)
        else:
            await ctx.success("Tracker has not been added to your guild yet.")

    @commands.group(
        invoke_without_command=True,
        name='reaction',
        description='Set up reaction triggers',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: add court 🦈',
        aliases=['reactiontrigger', 'react', 'rt'],
        extras={'perms': 'Manage Messages'}
    )
    async def reactiontrigger(self, ctx):
        await ctx.send_help(ctx.command)

    @reactiontrigger.command(
        name='add',
        description='Add a reaction trigger',
        brief='trigger, emote',
        usage=
        'Syntax: (trigger) (emote)\n'
        'Example: court 🦈',
        aliases=['create'],
        extras={'perms':'Manage Message'}
    )
    async def add_reaction_trigger(self, ctx, trigger: str, reaction: str):
        await ctx.typing()

        await self.bot.db.execute("INSERT INTO reaction_trigger (guild_id, trigger, reaction) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING", ctx.guild.id, trigger.lower(), reaction)
        await ctx.success(f"Added **reaction trigger** for `{trigger}`")

    @reactiontrigger.command(
        name='remove',
        description='Remove a reaction trigger',
        brief='trigger',
        usage=
        'Syntax: (trigger)\n'
        'Example: court',
        aliases=['delete'],
        extras={'perms':'Manage Message'}
        )
    async def remove_reaction_trigger(self, ctx, trigger: str):
        await ctx.typing()

        await self.bot.db.execute("DELETE FROM reaction_trigger WHERE guild_id = $1 AND trigger = $2", ctx.guild.id, trigger)
        await ctx.success(f"Removed **reaction trigger** for `{trigger}`")

    @commands.group(
        invoke_without_command=True,
        name='vanity',
        description='Award users for advertising your server',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: set /voidbot'
    )
    async def vanity(self, ctx):
        await ctx.send_help(ctx.command)

    @vanity.group(
        name='set',
        description='Set a substring to detect in a status',
        brief='substring',
        usage=
        'Syntax: (substring)\n'
        'Example: /voidbot',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    @commands.has_permissions(manage_guild=True, manage_roles=True)
    async def vanity_set(self, ctx, *, substring: str):
        data = await self.bot.db.fetch('SELECT * FROM vanity WHERE guild = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO vanity (guild, substring) VALUES ($1, $2)', ctx.guild.id, substring)
            await ctx.success(f'Vanity substring set to `{substring}`')
        if data:
            await self.bot.db.execute('UPDATE vanity SET substring = $1 WHERE guild = $2', substring, ctx.guild.id)
            await ctx.success(f'Vanity substring updated to `{substring}`')
        if not substring:
            await ctx.send_help(ctx.command)

    # @vanity_set.group(
    #     name='view',
    #     description='View the settings for vanity',
    #     usage='Syntax: ',
    #     aliases=['check']
    # )
    # async def vanity_set_view(self, ctx):
    #     await ctx.send_help(ctx.command)

    @vanity.group(
        invoke_without_command=True,
        name='role',
        description='Award members with a role for advertising your server',
        usage=
        'Syntax: (role)\n'
        'Example: Promoter',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    @commands.has_permissions(manage_guild=True)
    async def vanity_role(self, ctx, role: discord.Role):
        data = await self.bot.db.fetch('SELECT * FROM vanity WHERE guild = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO vanity (guild, role) VALUES ($1, $2)', ctx.guild.id, role.id)
            await ctx.success(f'Vanity role set to {role.mention}')
        if data:
            await self.bot.db.execute('UPDATE vanity SET role = $1 WHERE guild = $2', role.id, ctx.guild.id)
            await ctx.success(f'Vanity role updated to {role.mention}')
        if not role:
            await ctx.send_help(ctx.command)

    @vanity.group(
        name='channel',
        description='Set an award channel for advertising members',
        brief='channel',
        usage=
        'Syntax: (channel)\n'
        'Example: #rep',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    async def vanity_channel(self, ctx, channel: discord.TextChannel):
        data = await self.bot.db.fetch('SELECT * FROM vanity WHERE guild = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO vanity (guild, channel) VALUES ($1, $2)', ctx.guild.id, channel.id)
            await ctx.success(f'Vanity award channel set to {channel.mention}')
        if data:
            await self.bot.db.execute('UPDATE vanity SET channel = $1 WHERE guild = $2', channel.id, ctx.guild.id)
            await ctx.success(f'Vanity award channel updated to {channel.mention}')
        if not channel:
            await ctx.send_help(ctx.command)

    @vanity.group(
        name='message',
        description='Set an award message for advertising members',
        brief='message',
        usage=
        'Syntax: (message)\n'
        'Example: thanks for repping /voidbot!',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    async def vanity_message(self, ctx, *, message: str):
        data = await self.bot.db.fetch('SELECT * FROM vanity WHERE guild = $1', ctx.guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO vanity (guild, message) VALUES ($1, $2)', ctx.guild.id, message)
            await ctx.success(f'Vanity message set to `{message}`')
        if data:
            await self.bot.db.execute('UPDATE vanity SET message = $1 WHERE guild = $2', message, ctx.guild.id)
            await ctx.success(f'Vanity message updated to `{message}`')
        if not message:
            await ctx.send_help(ctx.command)
            
    @vanity.group(
        name='reset',
        description='Reset all the vanity settings of your guild',
        usage='Syntax: ',
        extras={'perms': 'Manage Guild, Manage Roles'}
    )
    async def vanity_reset(self, ctx):
        await self.bot.db.execute('DELETE FROM vanity WHERE guild = $1', ctx.guild.id)
        await ctx.success('Vanity configuration has been **reset**')

async def setup(bot):
    await bot.add_cog(Servers(bot))
