from modules import logging, utils


class Cache:
    def __init__(self, bot):
        self.bot = bot
        self.prefixes = {}
        self.googlesafe = {}
        self.blacklist = {}
        self.autoresponse = {}
        self.autoreact = {}
        self.autoroles = {}
        self.apikeys = []
        self.chatfilter = {}
        self.levelupmessage = {}
        self.global_bl = {
            "guilds": [],
            "users": []
        }
        self.whitelist = {}
        self.welcome = {}
        self.boost = {}
        self.api_access_address = []
        self.lastfm = {}
        self.donators = []
        self.antinuke = {}
        self.bans = {}
        self.punishment = {}
        self.logging_settings = {}
        self.autoroles = {}
        self.afk = {}
        self.event_triggers = {
            "message": 0,
            "message_delete": 0,
            "message_edit": 0,
            "reaction_add": 0,
            "reaction_remove": 0,
            "member_join": 0,
            "member_remove": 0,
            "guild_join": 0,
            "guild_remove": 0,
            "member_ban": 0,
            "member_unban": 0,
        }
        self.stats_notifications_sent = 0
        self.stats_lastfm_requests = 0
        self.stats_html_rendered = 0
        # bot.Loop.create_task(self.initialize_settings_cache())

    async def initialize_settings_cache(self):
        
        prefixes = self.bot.db("prefixes")
        wlc = self.bot.db("welcome")
        bst = self.bot.db("boost")
        anti = self.bot.db("antinuke")
        punishments = self.bot.db("antinuke")
        cfs = self.bot.db("chatfilter")
        ars = self.bot.db("autoresponder")
        ared = self.bot.db("autoreact")
        lfs = self.bot.db("fmuser")
        keys = self.bot.db("apikeys")["keys"]
        autoroles = self.bot.db("autorole")
        gbl = self.bot.db("blacklisted")
        
        for g in anti:
            x = anti[g]
            self.whitelist[int(g)] = x["whitelisted"]
        for g in wlc:
            x = wlc[g]
            self.welcome[int(g)] = x
        for u in prefixes:
            x = prefixes[u]
            self.prefixes[int(u)] = x["prefix"]
        for g in punishments:
            x = punishments[g]
            self.punishment[int(g)] = x["punishment"]
        for g in cfs:
            x = cfs[g]
            self.chatfilter[int(g)] = x
        for g in ars:
            x = ars[g]
            self.autoresponse[int(g)] = x
        for u in lfs:
            x = lfs[u]
            self.lastfm[int(u)] = x

        for g in bst:
            x = bst[g]
            self.boost[int(g)] = x
        for g in wlc:
            x = wlc[g]
            self.welcome[int(g)] = x
        for key in keys:
            self.apikeys.append(key)
        for g in self.bot.guilds:
            try:
                self.bans[g.id] = [ban async for ban in g.bans(limit=None)]
            except:
                continue
            
        for g in gbl['servers']:
            self.global_bl['guilds'].append(g)
        
        for u in prefixes:
            if prefixes[u] == '\u2026':
                self.global_bl['users'].append(int(u))
            
    def __repr__(self):
        return f'<{self.__class__.__name__} synced=True>'