import discord
from discord.ext import commands


color = 0x2b2d31

class TransferModal(discord.ui.Modal, title="Transfer"):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    firstfield = discord.ui.TextInput(
        label="Transfer ownership of your voice channel",
        placeholder="e.g: void#0480",
        min_length=1,
        max_length=32,
        style=discord.TextStyle.short,
    )
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data['components'][0]['components'][0]['value']:
            value = interaction.data['components'][0]['components'][0]['value']
            member = interaction.guild.get_member_named(value)
            if member:
                data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE owner = $1', member.id)
                if data:
                    e = discord.Embed(
                        color=color,
                        description=f'{member.mention} already owns a **voice channel**'
                    )
                    await interaction.response.send_message(embed=e, ephemeral=True)
                else:
                    await self.bot.db.execute('UPDATE voicemaster_data SET owner = $1 WHERE owner = $2', member.id, interaction.user.id)
                    channel = interaction.guild.get_channel(await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE owner = $1', member.id))
                    await channel.edit(name=f'{member.name}\'s channel')
                    e = discord.Embed(
                        color=color,
                        description=f'Your **voice channel** ownership has been **transferred** to {member.mention}'
                    )
                    await interaction.response.send_message(embed=e, ephemeral=True)
            else:
                e = discord.Embed(
                    color=color,
                    description=f'That **user** doesn\'t exist'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)

class RenameModal(discord.ui.Modal, title="Rename"):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    firstfield = discord.ui.TextInput(
        label="Rename your voice channel",
        placeholder="e.g: Movie Night",
        min_length=1,
        max_length=32,
        style=discord.TextStyle.short,
    )
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data['components'][0]['components'][0]['value']:
            name = interaction.data['components'][0]['components'][0]['value']
            if name is None:
                name = f'{interaction.author}\'s channel'
            if interaction.user.voice.channel:
                data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
                if data:
                    vc=interaction.guild.get_channel(data)
                    await vc.edit(name=name)
                    e = discord.Embed(
                        color=color,
                        description=f'Your **voice channel** has been renamed to **{name}**'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)
                else:
                    e = discord.Embed(
                        color=color,
                        description='You don\'t **own** this voice channel'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)
            else:
                e = discord.Embed(
                    color=color,
                    description='You aren\'t **connected** to a voice channel'
                )
                return await interaction.response.send_message(embed=e, ephemeral=True)

class IncreaseModal(discord.ui.Modal, title="Increase"):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    firstfield = discord.ui.TextInput(
        label="Increase your voice channel's limit",
        placeholder="e.g: 10",
        min_length=1,
        max_length=99,
        style=discord.TextStyle.short,
        required=True,
    )
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data['components'][0]['components'][0]['value']:
            limit = interaction.data['components'][0]['components'][0]['value']
            if str(limit).isdigit():
                if interaction.user.voice.channel:
                    data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
                    if data:
                        vc=interaction.guild.get_channel(data)
                        oldlimit = vc.user_limit
                        new = int(oldlimit) + int(limit)
                        if new > 99:
                            e = discord.Embed(
                                color=color,
                                description='You can\'t **increase** your voice channel\'s limit **above** 99'
                            )
                            return await interaction.response.send_message(embed=e, ephemeral=True)
                        await vc.edit(user_limit=new)
                        e = discord.Embed(
                            color=color,
                            description=f'Your **voice channel** user limit has been increased to **{new}**'
                        )
                        return await interaction.response.send_message(embed=e, ephemeral=True)
                    else:
                        e = discord.Embed(
                            color=color,
                            description='You don\'t **own** this voice channel'
                        )
                        return await interaction.response.send_message(embed=e, ephemeral=True)
                else:
                    e = discord.Embed(
                        color=color,
                        description='You aren\'t **connected** to a voice channel'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)

class DecreaseModal(discord.ui.Modal, title="Decrease"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    firstfield = discord.ui.TextInput(
        label="Decrease your voice channel's limit",
        placeholder="e.g: 10",
        min_length=1,
        max_length=99,
        style=discord.TextStyle.short,
        required=True,
    )
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data['components'][0]['components'][0]['value']:
            limit = interaction.data['components'][0]['components'][0]['value']
            if str(limit).isdigit():
                if interaction.user.voice.channel:
                    data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
                    if data:
                        vc=interaction.guild.get_channel(data)
                        old_amount = vc.user_limit
                        new = old_amount - int(limit)
                        if new < 0:
                            e = discord.Embed(
                                color=color,
                                description='You can\'t **decrease** your voice channel\'s limit **below** 0'
                            )
                            return await interaction.response.send_message(embed=e, ephemeral=True)
                        await vc.edit(user_limit=new)
                        e = discord.Embed(
                            color=color,
                            description=f'Your **voice channel** user limit has been decreased to **{new}**'
                        )
                        return await interaction.response.send_message(embed=e, ephemeral=True)
                    else:
                        e = discord.Embed(
                            color=color,
                            description='You don\'t **own** this voice channel'
                        )
                        return await interaction.response.send_message(embed=e, ephemeral=True)
                else:
                    e = discord.Embed(
                        color=color,
                        description='You aren\'t **connected** to a voice channel'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)

class DisconnectModal(discord.ui.Modal, title="Disconnect"):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    firstfield = discord.ui.TextInput(
        label="Disconnect a member from your voice channel",
        placeholder="e.g: void#0480",
        min_length=1,
        max_length=32,
        style=discord.TextStyle.short,
    )
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.data['components'][0]['components'][0]['value']:
            value = interaction.data['components'][0]['components'][0]['value']
            member = interaction.guild.get_member_named(value)
            if member:
                data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
                if data:
                    for m in interaction.user.voice.channel.members:
                        if member.id == m.id:
                            await member.move_to(None)
                        else:
                            e = discord.Embed(
                                color=color,
                                description=f'**{member}** isn\'t **connected** to your voice channel'
                            )
                            return await interaction.response.send_message(embed=e, ephemeral=True)
                    e = discord.Embed(
                        color=color,
                        description=f'**{member}** has been **disconnected** from your voice channel'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)
                else:
                    e = discord.Embed(
                        color=color,
                        description='You don\'t **own** this voice channel'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)
            else:
                e = discord.Embed(
                    color=color,
                    description=f'That **user** doesn\'t exist'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)

class Buttons(discord.ui.View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx
        self.value = None
        
    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_lock:1082284045372768286>')
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data:
                vc = interaction.guild.get_channel(data)
                if vc.overwrites_for(interaction.guild.default_role).connect is False:
                    e = discord.Embed(
                        color=color,
                        description='Your **voice channel** is already **locked**'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)
                await vc.set_permissions(interaction.guild.default_role, connect=False)
                e = discord.Embed(
                    color=color,
                    description='Your **voice channel** has been locked'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)
    
    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_unlock:1082284048266825738>')
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data:
                vc = interaction.guild.get_channel(data)
                if vc.overwrites_for(interaction.guild.default_role).connect is None:
                    e = discord.Embed(
                        color=color,
                        description='Your **voice channel** is already **unlocked**'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)
                await vc.set_permissions(interaction.guild.default_role, connect=None)
                e = discord.Embed(
                    color=color,
                    description='Your **voice channel** has been unlocked'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_hide:1082284058521899029>')
    async def ghost(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data: # test ahah
                vc = interaction.guild.get_channel(data)
                if vc.overwrites_for(interaction.guild.default_role).view_channel is False:
                    e = discord.Embed(
                        color=color,
                        description='Your **voice channel** is already **ghosted**'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)
                await vc.set_permissions(interaction.guild.default_role, view_channel=False)
                e = discord.Embed(
                    color=color,
                    description='Your **voice channel** has been ghosted'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_reveal:1082284056756097054>')
    async def unghost(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data:
                vc = interaction.guild.get_channel(data)
                if vc.overwrites_for(interaction.guild.default_role).view_channel is None:
                    e = discord.Embed(
                        color=color,
                        description='Your **voice channel** is already **unghosted**'
                    )
                    return await interaction.response.send_message(embed=e, ephemeral=True)
                await vc.set_permissions(interaction.guild.default_role, view_channel=None)
                e = discord.Embed(
                    color=color,
                    description='Your **voice channel** has been unghosted'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_trash:1082294834909417592>')
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data:
                vc = interaction.guild.get_channel(data)
                await vc.delete()
                await self.bot.db.execute('DELETE FROM voice WHERE voicemaster_data WHERE voice = $1', interaction.user.voice.channel.id)
                e = discord.Embed(
                    color=color,
                    description='Your **voice channel** has been deleted'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_owner:1082288435689173083>')
    async def transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data:
                await interaction.response.send_modal(TransferModal(self.bot))
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_rename:1082284054113697894>')
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data:
                await interaction.response.send_modal(RenameModal(self.bot))
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)
        
    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_plus:1082284036501811270>')
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data:
                await interaction.response.send_modal(IncreaseModal(self.bot))
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_minus:1082284039970488420>')
    async def decrease(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data:
                await interaction.response.send_modal(DecreaseModal(self.bot))
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.grey, emoji='<:void_hammer:1082284052616314943>')
    async def disconnect(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.voice is not None:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', interaction.user.voice.channel.id, interaction.user.id)
            if data:
                await interaction.response.send_modal(DisconnectModal(self.bot))
            else:
                e = discord.Embed(
                    color=color,
                    description='You don\'t **own** this voice channel'
                )
                await interaction.response.send_message(embed=e, ephemeral=True)
        else:
            e = discord.Embed(
                color=color,
                description='You aren\'t **connected** to a voice channel'
            )
            await interaction.response.send_message(embed=e, ephemeral=True)
        
class VoiceMaster(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.group(
        invoke_without_command=True,
        name='voicemaster',
        usage=
        'Syntax: (subcommand) <args>\n'
        'Example: setup',
        aliases=['vm', 'voice', 'vc']
    )
    async def voicemaster(self, ctx):
        await ctx.send_help(ctx.command)
    
    @voicemaster.group(
        name='setup',
        description='Setup the VoiceMaster channel',
        usage='Syntax: ',
        aliases=['create'],
        extras={'perms': 'Manage Channels'}
    )
    @commands.has_permissions(manage_channels=True)
    async def setup(self, ctx, category: discord.CategoryChannel=None):
        data = await self.bot.db.fetch('SELECT * FROM voicemaster WHERE guild_id = $1', ctx.guild.id)
        if not data:
            e = discord.Embed(
                color=color,
                description=f'Setting up **VoiceMaster** for **{ctx.guild}**'
            )
            msg = await ctx.reply(embed=e, mention_author=False)
            category = await ctx.guild.create_category_channel('void VoiceMaster')
            text = await ctx.guild.create_text_channel("interface", category=category)
            await text.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False))
            voice = await ctx.guild.create_voice_channel("Join to Create", category=category)
            e = discord.Embed(
                color=color,
                title='VoiceMaster Interface', url='https://discord.gg/voidbot',
                description=
                f'Click the buttons below to control your voice channel\n'
                f'> **[VoiceMaster Interface](https://discord.gg/voidbot)** is constrained to {voice.mention}'
            )
            e.add_field(name='Management',
                        value=
                        '> <:void_lock:1082284045372768286> **[Lock](https://discord.gg/voidbot)** your voice channel\n'
                        '> <:void_unlock:1082284048266825738> **[Unlock](https://discord.gg/voidbot)** your voice channel\n'
                        '> <:void_hide:1082284058521899029> **[Hide](https://discord.gg/voidbot)** your voice channel\n'
                        '> <:void_reveal:1082284056756097054> **[Reveal](https://discord.gg/voidbot)** your voice channel\n'
                        '> <:void_trash:1082294834909417592> **[Delete](https://discord.gg/voidbot)** your voice channel'
                        )
            e.add_field(name='Miscellaneous',
                        value=
                        '> <:void_owner:1082288435689173083> **[Transfer](https://discord.gg/voidbot)** the voice channel\n'
                        '> <:void_rename:1082284054113697894> **[Rename](https://discord.gg/voidbot)** your voice channel\n'
                        '> <:void_plus:1082284036501811270> **[Increase](https://discord.gg/voidbot)** the user limit\n'
                        '> <:void_minus:1082284039970488420> **[Decrease](https://discord.gg/voidbot)** the user limit\n'
                        '> <:void_hammer:1082284052616314943> **[Disconnect](https://discord.gg/voidbot)** a member'
                        )
            e.set_author(name=f'{ctx.guild.name}', icon_url=ctx.guild.icon.url)
            message = await text.send(embed=e, view=Buttons(self.bot, ctx))
            await self.bot.db.execute('INSERT INTO voicemaster (guild_id, category_id, voice, text, message) VALUES ($1, $2, $3, $4, $5)', ctx.guild.id, category.id, voice.id, text.id, message.id)

            e = discord.Embed(
                color=color,
                description=f'The **VoiceMaster** channel has been **setup**'
            )
            await msg.edit(embed=e)
        else:
            await ctx.success('The **VoiceMaster** channel has already been **setup**')
    
    @voicemaster.group(
        name='reset',
        description='Resets the VoiceMaster channel',
        usage='Syntax: ',
        extras={'perms': 'Manage Channels'}
    )
    @commands.has_permissions(manage_channels=True)
    async def reset(self, ctx):
        data = await self.bot.db.fetch('SELECT * FROM voicemaster WHERE guild_id = $1', ctx.guild.id)
        if data:
            check = await self.bot.db.fetch('SELECT voice, text FROM voicemaster WHERE guild_id = $1', ctx.guild.id)
            if check:
                for voice, text in check:
                    vc = ctx.guild.get_channel(voice)
                    txt = ctx.guild.get_channel(text)
                    await vc.delete()
                    await txt.category.delete()
                    await txt.delete()
            await self.bot.db.execute('DELETE FROM voicemaster WHERE guild_id = $1', ctx.guild.id)
            await ctx.success('The **VoiceMaster** channel has been reset')
        else:
            await ctx.success('The **VoiceMaster** channel has not been setup yet')

    @voicemaster.group(
        name='lock',
        description='Lock your voice channel',
        usage=
        'Syntax: '
    )
    async def lock(self, ctx):
        if ctx.author.voice.channel:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', ctx.author.voice.channel.id, ctx.author.id)
            if data:
                vc = ctx.guild.get_channel(data)
                await vc.set_permissions(ctx.guild.default_role, connect=False)
                await ctx.success('Your **voice channel** has been locked')
            else:
                await ctx.success(f'You don\'t **own** this voice channel')
        else:
            await ctx.success(f'You aren\'t **connected** to a voice channel')

    @voicemaster.group(
        name='unlock',
        description='Unlock your voice channel',
        usage=
        'Syntax: '
    )
    async def unlock(self, ctx):
        if ctx.author.voice.channel:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', ctx.author.voice.channel.id, ctx.author.id)
            if data:
                vc = ctx.guild.get_channel(data)
                await vc.set_permissions(ctx.guild.default_role, connect=None)
                await ctx.success('Your **voice channel** has been unlocked')
            else:
                await ctx.success(f'You don\'t **own** this voice channel')
        else:
            await ctx.success(f'You aren\'t **connected** to a voice channel')
    
    @voicemaster.group(
        name='permit',
        description='Permit a user access to your voice channel',
        brief='user',
        usage=
        'Syntax: (user)\n'
        'Example: void#0480',
        aliases=['allow']
    )
    async def permit(self, ctx, *, member: discord.Member):
        if ctx.author.voice.channel:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', ctx.author.voice.channel.id, ctx.author.id)
            if data:
                vc=ctx.guild.get_channel(data)
                await vc.set_permissions(member, connect=True)
                return await ctx.success(f'You permitted {member.mention} to access your **voice channel**')
            else:
                return await ctx.success('You don\'t **own** this voice channel')
        else:
            return await ctx.success('You aren\'t **connected** to a voice channel')

    @voicemaster.group(
        name='reject',
        description='Reject a user access to your voice channel',
        brief='user',
        usage=
        'Syntax: (user)\n'
        'Example: void#0480',
        aliases=['deny']
    )
    async def reject(self, ctx, *, member: discord.Member):
        if ctx.author.voice.channel:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', ctx.author.voice.channel.id, ctx.author.id)
            if data:
                vc=ctx.guild.get_channel(data)
                await vc.set_permissions(member, connect=False)
                return await ctx.success(f'You rejected {member.mention} to access your **voice channel**')
            else:
                return await ctx.success('You don\'t **own** this voice channel')
        else:
            return await ctx.success('You aren\'t **connected** to a voice channel')
    
    @voicemaster.group(
        name='ghost',
        description='Hide your voice channel',
        usage='Syntax: ',
        aliases=['hide']
    )
    async def ghost(self, ctx):
        if ctx.author.voice.channel:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', ctx.author.voice.channel.id, ctx.author.id)
            if data:
                vc=ctx.guild.get_channel(data)
                await vc.set_permissions(ctx.guild.default_role, view_channel=False)
                return await ctx.success(f'Your **voice channel** has been ghosted')
            else:
                return await ctx.success('You don\'t **own** this voice channel')
        else:
            return await ctx.success('You aren\'t **connected** to a voice channel')
        
    @voicemaster.group(
        name='unghost',
        description='Reveal your voice channel',
        usage='Syntax: ',
        aliases=['reveal']
    )
    async def unghost(self, ctx):
        if ctx.author.voice.channel:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', ctx.author.voice.channel.id, ctx.author.id)
            if data:
                vc=ctx.guild.get_channel(data)
                await vc.set_permissions(ctx.guild.default_role, view_channel=None)
                return await ctx.success(f'Your **voice channel** has been unghosted')
            else:
                return await ctx.success('You don\'t **own** this voice channel')
        else:
            return await ctx.success('You aren\'t **connected** to a voice channel')
        
    @voicemaster.group(
        name='limit',
        description='Set a user limit on your voice channel',
        usage=
        'Syntax: (amount)\n'
        'Example: 10'
    )
    async def limit(self, ctx, amount: int):
        if ctx.author.voice.channel:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', ctx.author.voice.channel.id, ctx.author.id)
            if data:
                vc=ctx.guild.get_channel(data)
                await vc.edit(user_limit=amount)
                if amount < 99:
                    return await ctx.success(f'Your **voice channel** limit has been set to **{amount}**')
                else:
                    return await ctx.success(f'The **voice channel** limit must be smaller than **99**')
            else:
                return await ctx.success('You don\'t **own** this voice channel')
        else:
            return await ctx.success('You aren\'t **connected** to a voice channel')
        
    @voicemaster.group(
        name='name',
        description='Rename your voice channel',
        usage=
        'Syntax: (new name)\n'
        'Example: movie night',
        aliases=['rename']
    )
    async def name(self, ctx, *, name: str):
        if ctx.author.voice.channel:
            data = await self.bot.db.fetchval('SELECT voice FROM voicemaster_data WHERE voice = $1 AND owner = $2', ctx.author.voice.channel.id, ctx.author.id)
            if data:
                vc=ctx.guild.get_channel(data)
                await vc.edit(name=name)
                return await ctx.success(f'Your **voice channel** has been renamed to **{name}**')
            else:
                return await ctx.success('You don\'t **own** this voice channel')
        else:
            return await ctx.success('You aren\'t **connected** to a voice channel')
        
    @voicemaster.group(
        name='claim',
        description='Claim an inactive voice channel',
        usage='Syntax: ',
        aliases=['steal']
    )
    async def claim(self, ctx):
        if ctx.author.voice is not None:
            data = await self.bot.db.fetchval('SELECT owner FROM voicemaster_data WHERE voice = $1', ctx.author.voice.channel.id)
            c2 = ctx.guild.get_member(data)
            if c2 in ctx.author.voice.channel.members:
                return await ctx.success('The **owner** is still in the **voice channel**')
            else:
                c = ctx.author.voice.channel
                try:
                    owner = ctx.guild.get_member(await self.bot.db.fetchval('SELECT owner FROM voicemaster_data WHERE voice = $1', c.id))
                except:
                    owner = await self.bot.fetch_user(data)
                if ctx.author.voice.channel.name == f"{owner.name}'s channel":
                    await c.edit(name=f"{ctx.author.name}'s channel")
                await self.bot.db.execute('UPDATE voicemaster_data SET owner = $1 WHERE owner = $2', ctx.author.id, c2.id)
                return await ctx.success('You\'re now the owner of the **voice channel**')
        else:
            return await ctx.success('You don\'t **own** this voice channel')
    
async def setup(bot):
    await bot.add_cog(VoiceMaster(bot))