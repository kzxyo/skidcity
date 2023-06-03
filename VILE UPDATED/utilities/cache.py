from discord.ext import commands
from . import utils
import json, tuuid

class VileCache:
    def __init__(self, bot: 'Vile'):
        self.bot = bot
        self._namespace = tuuid.tuuid() 
        self.force_nickname = dict()
        self.image_only = dict()
        self.tracker = dict()
        self.tiktok_reposting = dict()
        self.youtube_reposting = dict()
        self.member_joins = dict()
        self.antiraid = dict()
        self.antiraid_trigger = dict()
        self.antiraid_whitelist = dict()
        self.automod = dict()
        self.automod_whitelist = dict()
        self.customprefixes = dict()
        self.reactionroles = dict()
        self.fakepermissions = dict()
        self.aliases = dict()
        self.highlights = dict()
        self.discriminator_roles = dict()
        self.uwulock = dict()
        self.verification = dict()
        self.semimute = dict()
        self.guildprefixes = dict()
        self.afk = dict()
        self.googlesafe = dict()
        self.blacklist = dict()
        self.autoresponder = dict()
        self.joindm = dict()
        self.pingonjoin = dict()
        self.disabled_commands = dict()
        self.autoreact = dict()
        self.autoroles = dict()
        self.nodata = dict()
        self.chatfilter = dict()
        self.warden = {'ban': dict(), 'kick': dict()}
        self.warden_limit = {'ban': dict(), 'kick': dict()}
        self.leveling = dict()
        self.levels = dict()
        self.global_bl = {
            'guilds': set(),
            'users': set()
        }
        self.errors = dict()
        self.admin = {}
        self.whitelist = dict()
        self.goodbyemessage = dict()
        self.goodbyechannel = dict()
        self.welcomemessage = dict()
        self.welcomechannel = dict()
        self.boostmessage = dict()
        self.boostchannel = dict()
        self.api_access_address = list()
        self.lastfm = dict()
        self.donators = dict()
        self.skullboard = dict()
        self.antinuke = dict()
        self.antinuke_logs = dict()
        self.punishment = dict()
        self.logging_settings = dict()
        self.autoroles = dict()
        self.afk = dict()
        self.event_triggers = {
            'message': 0,
            'message_delete': 0,
            'message_edit': 0,
            'reaction_add': 0,
            'reaction_remove': 0,
            'member_join': 0,
            'member_remove': 0,
            'guild_join': 0,
            'guild_remove': 0,
            'member_ban': 0,
            'member_unban': 0,
        }
        self.limits = {
            'dms': dict(),
            'bans': dict(),
            'kicks': dict(),
            'role_delete': dict(),
            'role_create': dict()
        }
        self.stats_notifications_sent = 0
        self.stats_lastfm_requests = 0
        self.stats_html_rendered = 0
        # bot.Loop.create_task(self.initialize_settings_cache())


    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self._namespace} items={sum([len(getattr(self, i)) for i in dir(self) if isinstance(getattr(self, i), (dict, list))])}>'


    async def cache_lastfm(self) -> None:
        self.lastfm = dict()
        lfembeds = await self.bot.db.execute('SELECT user_id, code FROM lastfm_embed')
        lfs = await self.bot.db.execute('SELECT user_id, lastfm_username FROM lastfm')
        lfcommands = await self.bot.db.execute('SELECT user_id, name FROM lastfm_command')
        lfreactions = await self.bot.db.execute('SELECT user_id, emoji_id FROM lastfm_reactions')

        for user_id, lastfm_username in lfs:
            if user_id not in self.lastfm:
                self.lastfm[user_id] = {'username': None, 'embed': None, 'command': None, 'reactions': list()}

            self.lastfm[user_id]['username'] = lastfm_username

        for user_id, code in lfembeds:
            if user_id not in self.lastfm:
                self.lastfm[user_id] = {'username': None, 'embed': None, 'command': None, 'reactions': list()}

            self.lastfm[user_id]['embed'] = code

        for user_id, name in lfcommands:
            if user_id not in self.lastfm:
                self.lastfm[user_id] = {'username': None, 'embed': None, 'command': None, 'reactions': list()}

            self.lastfm[user_id]['command'] = name

        for user_id, emoji_id in lfreactions:
            if user_id not in self.lastfm:
                self.lastfm[user_id] = {'username': None, 'embed': None, 'command': None, 'reactions': list()}

            self.lastfm[user_id]['reactions'].append(emoji_id)


    async def cache_autoroles(self) -> None:
        self.autoroles = dict()
        autoroles = await self.bot.db.execute('SELECT guild_id, role_id FROM autorole')

        for guild_id, role_id in autoroles:
            if guild_id not in self.autoroles:
                self.autoroles[guild_id] = list()

            self.autoroles[guild_id].append(role_id)


    async def cache_discriminator_roles(self) -> None:
        self.discriminator_roles = dict()
        drs = await self.bot.db.execute('SELECT guild_id, role_id, discriminator FROM discriminator_roles')

        for guild_id, role_id, discriminator in drs:
            if guild_id not in self.discriminator_roles:
                self.discriminator_roles[guild_id] = list()

            self.discriminator_roles[guild_id].append({'role_id': role_id, 'discriminator': discriminator})


    async def cache_discriminator_trackers(self) -> None:
        self.tracker = dict()
        dts = await self.bot.db.execute('SELECT guild_id, channel_id, discriminator FROM tracker')

        for guild_id, channel_id, discriminator in dts:
            if guild_id not in self.tracker:
                self.tracker[guild_id] = list()

            self.tracker[guild_id].append({'channel_id': channel_id, 'discriminator': discriminator})


    async def cache_verification_channels(self) -> None:
        self.verification = dict()
        vcss = await self.bot.db.execute('SELECT guild_id, channel_id, role_id, text FROM verification')

        for guild_id, channel_id, role_id, text in vcss:
            if guild_id not in self.verification:
                self.verification[guild_id] = dict()

            self.verification[guild_id][channel_id] = {'role_id': role_id, 'text': text}


    async def cache_prefixes(self) -> None:
        self.customprefixes=dict()
        self.guildprefixes = dict()
        customprefixes = await self.bot.db.execute("SELECT user_id, prefix FROM customprefix")
        guildprefixes = await self.bot.db.execute("SELECT guild_id, prefix FROM guildprefix")

        for user_id, prefix in customprefixes:
            self.customprefixes[user_id] = prefix

        for guild_id, prefix in guildprefixes:
            self.guildprefixes[guild_id] = prefix
    

    async def cache_afk(self) -> None:
        self.afk = dict()
        afk = await self.bot.db.execute('SELECT user_id, guild_id, status, lastseen FROM afk')

        for user_id, guild_id, status, lastseen in afk:
            if user_id not in self.afk:
                self.afk[user_id] = list()

            self.afk[user_id].append({
                'guild_id': guild_id,
                'status': status,
                'lastseen': lastseen
            })


    async def cache_welcome(self) -> None:
        self.welcomemessage = dict()
        self.welcomechannel = dict()
        welcome = await self.bot.db.execute("SELECT guild_id, message FROM welcome_message")
        welcomechannels = await self.bot.db.execute("SELECT guild_id, channel_id FROM welcome_channel")

        for guild_id, message in welcome:
            self.welcomemessage[guild_id] = message
            
        for guild_id, channel_id in welcomechannels:
            self.welcomechannel[guild_id] = channel_id


    async def cache_goodbye(self) -> None:
        self.goodbyemessage = dict()
        self.goodbyechannel = dict()
        goodbye = await self.bot.db.execute("SELECT guild_id, message FROM goodbye_message")
        goodbyechannels = await self.bot.db.execute("SELECT guild_id, channel_id FROM goodbye_channel")

        for guild_id, message in goodbye:
            self.goodbyemessage[guild_id] = message

        for guild_id, channel_id in goodbyechannels:
            self.goodbyechannel[guild_id] = channel_id


    async def cache_boost(self) -> None:
        self.boostmessage = dict()
        self.boostchannel = dict()
        boost = await self.bot.db.execute('SELECT guild_id, message FROM boost_message')
        boostchannels = await self.bot.db.execute('SELECT guild_id, channel_id FROM boost_channel')

        for guild_id, message in boost:
            self.boostmessage[guild_id] = message

        for guild_id, channel_id in boostchannels:
            self.boostchannel[guild_id] = channel_id


    async def cache_chatfilter(self) -> None:
        self.chatfilter = dict()
        cfs = await self.bot.db.execute('SELECT guild_id, strr FROM chatfilter')

        for guild_id, strr in cfs:
            if guild_id not in self.chatfilter:
                self.chatfilter[guild_id] = set()

            self.chatfilter[guild_id].add(strr)


    async def cache_uwulock(self) -> None:
        self.uwulock = dict()
        uwus = await self.bot.db.execute('SELECT guild_id, user_id FROM uwulock')

        for guild_id, user_id in uwus:
            if guild_id not in self.uwulock:
                self.uwulock[guild_id] = set()

            self.uwulock[guild_id].add(user_id)


    async def cache_semimute(self) -> None:
        self.semimute= dict()
        semis = await self.bot.db.execute('SELECT guild_id, user_id FROM semimute')

        for guild_id, user_id in semis:
            if guild_id not in self.semimute:
                self.semimute[guild_id] = set()

            self.semimute[guild_id].add(user_id)


    async def cache_autoresponder(self) -> None:
        self.autoresponder = dict()
        ars = await self.bot.db.execute('SELECT guild_id, trig, content FROM autoresponder')

        for guild_id, trig, content in ars:
            if guild_id not in self.autoresponder:
                self.autoresponder[guild_id] = list()

            self.autoresponder[guild_id].append((trig, content))


    async def cache_autoreact(self) -> None:
        self.autoreact = dict()
        ars = await self.bot.db.execute('SELECT guild_id, trig, reaction FROM autoreact')

        for guild_id, trig, reaction in ars:
            if guild_id not in self.autoreact:
                self.autoreact[guild_id] = list()

            self.autoreact[guild_id].append((trig, reaction))


    async def cache_skullboard(self) -> None:
        skull = await self.bot.db.execute('SELECT guild_id, channel_id FROM skullboard')

        for guild_id, channel_id in skull:
            self.skullboard[guild_id] = channel_id


    async def cache_pingonjoin(self) -> None:
        poj = await self.bot.db.execute('SELECT guild_id, channel_id FROM ping_on_join')

        for guild_id, channel_id in poj:
            if guild_id not in self.pingonjoin:
                self.pingonjoin[guild_id] = list()

            self.pingonjoin[guild_id].append(channel_id)


    async def cache_warden(self) -> None:
        self.warden = {'ban': dict(), 'kick': dict()}
        self.warden_limit = {'ban': dict(), 'kick': dict()}
        warden = await self.bot.db.execute('SELECT guild_id, ban, kick, banlimit, kicklimit FROM warden')

        for guild_id, ban, kick, banlimit, kicklimit in warden:
            self.warden['ban'][guild_id] = 0
            self.warden['kick'][guild_id] = 0
            self.warden_limit['ban'][guild_id] = banlimit
            self.warden_limit['kick'][guild_id] = kicklimit
    

    async def cache_disabledcommands(self) -> None:
        self.disabled_commands = dict()
        disabledcommands = await self.bot.db.execute('SELECT guild_id, command FROM disabled_commands')

        for guild_id, command in disabledcommands:
            if guild_id not in self.disabled_commands:
                self.disabled_commands[guild_id] = list()

            self.disabled_commands[guild_id].append(command)


    async def cache_nodata(self) -> None:
        self.nodata = dict()
        nodata = await self.bot.db.execute('SELECT user_id, data FROM nodata')

        for user_id, data in nodata:
            self.nodata[user_id] = data


    async def cache_imageonly(self) -> None:
        self.image_only = dict()
        imgonly = await self.bot.db.execute('SELECT guild_id, channel_id FROM image_only')

        for guild_id, channel_id in imgonly:
            if guild_id not in self.image_only:
                self.image_only[guild_id] = list()

            self.image_only[guild_id].append(channel_id)

    
    async def cache_joindm(self) -> None:
        self.joindm = dict()
        jdm = await self.bot.db.execute('SELECT guild_id, message FROM joindm')

        for guild_id, message in jdm:
            self.joindm[guild_id] = message


    async def cache_reactionroles(self) -> None:
        self.reactionroles = dict()
        rrs = await self.bot.db.execute('SELECT guild_id, message_id, role_id, emoji FROM reaction_roles')

        for guild_id, message_id, role_id, emoji in rrs:
            if guild_id not in self.reactionroles:
                self.reactionroles[guild_id] = dict()
            
            if message_id not in self.reactionroles[guild_id]:
                self.reactionroles[guild_id][message_id] = list()

            self.reactionroles[guild_id][message_id].append({'role_id': role_id, 'emoji': emoji})


    async def cache_forcenickname(self) -> None:
        self.force_nickname = dict()
        forcenick = await self.bot.db.execute('SELECT guild_id, user_id, nickname FROM forcenick')

        for guild_id, user_id, nickname in forcenick:
            if guild_id not in self.force_nickname:
                self.force_nickname[guild_id] = dict()

            self.force_nickname[guild_id][user_id] = nickname


    async def cache_highlights(self) -> None:
        self.highlights = dict()
        hl = await self.bot.db.execute('SELECT guild_id, creator_id, name FROM highlights')

        for guild_id, creator_id, name in hl:
            if guild_id not in self.highlights:
                self.highlights[guild_id] = dict()

            self.highlights[guild_id][name] = creator_id


    async def cache_antiraid(self) -> None:
        self.antiraid = dict()
        antiraid = await self.bot.db.execute('SELECT guild_id, avatar, joins, age FROM antiraid')
        antiraidwhitelist = await self.bot.db.execute('SELECT guild_id, user_id FROM antiraid_whitelist')

        for guild_id, avatars, joins, age in antiraid:
            self.antiraid[guild_id] = {'avatar': avatars, 'joins': joins, 'age': age}

        for guild_id, user_id in antiraidwhitelist:
            if guild_id not in self.antiraid_whitelist:
                self.antiraid_whitelist[guild_id] = set()

            self.antiraid_whitelist[guild_id].add(user_id)


    async def cache_automod(self) -> None:
        self.automod = dict()
        automod = await self.bot.db.execute('SELECT guild_id, spam, invites, massmention FROM automod')
        automodwhitelist = await self.bot.db.execute('SELECT guild_id, user_id FROM automod_whitelist')

        for guild_id, spam, invites, massmention in automod:
            self.automod[guild_id] = {'spam': spam, 'invites': invites, 'massmention': massmention}

        for guild_id, user_id in automodwhitelist:
            if guild_id not in self.automod_whitelist:
                self.automod_whitelist[guild_id] = set()

            self.automod_whitelist[guild_id].add(user_id)
                

    async def cache_aliases(self) -> None:
        self.aliases = dict()
        aliases = await self.bot.db.execute('SELECT guild_id, alias, command FROM aliases')

        for guild_id, alias, command in aliases:
            if guild_id not in self.aliases:
                self.aliases[guild_id] = dict()

            self.aliases[guild_id][alias] = command


    async def cache_antinuke(self) -> None:
        self.antinuke = dict()
        self.punishment = dict()
        self.whitelist = dict()
        self.admin = dict()
        punishments = await self.bot.db.execute('SELECT guild_id, punishment FROM punishment')
        whitelisted = await self.bot.db.execute('SELECT guild_id, user_id FROM antinuke_whitelist')
        admins = await self.bot.db.execute('SELECT guild_id, user_id FROM antinuke_admins')
        antinuke = await self.bot.db.execute('SELECT guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook FROM antinuke')

        for guild_id, punishment in punishments:
            self.punishment[guild_id] = punishment
            
        for guild_id, user_id in whitelisted:
            if guild_id not in self.whitelist:
                self.whitelist[guild_id] = set()

            self.whitelist[guild_id].add(user_id)

        for guild_id, user_id in admins:
            if guild_id not in self.admin:
                self.admin[guild_id] = set()

            self.admin[guild_id].add(user_id)

        for (guild_id, ban, kick, rolecreate, roledelete, channelcreate, channeldelete, webhook) in antinuke:
            self.antinuke[guild_id] = {'ban': ban, 'kick': kick, 'rolecreate': rolecreate, 'roledelete': roledelete, 'channelcreate': channelcreate, 'channeldelete': channeldelete, 'webhook': webhook}
        

    async def cache_fakepermissions(self) -> None:
        self.fakepermissions = dict()
        fp = await self.bot.db.execute('SELECT guild_id, role_id, permission FROM fake_permissions')

        for guild_id, role_id, permission in fp:
            if guild_id not in self.fakepermissions:
                self.fakepermissions[guild_id] = dict()

            if role_id not in self.fakepermissions[guild_id]:
                self.fakepermissions[guild_id][role_id] = set()

            self.fakepermissions[guild_id][role_id].add(permission)


    async def initialize_settings_cache(self) -> None:
        blusers = await self.bot.db.fetch('SELECT user_id FROM blacklisted_users')
        blguilds = await self.bot.db.fetch('SELECT guild_id FROM blacklisted_guilds')
        tiktok = await self.bot.db.execute('SELECT guild_id, state FROM tiktok_reposting')
        youtube = await self.bot.db.execute('SELECT guild_id, state FROM youtube_reposting')
        levels = await self.bot.db.execute('SELECT guild_id, user_id, experience, level FROM levels')
        levelsettings = await self.bot.db.execute('SELECT guild_id, state, message FROM level_settings')

        await self.cache_antinuke()
        await self.cache_autoresponder()
        await self.cache_lastfm()
        await self.cache_boost()
        await self.cache_skullboard()
        await self.cache_pingonjoin()
        await self.cache_disabledcommands()
        await self.cache_afk()
        await self.cache_nodata()
        await self.cache_chatfilter()
        await self.cache_prefixes()
        await self.cache_warden()
        await self.cache_welcome()
        await self.cache_goodbye()
        await self.cache_boost()
        await self.cache_imageonly()
        await self.cache_joindm()
        await self.cache_forcenickname()
        await self.cache_highlights()
        await self.cache_antiraid()
        await self.cache_autoroles()
        await self.cache_aliases()
        await self.cache_fakepermissions()
        await self.cache_automod()
        await self.cache_uwulock()
        await self.cache_semimute()
        await self.cache_discriminator_roles()
        await self.cache_discriminator_trackers()
        await self.cache_verification_channels()

        for user_id in blusers:
            self.global_bl['users'].add(user_id)

        for guild_id in blguilds:
            self.global_bl['guilds'].add(guild_id)

        for guild_id, state in tiktok:
            self.tiktok_reposting[guild_id] = state

        for guild_id, state in youtube:
            self.youtube_reposting[guild_id] = state

        for guild_id, user_id, experience, level in levels:
            if guild_id not in self.levels:
                self.levels[guild_id] = dict()

            self.levels[guild_id][user_id] = {'experience': experience, 'level': level} 
            
        for guild_id, state, message in levelsettings:
            self.leveling[guild_id] = {'state': state, 'message': message}
