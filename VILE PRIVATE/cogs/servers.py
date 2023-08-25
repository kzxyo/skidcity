import discord, tempfile, zipfile, random, xxhash, asyncio, traceback
from typing import Optional, Union
from discord.ext import commands, tasks
from utilities import vile
from io import BytesIO
from PIL import Image


TUPLE = ()
DICT = {}

class Servers(commands.Cog):
    def __init__(self, bot: "VileBot") -> None:
        self.bot = bot
        
        
    async def cog_load(self) -> None:
        if not self.stickymessage_loop.is_running():
            self.stickymessage_loop.start()
            
            
    async def cog_unload(self) -> None:
        if self.stickymessage_loop.is_running():
            self.stickymessage_loop.cancel()
        
        
    @tasks.loop(seconds=30)
    async def stickymessage_loop(self):
        """A background loop that manages sending/deleting sticky messages"""
        
        async def do_stickymessage():
            for guild in self.bot.guilds:
                if guild.id in self.bot.cache.sticky_message_settings:
                    for channel_id in self.bot.cache.sticky_message_settings[guild.id]:
                        if (channel := self.bot.get_channel(channel_id)) is not None:
                            settings = self.bot.cache.sticky_message_settings[guild.id][channel_id]
                            if settings["is_enabled"] == False:
                                continue
                                
                            do_sticky = True
                            message_id = await self.bot.db.fetchval("SELECT message_id FROM sticky_message WHERE channel_id = %s", channel.id)
                            async for m in channel.history(limit=1):
                                if m.id == message_id:
                                    do_sticky = False
                                    
                            if do_sticky is False:
                                continue
                                        
                            if message_id:
                                try:
                                    message = await channel.fetch_message(message_id)
                                    await message.delete()
                                except Exception:
                                    pass
                                
                            script = vile.ParsedEmbed(
                                vile.EmbedScriptValidator(),
                                self.bot.cache.sticky_message_settings[guild.id][channel.id]["message"]
                            )
                            msg = await script.send(
                                channel,
                                bot=self.bot,
                                guild=guild,
                                channel=channel,
                                user=None
                            )
                            await self.bot.db.execute(
                                "INSERT INTO sticky_message (channel_id, message_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message_id = VALUES(message_id);",
                                channel.id, msg.id
                            )
                            
        await asyncio.gather(do_stickymessage())
    
        
    @commands.Cog.listener()
    async def on_boost(self, member: discord.Member):
        
        if member.guild.id in self.bot.cache.boost_settings:
            for channel_id in self.bot.cache.boost_settings[member.guild.id]:
                if (channel := self.bot.get_channel(channel_id)) is not None:
                    if channel.permissions_for(member.guild.me).send_messages is True:
                        settings = self.bot.cache.boost_settings[member.guild.id][channel_id]
                        if settings["is_enabled"] == False:
                            continue
                            
                        script = vile.ParsedEmbed(
                            vile.EmbedScriptValidator(),
                            settings["message"]
                        )
                        await script.send(
                            channel,
                            bot=self.bot,
                            guild=member.guild,
                            channel=channel,
                            user=member
                        )
        
        if (role_id := self.bot.cache.booster_award.get(member.guild.id)) is not None:
            if (role := member.guild.get_role(role_id)) is not None:
                if member.guild.me.guild_permissions.manage_roles is True and role.position < member.guild.me.top_role.position:
                    await member.add_roles(role, reason="vile boosterrole: member boosted")
                    
                    
    @commands.Cog.listener()
    async def on_unboost(self, member: discord.Member):
        
        if member.guild.id in self.bot.cache.unboost_settings:
            for channel_id in self.bot.cache.unboost_settings[member.guild.id]:
                if (channel := self.bot.get_channel(channel_id)) is not None:
                    if channel.permissions_for(member.guild.me).send_messages is True:
                        settings = self.bot.cache.unboost_settings[member.guild.id][channel_id]
                        if settings["is_enabled"] == False:
                            continue
                            
                        script = vile.ParsedEmbed(
                            vile.EmbedScriptValidator(),
                            settings["message"]
                        )
                        await script.send(
                            channel,
                            bot=self.bot,
                            guild=member.guild,
                            channel=channel,
                            user=member
                        )
        
        if (role_id := self.bot.cache.booster_award.get(member.guild.id)) is not None:
            if (role := member.guild.get_role(role_id)) is not None:
                if member.guild.me.guild_permissions.manage_roles is True and role.position < member.guild.me.top_role.position:
                    await member.remove_roles(role, reason="vile boosterrole: member unboosted")
                    
        if member.guild.id in self.bot.cache.booster_role:
            if (booster_role := member.guild.get_role(self.bot.cache.booster_role[member.guild.id].get(member.id, 0))) is not None:
                await booster_role.delete(reason="vile boosterrole: member unboosted")
                await self.bot.cache.execute(
                    "DELETE FROM booster_role WHERE guild_id = %s AND user_id = %s;",
                    ctx.guild.id, member.id
                )
                del self.bot.cache.booster_role[member.guild.id][member.id]
                    
                    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        
        if member.guild.id in self.bot.cache.booster_role:
            if (role_id := self.bot.cache.booster_role[member.guild.id].get(member.id)) is not None:
                if (role := member.guild.get_role(role_id)) is not None:
                    if member.guild.me.guild_permissions.manage_roles is True:
                        await role.delete(reason="vile boosterrole: member left the server")
        
        
    @commands.hybrid_group(
        name="prefix",
        usage="<sub command>",
        example="set .",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx: vile.Context):
        """Manage the server's command prefix"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @prefix.command(
        name="set",
        usage="<prefix>",
        example="."
    )
    async def prefix_set(self, ctx: vile.Context, prefix: str):
        """Set the server's command prefix"""
        
        if prefix == self.bot.cache.guild_prefix.get(ctx.guild.id):
            return await ctx.error("That is **already** the server's command prefix.")
            
        if len(prefix) > 10:
            return await ctx.error("Please provide a **valid** prefix under 10 characters.")
            
        await self.bot.db.execute(
            "INSERT INTO guild_prefix (guild_id, prefix) VALUES (%s, %s) ON DUPLICATE KEY UPDATE prefix = VALUES(prefix);",
            ctx.guild.id, prefix
        )
        self.bot.cache.guild_prefix[ctx.guild.id] = prefix
        
        return await ctx.success(f"Successfully **binded** the server's command prefix to `{prefix}`.")
        
    
    @prefix.command(
        name="remove"
    )
    async def prefix_remove(self, ctx: vile.Context):
        """Remove the server's command prefix"""
        
        if ctx.guild.id not in self.bot.cache.guild_prefix:
            return await ctx.error("This server **doesn't have** a command prefix.")
            
        await self.bot.db.execute(
            "DELETE FROM guild_prefix WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.guild_prefix[ctx.guild.id]
        
        return await ctx.success(f"Successfully **removed** the server's command prefix.")
        
        
    @commands.hybrid_group(
        name="customprefix",
        aliases=("selfprefix", "cp",),
        usage="<sub command>",
        example="set .",
        invoke_without_command=True
    )
    async def customprefix(self, ctx: vile.Context):
        """Manage your command prefix"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @customprefix.command(
        name="set",
        usage="<prefix>",
        example="."
    )
    async def customprefix_set(self, ctx: vile.Context, prefix: str):
        """Set your command prefix"""
        
        if prefix == self.bot.cache.custom_prefix.get(ctx.author.id):
            return await ctx.error("That is **already** your command prefix.")
            
        if len(prefix) > 10:
            return await ctx.error("Please provide a **valid** prefix under 10 characters.")
            
        await self.bot.db.execute(
            "INSERT INTO custom_prefix (user_id, prefix) VALUES (%s, %s) ON DUPLICATE KEY UPDATE prefix = VALUES(prefix);",
            ctx.author.id, prefix
        )
        self.bot.cache.custom_prefix[ctx.author.id] = prefix
        
        return await ctx.success(f"Successfully **binded** your command prefix to `{prefix}`.")
        
    
    @customprefix.command(
        name="remove"
    )
    async def customprefix_remove(self, ctx: vile.Context):
        """Remove your command prefix"""
        
        if ctx.author.id not in self.bot.cache.custom_prefix:
            return await ctx.error("You **don't have** a command prefix.")
            
        await self.bot.db.execute(
            "DELETE FROM custom_prefix WHERE user_id = %s;",
            ctx.author.id
        )
        del self.bot.cache.custom_prefix[ctx.author.id]
        
        return await ctx.success(f"Successfully **removed** your custom command prefix.")
        
        
    @commands.group(
        name="data",
        aliases=("datacollection",),
        usage="<sub command>",
        example="optout",
        invoke_without_command=True
    )
    async def data(self, ctx: vile.Context):
        """Manage your Data Collection & Privacy settings"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @data.command(
        name="request",
        aliases=("export",)
    )
    async def data_request(self, ctx: vile.Context):
        """Get a copy of all your data"""
        return await ctx.respond(
            "Contact us @ `vilebot.business@gmail.com` with the subject `Data Request`. (case-sensitive)",
            content="**NOTE:** Requesting your data can take **up to 24 hours** to process!",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @commands.group(
        name="boosterrole",
        aliases=("br",),
        usage="<color> <name>",
        example="#b1aad8 flawless",
        extras={
            "permissions": "Booster"
        },
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole(self, ctx: vile.Context, color: str, *, name: str):
        """Get your own custom booster color role"""
        
        if ctx.guild.premium_subscriber_role not in ctx.author.roles:
            return await ctx.error("You must be a **booster** to create a **booster role**.")
            
        if ctx.author.id in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            if ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id]) is not None:
                return await ctx.error("You **already** have a **booster role**.")
            
        if len(color.strip("#")) != 6:
            return await ctx.error("Please provide a **valid** color.")
            
        try:
            int(color.strip("#"), 16)
        except Exception:
            return await ctx.error("Please provide a **valid** color.")
            
        if len(name) > 100:
            return await ctx.error("Please provide a **valid** name under 100 characters.")
            
        role = await ctx.guild.create_role(
            name=name,
            color=int(color.strip("#"), 16),
            reason=f"boosterrole: used by {ctx.author}"
        )
        if (base_role := ctx.guild.get_role(self.bot.cache.booster_base.get(ctx.guild.id, 0))) is not None:
            await role.edit(position=base_role.position-1)
            
        await self.bot.db.execute(
            "INSERT INTO booster_role (guild_id, user_id, role_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);",
            ctx.guild.id, ctx.author.id, role.id
        )
        
        if ctx.guild.id not in self.bot.cache.booster_role:
            self.bot.cache.booster_role[ctx.guild.id] = {}
            
        self.bot.cache.booster_role[ctx.guild.id][ctx.author.id] = role.id
        await ctx.author.add_roles(role, reason=f"boosterrole: used by {ctx.author}")
        return await ctx.success(f"Successfully **created** a **booster role** ({role.mention}).")
        
    
    @boosterrole.command(
        name="base",
        aliases=("baserole",),
        usage="<role>",
        example="@Boosters",
        extras={
            "permissions": "Booster"
        }
    )
    @commands.has_permissions(manage_guild=True)
    async def boosterrole_base(self, ctx: vile.Context, *, role: vile.RoleConverter):
        """Set the base role that booster roles will be under"""
        
        if role.id == self.bot.cache.booster_base.get(ctx.guild.id, 0):
            return await ctx.error("That is **already** the **base booster role**.")
            
        await self.bot.db.execute(
            "INSERT INTO booster_role_base (guild_id, role_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);",
            ctx.guild.id, role.id
        )
        self.bot.cache.booster_base[ctx.guild.id] = role.id
        return await ctx.success(f"Successfully **binded** {role.mention} as the **base booster role**.")
        
        
    @boosterrole.command(
        name="remove",
        aliases=("delete",),
        extras={
            "permissions": "Booster"
        }
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_remove(self, ctx: vile.Context):
        """Remove your custom booster role"""
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            return await ctx.error("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            return await ctx.error("You **don't have** a **booster role**.")
                
        await self.bot.db.execute(
            "DELETE FROM booster_role WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, ctx.author.id
        )
        del self.bot.cache.booster_role[ctx.guild.id][ctx.author.id]
        await role.delete(reason=f"boosterrole remove: used by {ctx.author}")
        return await ctx.success("Successfully **removed** your **booster role**.")
        
        
    @boosterrole.command(
        name="color",
        usage="<color>",
        example="#b1aad8",
        extras={
            "permissions": "Booster"
        }
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_color(self, ctx: vile.Context, color: str):
        """Set your booster role's color"""
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            return await ctx.error("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            return await ctx.error("You **don't have** a **booster role**.")
            
        if len(color.strip("#")) != 6:
            return await ctx.error("Please provide a **valid** color.")
            
        try:
            color = int(color.strip("#"), 16)
        except Exception:
            return await ctx.error("Please provide a **valid** color.")
            
        await role.edit(
            color=color,
            reason=f"boosterrole color: used by {ctx.author}"
        )
        return await ctx.success(f"Successfully **set** your **booster role's color** to **#{hex(color)[2:]}**")
        
        
    @boosterrole.command(
        name="icon",
        usage="<url>",
        example="https://cdn.discordapp.com/role-icons/1031657246804955258/27096a19b3f9092fe6f4fc385d21bcae.png?size=1024",
        extras={
            "permissions": "Booster"
        }
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_icon(self, ctx: vile.Context, url: str):
        """Set an icon for your booster role"""
            
        if ctx.guild.premium_tier < 2:
            return await ctx.error("This server needs more **boosts** to perform that action.")
            
        try:
            image = await vile.HTTP(proxy=True).read(url)
            BytesIO(image)
        except Exception:
            return await ctx.error("Please provide a **valid** image URL.")
            
        await role.edit(
            display_icon=image,
            reason=f"boosterrole icon: used by {ctx.author}"
        )
        return await ctx.success(f"Successfully **set** your [**booster role's icon**]({url}).")
        
        
    @boosterrole.group(
        name="award",
        usage="<role>",
        example="@Supporter",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def boosterrole_award(self, ctx: vile.Context, role: vile.RoleConverter):
        """Reward members a specific role upon boosting"""
        
        if role.id == self.bot.cache.booster_award.get(ctx.guild.id, 0):
            return await ctx.error("That is **already** the **booster reward role**.")
        
        if ctx.is_dangerous(role):
            return await ctx.error("That role has **dangerous** permissions.")
        
        await self.bot.db.execute(
            "INSERT INTO booster_role_award (guild_id, role_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);",
            ctx.guild.id, role.id
        )
        self.bot.cache.booster_award[ctx.guild.id] = role.id
        return await ctx.success(f"Successfully **binded** {role.mention} as the **booster reward role**.")
        
        
    @boosterrole_award.command(
        name="reset"
    )
    @commands.has_permissions(manage_guild=True)
    async def boosterrole_award_reset(self, ctx: vile.Context):
        """Remove the booster reward role"""
        
        if ctx.guild.id not in self.bot.cache.booster_award:
            return await ctx.error("There is no **booster award role** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM booster_role_award WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.booster_award[ctx.guild.id]
        
        return await ctx.success("Successfully **reset** the **booster reward role**.")
        
        
    @boosterrole_award.command(
        name="view"
    )
    @commands.has_permissions(manage_guild=True)
    async def boosterrole_award_view(self, ctx: vile.Context):
        """View the booster reward role"""
        
        if (role := ctx.guild.get_role(self.bot.cache.booster_award.get(ctx.guild.id, 0))) is None:
            return await ctx.error("There is no **booster award role** in this server.")
            
        return await ctx.success(f"{role.mention} **{role.name}** ( `{role.id}` )")
        
        
    @boosterrole.command(
        name="random",
        extras={
            "permissions": "Booster"
        }
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_random(self, ctx: vile.Context):
        """Set your booster role's color to a random hex"""
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            return await ctx.error("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            return await ctx.error("You **don't have** a **booster role**.")
            
        await role.edit(
            color=(color := random.randrange(16777216)),
            reason=f"boosterrole random: used by {ctx.author}"
        )
        return await ctx.success(f"Successfully **set** your **booster role's color** to **#{hex(color)[2:]}**.")
        
        
    @boosterrole.command(
        name="rename",
        aliases=("name",),
        usage="<name>",
        example="terrible bot",
        extras={
            "permissions": "Booster"
        }
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_rename(self, ctx: vile.Context, *, name: str):
        """Rename your booster role"""
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            return await ctx.error("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            return await ctx.error("You **don't have** a **booster role**.")
            
        if len(name) > 100:
            return await ctx.error("Please provide a **valid** name under 100 characters.") 
            
        await role.edit(
            name=name,
            reason=f"boosterrole name: used by {ctx.author}"
        )
        return await ctx.success(f"Successfully **renamed** your **booster role**.")
        
        
    @boosterrole.command(
        name="dominant",
        extras={
            "permissions": "Booster"
        }
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def boosterrole_dominant(self, ctx: vile.Context):
        """Set your booster role's color to your avatar's color"""
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            return await ctx.error("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            return await ctx.error("You **don't have** a **booster role**.")
            
        await role.edit(
            color=(color := await vile.dominant_color(ctx.author.display_avatar)),
            reason=f"boosterrole dominant: used by {ctx.author}"
        )
        return await ctx.success(f"Successfully **set** your **booster role's color** to **#{hex(color)[2:]}**.")
        
        
    @boosterrole.command(
        name="list",
        aliases=("view",),
        extras={
            "permissions": "Booster"
        }
    )
    @commands.has_permissions(manage_guild=True)
    async def boosterrole_list(self, ctx: vile.Context):
        """View every booster role"""
        
        if not self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            return await ctx.error("There are no **booster roles** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Booster Roles in {ctx.guild.name}"
        )
        for role_id in self.bot.cache.booster_role[ctx.guild.id].values():
            if (role := ctx.guild.get_role(role_id)) is not None:
                rows.append(f"{role.mention}: **{role.name}** ( `{role.id}` )")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="stickymessage",
        aliases=("sm",),
        usage="<sub command>",
        example="add #selfie {content: trolling = ban}",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_channels=True)
    async def stickymessage(self, ctx: vile.Context):
        """Set up a sticky message in one or multiple channels"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @stickymessage.command(
        name="toggle",
        usage="[channel] <state>",
        example="#selfie true"
    )
    async def stickymessage_toggle(self, ctx: vile.Context, channel: Optional[discord.TextChannel], state: str):
        """Toggle the sticky message in a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.sticky_message_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **sticky message** in that channel.")
            
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
            
        else:
            state = 0
            
        if state == self.bot.cache.sticky_message_settings[ctx.guild.id][channel.id]["is_enabled"]:
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            "UPDATE sticky_message_settings SET is_enabled = %s WHERE channel_id = %s;",
            state, channel.id
        )
        self.bot.cache.sticky_message_settings[ctx.guild.id][channel.id]["is_enabled"] = state
            
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** {channel.mention}'s **sticky message**.")
        
        
    
    @stickymessage.command(
        name="add",
        usage="[channel] <message>",
        example="#selfie {content: trolling = ban}"
    )
    async def stickymessage_add(self, ctx: vile.Context, channel: Optional[discord.TextChannel], *, message: str):
        """Add a sticky message to a channel"""
        
        channel = channel or ctx.channel
        if channel.id in self.bot.cache.sticky_message_settings.get(ctx.guild.id, DICT) and message == self.bot.cache.sticky_message_settings[ctx.guild.id][channel.id]["message"]:
            return await ctx.error("That is **already** the **sticky message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO sticky_message_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        if ctx.guild.id not in self.bot.cache.sticky_message_settings:
            self.bot.cache.sticky_message_settings[ctx.guild.id] = {}
            
        if channel.id in self.bot.cache.sticky_message_settings[ctx.guild.id]:
            self.bot.cache.sticky_message_settings[ctx.guild.id][channel.id]["message"] = message
        else:
            self.bot.cache.sticky_message_settings[ctx.guild.id][channel.id] = {
                "is_enabled": 1,
                "message": message
            }
            
        return await ctx.success(f"Successfully **binded** {channel.mention}'s **sticky message** to \n```{message}```")
        
        
    @stickymessage.command(
        name="remove",
        usage="[channel]",
        example="#selfie"
    )
    async def stickymessage_remove(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """Remove a sticky message from a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.sticky_message_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **sticky message** in that channel.")
            
        await self.bot.db.execute(
            "DELETE FROM sticky_message_settings WHERE channel_id = %s;",
            channel.id
        )
        del self.bot.cache.sticky_message_settings[ctx.guild.id][channel.id]
            
        return await ctx.success(f"Successfully **removed** {channel.mention}'s **sticky message**.")
        
    
    @stickymessage.command(
        name="view",
        usage="[channel]",
        example="#selfie"
    )
    async def stickymessage_view(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """View a channel's sticky message"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.sticky_message_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **sticky message** in that channel.")
            
        script = await vile.EmbedScriptValidator().convert(ctx, self.bot.cache.sticky_message_settings[ctx.guild.id][channel.id]["message"])
        return await script.send(
            ctx,
            bot=self.bot,
            guild=ctx.guild,
            channel=channel,
            user=None
        )
        
        
    @stickymessage.command(
        name="clear"
    )
    async def stickymessage_clear(self, ctx: vile.Context):
        """Clear every sticky message in this server"""
        
        if ctx.guild.id not in self.bot.cache.sticky_message_settings:
            return await ctx.error("There **aren't** any **sticky messages** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM sticky_message_settings WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.sticky_message_settings[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **sticky message**.")
        
        
    @stickymessage.command(
        name="variables",
        aliases=("variable", "vars",)
    )
    async def stickymessage_variables(self, ctx: vile.Context):
        """View the available sticky message variables"""
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @stickymessage.command(
        name="list"
    )
    @commands.has_permissions(manage_guild=True)
    async def stickymessage_list(self, ctx: vile.Context):
        """View every sticky message"""
        
        if not self.bot.cache.sticky_message_settingd.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **sticky messages** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Sticky Messages in {ctx.guild.name}"
        )
        for channel_id, config in self.bot.cache.sticky_message_settings[ctx.guild.id].items():
            if (channel := self.bot.get_channel(channel_id)) is not None:
                message = config["message"].replace("`", "\`")
                state = "enabled" if config["is_enabled"] else "disabled"
                rows.append(f"{channel.mention}\n{self.bot.reply} **state:** {state}\n{self.bot.reply} **message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="boost",
        aliases=("bst", "boostmessage",),
        usage="<sub command>",
        example="add #boosts {content: {user.mention} thanks :3}",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def boost(self, ctx: vile.Context):
        """Set up a boost message in one or multiple channels"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @boost.command(
        name="toggle",
        usage="[channel] <state>",
        example="#boosts true"
    )
    async def boost_toggle(self, ctx: vile.Context, channel: Optional[discord.TextChannel], state: str):
        """Toggle the boost message in a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.boost_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **boost message** in that channel.")
            
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
            
        else:
            state = 0
    
        if state == self.bot.cache.boost_settings[ctx.guild.id][channel.id]["is_enabled"]:
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            "UPDATE boost_settings SET is_enabled = %s WHERE channel_id = %s;",
            state, channel.id
        )
        self.bot.cache.boost_settings[ctx.guild.id][channel.id]["is_enabled"] = state
            
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** {channel.mention}'s **boost message**.")
        
        
    
    @boost.command(
        name="add",
        usage="[channel] <message>",
        example="#boosts {content: {user.mention} thanks :3}"
    )
    async def boost_add(self, ctx: vile.Context, channel: Optional[discord.TextChannel], *, message: str):
        """Add a boost message to a channel"""
        
        channel = channel or ctx.channel
        if channel.id in self.bot.cache.boost_settings.get(ctx.guild.id, DICT) and message == self.bot.cache.boost_settings[ctx.guild.id][channel.id]["message"]:
            return await ctx.error("That is **already** the **boost message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO boost_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        if ctx.guild.id not in self.bot.cache.boost_settings:
            self.bot.cache.boost_settings[ctx.guild.id] = {}
            
        if channel.id in self.bot.cache.boost_settings[ctx.guild.id]:
            self.bot.cache.boost_settings[ctx.guild.id][channel.id]["message"] = message
        else:
            self.bot.cache.boost_settings[ctx.guild.id][channel.id] = {
                "is_enabled": 1,
                "message": message
            }
            
        return await ctx.success(f"Successfully **binded** {channel.mention}'s **boost message** to \n```{message}```")
        
        
    @boost.command(
        name="remove",
        usage="[channel]",
        example="#boosts"
    )
    async def boost_remove(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """Remove a boost message from a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.boost_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **boost message** in that channel.")
            
        await self.bot.db.execute(
            "DELETE FROM boost_settings WHERE channel_id = %s;",
            channel.id
        )
        del self.bot.cache.boost_settings[ctx.guild.id][channel.id]
            
        return await ctx.success(f"Successfully **removed** {channel.mention}'s **boost message**.")
        
    
    @boost.command(
        name="view",
        usage="[channel]",
        example="#boosts"
    )
    async def boost_view(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """View a channel's boost message"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.boost_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **boost message** in that channel.")
            
        script = await vile.EmbedScriptValidator().convert(ctx, self.bot.cache.boost_settings[ctx.guild.id][channel.id]["message"])
        return await script.send(
            ctx,
            bot=self.bot,
            guild=ctx.guild,
            channel=channel,
            user=ctx.author
        )
        
        
    @boost.command(
        name="clear"
    )
    async def boost_clear(self, ctx: vile.Context):
        """Clear every boost message in this server"""
        
        if ctx.guild.id not in self.bot.cache.boost_settings:
            return await ctx.error("There **aren't** any **boost messages** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM boost_settings WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.boost_settings[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **boost message**.")
        
        
    @boost.command(
        name="variables",
        aliases=("variable", "vars",)
    )
    async def boost_variables(self, ctx: vile.Context):
        """View the available boost message variables"""
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @boost.command(
        name="list"
    )
    @commands.has_permissions(manage_guild=True)
    async def boost_list(self, ctx: vile.Context):
        """View every boost message"""
        
        if not self.bot.cache.boost_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **boost messages** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Boost Messages in {ctx.guild.name}"
        )
        for channel_id, config in self.bot.cache.boost_settings[ctx.guild.id].items():
            if (channel := self.bot.get_channel(channel_id)) is not None:
                message = config["message"].replace("`", "\`")
                state = "enabled" if config["is_enabled"] else "disabled"
                rows.append(f"{channel.mention}\n{self.bot.reply} **state:** {state}\n{self.bot.reply} **message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="unboost",
        aliases=("unbst", "jnboostmessage",),
        usage="<sub command>",
        example="add #boosts {content: {user.mention} unboosted :(}",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def unboost(self, ctx: vile.Context):
        """Set up an unboost message in one or multiple channels"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @unboost.command(
        name="toggle",
        usage="[channel] <state>",
        example="#boosts true"
    )
    async def unboost_toggle(self, ctx: vile.Context, channel: Optional[discord.TextChannel], state: str):
        """Toggle the unboost message in a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.unboost_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** an **unboost message** in that channel.")
            
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
            
        else:
            state = 0
            
        if state == self.bot.cache.unboost_settings[ctx.guild.id][channel.id]["is_enabled"]:
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            "UPDATE unboost_settings SET is_enabled = %s WHERE channel_id = %s;",
            state, channel.id
        )
        self.bot.cache.unboost_settings[ctx.guild.id][channel.id]["is_enabled"] = state
            
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** {channel.mention}'s **unboost message**.")
        
        
    
    @unboost.command(
        name="add",
        usage="[channel] <message>",
        example="#boosts {content: {user.mention} unboosted :(}"
    )
    async def unboost_add(self, ctx: vile.Context, channel: Optional[discord.TextChannel], *, message: str):
        """Add an unboost message to a channel"""
        
        channel = channel or ctx.channel
        if channel.id in self.bot.cache.unboost_settings.get(ctx.guild.id, DICT) and message == self.bot.cache.boost_settings[ctx.guild.id][channel.id]["message"]:
            return await ctx.error("That is **already** the **unboost message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO unboost_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        if ctx.guild.id not in self.bot.cache.unboost_settings:
            self.bot.cache.unboost_settings[ctx.guild.id] = {}
            
        if channel.id in self.bot.cache.unboost_settings[ctx.guild.id]:
            self.bot.cache.unboost_settings[ctx.guild.id][channel.id]["message"] = message
        else:
            self.bot.cache.unboost_settings[ctx.guild.id][channel.id] = {
                "is_enabled": 1,
                "message": message
            }
            
        return await ctx.success(f"Successfully **binded** {channel.mention}'s **unboost message** to \n```{message}```")
        
        
    @unboost.command(
        name="remove",
        usage="[channel]",
        example="#boosts"
    )
    async def unboost_remove(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """Remove an unboost message from a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.unboost_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** an **unboost message** in that channel.")
            
        await self.bot.db.execute(
            "DELETE FROM unboost_settings WHERE channel_id = %s;",
            channel.id
        )
        del self.bot.cache.unboost_settings[ctx.guild.id][channel.id]
            
        return await ctx.success(f"Successfully **removed** {channel.mention}'s **unboost message**.")
        
    
    @unboost.command(
        name="view",
        usage="[channel]",
        example="#boosts"
    )
    async def unboost_view(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """View a channel's unboost message"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.unboost_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** an **unboost message** in that channel.")
            
        script = await vile.EmbedScriptValidator().convert(ctx, self.bot.cache.unboost_settings[ctx.guild.id][channel.id]["message"])
        return await script.send(
            ctx,
            bot=self.bot,
            guild=ctx.guild,
            channel=channel,
            user=ctx.author
        )
        
        
    @unboost.command(
        name="clear"
    )
    async def unboost_clear(self, ctx: vile.Context):
        """Clear every unboost message in this server"""
        
        if ctx.guild.id not in self.bot.cache.unboost_settings:
            return await ctx.error("There **aren't** any **unboost messages** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM unboost_settings WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.unboost_settings[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **unboost message**.")
        
        
    @unboost.command(
        name="variables",
        aliases=("variable", "vars",)
    )
    async def unboost_variables(self, ctx: vile.Context):
        """View the available unboost message variables"""
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @unboost.command(
        name="list"
    )
    @commands.has_permissions(manage_guild=True)
    async def unboost_list(self, ctx: vile.Context):
        """View every unboost message"""
        
        if not self.bot.cache.unboost_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **unboost messages** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Unboost Messages in {ctx.guild.name}"
        )
        for channel_id, config in self.bot.cache.unboost_settings[ctx.guild.id].items():
            if (channel := self.bot.get_channel(channel_id)) is not None:
                message = config["message"].replace("`", "\`")
                state = "enabled" if config["is_enabled"] else "disabled"
                rows.append(f"{channel.mention}\n{self.bot.reply} **state:** {state}\n{self.bot.reply} **message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="welcome",
        aliases=("wlc", "welcomemessage",),
        usage="<sub command>",
        example="add #welcome {content: {user.mention} welcome :3}",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx: vile.Context):
        """Set up a welcome message in one or multiple channels"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @welcome.command(
        name="toggle",
        usage="[channel] <state>",
        example="#boosts true"
    )
    async def welcome_toggle(self, ctx: vile.Context, channel: Optional[discord.TextChannel], state: str):
        """Toggle the welcome message in a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.welcome_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **welcome message** in that channel.")
            
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
            
        else:
            state = 0
            
        if state == self.bot.cache.welcome_settings[ctx.guild.id][channel.id]["is_enabled"]:
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            "UPDATE welcome_settings SET is_enabled = %s WHERE channel_id = %s;",
            state, channel.id
        )
        self.bot.cache.welcome_settings[ctx.guild.id][channel.id]["is_enabled"] = state
            
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** {channel.mention}'s **welcome message**.")
        
        
    
    @welcome.command(
        name="add",
        usage="[channel] <message>",
        example="#welcome {content: {user.mention} welcome :3}"
    )
    async def welcome_add(self, ctx: vile.Context, channel: Optional[discord.TextChannel], *, message: str):
        """Add a welcome message to a channel"""
        
        channel = channel or ctx.channel
        if channel.id in self.bot.cache.welcome_settings.get(ctx.guild.id, DICT) and message == self.bot.cache.welcome_settings[ctx.guild.id][channel.id]["message"]:
            return await ctx.error("That is **already** the **welcome message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO welcome_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        if ctx.guild.id not in self.bot.cache.welcome_settings:
            self.bot.cache.welcome_settings[ctx.guild.id] = {}
            
        if channel.id in self.bot.cache.welcome_settings[ctx.guild.id]:
            self.bot.cache.welcome_settings[ctx.guild.id][channel.id]["message"] = message
        else:
            self.bot.cache.welcome_settings[ctx.guild.id][channel.id] = {
                "is_enabled": 1,
                "message": message
            }
            
        return await ctx.success(f"Successfully **binded** {channel.mention}'s **welcome message** to \n```{message}```")
        
        
    @welcome.command(
        name="remove",
        usage="[channel]",
        example="#boosts"
    )
    async def welcome_remove(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """Remove a welcome message from a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.welcome_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **welcome message** in that channel.")
            
        await self.bot.db.execute(
            "DELETE FROM welcome_settings WHERE channel_id = %s;",
            channel.id
        )
        del self.bot.cache.welcome_settings[ctx.guild.id][channel.id]
            
        return await ctx.success(f"Successfully **removed** {channel.mention}'s **welcome message**.")
        
    
    @welcome.command(
        name="view",
        usage="[channel]",
        example="#boosts"
    )
    async def welcome_view(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """View a channel's welcome message"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.welcome_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **welcome message** in that channel.")
            
        script = await vile.EmbedScriptValidator().convert(ctx, self.bot.cache.welcome_settings[ctx.guild.id][channel.id]["message"])
        return await script.send(
            ctx,
            bot=self.bot,
            guild=ctx.guild,
            channel=channel,
            user=ctx.author
        )
        
        
    @welcome.command(
        name="clear"
    )
    async def welcome_clear(self, ctx: vile.Context):
        """Clear every welcome message in this server"""
        
        if ctx.guild.id not in self.bot.cache.welcome_settings:
            return await ctx.error("There **aren't** any **welcome messages** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM welcome_settings WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.welcome_settings[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **welcome message**.")
        
        
    @welcome.command(
        name="variables",
        aliases=("variable", "vars",)
    )
    async def welcome_variables(self, ctx: vile.Context):
        """View the available welcome message variables"""
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @welcome.command(
        name="list"
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_list(self, ctx: vile.Context):
        """View every welcome message"""
        
        if not self.bot.cache.welcome_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **welcome messages** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Welcome Messages in {ctx.guild.name}"
        )
        for channel_id, config in self.bot.cache.welcome_settings[ctx.guild.id].items():
            if (channel := self.bot.get_channel(channel_id)) is not None:
                message = config["message"].replace("`", "\`")
                state = "enabled" if config["is_enabled"] else "disabled"
                rows.append(f"{channel.mention}\n{self.bot.reply} **state:** {state}\n{self.bot.reply} **message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="leave",
        aliases=("bye", "leavemessage",),
        usage="<sub command>",
        example="add #leave {content: {user.mention} left :()}",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx: vile.Context):
        """Set up a leave message in one or multiple channels"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @leave.command(
        name="toggle",
        usage="[channel] <state>",
        example="#boosts true"
    )
    async def leave_toggle(self, ctx: vile.Context, channel: Optional[discord.TextChannel], state: str):
        """Toggle the leave message in a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.leave_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **leave message** in that channel.")
            
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
            
        else:
            state = 0
            
        if state == self.bot.cache.leave_settings[ctx.guild.id][channel.id]["is_enabled"]:
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            "UPDATE leave_settings SET is_enabled = %s WHERE channel_id = %s;",
            state, channel.id
        )
        self.bot.cache.leave_settings[ctx.guild.id][channel.id]["is_enabled"] = state
            
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** {channel.mention}'s **leave message**.")
        
        
    
    @leave.command(
        name="add",
        usage="[channel] <message>",
        example="#leave {content: {user.mention} left :()}"
    )
    async def leave_add(self, ctx: vile.Context, channel: Optional[discord.TextChannel], *, message: str):
        """Add a leave message to a channel"""
        
        channel = channel or ctx.channel
        if channel.id in self.bot.cache.leave_settings.get(ctx.guild.id, DICT) and message == self.bot.cache.leave_settings[ctx.guild.id][channel.id]["message"]:
            return await ctx.error("That is **already** the **leave message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO leave_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        if ctx.guild.id not in self.bot.cache.leave_settings:
            self.bot.cache.leave_settings[ctx.guild.id] = {}
            
        if channel.id in self.bot.cache.leave_settings[ctx.guild.id]:
            self.bot.cache.leave_settings[ctx.guild.id][channel.id]["message"] = message
        else:
            self.bot.cache.leave_settings[ctx.guild.id][channel.id] = {
                "is_enabled": 1,
                "message": message
            }
            
        return await ctx.success(f"Successfully **binded** {channel.mention}'s **leave message** to \n```{message}```")
        
        
    @leave.command(
        name="remove",
        usage="[channel]",
        example="#boosts"
    )
    async def leave_remove(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """Remove a leave message from a channel"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.leave_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **leave message** in that channel.")
            
        await self.bot.db.execute(
            "DELETE FROM leave_settings WHERE channel_id = %s;",
            channel.id
        )
        del self.bot.cache.leave_settings[ctx.guild.id][channel.id]
            
        return await ctx.success(f"Successfully **removed** {channel.mention}'s **leave message**.")
        
    
    @leave.command(
        name="view",
        usage="[channel]",
        example="#boosts"
    )
    async def leave_view(self, ctx: vile.Context, channel: Optional[discord.TextChannel]):
        """View a channel's leave message"""
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.leave_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **leave message** in that channel.")
            
        script = await vile.EmbedScriptValidator().convert(ctx, self.bot.cache.leave_settings[ctx.guild.id][channel.id]["message"])
        return await script.send(
            ctx,
            bot=self.bot,
            guild=ctx.guild,
            channel=channel,
            user=ctx.author
        )
        
        
    @leave.command(
        name="clear"
    )
    async def leave_clear(self, ctx: vile.Context):
        """Clear every leave message in this server"""
        
        if ctx.guild.id not in self.bot.cache.leave_settings:
            return await ctx.error("There **aren't** any **leave messages** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM leave_settings WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.leave_settings[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **leave message**.")
        
        
    @leave.command(
        name="variables",
        aliases=("variable", "vars",)
    )
    async def leave_variables(self, ctx: vile.Context):
        """View the available leave message variables"""
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @leave.command(
        name="list"
    )
    @commands.has_permissions(manage_guild=True)
    async def leave_list(self, ctx: vile.Context):
        """View every leave message"""
        
        if not self.bot.cache.leave_settings.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **leave messages** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"leave Messages in {ctx.guild.name}"
        )
        for channel_id, config in self.bot.cache.leave_settings[ctx.guild.id].items():
            if (channel := self.bot.get_channel(channel_id)) is not None:
                message = config["message"].replace("`", "\`")
                state = "enabled" if config["is_enabled"] else "disabled"
                rows.append(f"{channel.mention}\n{self.bot.reply} **state:** {state}\n{self.bot.reply} **message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
    
    @commands.command(
        name="invoke",
        usage="<command> <message>",
        example="ban {content: {user.mention} got :poop: on by {moderator}}"
    )
    @commands.has_permissions(manage_guild=True)
    async def invoke(self, ctx: vile.Context, command: str, *, message: str):
        """Set a custom invoke message for moderation commands"""
        
        command = self.bot.get_command(command)
        if command is None or command.cog_name != "Moderation":
            return await ctx.error("Please provide a **valid** moderation command.")
            
        if message == await self.bot.db.fetchval("SELECT message FROM invoke_message WHERE guild_id = %s AND command_name = %s;", ctx.guild.id, command.qualified_name):
            return await ctx.error("That is **already** the **invoke message** for that command.")
            
        await self.bot.db.execute(
            "INSERT INTO invoke_message (guild_id, command_name, message) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUESS(message);",
            ctx.guild.id, command.qualified_name, message
        )
        return await ctx.success(f"Successfully **binded** `{command.qualified_name}`'s invoke message to \n```{message}```")
        
        
    @commands.group(
        name0="alias",
        aliases=("aliases",),
        usage="<sub command>",
        example="add ban pack",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def alias(self, ctx: vile.Context):
        """Add an alias to a command"""
        return await ctx.send_help(ctx.command.qualified_name)
        
    
    @alias.command(
        name="add",
        usage="<command> <alias>",
        example="ban pack"
    )
    async def alias_add(self, ctx: vile.Context, command: str, alias: str):
        """Add an alias to a command"""
        
        if (command := self.bot.get_command(command)) is None:
            return await ctx.error("Please provide a **valid** command.")
         
        if ctx.guild.id in self.bot.cache.aliases and alias in self.bot.cache.aliases[ctx.guild.id].get(command.qualified_name, TUPLE):
            return await ctx.error("That is **already** an **alias** for that command.")
           
        await self.bot.db.execute(
            "INSERT INTO aliases (guild_id, command_name, alias) VALUES (%s, %s, %s);",
            ctx.guild.id, command.qualified_name, alias
        )
        if ctx.guild.id not in self.bot.cache.aliases:
            self.bot.cache.aliases[ctx.guild.id] = {}
            
        if command.qualified_name not in self.bot.cache.aliases[ctx.guild.id]:
            self.bot.cache.aliases[ctx.guild.id][command.qualified_name] = []
        
        self.bot.cache.aliases[ctx.guild.id][command.qualified_name].append(alias)
        return await ctx.success(f"Successfully **added** the **alias** `{command.qualified_name} / {alias}`")
        
        
    @alias.command(
        name="remove",
        usage="<command> <alias>",
        example="ban pack"
    )
    async def alias_remove(self, ctx: vile.Context, command: str, alias: str):
        """Remove an alias from a command"""
        
        if (command := self.bot.get_command(command)) is None:
            return await ctx.error("Please provide a **valid** command.")
         
        if ctx.guild.id not in self.bot.cache.aliases:
            return await ctx.error("There **aren't** any **aliases** in this server.")
            
        if alias not in self.bot.cache.aliases[ctx.guild.id].get(command.qualified_name, TUPLE):
            return await ctx.error("Please provide a **valid** alias for that command.")
           
        await self.bot.db.execute(
            "DELETE FROM aliases WHERE guild_id = %s AND command_name = %s AND alias = %s;",
            ctx.guild.id, command.qualified_name, alias
        )
        self.bot.cache.aliases[ctx.guild.id][command.qualified_name].remove(alias)
            
        return await ctx.success(f"Successfully **removed** the **alias** `{command.qualified_name} / {alias}`")
        
        
    @alias.command(
        name="clear"
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_clear(self, ctx: vile.Context):
        """Clear every alias in this server"""
        
        if ctx.guild.id not in self.bot.cache.aliases:
            return await ctx.error("There **aren't** any **alias** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM aliases WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.aliases[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **alias**.")

        
    @alias.command(
        name="list"
    )
    @commands.has_permissions(manage_guild=True)
    async def alias_list(self, ctx: vile.Context):
        """View every command alias"""
        
        if not self.bot.cache.aliases.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **aliases** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Command Aliases in {ctx.guild.name}"
        )
        for command, aliases in self.bot.cache.aliases[ctx.guild.id].items():
            if aliases:
                rows.append(f"{command} **—** {', '.join(aliases)}")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="filter",
        aliases=("chatfilter", "cf",),
        usage="<sub command>",
        example="exempt @trey#0006",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_channels=True)
    async def _filter(self, ctx: vile.Context):
        """View a variety of options to help clean the chat"""
        return await ctx.send_help(ctx.command.qualified_name)
        

    @_filter.command(
        name="clear"
    )
    async def filter_clear(self, ctx: vile.Context):
        """Clear every filtered word in this server"""
        
        if ctx.guild.id not in self.bot.cache.filter:
            return await ctx.error("There **aren't** any **filtered words** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM filter WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.filter[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **filtered word**.")
        
        
    @_filter.command(
        name="add",
        aliases=("create",),
        usage="<keyword>",
        example="nig"
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_add(self, ctx: vile.Context, keyword: str):
        """Add a filtered word"""
        
        if keyword in self.bot.cache.filter.get(ctx.guild.id, TUPLE):
            return await ctx.error("That is **already** a **filtered word**.")
            
        if len(keyword.split()) > 1:
            return await ctx.error("The keyword must be **one word**.")
            
        if len(keyword) > 32:
            return await ctx.error("Please provide a **valid** keyword under **32 characters**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter (guild_id, keyword) VALUES (%s, %s);",
            ctx.guild.id, keyword
        )
        if ctx.guild.id not in self.bot.cache.filter:
            self.bot.cache.filter[ctx.guild.id] = []
            
        self.bot.cache.filter[ctx.guild.id].append(keyword)
        return await ctx.success(f"Successfully **added** the filtered keyword \n```{keyword}```")
        
        
    @_filter.command(
        name="list"
    )
    @commands.has_permissions(manage_guild=True)
    async def filter_list(self, ctx: vile.Context):
        """View every filtered word"""
        
        if not self.bot.cache.filter.get(ctx.guild.id, TUPLE):
            return await ctx.error("There **aren't** any **filtered words** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Filtered Words in {ctx.guild.name}"
        )
        for keyword in self.bot.cache.filter[ctx.guild.id]:
            rows.append(keyword)
                
        return await ctx.paginate((embed, rows))
        
        
        
    @_filter.command(
        name="whitelist",
        aliases=("exempt", "ignore",),
        usage="<member or channel or role>",
        example="#nsfw"
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_whitelist(self, ctx: vile.Context, *, source: Union[vile.MemberConverter, discord.TextChannel, vile.RoleConverter]):
        """Exempt roles from the word filter"""
        
        if isinstance(source, discord.Member):
            if await ctx.can_moderate(source, "whitelist") is not None:
                return
                
        if source.id in self.bot.cache.filter_whitelist.get(ctx.guild.id, TUPLE):
            await self.bot.db.execute(
                "DELETE FROM filter_whitelist WHERE user_id = %s;",
                source.id
            )
            self.bot.cache.filter_whitelist[ctx.guild.id].remove(source.id)
            return await ctx.success(f"Successfully **unwhitelisted** {source.mention}.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_whitelist (guild_id, user_id) VALUES (%s, %s);",
            ctx.guild.id, source.id
        )
        if ctx.guild.id not in self.bot.cache.filter_whitelist:
            self.bot.cache.filter_whitelist[ctx.guild.id] = []
            
        self.bot.cache.filter_whitelist[ctx.guild.id].append(source.id)
        return await ctx.success(f"Successfully **whitelisted** {source.mention}.")
        
        
    @_filter.command(
        name="whitelisted"
    )
    @commands.has_permissions(manage_guild=True)
    async def filter_whitelisted(self, ctx: vile.Context):
        """View every whitelisted member"""
        
        if ctx.guild.id not in self.bot.cache.filter_whitelist:
            return await ctx.error("There **aren't** any **whitelisted members** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Whitelisted Members in {ctx.guild.name}"
        )
        for source_id in self.bot.cache.filter_whitelist[ctx.guild.id]:
            if (source := ctx.guild.get_member(source_id) or ctx.guild.get_channel(source_id) or ctx.guild.get_role(source_id)) is not None:
                rows.append(f"{source.mention} {source.name} (`{source.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @_filter.command(
        name="nicknames",
        aliases=("nick", "nicks",),
        usage="<state>",
        example="true"
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_nicknames(self, ctx: vile.Context, state: str):
        """Automatically reset nicknames if a filtered word is detected"""
        
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
              
        else:
            state = 0
            
        if state == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("nicknames", DICT).get("is_enabled"):
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled);",
            ctx.guild.id, "nicknames", state
        )
        if ctx.guild.id not in self.bot.cache.filter_event:
            self.bot.cache.filter_event[ctx.guild.id] = {}
            
        if "nicknames" not in self.bot.cache.filter_event[ctx.guild.id]:
            self.bot.cache.filter_event[ctx.guild.id]["nicknames"] = {
                "is_enabled": state,
                "threshold": 2 # default value, as this doesnt require a threshold
            }
            
        else:
            self.bot.cache.filter_event[ctx.guild.id]["nicknames"]["is_enabled"] = state
        
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **nickname filter**.")
        
        
    @_filter.command(
        name="spoilers",
        aliases=("spoiler",),
        usage="<state> <flags --threshold>",
        example="true --threshold 2",
        parameters={
            "threshold": {
                "converter": int,
                "description": "The limit for spoilers in one message",
                "aliases": [
                    "limit"
                ]
            }
        }
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_spoilers(self, ctx: vile.Context, state: str):
        """Delete any message exceeding the threshold for spoilers"""
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.filter_event.get(ctx.guild.id, {}).get("spoilers", DICT).get("threshold") or 2
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
              
        else:
            state = 0
            
        if state == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("spoilers", {}).get("is_enabled") and threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("spoilers", DICT).get("threshold"):
            return await ctx.error("That is **already** the **current state**.")
            
        if state:
            if threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("spoilers", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                return await ctx.error("That is **already** the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                return await ctx.error("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "spoilers", state, threshold
        )
        if ctx.guild.id not in self.bot.cache.filter_event:
            self.bot.cache.filter_event[ctx.guild.id] = {}
            
        self.bot.cache.filter_event[ctx.guild.id]["spoilers"] = {
            "is_enabled": state,
            "threshold": threshold
        }
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **spoiler filter**{f' (with threshold: {threshold})' if state else '.'}")
        
        
    @_filter.command(
        name="links",
        aliases=("urls",),
        usage="<state>",
        example="true"
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_links(self, ctx: vile.Context, state: str):
        """Delete any message that contains a link"""
        
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
              
        else:
            state = 0
            
        if state == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("links", DICT).get("is_enabled"):
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled);",
            ctx.guild.id, "links", state
        )
        if ctx.guild.id not in self.bot.cache.filter_event:
            self.bot.cache.filter_event[ctx.guild.id] = {}
            
        if "nicknames" not in self.bot.cache.filter_event[ctx.guild.id]:
            self.bot.cache.filter_event[ctx.guild.id]["links"] = {
                "is_enabled": state,
                "threshold": 2 # default value, as this doesnt require a threshold
            }
            
        else:
            self.bot.cache.filter_event[ctx.guild.id]["links"]["is_enabled"] = state
        
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **link filter**.")
        
        
    @_filter.command(
        name="spam",
        usage="<state> <flags --threshold>",
        example="true --threshold 2",
        parameters={
            "threshold": {
                "converter": int,
                "description": "The limit of messages for one user in 5 seconds",
                "aliases": [
                    "limit"
                ]
            }
        }
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_spam(self, ctx: vile.Context, state: str):
        """Delete messages from users that send messages too fast"""
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.filter_event.get(ctx.guild.id, {}).get("spam", DICT).get("threshold") or 5
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
              
        else:
            state = 0
            
        if state == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("spam", {}).get("is_enabled") and threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("spam", DICT).get("threshold"):
            return await ctx.error("That is **already** the **current state**.")
            
        if state:
            if threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("spam", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                return await ctx.error("That is **already** the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                return await ctx.error("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "spam", state, threshold
        )
        if ctx.guild.id not in self.bot.cache.filter_event:
            self.bot.cache.filter_event[ctx.guild.id] = {}
            
        self.bot.cache.filter_event[ctx.guild.id]["spam"] = {
            "is_enabled": state,
            "threshold": threshold
        }
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **spam filter**{f' (with threshold: {threshold})' if state else '.'}")
              
            
    @_filter.command(
        name="emojis",
        aliases=("emoji",),
        usage="<state> <flags --threshold>",
        example="true --threshold 2",
        parameters={
            "threshold": {
                "converter": int,
                "description": "The limit for emojis in one message",
                "aliases": [
                    "limit"
                ]
            }
        }
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_emojis(self, ctx: vile.Context, state: str):
        """Delete any messages exceeding the threshold for emojis"""
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.filter_event.get(ctx.guild.id, {}).get("emojis", DICT).get("threshold") or 5
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
              
        else:
            state = 0
            
        if state == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("emojis", {}).get("is_enabled") and threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("emojis", DICT).get("threshold"):
            return await ctx.error("That is **already** the **current state**.")
            
        if state:
            if threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("emojis", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                return await ctx.error("That is **already** the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                return await ctx.error("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "emojis", state, threshold
        )
        if ctx.guild.id not in self.bot.cache.filter_event:
            self.bot.cache.filter_event[ctx.guild.id] = {}
            
        self.bot.cache.filter_event[ctx.guild.id]["emojis"] = {
            "is_enabled": state,
            "threshold": threshold
        }
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **emoji filter**{f' (with threshold: {threshold})' if state else '.'}")
              
            
    @_filter.command(
        name="invites",
        aliases=("invs",),
        usage="<state> <flags --threshold>",
        example="true --threshold 2"
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_invites(self, ctx: vile.Context, state: str):
        """Delete any messages exceeding the threshold for emojis"""
        
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
              
        else:
            state = 0
            
        if state == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("invites", DICT).get("is_enabled"):
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled);",
            ctx.guild.id, "invites", state
        )
        if ctx.guild.id not in self.bot.cache.filter_event:
            self.bot.cache.filter_event[ctx.guild.id] = {}
            
        self.bot.cache.filter_event[ctx.guild.id]["invites"] = {
            "is_enabled": state,
            "threshold": 2
        }
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **invite filter**.")
        
        
    @_filter.command(
        name="caps",
        aliases=("capslock",),
        usage="<state> <flags --threshold>",
        example="true --threshold 10",
        parameters={
            "threshold": {
                "converter": int,
                "description": "The limit for caps in one message",
                "aliases": [
                    "limit"
                ]
            }
        }
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_caps(self, ctx: vile.Context, state: str):
        """Delete any messages exceeding the threshold for caps"""
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.filter_event.get(ctx.guild.id, {}).get("caps", DICT).get("threshold") or 10
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
              
        else:
            state = 0
            
        if state == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("caps", {}).get("is_enabled") and threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("caps", DICT).get("threshold"):
            return await ctx.error("That is **already** the **current state**.")
            
        if state:
            if threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("caps", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                return await ctx.error("That is **already** the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                return await ctx.error("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "caps", state, threshold
        )
        if ctx.guild.id not in self.bot.cache.filter_event:
            self.bot.cache.filter_event[ctx.guild.id] = {}
            
        self.bot.cache.filter_event[ctx.guild.id]["caps"] = {
            "is_enabled": state,
            "threshold": threshold
        }
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **cap filter**{f' (with threshold: {threshold})' if state else '.'}")
        
        
    @_filter.command(
        name="snipe",
        usage="<option invites/links/images/words> <state>",
        example="invites true"
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_snipe(self, ctx: vile.Context, option: str, state: str):
        """Filter snipe command from allowing certain content"""
        
        if option not in ("invites", "links", "images", "words"):
            return await ctx.error("Please provide a **valid** option.\n" \
            "{self.bot.reply} **note:** all the options are shown in the command's help menu")
        
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
              
        else:
            state = 0
            
        if state == self.bot.cache.filter_snipe.get(ctx.guild.id, {}).get(option, DICT):
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            f"INSERT INTO filter_snipe (guild_id, {option}) VALUES (%s, %s) ON DUPLICATE KEY UPDATE {option} = VALUES({option});",
            ctx.guild.id, state
        )
        if ctx.guild.id not in self.bot.cache.filter_snipe:
            self.bot.cache.filter_snipe[ctx.guild.id] = {
                "invites": 0,
                "links": 0,
                "images": 0,
                "words": 0
            }
            
        self.bot.cache.filter_snipe[ctx.guild.id][option] = state
        return await ctx.success(f"{option.title()} will now **{'apwar' if state else 'stop appearing'}** in the snipe embed.")
        
            
    @_filter.command(
        name="massmention",
        aliases=("mentions",),
        usage="<state> <flags --threshold>",
        example="true --threshold 10",
        parameters={
            "threshold": {
                "converter": int,
                "description": "The limit for mentions in one message",
                "aliases": [
                    "limit"
                ]
            }
        }
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_massmention(self, ctx: vile.Context, state: str):
        """Delete any messages exceeding the threshold for mentions"""
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.filter_event.get(ctx.guild.id, {}).get("massmention", DICT).get("threshold") or 5
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
              
        else:
            state = 0
            
        if state == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("massmention", {}).get("is_enabled") and threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("massmention", DICT).get("threshold"):
            return await ctx.error("That is **already** the **current state**.")
            
        if state:
            if threshold == self.bot.cache.filter_event.get(ctx.guild.id, {}).get("massmention", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                return await ctx.error("That is **already** the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                return await ctx.error("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "massmention", state, threshold
        )
        if ctx.guild.id not in self.bot.cache.filter_event:
            self.bot.cache.filter_event[ctx.guild.id] = {}
            
        self.bot.cache.filter_event[ctx.guild.id]["massmention"] = {
            "is_enabled": state,
            "threshold": threshold
        }
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **mention filter**{f' (with threshold: {threshold})' if state else '.'}")
        
        
    @_filter.command(
        name="remove",
        aliases=("delete",),
        usage="<keyword>",
        example="nig"
    )
    @commands.has_permissions(manage_channels=True)
    async def filter_remove(self, ctx: vile.Context, keyword: str):
        """Remove a filtered word"""
        
        if keyword not in self.bot.cache.filter.get(ctx.guild.id, TUPLE):
            return await ctx.error("That is **already** a **filtered word**.")
            
        await self.bot.db.execute(
            "DELETE FROM filter WHERE guild_id = %s AND keyword = %s;",
            ctx.guild.id, keyword
        )
        self.bot.cache.filter[ctx.guild.id].remove(keyword)
        
        return await ctx.success(f"Successfully **removed** the filtered keyword \n```{keyword}```")
        
            
    @commands.group(
        name="autoresponder",
        aliases=("autoreply", "autorespond",),
        usage="<sub command>",
        example="welcome {content: welcome to the server! :3}",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def autoresponder(self, ctx: vile.Context):
        """Set up automatic replies to messages that match a trigger"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @autoresponder.command(
        name="update",
        usage="<trigger> <response>",
        example="welcome {content: hello}"
    )
    async def autoresponder_update(self, ctx: vile.Context, trigger: str, *, response: str):
        """Update the response for an auto-reply triggee"""
        
        if trigger not in self.bot.cache.welcome_settings.get(ctx.guild.id, DICT):
            return await ctx.error("That **isn't** an existing **auto-reply trigger**.")
            
        if response == self.bot.cache.welcome_settings.get(ctx.guild.id, {}).get(trigger, DICT).get("response"):
            return await ctx.error("That is **already** the **current response**.")
            
        await self.bot.db.execute(
            "UPDATE autoresponder SET response = %s WHERE keyword = %s;",
            response, trigger
        )
        self.bot.cache.autoresponder[ctx.guild.id][trigger]["response"] = response
            
        return await ctx.success(f"Successfully **updated** `{trigger}`'s response to \n```{response}```")
        
    
    @autoresponder.group(
        name="add",
        usage="<trigger> <response>",
        example="welcome {content: welcome to the server! :3}",
        invoke_without_command=True
    )
    async def autoresponder_add(self, ctx: vile.Context, trigger: str, *, response: str):
        """Add a reply to a word"""
        
        if trigger in self.bot.cache.autoresponder.get(ctx.guild.id, DICT):
            return await ctx.error("That is **already** an existing **auto-reply trigger**.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder (guild_id, keyword, response, created_by) VALUES (%s, %s, %s, %s);",
            ctx.guild.id, trigger, response, ctx.author.id
        )
        if ctx.guild.id not in self.bot.cache.autoresponder:
            self.bot.cache.autoresponder[ctx.guild.id] = {}
            
        self.bot.cache.autoresponder[ctx.guild.id][trigger] = {
            "keyword": trigger,
            "response": response,
            "created_by": ctx.author.id
        }
            
        return await ctx.success(f"Successfully **binded** `{trigger}`'s response to \n```{response}```")
        
        
    @autoresponder_add.command(
        name="images",
        usage="<response>",
        example="{content: hot}"
    )
    @commands.has_permissions(manage_channels=True)
    async def autoresponder_add_images(self, ctx: vile.Context, *, response: str):
        """Add a response for images"""
        
        if response == self.bot.cache.autoresponder_event.get(ctx.guild.id, DICT).get("images", ""):
            return await ctx.error("That is **already** the **auto-response** for images.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder_event (guild_id, event, response) VALUES (%s, %s, %s);",
            ctx.guild.id, "images", response
        )
        if ctx.guild.id not in self.bot.cache.autoresponder_event:
            self.bot.cache.autoresponder_event[ctx.guild.id] = {}
            
        self.bot.cache.autoresponder_event[ctx.guild.id]["images"] = response
        return await ctx.success(f"Successfully **binded** the response for images to \n```{response}```")
        
        
    @autoresponder_add.command(
        name="spoilers",
        usage="<response>",
        example="{content: shhh}"
    )
    @commands.has_permissions(manage_channels=True)
    async def autoresponder_add_spoilers(self, ctx: vile.Context, *, response: str):
        """Add a response for spoilers"""
        
        if response == self.bot.cache.autoresponder_event.get(ctx.guild.id, DICT).get("spoilers", ""):
            return await ctx.error("That is **already** the **auto-response** for spoilers.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder_event (guild_id, event, response) VALUES (%s, %s, %s);",
            ctx.guild.id, "spoilers", response
        )
        if ctx.guild.id not in self.bot.cache.autoresponder_event:
            self.bot.cache.autoresponder_event[ctx.guild.id] = {}
            
        self.bot.cache.autoresponder_event[ctx.guild.id]["spoilers"] = response
        return await ctx.success(f"Successfully **binded** the response for spoilers to \n```{response}```")
    

    @autoresponder_add.command(
        name="emojis",
        usage="<response>",
        example="{content: hey}"
    )
    @commands.has_permissions(manage_channels=True)
    async def autoresponder_add_emojis(self, ctx: vile.Context, *, response: str):
        """Add a response for emojis"""
        
        if response == self.bot.cache.autoresponder_event.get(ctx.guild.id, DICT).get("emojis", ""):
            return await ctx.error("That is **already** the **auto-response** for emojis.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder_event (guild_id, event, response) VALUES (%s, %s, %s);",
            ctx.guild.id, "emojis", response
        )
        if ctx.guild.id not in self.bot.cache.autoresponder_event:
            self.bot.cache.autoresponder_event[ctx.guild.id] = {}
            
        self.bot.cache.autoresponder_event[ctx.guild.id]["emojis"] = response
        return await ctx.success(f"Successfully **binded** the response for emojis to \n```{response}```")
        
        
    @autoresponder_add.command(
        name="stickers",
        usage="<response>",
        example="{content: fat}"
    )
    @commands.has_permissions(manage_channels=True)
    async def autoresponder_add_stickers(self, ctx: vile.Context, *, response: str):
        """Add a response for stickers"""
        
        if response == self.bot.cache.autoresponder_event.get(ctx.guild.id, DICT).get("stickers", ""):
            return await ctx.error("That is **already** the **auto-response** for stickers.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder_event (guild_id, event, response) VALUES (%s, %s, %s);",
            ctx.guild.id, "stickers", response
        )
        if ctx.guild.id not in self.bot.cache.autoresponder_event:
            self.bot.cache.autoresponder_event[ctx.guild.id] = {}
            
        self.bot.cache.autoresponder_event[ctx.guild.id]["stickers"] = response
        return await ctx.success(f"Successfully **binded** the response for stickers to \n```{response}```")
        
        
    @autoresponder.group(
        name="remove",
        usage="<trigger>",
        example="welcome",
        invoke_without_command=True
    )
    async def autoresponder_remove(self, ctx: vile.Context, trigger: str):
        """Remove a auto-reply trigger"""
        
        if trigger not in self.bot.cache.autoresponder.get(ctx.guild.id, DICT):
            return await ctx.error("There **isn't** a **auto-reply trigger** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder WHERE guild_id = %s AND keyword = %s;",
            ctx.guild.id, trigger
        )
        del self.bot.cache.autoresponder[ctx.guild.id][trigger]
            
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** with name `{trigger}`.")
        
        
    @autoresponder_remove.command(
        name="images",
        invoke_without_command=True
    )
    async def autoresponder_remove_images(self, ctx: vile.Context):
        """Remove the response for images"""
        
        if not self.bot.cache.autoresponder_event.get(ctx.guild.id, DICT).get("images", ""):
            return await ctx.error("There **isn't** a **auto-reply trigger** for images.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
            ctx.guild.id, "images"
        )
        del self.bot.cache.autoresponder[ctx.guild.id]["images"]
            
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** for images.")
        
        
    @autoresponder_remove.command(
        name="spoilers",
        invoke_without_command=True
    )
    async def autoresponder_remove_spoilers(self, ctx: vile.Context):
        """Remove the response for spoilers"""
        
        if not self.bot.cache.autoresponder_event.get(ctx.guild.id, DICT).get("spoilers", ""):
            return await ctx.error("There **isn't** a **auto-reply trigger** for spoilers.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
            ctx.guild.id, "spoilers"
        )
        del self.bot.cache.autoresponder[ctx.guild.id]["spoilers"]
            
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** for spoilers.")
        
        
    @autoresponder_remove.command(
        name="emojis",
        invoke_without_command=True
    )
    async def autoresponder_remove_emojis(self, ctx: vile.Context):
        """Remove the response for emojis"""
        
        if not self.bot.cache.autoresponder_event.get(ctx.guild.id, DICT).get("emojis", ""):
            return await ctx.error("There **isn't** a **auto-reply trigger** for emojis.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
            ctx.guild.id, "emojis"
        )
        del self.bot.cache.autoresponder[ctx.guild.id]["emojis"]
            
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** for emojis.")
        
        
    @autoresponder_remove.command(
        name="stickers",
        invoke_without_command=True
    )
    async def autoresponder_remove_stickers(self, ctx: vile.Context):
        """Remove the response for stickers"""
        
        if not self.bot.cache.autoresponder_event.get(ctx.guild.id, DICT).get("stickers", ""):
            return await ctx.error("There **isn't** a **auto-reply trigger** for stickers.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
            ctx.guild.id, "stickers"
        )
        del self.bot.cache.autoresponder[ctx.guild.id]["stickers"]
            
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** for stickers.")

        
    @autoresponder.command(
        name="clear"
    )
    async def autoresponder_clear(self, ctx: vile.Context, type: Optional[str] = None):
        """Clear every auto-reply trigger in this server"""
        
        if ctx.guild.id not in self.bot.cache.autoresponder and ctx.guild.id not in self.bot.cache.autoresponder_event:
            return await ctx.error("There **aren't** any **auto-reply triggers** in this server.")
            
        if type is not None:
            if type.lower() not in ("images", "spoilers", "emojis", "stickers"):
                return await ctx.error("There **isn't** an **auto-reply event** like that.")
                
            if ctx.guild.id not in self.bot.cache.autoresponder_event:
                return await ctx.error("There **aren't** any **auto-reply events** in this server.")
                
            if type.lower() not in self.bot.cache.autoresponder_event[ctx.guild.id]:
                return await ctx.error("There **isn't** an **auto-reply event** like that in this server.")
            
            await self.bot.db.execute(
                "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
                ctx.guild.id, type.lower()
            )
            del self.bot.cache.autoresponder_event[ctx.guild.id][type.lower()]
            return await ctx.success("Successfully **cleared** every **auto-reply** for that event.")
        
        if ctx.guild.id in self.bot.cache.autoresponder:
            await self.bot.db.execute(
                "DELETE FROM autoresponder WHERE guild_id = %s;",
                ctx.guild.id
            )
            del self.bot.cache.autoresponder[ctx.guild.id]
        
        if ctx.guild.id in self.bot.cache.autoresponder_event:  
            await self.bot.db.execute(
                "DELETE FROM autoresponder_event WHERE guild_id = %s;",
                ctx.guild.id
            )
            del self.bot.cache.autoresponder_event[ctx.guild.id]
        
        return await ctx.success("Successfully **cleared** every **auto-reply trigger**.")
        
        
    @autoresponder.command(
        name="variables",
        aliases=("variable", "vars",)
    )
    async def autoresponder_variables(self, ctx: vile.Context):
        """View the available autoresponder message variables"""
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @autoresponder.command(
        name="list",
        parameters={
            "extras": {
                "require_value": False,
                "description": "Whether to show the extra features",
                "aliases": [
                    "extra",
                    "e"
                ]
            }
        }
    )
    @commands.has_permissions(manage_channels=True)
    async def autoresponder_list(self, ctx: vile.Context):
        """View every auto-reply trigger"""
        
        if ctx.parameters.get("extras") is True:
            rows, embed = [], discord.Embed(
                color=self.bot.color,
                title=f"Auto-Reply Extras in {ctx.guild.name}"
            )
            for event, response in self.bot.cache.autoresponder_event.get(ctx.guild.id, DICT).items():
                rows.append(f"{event}\n{self.bot.reply} **Response:** {discord.utils.escape_markdown(response)}")
                
            return await ctx.paginate((embed, rows))
        
        if not self.bot.cache.autoresponder.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **auto-reply triggers** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Auto-Reply Triggers in {ctx.guild.name}"
        )
        for keyword, _dict in self.bot.cache.autoresponder[ctx.guild.id].items():
            owner = self.bot.get_user(_dict["created_by"]) or await self.bot.fetch_user(_dict["created_by"])
            rows.append(f"{keyword}\n{self.bot.reply} **Owner:** {owner.mention} (`{owner.id}`)\n{self.bot.reply} **Response:** {discord.utils.escape_markdown(_dict['response'])}")
                
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="autoreact",
        aliases=("reaction", "autoreaction",),
        usage="<sub command>",
        example="add 50DollaLemonade :jitTrippin:",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact(self, ctx: vile.Context):
        """Set up automatic reactions to messages that match a trigger"""
        return await ctx.send_help(ctx.command.qualified_name)
        
    
    @autoreact.group(
        name="add",
        usage="<trigger> <reaction>",
        example="50DollaLemondate :jitTrippin:",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_add(self, ctx: vile.Context, trigger: str, reaction: vile.EmojiConverter):
        """Add a reaction to a trigger"""
        
        if reaction in self.bot.cache.autoreact.get(ctx.guild.id, DICT).get(trigger, TUPLE):
            return await ctx.error("That is **already** a reaction for that **auto-reply trigger**.")
            
        if len(self.bot.cache.autoreact.get(ctx.guild.id, DICT).get(trigger, TUPLE)) > 15:
            return await ctx.error("There are too many reactions for that trigger.")
            
        if len(trigger) > 32:
            return await ctx.error("Please provide a **valid** trigger under 32 characters.")
            
        await self.bot.db.execute(
            "INSERT INTO autoreact (guild_id, keyword, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, trigger, reaction
        )
        if ctx.guild.id not in self.bot.cache.autoreact:
            self.bot.cache.autoreact[ctx.guild.id] = {}
            
        if trigger not in self.bot.cache.autoreact[ctx.guild.id]:
            self.bot.cache.autoreact[ctx.guild.id][trigger] = []
            
        self.bot.cache.autoreact[ctx.guild.id][trigger].append(str(reaction))
        return await ctx.success(f"Successfully **added** {reaction} as a reaction for `{trigger}`.")
        
    
    @autoreact_add.command(
        name="images",
        usage="<reaction>",
        example=":smash:"
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_add_images(self, ctx: vile.Context, reaction: vile.EmojiConverter):
        """Add a reaction for images"""
        
        if reaction in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("images", TUPLE):
            return await ctx.error("That is **already** an **auto-reaction** for images.")
            
        if len(self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("images", TUPLE)) > 15:
            return await ctx.error("There are too many reactions for that trigger.")
            
        await self.bot.db.execute(
            "INSERT INTO autoreact_event (guild_id, event, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, "images", reaction
        )
        if ctx.guild.id not in self.bot.cache.autoreact_event:
            self.bot.cache.autoreact_event[ctx.guild.id] = {}
            
        if "images" not in self.bot.cache.autoreact_event[ctx.guild.id]:
            self.bot.cache.autoreact_event[ctx.guild.id]["images"] = []
            
        self.bot.cache.autoreact_event[ctx.guild.id]["images"].append(str(reaction))
        return await ctx.success(f"Successfully **added** {reaction} as a reaction for images.")
    
    
    @autoreact_add.command(
        name="spoilers",
        usage="<reaction>",
        example=":hushed_face:"
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_add_spoilers(self, ctx: vile.Context, reaction: vile.EmojiConverter):
        """Add a reaction for spoilers"""
        
        if reaction in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("spoilers", TUPLE):
            return await ctx.error("That is **already** an **auto-reaction** for spoilers.")
            
        if len(self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("spoilers", TUPLE)) > 15:
            return await ctx.error("There are too many reactions for that trigger.")
            
        await self.bot.db.execute(
            "INSERT INTO autoreact_event (guild_id, event, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, "spoilers", reaction
        )
        if ctx.guild.id not in self.bot.cache.autoreact_event:
            self.bot.cache.autoreact_event[ctx.guild.id] = {}
            
        if "spoilers" not in self.bot.cache.autoreact_event[ctx.guild.id]:
            self.bot.cache.autoreact_event[ctx.guild.id]["spoilers"] = []
            
        self.bot.cache.autoreact_event[ctx.guild.id]["spoilers"].append(str(reaction))
        return await ctx.success(f"Successfully **added** {reaction} as a reaction for spoilers.")
        
        
    @autoreact_add.command(
        name="emojis",
        usage="<reaction>",
        example=":wave:"
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_add_emojis(self, ctx: vile.Context, reaction: vile.EmojiConverter):
        """Add a reaction for emojis"""
        
        if reaction in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("emojis", TUPLE):
            return await ctx.error("That is **already** an **auto-reaction** for emojis.")
            
        if len(self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("emojis", TUPLE)) > 15:
            return await ctx.error("There are too many reactions for that trigger.")
             
        await self.bot.db.execute(
            "INSERT INTO autoreact_event (guild_id, event, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, "emojis", reaction
        )
        if ctx.guild.id not in self.bot.cache.autoreact_event:
            self.bot.cache.autoreact_event[ctx.guild.id] = {}
            
        if "emojis" not in self.bot.cache.autoreact_event[ctx.guild.id]:
            self.bot.cache.autoreact_event[ctx.guild.id]["emojis"] = []
            
        self.bot.cache.autoreact_event[ctx.guild.id]["emojis"].append(str(reaction))
        return await ctx.success(f"Successfully **added** {reaction} as a reaction for emojis.")
    
    
    @autoreact_add.command(
        name="stickers",
        usage="<reaction>",
        example=":zzz:"
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_add_stickers(self, ctx: vile.Context, reaction: vile.EmojiConverter):
        """Add a reaction for stickers"""
        
        if reaction in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("stickers", TUPLE):
            return await ctx.error("That is **already** an **auto-reaction** for stickers.")
            
        if len(self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("stickers", TUPLE)) > 15:
            return await ctx.error("There are too many reactions for that trigger.")
            
        await self.bot.db.execute(
            "INSERT INTO autoreact_event (guild_id, event, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, "stickers", reaction
        )
        if ctx.guild.id not in self.bot.cache.autoreact_event:
            self.bot.cache.autoreact_event[ctx.guild.id] = {}
            
        if "stickers" not in self.bot.cache.autoreact_event[ctx.guild.id]:
            self.bot.cache.autoreact_event[ctx.guild.id]["stickers"] = []
            
        self.bot.cache.autoreact_event[ctx.guild.id]["stickers"].append(str(reaction))
        return await ctx.success(f"Successfully **added** {reaction} as a reaction for stickers.")
    
        
    @autoreact.group(
        name="remove",
        usage="<trigger>",
        example="50DollaLemonade",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_remove(self, ctx: vile.Context, trigger: str, reactiin: vile.EmojiConverter):
        """Remove a reaction from an auto-react trigger"""
        
        if reaction not in self.bot.cache.autoreply.get(ctx.guild.id, DICT).get(trigger, TUPLE):
            return await ctx.error("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreply WHERE keyword = %s AND reaction = %s;",
            trigger, reaction
        )
        self.bot.cache.autoreply[ctx.guild.id][trigger].remove(reaction)
            
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
        
        
    @autoreact_remove.command(
        name="images",
        usage="<reaction>",
        example=":smash:"
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_remove_images(self, ctx: vile.Context, reaction: vile.EmojiConverter):
        """Remove a reaction for images"""
        
        if reaction not in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("images", TUPLE):
            return await ctx.error("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact_event WHERE guild_id = %s AND event = %s AND reaction = %s;",
            ctx.guild.id, "images", reaction
        )
        self.bot.cache.autoreact_event[ctx.guild.id]["images"].remove(reaction)
        
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
    
    
    @autoreact_remove.command(
        name="spoilers",
        usage="<reaction>",
        example=":hushed_face:"
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_remove_spoilers(self, ctx: vile.Context, reaction: vile.EmojiConverter):
        """Remove a reaction for spoilers"""
        
        if reaction not in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("spoilers", TUPLE):
            return await ctx.error("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact_event WHERE guild_id = %s AND event = %s AND reaction = %s;",
            ctx.guild.id, "spoilers", reaction
        )
        self.bot.cache.autoreact_event[ctx.guild.id]["spoilers"].remove(reaction)
        
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
    
    
    @autoreact_remove.command(
        name="emojis",
        usage="<reaction>",
        example=":wave:"
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_remove_emojis(self, ctx: vile.Context, reaction: vile.EmojiConverter):
        """Remove a reaction for emojis"""
        
        if reaction not in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("emojis", TUPLE):
            return await ctx.error("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact_event WHERE guild_id = %s AND event = %s AND reaction = %s;",
            ctx.guild.id, "emojis", reaction
        )
        self.bot.cache.autoreact_event[ctx.guild.id]["emojis"].remove(reaction)
        
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
    
    
    @autoreact_remove.command(
        name="stickers",
        usage="<reaction>",
        example=":zzz:"
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_remove_stickers(self, ctx: vile.Context, reaction: vile.EmojiConverter):
        """Remove a reaction for stickers"""
        
        if reaction not in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("stickers", TUPLE):
            return await ctx.error("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact_event WHERE guild_id = %s AND event = %s AND reaction = %s;",
            ctx.guild.id, "stickers", reaction
        )
        self.bot.cache.autoreact_event[ctx.guild.id]["stickers"].remove(reaction)
        
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
    
        
    @autoreact.command(
        name="clear"
    )
    async def autoreact_clear(self, ctx: vile.Context, type: Optional[str] = None):
        """Clear every auto-react trigger in this server"""
        
        if ctx.guild.id not in self.bot.cache.autoreact and ctx.guild.id not in self.bot.cache.autoreact_event:
            return await ctx.error("There **aren't** any **auto-react triggers** in this server.")
            
        if type is not None:
            if type.lower() not in ("images", "spoilers", "emojis", "stickers"):
                return await ctx.error("There **isn't** an **auto-react event** like that.")
                
            if ctx.guild.id not in self.bot.cache.autoreact_event:
                return await ctx.error("There **aren't** any **auto-react events** in this server.")
                
            if type.lower() not in self.bot.cache.autoreact_event[ctx.guild.id]:
                return await ctx.error("There **isn't** an **auto-react event** like that in this server.")
            
            await self.bot.db.execute(
                "DELETE FROM autoreact_event WHERE guild_id = %s AND event = %s;",
                ctx.guild.id, type.lower()
            )
            del self.bot.cache.autoreact_event[ctx.guild.id][type.lower()]
            return await ctx.success("Successfully **cleared** every **auto-reaction** for that event.")
        
        if ctx.guild.id in self.bot.cache.autoreact:
            await self.bot.db.execute(
                "DELETE FROM autoreact WHERE guild_id = %s;",
                ctx.guild.id
            )
            del self.bot.cache.autoreact[ctx.guild.id]
        
        if ctx.guild.id in self.bot.cache.autoreact_event:  
            await self.bot.db.execute(
                "DELETE FROM autoreact_event WHERE guild_id = %s;",
                ctx.guild.id
            )
            del self.bot.cache.autoreact_event[ctx.guild.id]
        
        return await ctx.success("Successfully **cleared** every **auto-react trigger**.")
        
        
    @autoreact.command(
        name="removeall",
        aliases=("deleteall",)
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_removeall(self, ctx: vile.Context, trigger: str):
        """Clear every auto-reaction from a trigger"""
        
        if trigger not in self.bot.cache.autoreact.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **auto-reactions** for that trigger.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact WHERE guild_id = %s AND trigger = %s;",
            ctx.guild.id, trigger
        )
        del self.bot.cache.autoreact[ctx.guild.id][trigger]
            
        return await ctx.success("Successfully **cleared** every **auto-reaction** belonging to that trigger.")
        
        
    @autoreact.command(
        name="list",
        parameters={
            "extras": {
                "require_value": False,
                "description": "Whether to show the extra features",
                "aliases": [
                    "extra",
                    "e"
                ]
            }
        }
    )
    @commands.has_permissions(manage_emojis=True)
    async def autoreact_list(self, ctx: vile.Context):
        """View every auto-react trigger"""
        
        if ctx.parameters.get("extras") is True:
            rows, embed = [], discord.Embed(
                color=self.bot.color,
                title=f"Auto-React Extras in {ctx.guild.name}"
            )
            for event, reactions in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).items():
                rows.append(f"{event}\n{self.bot.reply} **Reactions:** {', '.join(reactions)}")
                
            return await ctx.paginate((embed, rows))
        
        if not self.bot.cache.autoreact.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **auto-react triggers** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Auto-React Triggers in {ctx.guild.name}"
        )
        for keyword, reactions in self.bot.cache.autoreact[ctx.guild.id].items():
            rows.append(f"{keyword}\n{self.bot.reply}{self.bot.reply} **Reactions:** {', '.join(reactions)}")
                
        return await ctx.paginate((embed, rows))

        
    @commands.group(
        name="disable",
        aliases=("d",),
        usage="<sub command>",
        example="module lastfm",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx: vile.Context):
        """Disable a feature"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @disable.command(
        name="module",
        aliases=("category",),
        usage="<module>",
        example="lastfm"
    )
    async def disable_module(self, ctx: vile.Context, module: str):
        """Disable a module"""
        
        if module.lower() not in list(map(lambda c: c.replace("LastFM Integration", "LastFM").lower(), self.bot.cogs.keys())) or module.lower() == "developer":
            return await ctx.error("Please provide a **valid** module.")
            
        if module.lower() in self.bot.cache.disabled_module.get(ctx.guild.id, TUPLE):
            return await ctx.error("That module is **already disabled**.")
            
        if module.lower() == "servers":
            return await ctx.error("You can't **disable** that module.")
            
        await self.bot.db.execute(
            "INSERT INTO disabled_feature (guild_id, name, type) VALUES (%s, %s, 'module');",
            ctx.guild.id, module
        )
        if ctx.guild.id not in self.bot.cache.disabled_module:
            self.bot.cache.disabled_module[ctx.guild.id] = []
            
        self.bot.cache.disabled_module[ctx.guild.id].append(module)
        return await ctx.success(f"Successfully **disabled** the module `{module}`.")
        
        
    @disable.command(
        name="command",
        aliases=("cmd",),
        usage="<command>",
        example="image"
    )
    async def disable_command(self, ctx: vile.Context, *, command: str):
        """Disable a command"""
        
        if not (cmd := self.bot.get_command(command.lower())) or cmd.cog_name == "Developer":
            return await ctx.error("Please provide a **valid** command.")
            
        if cmd.qualified_name in self.bot.cache.disabled_command.get(ctx.guild.id, TUPLE):
            return await ctx.error("That command is **already disabled**.")
            
        if (cmd.root_parent or cmd).qualified_name in ("disable", "enable"):
            return await ctx.error("You can't **disable** that command.")
            
        await self.bot.db.execute(
            "INSERT INTO disabled_feature (guild_id, name, type) VALUES (%s, %s, 'command');",
            ctx.guild.id, cmd.qualified_name
        )
        if ctx.guild.id not in self.bot.cache.disabled_command:
            self.bot.cache.disabled_command[ctx.guild.id] = []
            
        self.bot.cache.disabled_command[ctx.guild.id].append(cmd.qualified_name)
        return await ctx.success(f"Successfully **disabled** the command `{cmd.qualified_name}`.")
    
    
    @disable.command(
        name="list"
    )
    @commands.has_permissions(manage_channels=True)
    async def disable_list(self, ctx: vile.Context):
        """View every disabled feature"""
        
        if not (self.bot.cache.disabled_module.get(ctx.guild.id, []) + self.bot.cache.disabled_command.get(ctx.guild.id, TUPLE)):
            return await ctx.error("There **aren't** any **disabled features** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Disabled Features in {ctx.guild.name}"
        )
        
        # I don't store the types in cache so a db query is necessary
        for name, type in await self.bot.db.execute("SELECT name, type FROM disabled_feature WHERE guild_id = %s;", ctx.guild.id):
            rows.append(f"{name}\n{self.bot.reply} **type:** {type}")
            
        return await ctx.paginate((embed, rows))
        
    
    @commands.group(
        name="pagination",
        aliases=("paginate",),
        usage="<sub command>",
        example="list",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_messages=True)
    async def pagination(self, ctx: vile.Context):
        """Set up multiple embeds on one message"""
        return await ctx.send_help(ctx.command.qualified_name)
    
    
    @pagination.command(
        name="add",
        usage="<message> <embed code>",
        example="1115893655962665071 ..."
    )
    @commands.has_permissions(manage_messages=True)
    async def pagination_add(self, ctx: vile.Context, message: vile.MessageConverter, *, code: str):
        """Add a page to a pagination embed"""
        
        if message.author != ctx.guild.me:
            return await ctx.error("The message be sent by me.")
            
        if len(code) > 1024:
            return await ctx.error("Please provide a **valid** embed script under 1024 characters.")
            
        await self.bot.db.execute(
            """
            INSERT IGNORE INTO pagination (guild_id, channel_id, message_id, current_page) VALUES (%s, %s, %s, %s);
            INSERT INTO pagination_pages (guild_id, channel_id, message_id, page, page_number) VALUES (%s, %s, %s, %s, %s);
            """,
            ctx.guild.id, message.channel.id, message.id, 1,
            ctx.guild.id, message.channel.id, message.id, code, len(self.bot.cache.pagination_pages.get(ctx.guild.id, DICT).get(message.id, TUPLE))+1
        )
        
        if ctx.guild.id not in self.bot.cache.pagination:
            self.bot.cache.pagination[ctx.guild.id] = {}
            
        if ctx.guild.id not in self.bot.cache.pagination_pages:
            self.bot.cache.pagination_pages[ctx.guild.id] = {}
            
        if message.id not in self.bot.cache.pagination[ctx.guild.id]:
            self.bot.cache.pagination[ctx.guild.id][message.id] = 1
            
        else:
            self.bot.cache.pagination[ctx.guild.id][message.id] = self.bot.cache.pagination[ctx.guild.id][message.id]+1

        if message.id not in self.bot.cache.pagination_pages[ctx.guild.id]:
            self.bot.cache.pagination_pages[ctx.guild.id][message.id] = []
            
        self.bot.cache.pagination_pages[ctx.guild.id][message.id].append((code, len(self.bot.cache.pagination_pages[ctx.guild.id][message.id])+1))
        
        validator = vile.EmbedScriptValidator()
        data = await validator.to_embed(await vile.pagination_replacement(
            code, 
            ctx.guild, 
            len(self.bot.cache.pagination_pages[ctx.guild.id][message.id]), 
            self.bot.cache.pagination[ctx.guild.id][message.id]
        ))
        del data["files"]
        await message.edit(**data)
        await self.bot.db.execute(
            "UPDATE pagination SET current_page = %s WHERE message_id = %s",
            self.bot.cache.pagination[ctx.guild.id][message.id], message.id
        )
                    
        asyncio.gather(*[
            message.add_reaction("<:v_left_page:1067034010624200714>"),
            message.add_reaction("<:v_right_page:1067034017108607076>")
        ])
        return await ctx.success(f"Successfully **added** a page to the pagination embed with this script:\n```{code}```")
        
        
    @pagination.command(
        name="update",
        aliases=("edit",),
        usage="<message> <id> <embed code>",
        example="1115893655962665071 2 ..."
    )
    @commands.has_permissions(manage_messages=True)
    async def pagination_update(self, ctx: vile.Context, message: vile.MessageConverter, id: int, *, code: str):
        """Update an existing page on pagination embed"""
        
        if message.id not in self.bot.cache.pagination_pages.get(ctx.guild.id, DICT):
            return await ctx.error("That **isn't** a pagination embed.")
            
        page = next(filter(lambda page: page[1] == id, self.bot.cache.pagination_pages[ctx.guild.id][message.id]), None)
        if page is None:
            return await ctx.error("Please provide a **valid** page ID for that pagination embed.")
            
        await self.bot.db.execute(
            "UPDATE pagination_pages SET page = %s WHERE message_id = %s AND page_number = %s;",
            code, message.id, id
        )
        pages = self.bot.cache.pagination_pages[ctx.guild.id][message.id]
        pages[pages.index(page)] = (code, id)
        
        return await ctx.success("Successfully **updated** that page.")
        
    
    @pagination.command(
        name="delete",
        usage="<message>",
        example="1115893655962665071"
    )
    @commands.has_permissions(manage_messages=True)
    async def pagination_delete(self, ctx: vile.Context, message: vile.MessageConverter):
        """Delete a pagination embed entirely"""
        
        if message.id not in self.bot.cache.pagination_pages.get(ctx.guild.id, DICT):
            return await ctx.error("That **isn't** a pagination embed.")
            
        await self.bot.db.execute(
            """
            DELETE FROM pagination_pages WHERE message_id = %s;
            DELETE FROM pagination WHERE message_id = %s;
            """,
            message.id,
            message.id
        )
        del self.bot.cache.pagination_pages[ctx.guild.id][message.id]
        del self.bot.cache.pagination[ctx.guild.id][message.id]
        
        return await ctx.success("Successfully **deleted** that pagination embed.")
        
        
    @pagination.command(
        name="remove",
        usage="<message> <id>",
        example="1115893655962665071 2"
    )
    @commands.has_permissions(manage_messages=True)
    async def pagination_remove(self, ctx: vile.Context, message: vile.MessageConverter, id: int):
        """Remove a page from a pagination embed"""
        
        if message.id not in self.bot.cache.pagination_pages.get(ctx.guild.id, DICT):
            return await ctx.error("That **isn't** a pagination embed.")
            
        page = next(filter(lambda page: page[1] == id, self.bot.cache.pagination_pages[ctx.guild.id][message.id]), None)
        if page is None:
            return await ctx.error("Please provide a **valid** page ID for that pagination embed.")
            
        await self.bot.db.execute(
            """
            DELETE FROM pagination_pages WHERE message_id = %s AND page_number = %s;
            UPDATE pagination SET current_page = %s WHERE message_id = %s;
            """,
            message.id, id,
            self.bot.cache.pagination[ctx.guild.id][message.id]-1, message.id
        )
        pages = self.bot.cache.pagination_pages[ctx.guild.id][message.id]
        pages.remove(pages.index(page))
        
        return await ctx.success("Successfully **removed** that page.")
        
    
    @pagination.command(
        name="restorereactions",
        aliases=("rr",),
        usage="<message>",
        example="1115893655962665071"
    )
    @commands.has_permissions(manage_messages=True)
    async def pagination_restorereactions(self, ctx: vile.Context, message: vile.MessageConverter):
        """Restore reactions to an existing pagination embed"""
        
        if message.id not in self.bot.cache.pagination_pages.get(ctx.guild.id, DICT):
            return await ctx.error("That **isn't** a pagination embed.")
            
        asyncio.gather(*[
            message.add_reaction("<:v_left_page:1067034010624200714>"),
            message.add_reaction("<:v_right_page:1067034017108607076>")
        ])
        return await ctx.success("Successfully **restored** that pagination embed's reactions.")
        
        
    @pagination.command(
        name="reset"
    )
    @commands.has_permissions(manage_messages=True)
    async def pagination_reset(self, ctx: vile.Context):
        """Remove every existing pagination embed"""
        
        if ctx.guild.id not in self.bot.cache.pagination_pages:
            return await ctx.error("That **aren't** any **pagination embeds** in this server.")
            
        await self.bot.db.execute(
            """
            DELETE FROM pagination_pages WHERE guild_id = %s;
            DELETE FROM pagination WHERE guild_id = %s;
            """,
            ctx.guild.id,
            ctx.guild.id
        )
        del self.bot.cache.pagination_pages[ctx.guild.id]
        del self.bot.cache.pagination[ctx.guild.id]
        
        return await ctx.success("Successfully **reset** every pagination embed in this server.")
        
        
    @pagination.command(
        name="list"
    )
    @commands.has_permissions(manage_guild=True)
    async def pagination_list(self, ctx: vile.Context):
        """View all existing pagination embeds"""
        
        if ctx.guild.id not in self.bot.cache.pagination:
            return await ctx.error("There **aren't** any **pagination embeds** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Pagination Embeds in {ctx.guild.name}"
        )
        for channel_id, message_id in await self.bot.db.execute("SELECT channel_id, message_id FROM pagination_pages WHERE guild_id = %s", ctx.guild.id):
            rows.append(f"[**{message_id}**](https://discord.com/channels/{ctx.guild.id}/{channel_id}/{message_id})")
                
        return await ctx.paginate((embed, rows))
    
        
    @commands.group(
        name="enable",
        usage="<sub command>",
        example="module lastfm",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx: vile.Context):
        """Enable a feature"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @enable.command(
        name="module",
        aliases=("category",),
        usage="<module>",
        example="lastfm"
    )
    async def enable_module(self, ctx: vile.Context, module: str):
        """Enable a module"""
        
        if module.lower() not in list(map(lambda c: c.replace("LastFM Integration", "LastFM").lower(), self.bot.cogs.keys())) or module.lower() == "developer":
            return await ctx.error("Please provide a **valid** module.")
            
        if module.lower() not in self.bot.cache.disabled_module.get(ctx.guild.id, TUPLE):
            return await ctx.error("That module is **already enabled**.")
            
        await self.bot.db.execute(
            "DELETE FROM disabled_feature WHERE guild_id = %s AND name = %s AND type = 'module';",
            ctx.guild.id, module
        )
        self.bot.cache.disabled_module[ctx.guild.id].remove(module)
        
        return await ctx.success(f"Successfully **disabled** the module `{module}`.")
        
        
    @enable.command(
        name="command",
        aliases=("cmd",),
        usage="<command>",
        example="image"
    )
    async def enable_command(self, ctx: vile.Context, *, command: str):
        """Enable a command"""
        
        if not (cmd := self.bot.get_command(command.lower())) or cmd.cog_name == "Developer":
            return await ctx.error("Please provide a **valid** command.")
            
        if cmd.qualified_name not in self.bot.cache.disabled_command.get(ctx.guild.id, TUPLE):
            return await ctx.error("That command is **already enabled**.")
            
        await self.bot.db.execute(
            "DELETE FROM disabled_feature WHERE guild_id = %s AND name = %s AND type = 'command';",
            ctx.guild.id, cmd.qualified_name
        )
        self.bot.cache.disabled_command[ctx.guild.id].remove(cmd.qualified_name)
        
        return await ctx.success(f"Successfully **enabled** the command `{cmd.qualified_name}`.")
        
        
    @commands.group(
        name="ignore",
        usage="<member or channel or role>",
        example="@trey#0006",
        invoke_without_command=True
    )
    @commands.has_permissions(administrator=True)
    async def ignore(self, ctx: vile.Context, *, source: Union[vile.MemberConverter, discord.TextChannel, vile.RoleConverter]):
        """Ignore commands from a member or channel or role"""
        
        if isinstance(source, discord.Member) and await ctx.can_moderate(source, "ignore") is not None:
            return
        
        if source.id in self.bot.cache.ignore.get(ctx.guild.id, TUPLE):
            await self.bot.db.execute(
                "DELETE FROM ignore_object WHERE object_id = %s;",
                source.id
            )
            self.bot.cache.ignore[ctx.guild.id].remove(source.id)
            return await ctx.success(f"No longer **ignoring commands** from {source.mention}.")
            
        if isinstance(source, discord.Member):
            type = "member"
        
        elif isinstance(source, discord.TextChannel):
            type = "channel"
            
        elif isinstance(source, discord.Role):
            type = "role"
            
        await self.bot.db.execute(
            "INSERT INTO ignore_object (guild_id, object_id, type) VALUES (%s, %s, %s);",
            ctx.guild.id, source.id, type
        )
        if ctx.guild.id not in self.bot.cache.ignore:
            self.bot.cache.ignore[ctx.guild.id] = []
            
        self.bot.cache.ignore[ctx.guild.id].append(source.id)
        return await ctx.success(f"Commands from {source.mention} will now be **ignored**.")
        
        
    @ignore.command(
        name="list"
    )
    @commands.has_permissions(manage_channels=True)
    async def ignore_list(self, ctx: vile.Context):
        """View every ignored member or channel or role"""
        
        if not self.bot.cache.ignore.get(ctx.guild.id, TUPLE):
            return await ctx.error("There **aren't** any **ignored members or channels or roles** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Ignored Objects in {ctx.guild.name}"
        )
        
        # i dont store the types in cache so a db query is necessary
        for object_id, type in await self.bot.db.execute("SELECT object_id, type FROM ignore_object WHERE guild_id = %s;", ctx.guild.id):
            object = ctx.guild.get_member(object_id) or ctx.guild.get_channel(object_id) or ctx.guild.get_role(object_id)
            if object:
                rows.append(f"{object.mention}\n{self.bot.reply} **type:** {type}")
            
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="set",
        usage="<sub command>",
        example="icon ...",
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def _set(self, ctx: vile.Context):
        """Set the new server icon or splash or banner"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @_set.command(
        name="icon",
        usage="[link or attachment]",
        example="..."
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def set_icon(self, ctx: vile.Context, image: vile.AttachmentConverter):
        """Set the new server icon"""
        
        image_bytes = await self.bot.proxied_session.read(image)

        try:
            await ctx.guild.edit(icon=image_bytes)
        except Exception:
            if not ctx.message.attachments or image != ctx.message.attachments[0].url:
                if await self.bot.cache.ratelimited(f"globalrl:suspicious_urls{image}", 3, 86400):
                    return await self.bot.blacklist(ctx.author.id, type=1)
                    
            return await ctx.error("Please provide a **valid** image.")
            
        return await ctx.success(f"Successfully **set** the new [**server icon**]({ctx.guild.icon.url}).")
    
    
    @_set.command(
        name="splash",
        usage="[link or attachment]",
        example="..."
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def set_splash(self, ctx: vile.Context, image: Optional[str] = None):
        """Set the new server splash"""
        
        if ctx.guild.premium_tier < 1:
            return await ctx.error("This server doesn't reach the **boost requirement** for a **splash background**.")
            
        try:
            image = await vile.AttachmentConverter().convert(ctx, image)
            image_bytes = await self.bot.proxied_session.read(image)
        except Exception:
            return
            
        try:
            await ctx.guild.edit(splash=image_bytes)
        except Exception:
            if not ctx.message.attachments or image != ctx.message.attachments[0].url:
                if await self.bot.ratelimited(f"globalrl:suspicious_urls{image}", 3, 86400):
                    return await self.bot.blacklist(ctx.author.id, type=1)
                    
            return await ctx.error("Please provide a **valid** image.")
            
        return await ctx.success(f"Successfully **set** the new [**server splash background**]({ctx.guild.icon.url}).")
    
    
    @_set.command(
        name="banner",
        usage="[link or attachment]",
        example="..."
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def set_banner(self, ctx: vile.Context, image: Optional[str] = None):
        """Set the new server banner"""
        
        if ctx.guild.premium_tier < 2:
            return await ctx.error("This server doesn't reach the **boost requirement** for a **banner**.")
            
        try:
            image = await vile.AttachmentConverter().convert(ctx, image)
            image_bytes = await self.bot.proxied_session.read(image)
        except Exception:
            return
            
        try:
            await ctx.guild.edit(banner=image_bytes)
        except Exception:
            if not ctx.message.attachments or image != ctx.message.attachments[0].url:
                if await self.bot.ratelimited(f"globalrl:suspicious_urls{image}", 3, 86400):
                    return await self.bot.blacklist(ctx.author.id, type=1)
                    
            return await ctx.error("Please provide a **valid** image.")
            
        return await ctx.success(f"Successfully **set** the new [**server banner**]({ctx.guild.banner.url}).")
        
    
    @commands.group(
        name="unset",
        usage="<sub command>",
        example="icon",
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def unset(self, ctx: vile.Context):
        """Unset the new server icon or splash or banner"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @unset.command(
        name="icon"
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def unset_icon(self, ctx: vile.Context):
        """Unset the server icon"""
        
        if ctx.guild.banner is None:
            return await ctx.error("This server **doesn't have** an **icon**")
            
        await ctx.guild.edit(icon=None)
        return await ctx.success(f"Successfully **unset** the **server icon**.")
    
    
    @unset.command(
        name="splash"
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def unset_splash(self, ctx: vile.Context):
        """Unset the server splash"""
        
        if ctx.guild.banner is None:
            return await ctx.error("This server **doesn't have** a **splash**")
            
        await ctx.guild.edit(splasy=None)
        return await ctx.success(f"Successfully **unset** the **server splash**.")
    
    
    @unset.command(
        name="banner"
    )
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def unset_banner(self, ctx: vile.Context):
        """Unset the server banner"""
        
        if ctx.guild.banner is None:
            return await ctx.error("This server **doesn't have** a **banner**")
            
        await ctx.guild.edit(banner=None)
        return await ctx.success(f"Successfully **unset** the **server banner**.")
        
        
    @commands.command(
        name="pin",
        usage="[message or reply]",
        example="..."
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def pin(self, ctx: vile.Context, message: Optional[vile.MessageConverter] = None):
        """Pin the provided or most recent message"""
        
        if not message:
            if reference := ctx.message.reference:
                message = reference.resolved
            else:
                async for message in ctx.channel.history(limit=2):
                    message = message
                
                if not message:
                    return await ctx.send_help(ctx.command.qualified_name)
                
        if len(await ctx.channel.pins()) == 50:
            return await ctx.error("This channel exceeds the **50 pin limit**.")
            
        await message.pin()
        return await ctx.success(f"Successfully **pinned** the [**provided message**]({message.jump_url}).")
        
        
    @commands.command(
        name="unpin",
        usage="[message or reply]",
        example="..."
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def unpin(self, ctx: vile.Context, message: Optional[vile.MessageConverter] = None):
        """Unpin the provided or most recent message"""
        
        if not message:
            if reference := ctx.message.reference:
                message = reference.resolved
            else:
                async for message in ctx.channel.history(limit=2):
                    message = message
                
                if not message:
                    return await ctx.send_help(ctx.command.qualified_name)
                
        if message.pinned is False:
            return await ctx.error("That message **isn't pinned**.")
            
        await message.unpin()
        return await ctx.success(f"Successfully **unpinned** the [**provided message**]({message.jump_url}).")
        

    @commands.command(
        name="firstmessage",
        aliases=("firstmsg",),
        usage="[channel]",
        example="..."
    )
    async def firstmessage(self, ctx: vile.Context, *, channel: Optional[discord.TextChannel] = None):
        """Get a link for the first message in a channel"""
        
        channel = channel or ctx.channel
        async for message in channel.history(limit=1, oldest_first=True):
            return await ctx.reply(view=discord.ui.View().add_item(
                discord.ui.Button(
                    label="First Message",
                    style=discord.ButtonStyle.link,
                    url=message.jump_url
                )
            ))
            
            
    @commands.group(
        name="pins",
        aliases=("pinarchive",),
        usage="<sub command>",
        example="archive",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def pins(self, ctx: vile.Context):
        """Setup the pin archival system"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @pins.command(
        name="archive",
        usage="[channel]",
        example="#chat"
    )
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_guild=True)
    async def pins_archive(self, ctx: vile.Context, *, channel: Optional[discord.TextChannel] = None):
        """Archive the pins in a channel"""
        
        channel = channel or ctx.channel
        if (config := self.bot.cache.pins.get(ctx.guild.id, DICT)) is None or (archive_channel := ctx.guild.get_channel(config.get("channel_id", 0))) is None:
            return await ctx.error("The pin archival system **is not set up** in this server.")
              
        if not (pins := await channel.pins()):
            return await ctx.error("There aren't any pins in that channel.")
            
        to_delete = await ctx.success(f"Archiving {channel.mention}'s pins...")
        async def do_pinarchive():
            for pin in pins:
                if pin.author.bot:
                    continue
                    
                embed = discord.Embed(
                    color=pin.author.color, 
                    description=pin.content + ("\n" + "\n".join(attachment.url for attachment in pin.attachments) if pin.attachments else ""),
                    timestamp=pin.created_at
                )
                embed.set_author(name=pin.author, icon_url=pin.author.display_avatar)
                embed.set_footer(text=f"Pin archived from #{channel.name}")
                if pin.attachments:
                    embed.set_image(url=pin.attachments[0].url)
                        
                try:
                    await archive_channel.send(
                        embed=embed,
                        view=discord.ui.View().add_item(
                            discord.ui.Button(
                                label="Jump to Message",
                                style=discord.ButtonStyle.link,
                                url=pin.jump_url
                            )
                        )
                    )
                    await pin.unpin()
                    await asyncio.sleep(1.25)
                except Exception:
                    continue
                
        await asyncio.gather(do_pinarchive())
        await to_delete.delete()
        return await ctx.success(f"Successfully **archived** this channel's pins! You can now find them in {channel.mention}.")
        
        
    @pins.command(
        name="channel",
        usage="<channel>",
        example="#pins"
    )
    @commands.has_permissions(manage_guild=True)
    async def pins_channel(self, ctx: vile.Context, *, channel: discord.TextChannel):
        """Set the pin archival channel"""
        
        if channel.id == self.bot.cache.pins.get(ctx.guild.id, DICT).get("channel_id", 0):
            return await ctx.error("That is **already** the **current pin archive channel**.")
            
        await self.bot.db.execute(
            "INSERT INTO pin_archive (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id);",
            ctx.guild.id, channel.id
        )
        if ctx.guild.id not in self.bot.cache.pins:
            self.bot.cache.pins[ctx.guild.id] = {
                "channel_id": channel.id,
                "is_enabled": 1
            }
        
        else:
            self.bot.cache.pins[ctx.guild.id]["channel_id"] = channel.id
            
        return await ctx.success(f"Successfully **binded** {channel.mention} as the pin archive channel.")
        
        
    @pins.command(
        name="toggle",
        usage="<state>",
        example="true"
    )
    async def pins_toggle(self, ctx: vile.Context, state: str):
        """Toggle the pin archival system"""
        
        if ctx.guild.id not in self.bot.cache.pins:
            return await ctx.error(f"The pin archival system **isn't setup** in this server! Please set the archive channel using `{ctx.prefix}pins channel #channel`.")
            
        if state not in ("on", "off", "enable", "disable", "true", "false"):
            return await ctx.error("Please provide a **valid** state.")
        
        if state in ("on", "enable", "true"):
            state = 1
            
        else:
            state = 0
            
        if state == self.bot.cache.pins[ctx.guild.id]["is_enabled"]:
            return await ctx.error("That is **already** the **current state**.")
            
        await self.bot.db.execute(
            "UPDATE pin_archive SET is_enabled = %s WHERE guild_id = %s;",
            state, ctx.guild.id
        )
        self.bot.cache.pins[ctx.guild.id]["is_enabled"] = state
            
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the pin archival system.")
        
        
    @pins.command(
        name="reset"
    )
    @commands.has_permissions(manage_guild=True)
    async def pins_reset(self, ctx: vile.Context):
        """Reset the pin archival system configuration"""
        
        if ctx.guild.id not in self.bot.cache.pins:
            return await ctx.error("The pin archival system **isn't setup** in this server. ")
            
        await self.bot.db.execute(
            "DELETE FROM pin_archive WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.pins[ctx.guild.id]
        
        return await ctx.success("Successfully **reset** the **pin archival system configuration**.")
        
        
    @commands.group(
        name="webhook",
        aliases=("webhooks",),
        usage="<sub command>",
        example="create #rules --name Server Rules --avatar ...",
        invoke_without_command=True
    )
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.has_permissions(manage_webhooks=True)
    async def webhook(self, ctx: vile.Context):
        """Set up webhooks in your server"""
        return await ctx.send_help(ctx.command.qualified_name)
        
    
    @webhook.command(
        name="create",
        usage="<channel> <flags --name/--avatar>",
        example="#rules --name Server Rules --avatar ...",
        parameters={
            "name": {
                "converter": str,
                "description": "The name of the webhook",
                "minimum": 2,
                "maximum": 32
            },
            "avatar": {
                "converter": str,
                "validator": lambda s: s.startswith("http"),
                "description": "The avatar of the webhook"
            }
        }
    )
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_create(self, ctx: vile.Context, channel: Optional[discord.TextChannel] = None):
        """Create a webhook to forward messages to"""
        
        channel = channel or ctx.channel
        if len(self.bot.cache.webhooks.get(ctx.guild.id, DICT)) > 10:
            return await ctx.error("This server **exceeds** vile's **maximum webhook limit** of 10.")
            
        avatar = ctx.parameters.get("avatar") or ctx.author.display_avatar.url
        try:
            webhook = await ctx.channel.create_webhook(
                name=ctx.parameters.get("name", "Captain Hook"),
                avatar=await self.bot.proxied_session.read(avatar),
                reason=f"webhook create: used by {ctx.author}"
            )
        except discord.HTTPException:
            return await ctx.error("Couldn't create a webhook using the provided flags.")
        except ValueError as e:
            if str(e) == "Unsupported image type given":
                return await ctx.error(f"Unsupported image type given.")
        
        identifier = vile.hash(webhook.url)
        await self.bot.db.execute(
            "INSERT INTO webhooks (guild_id, identifier, webhook_url, channel_id) VALUES (%s, %s, %s, %s);",
            ctx.guild.id, identifier, webhook.url, channel.id
        )
        if ctx.guild.id not in self.bot.cache.webhooks:
            self.bot.cache.webhooks[ctx.guild.id] = {}
        
        self.bot.cache.webhooks[ctx.guild.id][identifier] = {
            "webhook_url": webhook.url,
            "channel_id": channel.id
        }
        return await ctx.success(f"Successfully **created** a **webhook** with the identifier `{identifier}`.")
        
        
    @webhook.command(
        name="delete",
        usage="<identifier>",
        example="6110f4be8664323d"
    )
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_delete(self, ctx: vile.Context, identifier: str):
        """Delete a webhook using it's identifier"""
        
        if not (webhooks := self.bot.cache.webhooks.get(ctx.guild, DICT)):
            return await ctx.error("This server doesn't have any webhooks.\n**NOTE:** Webhooks must be created using my `,webhook create` command.")
            
        if identifier not in webhooks:
            return await ctx.error("Please provide a **valid** webhook.")
            
        await self.bot.db.execute(
            "DELETE FROM webhooks WHERE identifier = %s;",
            identifier
        )
        del webhooks[identifier]
        return await ctx.success("Successfully **deleted** webhook with identifier `{identifier}`.")
        
        
    @webhook.command(
        name="list"
    )
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_list(self, ctx: vile.Context):
        """View very available webhook"""
        
        if not self.bot.cache.webhooks.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **available webhooks** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Available Webhooks in {ctx.guild.name}"
        )

        for identifier, _dict in self.bot.cache.webhooks[ctx.guild.id].items():
            if channel := ctx.guild.get_channel(_dict["channel_id"]):
                rows.append(f"**{identifier}** - {channel.mention}")
            
        return await ctx.paginate((embed, rows))
        
        
    @webhook.command(
        name="send",
        usage="<identifier> <message>",
        example="3dc12ef0872723e7 {content: hi}",
        parameters={
            "username": {
                "converter": str,
                "descriptiion": "The username the Webhook Message will have",
                "minimum": 2,
                "maximum": 32
            }
        }
    )
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_send(self, ctx: vile.Context, identifier: str, *, message: vile.EmbedScriptValidator):
        """Send a message using an existing webhook"""
        
        if not self.bot.cache.webhooks.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **available webhooks** in this server.")
            
        if (_dict := self.bot.cache.webhooks[ctx.guild.id].get(identifier)) is None:
            return await ctx.error("That isn't an existing webhook.")
            
        webhook = discord.Webhook.from_url(
            _dict["webhook_url"],
            client=self.bot,
            bot_token=self.bot.http.token
        )
        try:
            webhook = await webhook.fetch()
        except discord.NotFound:
            await ctx.error("That webhook has been **deleted**.")
            await self.bot.db.execute(
                "DELETE FROM webhooks WHERE identifier = %s;",
                identifier
            )
            del self.bot.cache.webhooks[ctx.guild.id][identifier]
        
        webhook_message = await message.send(
            webhook,
            context=ctx,
            strip_text_of_flags=True,
            bot=self.bot,
            guild=ctx.guild,
            channel=webhook.channel,
            user=ctx.author,
            extras={
                "username": ctx.parameters.get("username", webhook.name),
                "wait": True
            }
        )
        await self.bot.db.execute(
            "INSERT INTO webhook_messages (identifier, webhook_url, message_id) VALUES (%s, %s, %s);",
            identifier, webhook.url, webhook_message.id
        )
        return await ctx.success(f"Successfully **sent** a message using webhook with identifier `{identifier}`.")
        
        
    @commands.group(
        name="fakepermissions",
        aliases=("fp", "fakeperm", "fakeperms",),
        usage="<sub command>",
        example="add @Moderator moderate_members",
        extras={
            "permissions": "Server Owner"
        },
        invoke_without_command=True
    )
    @commands.is_guild_owner()
    async def fakepermissions(self, ctx: vile.Context):
        """Set up fake permissions for a role using Vile"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @fakepermissions.command(
        name="add",
        aliases=("grant",),
        usage="<role> <permission>",
        example="@Moderator moderate_members",
        extras={
            "permissions": "Server Owner"
        }
    )
    @commands.is_guild_owner()
    async def fakepermissions_add(self, ctx: vile.Context, role: vile.RoleConverter, *, permission: str):
        """Grant a fake permission to a role"""
        
        permission = permission.replace(" ", "_").lower()
        if permission not in discord.Permissions.VALID_FLAGS:
            return await ctx.error("Please provide a **valid** permission.")
    
        if permission in self.bot.cache.fake_permissions.get(ctx.guild.id, DICT).get(role.id, TUPLE):
            return await ctx.error("That fake permission **already exists** for that role.")
            
        await self.bot.db.execute(
            "INSERT INTO fake_permissions (guild_id, role_id, permission) VALUES (%s, %s, %s);",
            ctx.guild.id, role.id, permission
        )
        if ctx.guild.id not in self.bot.cache.fake_permissions:
            self.bot.cache.fake_permissions[ctx.guild.id] = {}
            
        if role.id not in self.bot.cache.fake_permissions[ctx.guild.id]:
            self.bot.cache.fake_permissions[ctx.guild.id][role.id] = []
            
        self.bot.cache.fake_permissions[ctx.guild.id][role.id].append(permission)
        return await ctx.success(f"Successfully **added** fake permission `{permission}` to {role.mention}.")
        
        
    @fakepermissions.command(
        name="remove",
        usage="<role> <permission>",
        example="@Moderator moderate_members",
        extras={
            "permissions": "Server Owner"
        }
    )
    @commands.is_guild_owner()
    async def fakepermissions_remove(self, ctx: vile.Context, role: vile.RoleConverter, *, permission: str):
        """Remove a fake permission from a role"""
        
        permission = permission.replace(" ", "_").lower()
        if permission not in discord.Permissions.VALID_FLAGS:
            return await ctx.error("Please provide a **valid** permission.")
    
        if permission not in self.bot.cache.fake_permissions.get(ctx.guild.id, DICT).get(role.id, TUPLE):
            return await ctx.error("That fake permission **does not exist** for that role.")
            
        await self.bot.db.execute(
            "DELETE FROM fake_permissions WHERE role_id = %s AND permission = %s;",
            role.id, permission
        )
        self.bot.cache.fake_permissions[ctx.guild.id][role.id].remove(permission)
        
        return await ctx.success(f"Successfully **removed** fake permission `{permission}` from {role.mention}.")
        
        
    @fakepermissions.command(
        name="list",
        extras={
            "permissions": "Server Owner"
        }
    )
    @commands.is_guild_owner()
    async def fakepermissions_list(self, ctx: vile.Context):
        """View very fake permission"""
        
        if not self.bot.cache.fake_permissions.get(ctx.guild.id, DICT):
            return await ctx.error("There **aren't** any **fake permissions** in this server.")
            
        rows, embed = [], discord.Embed(
            color=self.bot.color,
            title=f"Fake Permissions in {ctx.guild.name}"
        )

        for role_id, permissions in self.bot.cache.fake_permissions[ctx.guild.id].items():
            if permissions and (role := ctx.guild.get_role(role_id)):
                rows.append(f"{role.mention}\n{self.bot.reply} **Permissions:** {', '.join(permission.replace('_', ' ').title() for permission in permissions)}")
            
        return await ctx.paginate((embed, rows))
        
        
    @commands.group(
        name="extract",
        aliases=("export",),
        usage="<sub command>",
        example="stickers",
        invoke_without_command=True
    )
    @commands.has_permissions(administrator=True)
    async def extract(self, ctx: vile.Context):
        """Sends all of an object in a ZIP file"""
        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @extract.command(
        name="stickers"
    )
    @commands.has_permissions(administrator=True)
    async def extract_stickers(self, ctx: vile.Context):
        """Sends all of your server's stickers in a ZIP file"""
        
        if not ctx.guild.stickers:
            return await ctx.error("This server doesn't have any stickers.")
            
        stickers = await asyncio.gather(*(s.read() for s in ctx.guild.stickers))
        with tempfile.NamedTemporaryFile(suffix=".zip") as zip_file:
            with zipfile.ZipFile(zip_file.name, "w") as zip_obj:
                for bytes, sticker in zip(stickers, ctx.guild.stickers):
                    filename = f"{sticker.name}.{sticker.format.name}"
                    zip_obj.writestr(filename, bytes)
            
            return await ctx.reply(file=discord.File(zip_file.name, f"stickers_export_{ctx.guild.id}.zip"))
        
        
    @extract.command(
        name="emojis"
    )
    @commands.has_permissions(administrator=True)
    async def extract_emojs(self, ctx: vile.Context):
        """Sends all of your server's emojis in a ZIP file"""
        
        if not ctx.guild.emojis:
            return await ctx.error("This server doesn't have any emojis.")
            
        emojis = await asyncio.gather(*(e.read() for e in ctx.guild.emojis))
        with tempfile.NamedTemporaryFile(suffix=".zip") as zip_file:
            with zipfile.ZipFile(zip_file.name, "w") as zip_obj:
                for bytes, emoji in zip(emojis, ctx.guild.emojis):
                    filename = f"{emoji.name}.{'gif' if emoji.animated else 'png'}"
                    zip_obj.writestr(filename, bytes)
            
            return await ctx.reply(file=discord.File(zip_file.name, f"emojis_export_{ctx.guild.id}.zip"))
        
        
async def setup(bot: "VileBot") -> None:
    await bot.add_cog(Servers(bot))