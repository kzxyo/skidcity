import discord, typing, time, arrow, psutil, copy, aiohttp, json, asyncio
from datetime import datetime
from typing import Optional, Union
from utilities import utils
from utilities.baseclass import Vile
from utilities.advancedutils import parse_timespan
from discord.ext import commands, tasks
from deep_translator import GoogleTranslator
from discord import app_commands


class ContextMenu(commands.Cog):
    def __init__(self, bot: Vile) -> None:
        self.bot = bot
        self.context_menus = [
            app_commands.ContextMenu(name='Translate to English', callback=self.translate_to_english),
            app_commands.ContextMenu(name='User Avatar', callback=self.user_avatar),
            app_commands.ContextMenu(name='User Info', callback=self.user_info)
        ]

        for context_menu in self.context_menus:
            self.bot.tree.add_command(context_menu)


    async def cog_unload(self):
        for context_menu in self.context_menus:
            self.bot.tree.remove_command(context_menu.name, type=context_menu.type)

        
    async def translate_to_english(self, interaction: discord.Interaction, message: discord.Message):

        await interaction.response.defer(thinking=True)
        trans = GoogleTranslator(source='auto', target='english')

        try:
            return await interaction.followup.send(await asyncio.to_thread(lambda: trans.translate(text=message.content)))
        except:
            return await interaction.followup.send(
                embed=discord.Embed(
                    color=self.bot.color,
                    description='failed to **translate** the provided text'
                )
            )


    async def user_avatar(self, interaction: discord.Interaction, member: discord.Member):
        
        await interaction.response.defer(thinking=True)

        embed = discord.Embed(color=await utils.dominant_color(member.display_avatar), title=f"{member.name}'s avatar")
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
        embed.url = member.display_avatar.url
        embed.set_image(url=member.display_avatar)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(style=discord.ButtonStyle.link, label='WEBP', url=str(member.display_avatar.replace(size=4096, format='webp')))
        )
        view.add_item(
            discord.ui.Button(style=discord.ButtonStyle.link, label='PNG', url=str(member.display_avatar.replace(size=4096, format='png')))
        )
        view.add_item(
            discord.ui.Button(style=discord.ButtonStyle.link, label='JPG', url=str(member.display_avatar.replace(size=4096, format='jpg')))
        )

        return await interaction.followup.send(embed=embed, view=view)


    async def user_info(self, interaction: discord.Interaction, member: discord.Member):
        
        await interaction.response.defer(thinking=True)

        embed = discord.Embed(color=await utils.dominant_color(member.display_avatar))

        # dates
        joined = f"{self.bot.reply} {discord.utils.format_dt(member.joined_at, style='R')}"
        created = f"{self.bot.reply} {discord.utils.format_dt(member.created_at, style='R')}"
        boosted = f'{self.bot.reply} N/A'

        if member.premium_since is not None:
            boosted = f"{self.bot.reply} {discord.utils.format_dt(member.premium_since, style='R')}"

        # roles
        roles = list() 
        if member.roles:
            if len(member.roles) > 5:
                roles = ', '.join([role.mention for role in list(reversed(member.roles[1:]))[:5]]) + f' + {len(member.roles) - 5} more'
            else:
                roles = ', '.join([role.mention for role in list(reversed(member.roles[1:]))[:5]]) + ', @everyone'

        # permissions
        if member.guild_permissions.administrator:
            permissions = 'Administrator'
                
        elif member.guild_permissions.create_instant_invite:
            permissions = 'Create Invite'

        else:
            permissions = 'No Permissions'

        # join position
        joinpos = utils.ordinal(sorted(interaction.guild.members, key=lambda m: m.joined_at).index(member) + 1)
        join_position = f'Join Position: {joinpos}'

        # badges
        ui = await utils.get_user(member.id)
        badges = list()
        emojis = {
            'nitro': '<:vile_nitro:1022941557541847101>',
            'hsbrilliance': '<:vile_hsbrilliance:1022941561392209991>',
            'hsbravery': '<:vile_hsbravery:1022941564349194240>',
            'hsbalance': '<:vile_hsbalance:1022941567318765619>',
            'bhunter': '<:vile_bhunter:991776532227969085>',
            'bhunterplus': '<:vile_bhunterplus:991776477278388386>',
            'cmoderator': '<:vile_cmoderator:1022943277340692521>',
            'esupporter': '<:vile_esupporter:1022943630945685514>',
            'dev': '<:vile_dev:1042082778629537832>',
            'partner': '<:vile_partner:1022944710895075389>',
            'dstaff': '<:vile_dstaff:1022944972858720327>',
            'vbot': '<:vile_vbot:1022945560094834728>',
            'sboost': '<:vile_sboost:1022950372576342146>',
            'activedev': '<:vile_activedev:1043160384124751962>'
        }

        flags = member.public_flags
        if flags.bug_hunter:
            badges.append(emojis['bhunter'])
        if flags.bug_hunter_level_2:
            badges.append(emojis['bhunterplus'])
        if flags.discord_certified_moderator:
            badges.append(emojis['cmoderator'])
        if flags.early_supporter:
            badges.append(emojis['esupporter'])
        if flags.hypesquad_balance:
            badges.append(emojis['hsbalance'])
        if flags.hypesquad_bravery:
            badges.append(emojis['hsbravery'])
        if flags.hypesquad_brilliance:
            badges.append(emojis['hsbrilliance'])
        if flags.partner:
            badges.append(emojis['partner'])
        if flags.staff:
            badges.append(emojis['dstaff'])
        if flags.verified_bot:
            badges.append(emojis['vbot'])
        if flags.verified_bot_developer:
            badges.append(emojis['dev'])
        if flags.active_developer:
            badges.append(emojis['activedev'])
        try:
            if ui['premium_since'] or 'NITRO' in ui['badges']:
                badges.append(emojis['nitro'])
            if ui['premium_guild_since']:
                badges.append(emojis['sboost'])
        except:
            pass


        if emojis['sboost'] not in badges:
            for guild in member.mutual_guilds:
                if guild.get_member(member.id).premium_since is not None:
                    if emojis['nitro'] not in badges:
                        badges.append(emojis['nitro'])
                    badges.append(emojis['sboost'])
                    break

        
        # mutuals
        mutual_guilds = 'No mutual guilds' if not member.mutual_guilds else f'{len(member.mutual_guilds)} mutual guild{"" if len(member.mutual_guilds) == 1 else "s"}'

        # buttons
        avatar = member.display_avatar.url
        memberr = await self.bot.fetch_user(member.id)
        banner = 'https://none.none' if not memberr.banner else memberr.banner.url
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(style=discord.ButtonStyle.link, label='avatar', url=avatar, disabled=False)
        )
        view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link, 
                label='banner', 
                url=banner, 
                disabled=True if banner == 'https://none.none' else False
            )
        )

        # embed
        embed.title = f"{member}  \u2022  {' '.join(badges)}"
        embed.set_author(name=f'{member.name} ( {member.id} )',icon_url=member.display_avatar)

        pp = f'{permissions} \u2022 {join_position} \u2022 '
        embed.set_footer(text=pp + mutual_guilds)

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name=f'{self.bot.dash} Created', value=created)
        embed.add_field(name=f'{self.bot.dash} Joined', value=joined)
        embed.add_field(name=f'{self.bot.dash} Boosted', value=boosted)

        if roles:
            embed.add_field(name=f'{self.bot.dash} Roles [{len(member.roles)}]', value=roles, inline=False)

        return await interaction.followup.send(embed=embed, view=view)


async def setup(bot: Vile):
    await bot.add_cog(ContextMenu(bot))
