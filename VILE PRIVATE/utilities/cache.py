from typing import Any, Union, Optional


class BaseKey:
    def __init__(self, cache: Union[dict, list, set], database: "MariaDB") -> None:
        self.cache = cache
        self.db = database

    
    def __setitem__(self, key: Any, value: Any) -> None:
        self.cache[key] = value


    def __getitem__(self, key: Any) -> Any:
        return self.cache.get(key)


    def store(self, key: Any, value: Any) -> Any:
        if value is None or len(value) == 0:
            return None

        self.cache[key] = value
        return value


class Blacklists(BaseKey):
    async def get(self, object_id: int) -> Any:
        if object_id in self.cache:
            return self.cache[object_id]

        if data := await self.db.fetchval("SELECT reason FROM blacklisted_object WHERE object_id = %s;", object_id):
            return self.store(object_id, data)


class CustomPrefix(BaseKey):
    async def get(self, user_id: int) -> Any:
        if user_id in self.cache:
            return self.cache[user_id]

        if data := await self.db.fetchval("SELECT prefix FROM custom_prefix WHERE user_id = %s;", user_id):
            return self.store(user_id, data)


class GuildPrefix(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetchval("SELECT prefix FROM guild_prefix WHERE guild_id = %s;", guild_id):
            return self.store(guild_id, data)


class LastfmVote(BaseKey):
    async def get(self, user_id: int) -> Any:
        if user_id in self.cache:
            return self.cache[user_id]

        if data := await self.db.fetchrow("SELECT is_enabled, upvote_emoji, downvote_emoji FROM lastfm_vote_setting WHERE user_id = %s;", user_id):       
            is_enabled, upvote_emoji, downvote_emoji = data
            return self.store(
                user_id,
                {"is_enabled": is_enabled, "upvote_emoji": upvote_emoji, "downvote_emoji": downvote_emoji}
            )


class Donator(BaseKey):
    async def get(self, user_id: int) -> Any:
        if user_id in self.cache:
            return self.cache[user_id]

        if data := await self.db.fetchrow("SELECT donation_tier, total_donated, donating_since FROM donator WHERE user_id = %s;", user_id):        
            donation_tier, total_donated, donating_since = data
            return self.store(
                user_id,
                {"donation_tier": donation_tier, "total_donated": total_donated, "donating_since": donating_since}
            )


class StarboardBlacklist(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetch("SELECT channel_id FROM starboard_blacklist WHERE guild_id = %s;", guild_id):
            return self.store(guild_id, list(data))


class WelcomeSettings(BaseKey):
    async def get(self, guild_id: int, channel_id: Optional[int] = None) -> Any:
        if guild_id in self.cache:
            if channel_id:
                if channel_id in self.cache[guild_id]:
                    return self.cache[guild_id][channel_id]
                
                return
            
            return self.cache[guild_id]

        if channel_id: 
            data = await self.db.fetchrow("SELECT is_enabled, message FROM welcome_settings WHERE guild_id = %s AND channel_id = %s;", guild_id, channel_id)
        
        else:
            data = await self.db.execute("SELECT channel_id, is_enabled, message FROM welcome_settings WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if channel_id:
                is_enabled, message = data
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
                return {"is_enabled": is_enabled, "message": message}

            for channel_id, is_enabled, message in data:
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
            
            return self.cache[guild_id]


class BoostSettings(BaseKey):
    async def get(self, guild_id: int, channel_id: Optional[int] = None) -> Any:
        if guild_id in self.cache:
            if channel_id:
                if channel_id in self.cache[guild_id]:
                    return self.cache[guild_id][channel_id]

                return
            
            return self.cache[guild_id]

        if channel_id: 
            data = await self.db.fetchrow("SELECT is_enabled, message FROM boost_settings WHERE guild_id = %s AND channel_id = %s;", guild_id, channel_id)
        
        else:
            data = await self.db.execute("SELECT channel_id, is_enabled, message FROM boost_settings WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if channel_id:
                is_enabled, message = data
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
                return {"is_enabled": is_enabled, "message": message}

            for channel_id, is_enabled, message in data:
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
            
            return self.cache[guild_id]


class UnboostSettings(BaseKey):
    async def get(self, guild_id: int, channel_id: Optional[int] = None) -> Any:
        if guild_id in self.cache:
            if channel_id:
                if channel_id in self.cache[guild_id]:
                    return self.cache[guild_id][channel_id]

                return
            
            return self.cache[guild_id]

        if channel_id: 
            data = await self.db.fetchrow("SELECT is_enabled, message FROM unboost_settings WHERE guild_id = %s AND channel_id = %s;", guild_id, channel_id)
        
        else:
            data = await self.db.execute("SELECT channel_id, is_enabled, message FROM unboost_settings WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if channel_id:
                is_enabled, message = data
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
                return {"is_enabled": is_enabled, "message": message}

            for channel_id, is_enabled, message in data:
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
            
            return self.cache[guild_id]


class BoosterRole(BaseKey):
    async def get(self, guild_id: int, user_id: Optional[int] = None) -> Any:
        if guild_id in self.cache:
            if user_id:
                if user_id in self.cache[guild_id]:
                    return self.cache[guild_id][user_id]

                return
            
            return self.cache[guild_id]

        if user_id: 
            data = await self.db.fetchval("SELECT role_id FROM booster_role WHERE guild_id = %s AND user_id = %s;", guild_id, user_id)
        
        else:
            data = await self.db.execute("SELECT guild_id, user_id, role_id FROM unboost_settings WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if user_id:
                self.cache[guild_id][user_id] = role_id
                return role_id

            for user_id, role_id in data:
                self.cache[guild_id][user_id] = role_id
            
            return self.cache[guild_id]


class BoosterRoleAward(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetchval("SELECT role_id FROM booster_role_award WHERE guild_id = %s;", guild_id):
            return self.store(guild_id, data)


class BoosterRoleBase(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetchval("SELECT role_id FROM booster_role_base WHERE guild_id = %s;", guild_id):
            return self.store(guild_id, data)


class LeaveSettings(BaseKey):
    async def get(self, guild_id: int, channel_id: Optional[int] = None) -> Any:
        if guild_id in self.cache:
            if channel_id:
                if channel_id in self.cache[guild_id]:
                    return self.cache[guild_id][channel_id]
                
                return
            
            return self.cache[guild_id]

        if channel_id: 
            data = await self.db.fetchrow("SELECT is_enabled, message FROM leave_settings WHERE guild_id = %s AND channel_id = %s;", guild_id, channel_id)
        
        else:
            data = await self.db.execute("SELECT channel_id, is_enabled, message FROM leave_settings WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if channel_id:
                is_enabled, message = data
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
                return {"is_enabled": is_enabled, "message": message}

            for channel_id, is_enabled, message in data:
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
            
            return self.cache[guild_id]


class StickyMessageSettings(BaseKey):
    async def get(self, guild_id: int, channel_id: Optional[int] = None) -> Any:
        if guild_id in self.cache:
            if channel_id:
                if channel_id in self.cache[guild_id]:
                    return self.cache[guild_id][channel_id]
                
                return
            
            return self.cache[guild_id]

        if channel_id: 
            data = await self.db.fetchrow("SELECT is_enabled, message FROM sticky_message_settings WHERE guild_id = %s AND channel_id = %s;", guild_id, channel_id)
        
        else:
            data = await self.db.execute("SELECT channel_id, is_enabled, message FROM sticky_message_settings WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if channel_id:
                is_enabled, message = data
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
                return {"is_enabled": is_enabled, "message": message}

            for channel_id, is_enabled, message in data:
                self.cache[guild_id][channel_id] = {"is_enabled": is_enabled, "message": message}
            
            return self.cache[guild_id]


class Aliases(BaseKey):
    async def get(self, guild_id: int, command_name: Optional[str] = None) -> Any:
        if guild_id in self.cache:
            if command_name:
                if command_name in self.cache[guild_id]:
                    return self.cache[guild_id][command_name]

                return
            
            return self.cache[guild_id]

        if command_name: 
            data = await self.db.fetch("SELECT alias FROM aliases WHERE guild_id = %s AND command_name = %s;", guild_id, command_name)
        
        else:
            data = await self.db.execute("SELECT command_name, alias FROM aliases WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if command_name:
                self.cache[guild_id][channel_id] = list(data)
                return list(data)

            for command_name, alias in data:
                if command_name not in self.cache[guild_id]:
                    self.cache[guild_id][command_name] = []

                self.cache[guild_id][command_name].append(alias)
            
            return self.cache[guild_id]


class Filter(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetch("SELECT keyword FROM filter WHERE guild_id = %s;", guild_id):
            return self.store(guild_id, list(data))


class FilterWhitelist(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetch("SELECT user_id FROM filter_whitelist WHERE guild_id = %s;", guild_id):
            return self.store(guild_id, list(data))


class FilterEvent(BaseKey):
    async def get(self, guild_id: int, event: Optional[str] = None) -> Any:
        if guild_id in self.cache:
            if event:
                if event in self.cache[guild_id]:
                    return self.cache[guild_id][event]
                
                return
            
            return self.cache[guild_id]

        if event: 
            data = await self.db.fetchrow("SELECT is_enabled, threshold FROM filter_event WHERE guild_id = %s AND event = %s;", guild_id, event)
        
        else:
            data = await self.db.execute("SELECT event, is_enabled, threshold FROM filter_event WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if event:
                is_enabled, threshold = data
                self.cache[guild_id][event] = {"is_enabled": is_enabled, "threshold": threshold}
                return {"is_enabled": is_enabled, "threshold": message}

            for event, is_enabled, threshold in data:
                self.cache[guild_id][event] = {"is_enabled": is_enabled, "threshold": threshold}
            
            return self.cache[guild_id]


class FilterSnipe(BaseKey):
    async def get(self, guild_id: int, option: Optional[str] = None) -> Any:
        if guild_id in self.cache:
            if option:
                if option not in ("invites", "links", "images", "words"):
                    return

                if option in self.cache[guild_id]:
                    return self.cache[guild_id][option]
                
                return
            
            return self.cache[guild_id]

        if option: 
            data = await self.db.fetchval(f"SELECT {option} FROM filter_snipe WHERE guild_id = %s;", guild_id)
        
        else:
            data = await self.db.fetchrow("SELECT invites, links, images, words FROM filter_snipe WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if option:
                self.cache[guild_id][option] = data
                return data

            return self.store(
                guild_id,
                {"invites": invites, "links": links, "images": images, "words": words}
            )


class Autoresponder(BaseKey):
    async def get(self, guild_id: int, keyword: Optional[str] = None) -> Any:
        if guild_id in self.cache:
            if keyword:
                if keyword in self.cache[guild_id]:
                    return self.cache[guild_id][keyword]
                
                return
            
            return self.cache[guild_id]

        if keyword: 
            data = await self.db.fetchrow("SELECT response, created_by FROM autoresponder WHERE guild_id = %s AND keyword = %s;", guild_id, keyword)
        
        else:
            data = await self.db.execute("SELECT keyword, response, created_by FROM autoresponder WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if keyword:
                response, created_by = data
                self.cache[guild_id][keyword] = {"response": response, "created_by": created_by}
                return {"response": response, "created_by": created_by}

            for keyword, response, created_by in data:
                self.cache[guild_id][keyword] = {"response": response, "created_by": created_by}
            
            return self.cache[guild_id]


class AutoresponderEvent(BaseKey):
    async def get(self, guild_id: int, event: Optional[str] = None) -> Any:
        if guild_id in self.cache:
            if event:
                if event in self.cache[guild_id]:
                    return self.cache[guild_id][event]
                
                return
            
            return self.cache[guild_id]

        if event: 
            data = await self.db.fetchval("SELECT response FROM autoresponder_event WHERE guild_id = %s AND event = %s;", guild_id, event)
        
        else:
            data = await self.db.execute("SELECT event, response FROM autoresponder_event WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if event:
                self.cache[guild_id][event] = data
                return data

            for event, response in data:
                self.cache[guild_id][event] = response
            
            return self.cache[guild_id]


class Autoreact(BaseKey):
    async def get(self, guild_id: int, keyword: Optional[str] = None) -> Any:
        if guild_id in self.cache:
            if keyword:
                if keyword in self.cache[guild_id]:
                    return self.cache[guild_id][keyword]
                
                return
            
            return self.cache[guild_id]

        if keyword: 
            data = await self.db.fetchval("SELECT reaction FROM autoreact WHERE guild_id = %s AND keyword = %s;", guild_id, keyword)
        
        else:
            data = await self.db.execute("SELECT keyword, reaction FROM autoreact WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if keyword:
                self.cache[guild_id][keyword] = reaction
                return reaction

            for keyword, reaction in data:
                self.cache[guild_id][keyword] = reaction
            
            return self.cache[guild_id]


class AutoreactEvent(BaseKey):
    async def get(self, guild_id: int, event: Optional[str] = None) -> Any:
        if guild_id in self.cache:
            if event:
                if event in self.cache[guild_id]:
                    return self.cache[guild_id][event]
                
                return
            
            return self.cache[guild_id]

        if event: 
            data = await self.db.fetchval("SELECT reaction FROM autoreact_event WHERE guild_id = %s AND event = %s;", guild_id, event)
        
        else:
            data = await self.db.execute("SELECT event, reaction FROM autoreact_event WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if event:
                self.cache[guild_id][event] = data
                return data

            for event, reaction in data:
                self.cache[guild_id][event] = reaction
            
            return self.cache[guild_id]
            
            
class DisabledModule(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetch("SELECT name FROM disabled_feature WHERE guild_id = %s AND type = %s;", guild_id, "module"):
            return self.store(guild_id, list(data))


class DisabledCommand(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetch("SELECT name FROM disabled_feature WHERE guild_id = %s AND type = %s;", guild_id, "command"):
            return self.store(guild_id, list(data))
            
            
class Ignore(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetch("SELECT object_id FROM ignore_object WHERE guild_id = %s;", guild_id):
            return self.store(guild_id, list(data))
            
            
class Pins(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetchrow("SELECT channel_id, is_enabled FROM pin_archive WHERE user_id = %s;", user_id):       
            channel_id, is_enabled = data
            return self.store(
                user_id,
                {"channel_id": channel_id, "is_enabled": is_enabled}
            )
            
            
class Webhooks(BaseKey):
    async def get(self, guild_id: int, identifier: Optional[str] = None) -> Any:
        if guild_id in self.cache:
            if identifier:
                if identifier in self.cache[guild_id]:
                    return self.cache[guild_id][identifier]
                
                return
            
            return self.cache[guild_id]

        if identifier: 
            data = await self.db.fetchrow("SELECT webhook_url, channel_id FROM webhooks WHERE guild_id = %s AND identifier = %s;", guild_id, identifier)
        
        else:
            data = await self.db.execute("SELECT identifier, webhook_url, channel_id FROM webhooks WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if identifier:
                webhook_url, channel_id = data
                self.cache[guild_id][identifier] = {"webhook_url": webhook_url, "channel_id": channel_id}
                return {"webhook_url": webhook_url, "channel_id": channel_id}

            for identifier, webhook_url, channel_id in data:
                self.cache[guild_id][identifier] = {"webhook_url": webhook_url, "channel_id": channel_id}
            
            return self.cache[guild_id]
            
            
class FakePermissions(BaseKey):
    async def get(self, guild_id: int, role_id: Optional[int] = None) -> Any:
        if guild_id in self.cache:
            if role_id:
                if role_id in self.cache[guild_id]:
                    return self.cache[guild_id][role_id]
                
                return
            
            return self.cache[guild_id]

        if role_id: 
            data = await self.db.fetch("SELECT permission FROM fake_permissions WHERE guild_id = %s AND role_id = %s;", guild_id, role_id)
        
        else:
            data = await self.db.execute("SELECT role_id, permission FROM fake_permissions WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if role_id:
                self.cache[guild_id][identifier] = list(data)
                return list(data)

            for role_id, permission in data:
                if role_id not in self.cache[guild_id]:
                    self.cache[guild_id][role_id] = []
                    
                self.cache[guild_id][role_id].append(permission)
            
            return self.cache[guild_id]
            
            
class Pagination(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetchval("SELECT current_page FROM pagination WHERE guild_id = %s;", guild_id):
            return self.store(guild_id, data)
            
            
class PaginationPages(BaseKey):
    async def get(self, guild_id: int, message_id: Optional[int] = None) -> Any:
        if guild_id in self.cache:
            if message_id:
                if message_id in self.cache[guild_id]:
                    return self.cache[guild_id][message_id]
                
                return
            
            return self.cache[guild_id]

        if message_id: 
            data = await self.db.fetchrow("SELECT page, page_number FROM pagination_pages WHERE guild_id = %s AND message_id = %s;", guild_id, message_id)
        
        else:
            data = await self.db.execute("SELECT message_id, page, page_number FROM pagination_pages WHERE guild_id = %s;", guild_id)
        
        if data:
            self.cache[guild_id] = {}
                
            if message_id:
                page, page_number = data
                self.cache[guild_id][message_id] = {"page": page, "page_number": page_number}
                return {"page": page, "page_number": page_number}

            for message_id, page, page_number in data:
                self.cache[guild_id][message_id] = {"page": page, "page_number": page_number}
            
            return self.cache[guild_id]
            
            
class StickyRoles(BaseKey):
    async def get(self, guild_id: int) -> Any:
        if guild_id in self.cache:
            return self.cache[guild_id]

        if data := await self.db.fetch("SELECT role_id FROM sticky_roles WHERE guild_id = %s;", guild_id):
            return self.store(guild_id, list(data))
            
