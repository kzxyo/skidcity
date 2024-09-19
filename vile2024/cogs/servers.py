from asyncio import (
    TimeoutError, 
    ensure_future, 
    gather, 
    sleep, 
    wait_for
)

from base64 import (
    b64decode, 
    b64encode
)

from contextlib import suppress
from datetime import datetime as Date
from io import BytesIO
from tempfile import NamedTemporaryFile
from time import time
from typing_extensions import NoReturn

from typing import (
    Optional, 
    Union
)

from zipfile import ZipFile

from discord import (
    ButtonStyle, 
    Embed, 
    File, 
    Forbidden, 
    PartialEmoji, 
    Permissions, 
    TextChannel, 
    Webhook,
    utils
)

from discord.errors import (
    HTTPException, 
    NotFound
)

from discord.ext import tasks

from discord.ext.commands import (
    BucketType, 
    Cog,
    Greedy, 
    bot_has_permissions, 
    command as Command, 
    CommandError,
    group as Group, 
    guild_has_vanity, 
    has_permissions, 
    hybrid_group as HybridGroup, 
    is_guild_owner, 
    max_concurrency, 
    parameter
)

from discord.ui import Button, View
from munch import Munch

from utilities.vile import (
    Attachment, 
    Color, 
    Context, 
    EmbedScript, 
    Emoji,
    hash,
    Member, 
    Message, 
    Role, 
    Sticker, 
    VileBot,
    dominant_color, 
    multi_replace,
    pagination_replacement
)

import orjson

TUPLE = ()
DICT = { }


class Servers(Cog):
    def __init__(self, bot: VileBot) -> NoReturn:
        self.bot: VileBot = bot
        
        
    async def cog_load(self) -> NoReturn:
        """
        Starts the stickymessage_loop if it is not running.
        """

        if not self.stickymessage_loop.is_running():
            self.stickymessage_loop.start()
            
            
    async def cog_unload(self) -> NoReturn:
        """
        Cancels the stickymessage_loop if it is running.
        """
        
        if self.stickymessage_loop.is_running():
            self.stickymessage_loop.cancel()
        
        
    @tasks.loop(seconds=30)
    async def stickymessage_loop(self):
        """
        A background loop that manages sending/deleting sticky messages
        """
        
        await self.bot.wait_until_ready()
        
        async def do_stickymessage():
            for guild in self.bot.guilds:
                if self.bot.cache.keys(pattern=f"data:sticky_message_settings:{guild.id}:*"):
                    for channel_id in tuple(
                        int(record.split(":")[::-1][0])
                        for record in self.bot.cache.keys(pattern=f"data:sticky_message_settings:{guild.id}:*")
                    ):
                        if channel := self.bot.get_channel(channel_id):
                            settings = self.bot.cache.get(f"data:sticky_message_settings:{guild.id}:{channel.id}")

                            if settings.is_enabled == False:
                                continue
                                
                            do_sticky = True

                            message_id = await self.bot.db.fetchval(
                                "SELECT message_id FROM sticky_message WHERE channel_id = %s", 
                                channel.id
                            )
                            
                            async for message in channel.history(limit=1):
                                if message.id == message_id:
                                    do_sticky = False
                                    
                            if do_sticky is False:
                                continue
                                        
                            if message_id:
                                with suppress(Exception):
                                    message = await channel.fetch_message(message_id)
                                    await message.delete()

                            message = await EmbedScript(settings.message).send(
                                channel,
                                guild=guild
                            )

                            await self.bot.db.execute(
                                "INSERT INTO sticky_message (channel_id, message_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE message_id = VALUES(message_id);",
                                channel.id, message.id
                            )
                            
        self.bot.loop.create_task(do_stickymessage())
    
        
    @Cog.listener()
    async def on_member_boost(self: "Servers", member: Member):
        """
        Listener function that is called when a member boosts a server.

        Parameters:
            member (Member): The member who boosted the server.
        """
        
        await self.bot.db.execute(
            "DELETE FROM boosters_lost WHERE guild_id = %s AND user_id = %s;",
            member.guild.id, member.id
        )

        if member.guild.id in self.bot.cache.boost_settings:
            if self.bot.cache.ratelimited(f"rl:boost_message{member.guild.id}", 5, 30):
                return
                
            for channel_id in self.bot.cache.boost_settings[member.guild.id]:
                if (channel := self.bot.get_channel(channel_id)) is not None and channel.permissions_for(member.guild.me).send_messages is True:
                    if self.bot.cache.boost_settings[member.guild.id][channel_id]["is_enabled"] == True:
                        self.bot.loop.create_task(EmbedScript(self.bot.cache.boost_settings[member.guild.id][channel_id]["message"]).send(
                            channel,
                            guild=member.guild,
                            user=member
                        ))
        
        if role_id := self.bot.cache.booster_award.get(member.guild.id):
            if role := member.guild.get_role(role_id):
                if member.guild.me.guild_permissions.manage_roles is True:
                    if role.permissions.administrator is False:
                        if role < member.guild.me.top_role:
                            await member.add_roles(
                                role, 
                                reason=f"{self.bot.user.name.title()} Booster Roles [{member}]: Member boosted"
                            )
                    
                    
    @Cog.listener()
    async def on_member_unboost(self: "Servers", member: Member):
        """
        Listener that is triggered when a member unboosts a server.

        Parameters:
            member (Member): The member who unboosted the server.
        """
        
        await self.bot.db.execute(
            "INSERT INTO boosters_lost (guild_id, user_id, expired) VALUES (%s, %s, %s);",
            member.guild.id, member.id, Date.now()
        )

        if member.guild.id in self.bot.cache.unboost_settings:
            if self.bot.cache.ratelimited(f"rl:unboost_message{member.guild.id}", 5, 30):
                return
                
            for channel_id in self.bot.cache.unboost_settings[member.guild.id]:
                if channel := self.get_channel(channel_id):
                    if channel.permissions_for(member.guild.me).send_messages is True:
                        if self.bot.cache.unboost_settings[member.guild.id][channel_id]["is_enabled"] == True:
                            self.bot.loop.create_task(EmbedScript(self.bot.cache.unboost_settings[member.guild.id][channel_id]["message"]).send(
                                channel,
                                guild=member.guild,
                                user=member
                            ))
        
        if role_id := self.bot.cache.booster_award.get(member.guild.id):
            if role := member.guild.get_role(role_id):
                if member.guild.me.guild_permissions.manage_roles is True:
                    if role.position < member.guild.me.top_role.position:
                        await member.remove_roles(
                            role, 
                            reason=f"{self.bot.user.name.title()} Booster Roles [{member}]: Member unboosted"
                        )
                    
        if member.guild.id in self.bot.cache.booster_role:
            if booster_role := member.guild.get_role(self.bot.cache.booster_role[member.guild.id].get(member.id)):
                await booster_role.delete(reason=f"{self.bot.user.name.title()} Booster Roles [{member}]: Member unboosted")
                
                self.bot.cache.execute(
                    "DELETE FROM booster_role WHERE guild_id = %s AND user_id = %s;",
                    member.guild.id, member.id
                )
                
                del self.bot.cache.booster_role[member.guild.id][member.id]
                    
                    
    @Cog.listener()
    async def on_member_remove(self: "Servers", member: Member):
        """
        Event listener function that is called when a member leaves a server.
        
        Parameters:
            member (Member): The member that left the server.
        """
        
        if member.guild.id in self.bot.cache.booster_role:
            if role_id := self.bot.cache.booster_role[member.guild.id].get(member.id):
                if role := member.guild.get_role(role_id):
                    if member.guild.me.guild_permissions.manage_roles is True:
                         await role.delete(reason=f"{self.bot.user.name.title()} Booster Roles [{member}]: Member left the server")
        
        
    @HybridGroup(
        name="prefix",
        aliases=("serverprefix",),
        usage="<sub command>",
        example="set .",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def prefix(self: "Servers", ctx: Context):
        """
        Manage the server's command prefix
        """
        
        return await ctx.respond(
            f"[**{self.bot.user.name.title()}'s**](https://gg/KsfkG3BZ4h) global prefix is `{self.bot.global_prefix}`, this server's prefix is {'not set' if ctx.guild.id not in self.bot.cache.guild_prefix else f'`{self.bot.cache.guild_prefix[ctx.guild.id]}`'} and your custom prefix is {'not set' if ctx.author.id not in self.bot.cache.custom_prefix else f'`{self.bot.cache.custom_prefix[ctx.author.id]}`'}.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @prefix.command(
        name="set",
        usage="<prefix>",
        example="."
    )
    async def prefix_set(self: "Servers", ctx: Context, prefix: str):
        """
        Set the server's command prefix
        """
        
        if prefix == self.bot.cache.guild_prefix.get(ctx.guild.id):
            raise CommandError("That is **already** the server's command prefix.")
            
        if len(prefix) > 10:
            raise CommandError("Please provide a **valid** prefix under 10 characters.")
            
        await self.bot.db.execute(
            "INSERT INTO guild_prefix (guild_id, prefix) VALUES (%s, %s) ON DUPLICATE KEY UPDATE prefix = VALUES(prefix);",
            ctx.guild.id, prefix
        )
        self.bot.cache.guild_prefix[ctx.guild.id] = prefix
        
        return await ctx.success(f"Successfully **binded** the server's command prefix to `{prefix}`.")
        
    
    @prefix.command(
        name="remove"
    )
    async def prefix_remove(self: "Servers", ctx: Context):
        """
        Remove the server's command prefix
        """
        
        if ctx.guild.id not in self.bot.cache.guild_prefix:
            raise CommandError("This server **doesn't have** a command prefix.")
            
        await self.bot.db.execute(
            "DELETE FROM guild_prefix WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.guild_prefix[ctx.guild.id]
        
        return await ctx.success(f"Successfully **removed** the server's command prefix.")
        
        
    @HybridGroup(
        name="customprefix",
        aliases=("selfprefix", "cp",),
        usage="<sub command>",
        example="set .",
        invoke_without_command=True
    )
    async def customprefix(self: "Servers", ctx: Context):
        """
        Manage your command prefix
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @customprefix.command(
        name="set",
        usage="<prefix>",
        example="."
    )
    async def customprefix_set(self: "Servers", ctx: Context, prefix: str):
        """
        Set your command prefix
        """
        
        if prefix == self.bot.cache.custom_prefix.get(ctx.author.id):
            raise CommandError("That is **already** your command prefix.")
            
        if len(prefix) > 10:
            raise CommandError("Please provide a **valid** prefix under 10 characters.")
            
        await self.bot.db.execute(
            "INSERT INTO custom_prefix (user_id, prefix) VALUES (%s, %s) ON DUPLICATE KEY UPDATE prefix = VALUES(prefix);",
            ctx.author.id, prefix
        )
        self.bot.cache.custom_prefix[ctx.author.id] = prefix
        
        return await ctx.success(f"Successfully **binded** your command prefix to `{prefix}`.")
        
    
    @customprefix.command(
        name="remove"
    )
    async def customprefix_remove(self: "Servers", ctx: Context):
        """
        Remove your command prefix
        """
        
        if ctx.author.id not in self.bot.cache.custom_prefix:
            raise CommandError("You **don't have** a command prefix.")
            
        await self.bot.db.execute(
            "DELETE FROM custom_prefix WHERE user_id = %s;",
            ctx.author.id
        )

        del self.bot.cache.custom_prefix[ctx.author.id]
        return await ctx.success(f"Successfully **removed** your custom command prefix.")
        
        
    @Group(
        name="data",
        aliases=("datacollection",),
        usage="<sub command>",
        example="optout",
        invoke_without_command=True
    )
    async def data(self: "Servers", ctx: Context):
        """
        Manage your Data Collection & Privacy settings
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @data.command(
        name="request",
        aliases=("export",)
    )
    async def data_request(self: "Servers", ctx: Context):
        """
        Get a copy of all your data
        """
        return await ctx.respond(
            "Contact us @ `support@vileb.org` with the subject `Data Request`. (case-sensitive)",
            content="**NOTE:** Requesting your data can take **up to 24 hours** to process!",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @Group(
        name="boosterrole",
        aliases=("br",),
        usage="<color> <name>",
        example="#b1aad8 flawless",
        extras={
            "permissions": "Booster"
        },
        invoke_without_command=True
    )
    @bot_has_permissions(manage_roles=True)
    async def boosterrole(
        self: "Servers", 
        ctx: Context, 
        color: Color, 
        *, 
        name: str
    ):
        """
        Get your own custom booster color role
        """
        
        if ctx.guild.premium_subscriber_role not in ctx.author.roles:
            raise CommandError("You must be a **booster** to create a **booster role**.")
            
        if ctx.author.id in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            if ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id]) is not None:
                raise CommandError("You **already** have a **booster role**.")
            
        if len(name) > 100:
            raise CommandError("Please provide a **valid** name under 100 characters.")
            
        if len(ctx.guild.roles) == 250:
            raise CommandError("This server exceeds the **role limit**.")
        
        role = await ctx.guild.create_role(
            name=name,
            color=color,
            reason=f"{self.bot.user.name.title()} Booster Roles [{ctx.author}]"
        )
        
        if (base_role := ctx.guild.get_role(self.bot.cache.booster_base.get(ctx.guild.id, 0))) is not None:
            await role.edit(position=base_role.position-1)

        try:
            await ctx.author.add_roles(
                role, 
                reason=f"{self.bot.user.name.title()} Booster Roles [{ctx.author}]"
            )

        except Forbidden:
            await role.delete(reason="Failed to assign role; missing required permissions")
            raise CommandError("I couldn't assign the role; I'm missing required permissions.")
            
        await self.bot.db.execute(
            "INSERT INTO booster_role (guild_id, user_id, role_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);",
            ctx.guild.id, ctx.author.id, role.id
        )
        
        if ctx.guild.id not in self.bot.cache.booster_role:
            self.bot.cache.booster_role[ctx.guild.id] = { }
            
        self.bot.cache.booster_role[ctx.guild.id][ctx.author.id] = role.id
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
    @has_permissions(manage_guild=True)
    async def boosterrole_base(self: "Servers", ctx: Context, *, role: Role):
        """
        Set the base role that booster roles will be under
        """
        
        if role.id == self.bot.cache.booster_base.get(ctx.guild.id, 0):
            raise CommandError("That is **already** the **base booster role**.")
            
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
    @bot_has_permissions(manage_roles=True)
    async def boosterrole_remove(self: "Servers", ctx: Context):
        """
        Remove your custom booster role
        """
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            raise CommandError("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            raise CommandError("You **don't have** a **booster role**.")
                
        await self.bot.db.execute(
            "DELETE FROM booster_role WHERE guild_id = %s AND user_id = %s;",
            ctx.guild.id, ctx.author.id
        )
        del self.bot.cache.booster_role[ctx.guild.id][ctx.author.id]
        await role.delete(reason=f"{self.bot.user.name.title()} Booster Roles [{ctx.author}]")
        return await ctx.success("Successfully **removed** your **booster role**.")
        
        
    @boosterrole.command(
        name="color",
        usage="<color>",
        example="#b1aad8",
        extras={
            "permissions": "Booster"
        }
    )
    @bot_has_permissions(manage_roles=True)
    async def boosterrole_color(self: "Servers", ctx: Context, color: Color):
        """
        Set your booster role's color
        """
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            raise CommandError("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            raise CommandError("You **don't have** a **booster role**.")
            
        await role.edit(
            color=color,
            reason=f"{self.bot.user.name.title()} Booster Roles [{ctx.author}]"
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
    @bot_has_permissions(manage_roles=True)
    async def boosterrole_icon(self: "Servers", ctx: Context, url: str):
        """
        Set an icon for your booster role
        """
            
        if ctx.guild.premium_tier < 2:
            raise CommandError("This server needs more **boosts** to perform that action.")
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            raise CommandError("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            raise CommandError("You **don't have** a **booster role**.")
            
        try:
            BytesIO(image := await self.bot.proxied_session.read(url))
            
        except Exception:
            raise CommandError("Please provide a **valid** image URL.")
            
        await role.edit(
            display_icon=image,
            reason=f"{self.bot.user.name.title()} Booster Roles [{ctx.author}]"
        )
        return await ctx.success(f"Successfully **set** your [**booster role's icon**]({url}).")
        
        
    @boosterrole.group(
        name="award",
        usage="<role>",
        example="@Supporter",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def boosterrole_award(self: "Servers", ctx: Context, role: Role):
        """
        Reward members a specific role upon boosting
        """
        
        if role.id == self.bot.cache.booster_award.get(ctx.guild.id, 0):
            raise CommandError("That is **already** the **booster reward role**.")
        
        if ctx.is_dangerous(role):
            raise CommandError("That role has **dangerous** permissions.")
        
        await self.bot.db.execute(
            "INSERT INTO booster_role_award (guild_id, role_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);",
            ctx.guild.id, role.id
        )
        self.bot.cache.booster_award[ctx.guild.id] = role.id
        return await ctx.success(f"Successfully **binded** {role.mention} as the **booster reward role**.")
        
        
    @boosterrole_award.command(name="reset")
    @has_permissions(manage_guild=True)
    async def boosterrole_award_reset(self: "Servers", ctx: Context):
        """
        Remove the booster reward role
        """
        
        if ctx.guild.id not in self.bot.cache.booster_award:
            raise CommandError("There is no **booster award role** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM booster_role_award WHERE guild_id = %s;",
            ctx.guild.id
        )

        del self.bot.cache.booster_award[ctx.guild.id]
        return await ctx.success("Successfully **reset** the **booster reward role**.")
        
        
    @boosterrole_award.command(
        name="view"
    )
    @has_permissions(manage_guild=True)
    async def boosterrole_award_view(self: "Servers", ctx: Context):
        """
        View the booster reward role
        """
        
        if (role := ctx.guild.get_role(self.bot.cache.booster_award.get(ctx.guild.id, 0))) is None:
            raise CommandError("There is no **booster award role** in this server.")
            
        return await ctx.success(f"{role.mention} **{role.name}** ( `{role.id}` )")
        
        
    @boosterrole.command(
        name="random",
        extras={
            "permissions": "Booster"
        }
    )
    @bot_has_permissions(manage_roles=True)
    async def boosterrole_random(self: "Servers", ctx: Context):
        """
        Set your booster role's color to a random hex
        """
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            raise CommandError("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            raise CommandError("You **don't have** a **booster role**.")

        await role.edit(
            color=(color := Color.random()),
            reason=f"{self.bot.user.name.title()} Booster Roles [{ctx.author}]"
        )
        return await ctx.success(f"Successfully **set** your **booster role's color** to **#{hex(color.value)[2:]}**.")
        
        
    @boosterrole.command(
        name="rename",
        aliases=("name",),
        usage="<name>",
        example="terrible bot",
        extras={
            "permissions": "Booster"
        }
    )
    @bot_has_permissions(manage_roles=True)
    async def boosterrole_rename(self: "Servers", ctx: Context, *, name: str):
        """
        Rename your booster role
        """
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            raise CommandError("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            raise CommandError("You **don't have** a **booster role**.")
            
        if len(name) > 100:
            raise CommandError("Please provide a **valid** name under 100 characters.") 
            
        await role.edit(
            name=name,
            reason=f"{self.bot.user.name.title()} Booster Roles [{ctx.author}]"
        )
        return await ctx.success(f"Successfully **renamed** your **booster role**.")
        
        
    @boosterrole.command(
        name="dominant",
        extras={
            "permissions": "Booster"
        }
    )
    @bot_has_permissions(manage_roles=True)
    async def boosterrole_dominant(self: "Servers", ctx: Context):
        """
        Set your booster role's color to your avatar's color
        """
        
        if ctx.author.id not in self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            raise CommandError("You **don't have** a **booster role**.")
            
        if (role := ctx.guild.get_role(self.bot.cache.booster_role[ctx.guild.id][ctx.author.id])) is None:
            raise CommandError("You **don't have** a **booster role**.")
            
        await role.edit(
            color=(color := await dominant_color(ctx.author.display_avatar)),
            reason=f"{self.bot.user.name.title()} Booster Roles [{ctx.author}]"
        )
        return await ctx.success(f"Successfully **set** your **booster role's color** to **#{hex(color)[2:]}**.")
        
        
    @boosterrole.command(
        name="list",
        aliases=("view", "show"),
        extras={
            "permissions": "Booster"
        }
    )
    @has_permissions(manage_guild=True)
    async def boosterrole_list(self: "Servers", ctx: Context):
        """
        View every booster role
        """
        
        if not self.bot.cache.booster_role.get(ctx.guild.id, DICT):
            raise CommandError("There are no **booster roles** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Booster Roles in '{ctx.guild.name}'"
        )
        for role_id in self.bot.cache.booster_role[ctx.guild.id].values():
            if (role := ctx.guild.get_role(role_id)) is not None:
                rows.append(f"{role.mention}: **{role.name}** ( `{role.id}` )")
                
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="stickymessage",
        aliases=("sm",),
        usage="<sub command>",
        example="add #selfie {content: trolling = ban}",
        invoke_without_command=True
    )
    @has_permissions(manage_channels=True)
    async def stickymessage(self: "Servers", ctx: Context):
        """
        Set up a sticky message in one or multiple channels
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @stickymessage.command(
        name="toggle",
        usage="[channel] <state>",
        example="#selfie true"
    )
    async def stickymessage_toggle(self: "Servers", ctx: Context, channel: Optional[TextChannel], state: bool):
        """
        Toggle the sticky message in a channel
        """
        
        channel = channel or ctx.channel

        if not (settings := self.bot.cache.get(f"data:sticky_message_settings:{ctx.guild.id}:{channel.id}")):
            raise CommandError("There isn't a **sticky message** in that channel.")
            
        if state == settings.is_enabled:
            raise CommandError("That is already the **current state**.")
            
        await self.bot.db.execute(
            "UPDATE sticky_message_settings SET is_enabled = %s WHERE channel_id = %s;",
            state, channel.id
        )

        self.bot.cache.set(
            f"data:sticky_message_settings:{ctx.guild.id}:{channel.id}", Munch(
                is_enabled=state,
                message=settings.message
            )
        )

        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** {channel.mention}'s **sticky message**.")
        
        
    
    @stickymessage.command(
        name="add",
        usage="[channel] <message>",
        example="#selfie {content: trolling = ban}"
    )
    async def stickymessage_add(self: "Servers", ctx: Context, channel: Optional[TextChannel], *, message: str):
        """
        Add a sticky message to a channel
        """
        
        channel = channel or ctx.channel

        if (settings := self.bot.cache.get(f"data:sticky_message_settings:{ctx.guild.id}:{channel.id}")) and message == settings.message:
            raise CommandError("That is already the **sticky message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO sticky_message_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        
        self.bot.cache.set(
            f"data:sticky_message_settings:{ctx.guild.id}:{channel.id}", Munch(
                is_enabled=1,
                message=message
            )
        )
            
        return await ctx.success(f"Successfully **binded** {channel.mention}'s **sticky message** to \n```{message}```")
        
        
    @stickymessage.command(
        name="remove",
        usage="[channel]",
        example="#selfie"
    )
    async def stickymessage_remove(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        Remove a sticky message from a channel
        """
        
        channel = channel or ctx.channel

        if not self.bot.cache.get(f"data:sticky_message_settings:{ctx.guild.id}:{channel.id}"):
            raise CommandError("There isn't a **sticky message** in that channel.")
            
        await self.bot.db.execute(
            "DELETE FROM sticky_message_settings WHERE channel_id = %s;",
            channel.id
        )
        
        self.bot.cache.delete(f"data:sticky_message_settings:{ctx.guild.id}:{channel.id}")
        return await ctx.success(f"Successfully **removed** {channel.mention}'s **sticky message**.")
        
    
    @stickymessage.command(
        name="view",
        usage="[channel]",
        example="#selfie"
    )
    async def stickymessage_view(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        View a channel's sticky message
        """
        
        channel = channel or ctx.channel
        if not (settings := self.bot.cache.get(f"data:sticky_message_settings:{ctx.guild.id}:{channel.id}")):
            raise CommandError("There isn't a **sticky message** in that channel.")

        return await EmbedScript(settings.message).send(
            ctx,
            guild=ctx.guild
        )
        
        
    @stickymessage.command(name="clear")
    async def stickymessage_clear(self: "Servers", ctx: Context):
        """
        Clear every sticky message in this server
        """
        
        if not self.bot.cache.keys(pattern=f"data:sticky_message_settings:{ctx.guild.id}:*"):
            raise CommandError("There aren't any **sticky messages** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM sticky_message_settings WHERE guild_id = %s;",
            ctx.guild.id
        )
       
        self.bot.cache.delete(pattern=f"data:sticky_message_settings:{ctx.guild.id}:*")
        return await ctx.success("Successfully **cleared** every **sticky message**.")
        
        
    @stickymessage.command(
        name="variables",
        aliases=("variable", "vars")
    )
    async def stickymessage_variables(self: "Servers", ctx: Context):
        """
        View the available sticky message variables
        """

        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @stickymessage.command(
        name="list",
        aliases=("show",)
    )
    @has_permissions(manage_guild=True)
    async def stickymessage_list(self: "Servers", ctx: Context):
        """
        View every sticky message
        """
        
        if not self.bot.cache.keys(pattern=f"data:sticky_message_settings:{ctx.guild.id}:*"):
            raise CommandError("There aren't any **sticky messages** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Sticky Messages in '{ctx.guild.name}'"
        )

        for channel_id in tuple(
            record.split(":")[::-1][0]
            for record in self.bot.cache.keys(pattern=f"data:sticky_message_settings:{ctx.guild.id}:*")
        ):
            if channel := self.bot.get_channel(channel_id):
                settings = self.bot.cache.get(f"data:sticky_message_settings:{ctx.guild.id}:{channel.id}")

                message = settings.message.replace("`", "\`")
                state = settings.is_enabled and "enabled" or "disabled"

                rows.append(f"{channel.mention}\n{self.bot.reply} **State:** {state}\n{self.bot.reply} **Message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="boost",
        aliases=("bst", "boostmessage",),
        usage="<sub command>",
        example="add #boosts {content: {user.mention} thanks :3}",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def boost(self: "Servers", ctx: Context):
        """
        Set up a boost message in one or multiple channels
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @boost.command(
        name="toggle",
        usage="[channel] <state>",
        example="#boosts true"
    )
    async def boost_toggle(self: "Servers", ctx: Context, channel: Optional[TextChannel], state: bool):
        """
        Toggle the boost message in a channel
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.boost_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** a **boost message** in that channel.")
    
        if state == self.bot.cache.boost_settings[ctx.guild.id][channel.id]["is_enabled"]:
            raise CommandError("That is **already** the **current state**.")
            
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
    async def boost_add(self: "Servers", ctx: Context, channel: Optional[TextChannel], *, message: str):
        """
        Add a boost message to a channel
        """
        
        channel = channel or ctx.channel
        if channel.id in self.bot.cache.boost_settings.get(ctx.guild.id, DICT) and message == self.bot.cache.boost_settings[ctx.guild.id][channel.id]["message"]:
            raise CommandError("That is **already** the **boost message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO boost_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        if ctx.guild.id not in self.bot.cache.boost_settings:
            self.bot.cache.boost_settings[ctx.guild.id] = { }
            
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
    async def boost_remove(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        Remove a boost message from a channel
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.boost_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** a **boost message** in that channel.")
            
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
    async def boost_view(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        View a channel's boost message
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.boost_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** a **boost message** in that channel.")
            
        script = EmbedScript(self.bot.cache.boost_settings[ctx.guild.id][channel.id]["message"])
        return await script.send(
            ctx,
            guild=ctx.guild,
            user=ctx.author
        )
        
        
    @boost.command(name="clear")
    async def boost_clear(self: "Servers", ctx: Context):
        """
        Clear every boost message in this server
        """
        
        if ctx.guild.id not in self.bot.cache.boost_settings:
            raise CommandError("There **aren't** any **boost messages** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM boost_settings WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.boost_settings[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **boost message**.")
        
        
    @boost.command(
        name="variables",
        aliases=("variable", "vars")
    )
    async def boost_variables(self: "Servers", ctx: Context):
        """
        View the available boost message variables
        """
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @boost.command(
        name="list",
        aliases=("show",)
    )
    @has_permissions(manage_guild=True)
    async def boost_list(self: "Servers", ctx: Context):
        """
        View every boost message
        """
        
        if not self.bot.cache.boost_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **aren't** any **boost messages** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Boost Messages in '{ctx.guild.name}'"
        )
        for channel_id, config in self.bot.cache.boost_settings[ctx.guild.id].items():
            if (channel := self.bot.get_channel(channel_id)) is not None:
                message = config["message"].replace("`", "\`")
                state = "enabled" if config["is_enabled"] else "disabled"
                rows.append(f"{channel.mention}\n{self.bot.reply} **state:** {state}\n{self.bot.reply} **message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="unboost",
        aliases=("unbst", "jnboostmessage",),
        usage="<sub command>",
        example="add #boosts {content: {user.mention} unboosted :(}",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def unboost(self: "Servers", ctx: Context):
        """
        Set up an unboost message in one or multiple channels
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @unboost.command(
        name="toggle",
        usage="[channel] <state>",
        example="#boosts true"
    )
    async def unboost_toggle(self: "Servers", ctx: Context, channel: Optional[TextChannel], state: bool):
        """
        Toggle the unboost message in a channel
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.unboost_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** an **unboost message** in that channel.")
            
        if state == self.bot.cache.unboost_settings[ctx.guild.id][channel.id]["is_enabled"]:
            raise CommandError("That is **already** the **current state**.")
            
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
    async def unboost_add(self: "Servers", ctx: Context, channel: Optional[TextChannel], *, message: str):
        """
        Add an unboost message to a channel
        """
        
        channel = channel or ctx.channel
        if channel.id in self.bot.cache.unboost_settings.get(ctx.guild.id, DICT) and message == self.bot.cache.boost_settings[ctx.guild.id][channel.id]["message"]:
            raise CommandError("That is **already** the **unboost message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO unboost_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        if ctx.guild.id not in self.bot.cache.unboost_settings:
            self.bot.cache.unboost_settings[ctx.guild.id] = { }
            
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
    async def unboost_remove(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        Remove an unboost message from a channel
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.unboost_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** an **unboost message** in that channel.")
            
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
    async def unboost_view(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        View a channel's unboost message
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.unboost_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** an **unboost message** in that channel.")
            
        script = EmbedScript(self.bot.cache.unboost_settings[ctx.guild.id][channel.id]["message"])
        return await script.send(
            ctx,
            guild=ctx.guild,
            user=ctx.author
        )
        
        
    @unboost.command(
        name="clear"
    )
    async def unboost_clear(self: "Servers", ctx: Context):
        """
        Clear every unboost message in this server
        """
        
        if ctx.guild.id not in self.bot.cache.unboost_settings:
            raise CommandError("There **aren't** any **unboost messages** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM unboost_settings WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.unboost_settings[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **unboost message**.")
        
        
    @unboost.command(
        name="variables",
        aliases=("variable", "vars")
    )
    async def unboost_variables(self: "Servers", ctx: Context):
        """
        View the available unboost message variables
        """
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @unboost.command(
        name="list",
        aliases=("show",)
    )
    @has_permissions(manage_guild=True)
    async def unboost_list(self: "Servers", ctx: Context):
        """
        View every unboost message
        """
        
        if not self.bot.cache.unboost_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **aren't** any **unboost messages** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Unboost Messages in '{ctx.guild.name}'"
        )
        for channel_id, config in self.bot.cache.unboost_settings[ctx.guild.id].items():
            if (channel := self.bot.get_channel(channel_id)) is not None:
                message = config["message"].replace("`", "\`")
                state = "enabled" if config["is_enabled"] else "disabled"
                rows.append(f"{channel.mention}\n{self.bot.reply} **state:** {state}\n{self.bot.reply} **message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="welcome",
        aliases=("wlc", "welcomemessage",),
        usage="<sub command>",
        example="add #welcome {content: {user.mention} welcome :3}",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def welcome(self: "Servers", ctx: Context):
        """
        Set up a welcome message in one or multiple channels
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @welcome.command(
        name="toggle",
        usage="[channel] <state>",
        example="#boosts true"
    )
    async def welcome_toggle(self: "Servers", ctx: Context, channel: Optional[TextChannel], state: bool):
        """
        Toggle the welcome message in a channel
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.welcome_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** a **welcome message** in that channel.")
            
        if state == self.bot.cache.welcome_settings[ctx.guild.id][channel.id]["is_enabled"]:
            raise CommandError("That is **already** the **current state**.")
            
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
    async def welcome_add(self: "Servers", ctx: Context, channel: Optional[TextChannel], *, message: str):
        """
        Add a welcome message to a channel
        """
        
        channel = channel or ctx.channel
        if channel.id in self.bot.cache.welcome_settings.get(ctx.guild.id, DICT) and message == self.bot.cache.welcome_settings[ctx.guild.id][channel.id]["message"]:
            raise CommandError("That is **already** the **welcome message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO welcome_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        if ctx.guild.id not in self.bot.cache.welcome_settings:
            self.bot.cache.welcome_settings[ctx.guild.id] = { }
            
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
    async def welcome_remove(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        Remove a welcome message from a channel
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.welcome_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** a **welcome message** in that channel.")
            
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
    async def welcome_view(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        View a channel's welcome message
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.welcome_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** a **welcome message** in that channel.")
            
        script = EmbedScript(self.bot.cache.welcome_settings[ctx.guild.id][channel.id]["message"])
        return await script.send(
            ctx,
            guild=ctx.guild,
            user=ctx.author
        )
        
        
    @welcome.command(
        name="clear"
    )
    async def welcome_clear(self: "Servers", ctx: Context):
        """
        Clear every welcome message in this server
        """
        
        if ctx.guild.id not in self.bot.cache.welcome_settings:
            raise CommandError("There **aren't** any **welcome messages** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM welcome_settings WHERE guild_id = %s;",
            ctx.guild.id
        )
        del self.bot.cache.welcome_settings[ctx.guild.id]
            
        return await ctx.success("Successfully **cleared** every **welcome message**.")
        
        
    @welcome.command(
        name="variables",
        aliases=("variable", "vars")
    )
    async def welcome_variables(self: "Servers", ctx: Context):
        """
        View the available welcome message variables
        """
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @welcome.command(
        name="list",
        aliases=("show",)
    )
    @has_permissions(manage_guild=True)
    async def welcome_list(self: "Servers", ctx: Context):
        """
        View every welcome message
        """
        
        if not self.bot.cache.welcome_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **aren't** any **welcome messages** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Welcome Messages in '{ctx.guild.name}'"
        )
        for channel_id, config in self.bot.cache.welcome_settings[ctx.guild.id].items():
            if (channel := self.bot.get_channel(channel_id)) is not None:
                message = config["message"].replace("`", "\`")
                state = "enabled" if config["is_enabled"] else "disabled"
                rows.append(f"{channel.mention}\n{self.bot.reply} **state:** {state}\n{self.bot.reply} **message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="leave",
        aliases=("bye", "leavemessage",),
        usage="<sub command>",
        example="add #leave {content: {user.mention} left :()}",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def leave(self: "Servers", ctx: Context):
        """
        Set up a leave message in one or multiple channels
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @leave.command(
        name="toggle",
        usage="[channel] <state>",
        example="#boosts true"
    )
    async def leave_toggle(self: "Servers", ctx: Context, channel: Optional[TextChannel], state: bool):
        """
        Toggle the leave message in a channel
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.leave_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** a **leave message** in that channel.")
            
        if state == self.bot.cache.leave_settings[ctx.guild.id][channel.id]["is_enabled"]:
            raise CommandError("That is **already** the **current state**.")
            
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
    async def leave_add(self: "Servers", ctx: Context, channel: Optional[TextChannel], *, message: str):
        """
        Add a leave message to a channel
        """
        
        channel = channel or ctx.channel
        if channel.id in self.bot.cache.leave_settings.get(ctx.guild.id, DICT) and message == self.bot.cache.leave_settings[ctx.guild.id][channel.id]["message"]:
            raise CommandError("That is **already** the **leave message** for that channel.")
            
        await self.bot.db.execute(
            "INSERT INTO leave_settings (guild_id, channel_id, is_enabled, message) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, channel.id, 1, message
        )
        if ctx.guild.id not in self.bot.cache.leave_settings:
            self.bot.cache.leave_settings[ctx.guild.id] = { }
            
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
    async def leave_remove(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        Remove a leave message from a channel
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.leave_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** a **leave message** in that channel.")
            
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
    async def leave_view(self: "Servers", ctx: Context, channel: Optional[TextChannel]):
        """
        View a channel's leave message
        """
        
        channel = channel or ctx.channel
        if channel.id not in self.bot.cache.leave_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **isn't** a **leave message** in that channel.")
            
        script = EmbedScript(self.bot.cache.leave_settings[ctx.guild.id][channel.id]["message"])
        return await script.send(
            ctx,
            guild=ctx.guild,
            user=ctx.author
        )
        
        
    @leave.command(
        name="clear"
    )
    async def leave_clear(self: "Servers", ctx: Context):
        """
        Clear every leave message in this server
        """
        
        if ctx.guild.id not in self.bot.cache.leave_settings:
            raise CommandError("There **aren't** any **leave messages** in this server.")
            
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
    async def leave_variables(self: "Servers", ctx: Context):
        """
        View the available leave message variables
        """
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @leave.command(
        name="list",
        aliases=("show",)
    )
    @has_permissions(manage_guild=True)
    async def leave_list(self: "Servers", ctx: Context):
        """
        View every leave message
        """
        
        if not self.bot.cache.leave_settings.get(ctx.guild.id, DICT):
            raise CommandError("There **aren't** any **leave messages** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"leave Messages in '{ctx.guild.name}'"
        )
        for channel_id, config in self.bot.cache.leave_settings[ctx.guild.id].items():
            if (channel := self.bot.get_channel(channel_id)) is not None:
                message = config["message"].replace("`", "\`")
                state = "enabled" if config["is_enabled"] else "disabled"
                rows.append(f"{channel.mention}\n{self.bot.reply} **state:** {state}\n{self.bot.reply} **message:** {message}")
                
        return await ctx.paginate((embed, rows))
        
    
    @Command(
        name="invoke",
        usage="<command> <message>",
        example="ban {content: {user.mention} got :poop: on by {moderator}}"
    )
    @has_permissions(manage_guild=True)
    async def invoke(self: "Servers", ctx: Context, command: str, *, message: str):
        """
        Set a custom invoke message for moderation commands
        """
        
        if (command := self.bot.get_command(command)) is None or command.cog_name != "Moderation":
            raise CommandError("Please provide a **valid** moderation command.")
            
        if message == await self.bot.db.fetchval("SELECT message FROM invoke_message WHERE guild_id = %s AND command_name = %s;", ctx.guild.id, command.qualified_name):
            raise CommandError("That is **already** the **invoke message** for that command.")
            
        await self.bot.db.execute(
            "INSERT INTO invoke_message (guild_id, command_name, message) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE message = VALUES(message);",
            ctx.guild.id, command.qualified_name, message
        )
        return await ctx.success(f"Successfully **binded** `{command.qualified_name}`'s invoke message to \n```{message}```")
        
        
    @Group(
        name0="alias",
        aliases=("aliases",),
        usage="<sub command>",
        example="add ban pack",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def alias(self: "Servers", ctx: Context):
        """
        Add an alias to a command
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
    
    @alias.command(
        name="add",
        usage="<command> <alias>",
        example="ban pack"
    )
    async def alias_add(self: "Servers", ctx: Context, command: str, alias: str):
        """
        Add an alias to a command
        """
        
        if (command := self.bot.get_command(command)) is None:
            raise CommandError("Please provide a **valid** command.")
         
        if self.bot.cache.keys(pattern=f"data:aliases:{ctx.guild.id}:*") and alias in self.bot.cache.smembers(f"data:aliases:{ctx.guild.id}:{command.qualified_name}"):
            raise CommandError("That is already an **alias** for that command.")
           
        await self.bot.db.execute(
            "INSERT INTO aliases (guild_id, command_name, alias) VALUES (%s, %s, %s);",
            ctx.guild.id, command.qualified_name, alias
        )

        self.bot.cache.sadd(
            f"data:aliases:{ctx.guild.id}:{command.qualified_name}",
            alias
        )

        return await ctx.success(f"Successfully **added** the **alias** `{command.qualified_name} / {alias}`")
        
        
    @alias.command(
        name="remove",
        usage="<command> <alias>",
        example="ban pack"
    )
    async def alias_remove(self: "Servers", ctx: Context, command: str, alias: str):
        """
        Remove an alias from a command
        """
        
        if (command := self.bot.get_command(command)) is None:
            raise CommandError("Please provide a **valid** command.")
         
        if not self.bot.cache.keys(pattern=f"data:aliases:{ctx.guild.id}:*"):
            raise CommandError("There aren't any **aliases** in this server.")
            
        if alias not in self.bot.cache.smembers(f"data:aliases:{ctx.guild.id}:{command.qualified_name}"):
            raise CommandError("Please provide a **valid** alias for that command.")
           
        await self.bot.db.execute(
            "DELETE FROM aliases WHERE guild_id = %s AND command_name = %s AND alias = %s;",
            ctx.guild.id, command.qualified_name, alias
        )
        
        self.bot.cache.srem(
            f"data:aliases:{ctx.guild.id}:{command.qualified_name}",
            alias
        )

        return await ctx.success(f"Successfully **removed** the **alias** `{command.qualified_name} / {alias}`")
        
        
    @alias.command(
        name="clear"
    )
    @has_permissions(manage_guild=True)
    async def alias_clear(self: "Servers", ctx: Context):
        """
        Clear every alias in this server
        """
        
        if not self.bot.cache.keys(pattern=f"data:aliases:{ctx.guild.id}:*"):
            raise CommandError("There aren't any **aliases** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM aliases WHERE guild_id = %s;",
            ctx.guild.id
        )

        for command in tuple(
            record.split(":")[::-1][0]
            for record in self.bot.cache.keys(pattern=f"data:aliases:{ctx.guild.id}:*")
        ):
            await sleep(1e-3)
            self.bot.cache.srem(
                f"data:aliases:{ctx.guild.id}:{command}",
                *self.bot.cache.smembers(f"data:aliases:{ctx.guild.id}:{command}")
            )
        
        return await ctx.success("Successfully **cleared** every **alias**.")

        
    @alias.command(
        name="list",
        aliases=("view", "show")
    )
    @has_permissions(manage_guild=True)
    async def alias_list(self: "Servers", ctx: Context):
        """
        View every command alias
        """
        
        if not self.bot.cache.keys(pattern=f"data:aliases:{ctx.guild.id}:*"):
            raise CommandError("There **aren't** any **aliases** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Command Aliases in '{ctx.guild.name}'"
        )
        
        commands = tuple(
            record.split(":")[::-1][0]
            for record in self.bot.cache.keys(pattern=f"data:aliases:{ctx.guild.id}:*")
        )

        for command in commands:
            if aliases := self.bot.cache.smembers(f"data:aliases:{ctx.guild.id}:{command}"):
                rows.append(f"{command} **—** {', '.join(aliases)}")
                
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="filter",
        aliases=("chatfilter", "cf",),
        usage="<sub command>",
        example="exempt @trey#0006",
        invoke_without_command=True
    )
    @has_permissions(manage_channels=True)
    async def _filter(self: "Servers", ctx: Context):
        """
        View a variety of options to help clean the chat
        """

        return await ctx.send_help(ctx.command.qualified_name)
        

    @_filter.command(
        name="clear"
    )
    async def filter_clear(self: "Servers", ctx: Context):
        """
        Clear every filtered word in this server
        """
        
        if not self.bot.cache.get(f"data:filter:{ctx.guild.id}"):
            raise CommandError("There aren't any **filtered words** in this server.")
            
        await self.bot.db.execute(
            "DELETE FROM filter WHERE guild_id = %s;",
            ctx.guild.id
        )

        self.bot.cache.srem(
            f"data:filter:{ctx.guild.id}",
            *self.bot.cache.smembers(f"data:filter:{ctx.guild.id}")
        )

        return await ctx.success("Successfully **cleared** every **filtered word**.")
        
        
    @_filter.command(
        name="add",
        aliases=("create",),
        usage="<keyword>",
        example="nig"
    )
    @has_permissions(manage_channels=True)
    async def filter_add(self: "Servers", ctx: Context, keyword: str):
        """
        Add a filtered word
        """
        
        if keyword in self.bot.cache.smembers(f"data:filter:{ctx.guild.id}"):
            raise CommandError("That is already a **filtered word**.")
            
        if len(keyword.split()) > 1:
            raise CommandError("The keyword must be **one word**.")
            
        if len(keyword) > 32:
            raise CommandError("Please provide a **valid** keyword under **32 characters**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter (guild_id, keyword) VALUES (%s, %s);",
            ctx.guild.id, keyword
        )

        self.bot.cache.sadd(
            f"data:filter:{ctx.guild.id}",
            keyword
        )

        return await ctx.success(f"Successfully **added** the filtered keyword \n```{keyword}```")
        
        
    @_filter.command(
        name="list",
        aliases=("view", "show")
    )
    @has_permissions(manage_guild=True)
    async def filter_list(self: "Servers", ctx: Context):
        """
        View every filtered word
        """
        
        if not self.bot.cache.get(f"data:filter:{ctx.guild.id}"):
            raise CommandError("There aren't any **filtered words** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Filtered Words in '{ctx.guild.name}'"
        )

        for keyword in self.bot.cache.smembers(f"data:filter:{ctx.guild.id}"):
            rows.append(keyword)
                
        return await ctx.paginate((embed, rows))
        
        
        
    @_filter.command(
        name="whitelist",
        aliases=("exempt", "ignore",),
        usage="<member or channel or role>",
        example="#nsfw"
    )
    @has_permissions(manage_channels=True)
    async def filter_whitelist(
        self: "Servers", 
        ctx: Context, 
        *, 
        source: Union[ Member, TextChannel, Role ]
    ):
        """
        Exempt roles from the word filter
        """
        
        if isinstance(source, Member):
            if await ctx.can_moderate(source, "whitelist") is not None:
                return
                
        if source.id in self.bot.cache.smembers(f"data:filter_whitelist:{ctx.guild.id}"):
            await self.bot.db.execute(
                "DELETE FROM filter_whitelist WHERE guild_id = %s AND user_id = %s;",
                source.id
            )

            self.bot.cache.srem(
                f"data:filter_whitelist:{ctx.guild.id}",
                source.id
            )

            return await ctx.success(f"Successfully **unwhitelisted** {source.mention}.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_whitelist (guild_id, user_id) VALUES (%s, %s);",
            ctx.guild.id, source.id
        )

        self.bot.cache.sadd(
            f"data:filter_whitelist:{ctx.guild.id}",
            source.id
        )

        return await ctx.success(f"Successfully **whitelisted** {source.mention}.")
        
        
    @_filter.command(
        name="whitelisted"
    )
    @has_permissions(manage_guild=True)
    async def filter_whitelisted(self: "Servers", ctx: Context):
        """
        View every whitelisted member
        """
        
        if not self.bot.cache.get(f"data:filter_whitelist:{ctx.guild.id}"):
            raise CommandError("There aren't any **whitelisted members** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Whitelisted Members in '{ctx.guild.name}'"
        )

        for source_id in self.bot.cache.smembers(f"data:filter_whitelist:{ctx.guild.id}"):
            if (source := ctx.guild.get_member(source_id) or ctx.guild.get_channel(source_id) or ctx.guild.get_role(source_id)) is not None:
                rows.append(f"{source.mention} {source.name} (`{source.id}`)")
                
        return await ctx.paginate((embed, rows))
        
        
    @_filter.command(
        name="nicknames",
        aliases=("nick", "nicks",),
        usage="<state>",
        example="true"
    )
    @has_permissions(manage_channels=True)
    async def filter_nicknames(self: "Servers", ctx: Context, state: bool):
        """
        Automatically reset nicknames if a filtered word is detected
        """
            
        if state == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:nicknames", DICT).get("is_enabled", 0):
            raise CommandError("That is already the **current state**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled);",
            ctx.guild.id, "nicknames", state
        )
            
        self.bot.cache.set(f"data:filter_event:{ctx.guild.id}:nicknames", Munch(
            is_enabled=state,
            threshold=0
        ))
        
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
    @has_permissions(manage_channels=True)
    async def filter_spoilers(self: "Servers", ctx: Context, state: bool):
        """
        Delete any message exceeding the threshold for spoilers
        """
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:spoilers", DICT).get("threshold", 2)
            
        if state == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:spoilers", DICT).get("is_enabled") and threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:spoilers", DICT).get("threshold"):
            raise CommandError("That is already the **current state**.")
            
        if state:
            if threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:spoilers", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                raise CommandError("That is **already** the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                raise CommandError("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "spoilers", state, threshold
        )

        self.bot.cache.set(f"data:filter_event:{ctx.guild.id}:spoilers", Munch(
            is_enabled=state,
            threshold=threshold
        ))
        
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **spoiler filter**{f' (with threshold: {threshold})' if state else '.'}")
        
        
    @_filter.command(
        name="links",
        aliases=("urls",),
        usage="<state>",
        example="true"
    )
    @has_permissions(manage_channels=True)
    async def filter_links(self: "Servers", ctx: Context, state: bool):
        """
        Delete any message that contains a link
        """
            
        if state == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:links", DICT).get("is_enabled"):
            raise CommandError("That is already the **current state**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled);",
            ctx.guild.id, "links", state
        )

        self.bot.cache.set(f"data:filter_event:{ctx.guild.id}:links", Munch(
            is_enabled=state,
            threshold=0
        ))
        
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
    @has_permissions(manage_channels=True)
    async def filter_spam(self: "Servers", ctx: Context, state: bool):
        """
        Delete messages from users that send messages too fast
        """
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:spam", DICT).get("threshold", 5)
            
        if state == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:links", DICT).get("is_enabled") and threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:spam", DICT).get("threshold"):
            raise CommandError("That is already the **current state**.")
            
        if state:
            if threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:spam", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                raise CommandError("That is already the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                raise CommandError("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "spam", state, threshold
        )

        self.bot.cache.set(f"data:filter_event:{ctx.guild.id}:spam", Munch(
            is_enabled=state,
            threshold=threshold
        ))

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
    @has_permissions(manage_channels=True)
    async def filter_emojis(self: "Servers", ctx: Context, state: bool):
        """
        Delete any messages exceeding the threshold for emojis
        """
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:emojis", DICT).get("threshold", 5)
            
        if state == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:emojis", DICT).get("is_enabled") and threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:emojis", DICT).get("threshold"):
            raise CommandError("That is already the **current state**.")
            
        if state:
            if threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:emojis", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                raise CommandError("That is already the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                raise CommandError("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "emojis", state, threshold
        )

        self.bot.cache.set(f"data:filter_event:{ctx.guild.id}:emojis", Munch(
            is_enabled=state,
            threshold=threshold
        ))

        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **emoji filter**{f' (with threshold: {threshold})' if state else '.'}")
              
            
    @_filter.command(
        name="invites",
        aliases=("invs",),
        usage="<state> <flags --threshold>",
        example="true"
    )
    @has_permissions(manage_channels=True)
    async def filter_invites(self: "Servers", ctx: Context, state: bool):
        """
        Delete any messages exceeding the threshold for emojis
        """
            
        if state == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:invites", DICT).get("is_enabled"):
            raise CommandError("That is already the **current state**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled);",
            ctx.guild.id, "invites", state
        )
            
        self.bot.cache.set(f"data:filter_event:{ctx.guild.id}:invites", Munch(
            is_enabled=state,
            threshold=0
        ))

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
    @has_permissions(manage_channels=True)
    async def filter_caps(self: "Servers", ctx: Context, state: bool):
        """
        Delete any messages exceeding the threshold for caps
        """
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:caps", DICT).get("threshold", 10)
            
        if state == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:caps", DICT).get("is_enabled") and threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:caps", DICT).get("threshold"):
            raise CommandError("That is already the **current state**.")
            
        if state:
            if threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:caps", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                raise CommandError("That is already the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                raise CommandError("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "caps", state, threshold
        )

        self.bot.cache.set(f"data:filter_event:{ctx.guild.id}:caps", Munch(
            is_enabled=state,
            threshold=threshold
        ))

        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **cap filter**{f' (with threshold: {threshold})' if state else '.'}")
        
        
    @_filter.command(
        name="snipe",
        usage="<option invites/links/images/words> <state>",
        example="invites true"
    )
    @has_permissions(manage_channels=True)
    async def filter_snipe(self: "Servers", ctx: Context, option: str, state: bool):
        """
        Filter snipe command from allowing certain content
        """
        
        if option not in ("invites", "links", "images", "words"):
            raise CommandError("Please provide a **valid** option.\n" \
            "{self.bot.reply} **Note:** all the options are shown in the command's help menu")
            
        if state == self.bot.cache.get(f"data:filter_snipe:{ctx.guild.id}", DICT).get(option, 0):
            raise CommandError("That is already the **current state**.")
            
        await self.bot.db.execute(
            f"INSERT INTO filter_snipe (guild_id, {option}) VALUES (%s, %s) ON DUPLICATE KEY UPDATE {option} = VALUES({option});",
            ctx.guild.id, state
        )

        if not self.bot.cache.get(f"data:filter_snipe:{ctx.guild.id}"):
            self.bot.cache.set(
                f"data:filter_snipe:{ctx.guild.id}", Munch(
                    invites=0,
                    links=0,
                    images= 0,
                    words=0
                )
            )
        
        current = self.bot.cache.get(f"data:filter_snipe:{ctx.guild.id}")
        
        self.bot.cache.set(
            f"data:filter_snipe:{ctx.guild.id}", Munch(
                invites=current.invites if option != "invites" else state,
                links=current.links if option != "links" else state,
                images= current.images if option != "images" else state,
                words=current.words if option != "words" else state
            )
        )
        
        return await ctx.success(f"{option.title()} will now **{'appear' if state else 'stop appearing'}** in the snipe embed.")
        
            
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
    @has_permissions(manage_channels=True)
    async def filter_massmention(self: "Servers", ctx: Context, state: bool):
        """
        Delete any messages exceeding the threshold for mentions
        """
        
        threshold = ctx.parameters.get("threshold") or self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:massmention", DICT).get("threshold", 5)
            
        if state == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:massmention", DICT).get("is_enabled") and threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:massmention", DICT).get("threshold"):
            raise CommandError("That is already the **current state**.")
            
        if state:
            if threshold == self.bot.cache.get(f"data:filter_event:{ctx.guild.id}:massmention", DICT).get("threshold") and ctx.parameters.get("threshold") is not None:
                raise CommandError("That is already the **current threshold**.")
            
            if threshold > 127 or threshold < 1:
                raise CommandError("Please provide a **valid** threshold between **1** and **127**.")
            
        await self.bot.db.execute(
            "INSERT INTO filter_event (guild_id, event, is_enabled, threshold) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_enabled = VALUES(is_enabled), threshold = VALUES(threshold);",
            ctx.guild.id, "massmention", state, threshold
        )

        self.bot.cache.set(f"data:filter_event:{ctx.guild.id}:massmention", Munch(
            is_enabled=state,
            threshold=threshold
        ))

        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the **mention filter**{f' (with threshold: {threshold})' if state else '.'}")
        
        
    @_filter.command(
        name="remove",
        aliases=("delete",),
        usage="<keyword>",
        example="nig"
    )
    @has_permissions(manage_channels=True)
    async def filter_remove(self: "Servers", ctx: Context, keyword: str):
        """
        Remove a filtered word
        """
        
        if keyword not in self.bot.cache.smembers(f"data:filter:{ctx.guild.id}"):
            raise CommandError("That isn't a **filtered word**.")
            
        await self.bot.db.execute(
            "DELETE FROM filter WHERE guild_id = %s AND keyword = %s;",
            ctx.guild.id, keyword
        )

        self.bot.cache.srem(
            f"data:filter:{ctx.guild.id}",
            keyword
        )

        return await ctx.success(f"Successfully **removed** the filtered keyword \n```{keyword}```")
        
            
    @Group(
        name="autoresponder",
        aliases=("autoreply", "autorespond",),
        usage="<sub command>",
        example="welcome {content: welcome to the server! :3}",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def autoresponder(self: "Servers", ctx: Context):
        """
        Set up automatic replies to messages that match a trigger
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @autoresponder.command(
        name="update",
        usage="<trigger> <response>",
        example="welcome {content: hello}"
    )
    async def autoresponder_update(self: "Servers", ctx: Context, trigger: str, *, response: str):
        """
        Update the response for an auto-reply triggee
        """
        
        if not (current_data := self.bot.cache.get(f"data:autoresponder:{ctx.guild.id}:{trigger}")):
            raise CommandError("That isn't an existing **auto-reply trigger**.")
            
        if response == current_data.response:
            raise CommandError("That is already the current response.")
            
        await self.bot.db.execute(
            "UPDATE autoresponder SET response = %s WHERE keyword = %s;",
            response, trigger
        )

        self.bot.cache.set(
            f"data:autoresponder:{ctx.guild.id}:{trigger}", Munch(
                response=response,
                created_by=current_data.created_by
            )
        )

        return await ctx.success(f"Successfully **updated** `{trigger}`'s response to \n```{response}```")
        
    
    @autoresponder.group(
        name="add",
        usage="<trigger> <response>",
        example="welcome {content: welcome to the server! :3}",
        invoke_without_command=True
    )
    async def autoresponder_add(self: "Servers", ctx: Context, trigger: str, *, response: str):
        """
        Add a reply to a word
        """
        
        if not trigger or not response:
            return await ctx.send_help(ctx.command.qualified_name)
        
        if self.bot.cache.get(f"data:autoresponder:{ctx.guild.id}:{trigger}"):
            raise CommandError("That is already an existing **auto-reply trigger**.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder (guild_id, keyword, response, created_by) VALUES (%s, %s, %s, %s);",
            ctx.guild.id, trigger, response, ctx.author.id
        )

        self.bot.cache.set(
            f"data:autoresponder:{ctx.guild.id}:{trigger}", Munch(
                response=response,
                created_by=ctx.author.id
            )
        )
            
        return await ctx.success(f"Successfully **binded** `{trigger}`'s response to \n```{response}```")
        
        
    @autoresponder_add.command(
        name="images",
        usage="<response>",
        example="{content: hot}"
    )
    @has_permissions(manage_channels=True)
    async def autoresponder_add_images(self: "Servers", ctx: Context, *, response: str):
        """
        Add a response for images
        """
        
        if (record := self.bot.cache.get(f"data:autoresponder_event:{ctx.guild.id}:images")) and response == record.response:
            raise CommandError("That is already the **auto-response** for images.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder_event (guild_id, event, response) VALUES (%s, %s, %s);",
            ctx.guild.id, "images", response
        )

        self.bot.cache.set(
            f"data:autoresponder_event:{ctx.guild.id}:images",
            response
        )

        return await ctx.success(f"Successfully **binded** the response for images to \n```{response}```")
        
        
    @autoresponder_add.command(
        name="spoilers",
        usage="<response>",
        example="{content: shhh}"
    )
    @has_permissions(manage_channels=True)
    async def autoresponder_add_spoilers(self: "Servers", ctx: Context, *, response: str):
        """
        Add a response for spoilers
        """
        
        if response == self.bot.cache.get(f"data:autoresponder_event:{ctx.guild.id}:spoilers").response:
            raise CommandError("That is already the **auto-response** for spoilers.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder_event (guild_id, event, response) VALUES (%s, %s, %s);",
            ctx.guild.id, "spoilers", response
        )

        self.bot.cache.set(
            f"data:autoresponder_event:{ctx.guild.id}:spoilers",
            response
        )

        return await ctx.success(f"Successfully **binded** the response for spoilers to \n```{response}```")
    

    @autoresponder_add.command(
        name="emojis",
        usage="<response>",
        example="{content: hey}"
    )
    @has_permissions(manage_channels=True)
    async def autoresponder_add_emojis(self: "Servers", ctx: Context, *, response: str):
        """
        Add a response for emojis
        """
        
        if response == self.bot.cache.get(f"data:autoresponder_event:{ctx.guild.id}:emojis").response:
            raise CommandError("That is already the **auto-response** for emojis.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder_event (guild_id, event, response) VALUES (%s, %s, %s);",
            ctx.guild.id, "emojis", response
        )

        self.bot.cache.set(
            f"data:autoresponder_event:{ctx.guild.id}:emojis",
            response
        )

        return await ctx.success(f"Successfully **binded** the response for emojis to \n```{response}```")
        
        
    @autoresponder_add.command(
        name="stickers",
        usage="<response>",
        example="{content: fat}"
    )
    @has_permissions(manage_channels=True)
    async def autoresponder_add_stickers(self: "Servers", ctx: Context, *, response: str):
        """
        Add a response for stickers
        """
        
        if response == self.bot.cache.get(f"data:autoresponder_event:{ctx.guild.id}:stickers").response:
            raise CommandError("That is already the **auto-response** for stickers.")
            
        await self.bot.db.execute(
            "INSERT INTO autoresponder_event (guild_id, event, response) VALUES (%s, %s, %s);",
            ctx.guild.id, "stickers", response
        )

        self.bot.cache.set(
            f"data:autoresponder_event:{ctx.guild.id}:stickers",
            response
        )

        return await ctx.success(f"Successfully **binded** the response for stickers to \n```{response}```")
        
        
    @autoresponder.group(
        name="remove",
        usage="<trigger>",
        example="welcome",
        invoke_without_command=True
    )
    async def autoresponder_remove(self: "Servers", ctx: Context, trigger: str):
        """
        Remove a auto-reply trigger
        """
        
        if not self.bot.cache.get(f"data:autoresponder:{ctx.guild.id}:{trigger}"):
            raise CommandError("There isn't a **auto-reply trigger** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder WHERE guild_id = %s AND keyword = %s;",
            ctx.guild.id, trigger
        )

        self.bot.cache.delete(f"data:autoresponder:{ctx.guild.id}:{trigger}")
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** with name `{trigger}`.")
        
        
    @autoresponder_remove.command(
        name="images",
        invoke_without_command=True
    )
    async def autoresponder_remove_images(self: "Servers", ctx: Context):
        """
        Remove the response for images
        """
        
        if not self.bot.cache.get(f"data:autoresponder_event:{ctx.guild.id}:images"):
            raise CommandError("There isn't a **auto-reply trigger** for images.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
            ctx.guild.id, "images"
        )

        self.bot.cache.delete(f"data:autoresponder_event:{ctx.guild.id}:stickers")
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** for images.")
        
        
    @autoresponder_remove.command(
        name="spoilers",
        invoke_without_command=True
    )
    async def autoresponder_remove_spoilers(self: "Servers", ctx: Context):
        """
        Remove the response for spoilers
        """
        
        if not self.bot.cache.get(f"data:autoresponder_event:{ctx.guild.id}:spoilers"):
            raise CommandError("There isn't a **auto-reply trigger** for spoilers.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
            ctx.guild.id, "spoilers"
        )

        self.bot.cache.delete(f"data:autoresponder_event:{ctx.guild.id}:spoilers")
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** for spoilers.")
        
        
    @autoresponder_remove.command(
        name="emojis",
        invoke_without_command=True
    )
    async def autoresponder_remove_emojis(self: "Servers", ctx: Context):
        """
        Remove the response for emojis
        """
        
        if not self.bot.cache.get(f"data:autoresponder_event:{ctx.guild.id}:emojis"):
            raise CommandError("There isn't a **auto-reply trigger** for emojis.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
            ctx.guild.id, "emojis"
        )

        self.bot.cache.delete(f"data:autoresponder_event:{ctx.guild.id}:emojis")
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** for emojis.")
        
        
    @autoresponder_remove.command(
        name="stickers",
        invoke_without_command=True
    )
    async def autoresponder_remove_stickers(self: "Servers", ctx: Context):
        """
        Remove the response for stickers
        """
        
        if not self.bot.cache.get(f"data:autoresponder_event:{ctx.guild.id}:stickers"):
            raise CommandError("There isn't a **auto-reply trigger** for stickers.")
            
        await self.bot.db.execute(
            "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
            ctx.guild.id, "stickers"
        )

        self.bot.cache.delete(f"data:autoresponder_event:{ctx.guild.id}:stickers")
        return await ctx.success(f"Successfully **removed** the **auto-reply trigger** for stickers.")

        
    @autoresponder.command(
        name="clear",
        usage="[type]",
        example="images"
    )
    async def autoresponder_clear(self: "Servers", ctx: Context, type: Optional[str] = None):
        """
        Clear every auto-reply trigger in this server
        """
        
        if not self.bot.cache.keys(pattern=f"data:autoresponder:{ctx.guild.id}:*") and not self.bot.cache.keys(pattern=f"data:autoresponder_event:{ctx.guild.id}:*"):
            raise CommandError("There aren't any **auto-reply triggers** in this server.")
            
        if type is not None:
            if type.lower() not in ("images", "spoilers", "emojis", "stickers"):
                raise CommandError("There isn't an **auto-reply event** like that.")
                
            if not self.bot.cache.keys(pattern=f"data:autoresponder_event:{ctx.guild.id}:*"):
                raise CommandError("There aren't any **auto-reply events** in this server.")
                
            if type.lower() not in tuple(
                record.split(":")[::-1][0]
                for record in self.bot.cache.keys(pattern=f"data:autoresponder_event:{ctx.guild.id}:*")
            ):
                raise CommandError("There isn't an **auto-reply event** like that in this server.")
            
            await self.bot.db.execute(
                "DELETE FROM autoresponder_event WHERE guild_id = %s AND event = %s;",
                ctx.guild.id, type.lower()
            )

            self.bot.cache.delete(f"data:autoresponder_event:{ctx.guild.id}:{type.lower()}")
            return await ctx.success("Successfully **cleared** every **auto-reply** for that event.")
        
        if self.bot.cache.keys(pattern=f"data:autoresponder:{ctx.guild.id}:*"):
            await self.bot.db.execute(
                "DELETE FROM autoresponder WHERE guild_id = %s;",
                ctx.guild.id
            )

            self.bot.cache.delete(pattern=f"data:autoresponder:{ctx.guild.id}:*")
        
        if self.bot.cache.keys(pattern=f"data:autoresponder_event:{ctx.guild.id}:*"):  
            await self.bot.db.execute(
                "DELETE FROM autoresponder_event WHERE guild_id = %s;",
                ctx.guild.id
            )

            self.bot.cache.delete(pattern=f"data:autoresponder_event:{ctx.guild.id}:*")
        
        return await ctx.success("Successfully **cleared** every **auto-reply trigger**.")
        
        
    @autoresponder.command(
        name="variables",
        aliases=("variable", "vars",)
    )
    async def autoresponder_variables(self: "Servers", ctx: Context):
        """
        View the available autoresponder message variables
        """
        return await ctx.respond(
            "Click [**here**](https://github.com/treyt3n/vile/blob/main/docs/variables.md) for a list of available variables.",
            emoji="<:v_slash:1067034025895665745>"
        )
        
        
    @autoresponder.command(
        name="list",
        aliases=("view", "show"),
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
    @has_permissions(manage_channels=True)
    async def autoresponder_list(self: "Servers", ctx: Context):
        """
        View every auto-reply trigger
        """
        
        if ctx.parameters.get("extras") is True:
            if not self.bot.cache.keys(pattern=f"data:autoresponder_event:{ctx.guild.id}:*"):
                raise CommandError("There aren't any **auto-reply events** in this server.")
            
            rows, embed = [ ], Embed(
                color=self.bot.color,
                title=f"Auto-Reply Extras in '{ctx.guild.name}'"
            )

            for event in tuple(
                record.split(":")[::-1][0]
                for record in self.bot.cache.keys(pattern=f"data:autoresponder_event:{ctx.guild.id}:*")
            ):
                data = self.bot.cache.get(f"data:autoresponder_event:{ctx.guild.id}:{event}")
                rows.append(f"{event}\n{self.bot.reply} **Response:** {utils.escape_markdown(data.response)}")
                
            return await ctx.paginate((embed, rows))
        
        if not self.bot.cache.keys(pattern=f"data:autoresponder:{ctx.guild.id}:*"):
            raise CommandError("There aren't any **auto-reply triggers** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Auto-Reply Triggers in '{ctx.guild.name}'"
        )

        for keyword in tuple(
            record.split(":")[::-1][0]
            for record in self.bot.cache.keys(pattern=f"data:autoresponder:{ctx.guild.id}:*")
        ):
            data = self.bot.cache.get(f"data:autoresponder:{ctx.guild.id}:{keyword}")
            rows.append(f"{keyword}\n{self.bot.reply} **Response:** {utils.escape_markdown(data.response)}")
                
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="autoreaction",
        aliases=("reaction", "autoreact",),
        usage="<sub command>",
        example="add 50DollaLemonade :jitTrippin:",
        invoke_without_command=True
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction(self: "Servers", ctx: Context):
        """
        Set up automatic reactions to messages that match a trigger
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
    
    @autoreaction.group(
        name="add",
        usage="<trigger> <reaction>",
        example="50DollaLemondate :jitTrippin:",
        invoke_without_command=True
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_add(self: "Servers", ctx: Context, trigger: str, reaction: Emoji):
        """
        Add a reaction to a trigger
        """
        
        if not trigger:
            return await ctx.send_help(ctx.command.qualified_name)
        
        if reaction is None:
            raise CommandError("I couldn't find that emoji.")
        
        if b64encode(str(reaction).encode()) in self.bot.cache.smembers(f"data:autoreaction:{ctx.guild.id}:{trigger}"):
            raise CommandError("That is **already** a reaction for that **auto-reaction trigger**.")
            
        if len(self.bot.cache.smembers(f"data:autoreaction:{ctx.guild.id}:{trigger}")) > 15:
            raise CommandError("There are too many reactions for that trigger.")
            
        if len(trigger) > 32:
            raise CommandError("Please provide a **valid** trigger under 32 characters.")
            
        await self.bot.db.execute(
            "INSERT INTO autoreact (guild_id, keyword, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, trigger, b64encode(str(reaction).encode())
        )

        self.bot.cache.sadd(
            f"data:autoreactionion:{trigger}:{ctx.guild.id}",
            b64encode(str(reaction).encode())
        )
            
        return await ctx.success(f"Successfully **added** {reaction} as a reaction for `{trigger}`.")
        
    
    @autoreaction_add.command(
        name="images",
        usage="<reaction>",
        example=":smash:"
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_add_images(self: "Servers", ctx: Context, reaction: Emoji):
        """
        Add a reaction for images
        """
        
        if reaction is None:
            raise CommandError("I couldn't find that emoji.")

        if b64encode(str(reaction).encode()) in self.bot.cache.smembers(f"data:autoreaction_event:{ctx.guild.id}:images"):
            raise CommandError("That is **already** an **auto-reaction** for images.")
            
        if len(self.bot.cache.smembers(f"data:autoreaction_event:{ctx.guild.id}:images")) > 15:
            raise CommandError("There are too many reactions for that trigger.")
            
        await self.bot.db.execute(
            "INSERT INTO autoreact_event (guild_id, event, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, "images", b64encode(str(reaction).encode())
        )

        self.bot.cache.sadd(
            f"data:autoreactionion_event:images:{ctx.guild.id}",
            b64encode(str(reaction).encode())
        )
        
        return await ctx.success(f"Successfully **added** {reaction} as a reaction for images.")
    
    
    @autoreaction_add.command(
        name="spoilers",
        usage="<reaction>",
        example=":hushed_face:"
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_add_spoilers(self: "Servers", ctx: Context, reaction: Emoji):
        """
        Add a reaction for spoilers
        """
        
        if reaction is None:
            raise CommandError("I couldn't find that emoji.")

        if b64encode(str(reaction).encode()) in self.bot.cache.smembers(f"data:autoreaction_event:{ctx.guild.id}:spoilers"):
            raise CommandError("That is **already** an **auto-reaction** for spoilers.")
            
        if len(self.bot.cache.smembers(f"data:autoreaction_event:{ctx.guild.id}:spoilers")) > 15:
            raise CommandError("There are too many reactions for that trigger.")
            
        await self.bot.db.execute(
            "INSERT INTO autoreact_event (guild_id, event, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, "spoilers", b64encode(str(reaction).encode())
        )

        self.bot.cache.sadd(
            f"data:autoreactionion_event:spoilers:{ctx.guild.id}",
            b64encode(str(reaction).encode())
        )

        return await ctx.success(f"Successfully **added** {reaction} as a reaction for spoilers.")
        
        
    @autoreaction_add.command(
        name="emojis",
        usage="<reaction>",
        example=":wave:"
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_add_emojis(self: "Servers", ctx: Context, reaction: Emoji):
        """
        Add a reaction for emojis
        """
        
        if reaction is None:
            raise CommandError("I couldn't find that emoji.")

        if b64encode(str(reaction).encode()) in self.bot.cache.smembers(f"data:autoreaction_event:{ctx.guild.id}:emojis"):
            raise CommandError("That is **already** an **auto-reaction** for emojis.")
            
        if len(self.bot.cache.smembers(f"data:autoreaction_event:{ctx.guild.id}:emojis")) > 15:
            raise CommandError("There are too many reactions for that trigger.")
             
        await self.bot.db.execute(
            "INSERT INTO autoreact_event (guild_id, event, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, "emojis", b64encode(str(reaction).encode())
        )

        self.bot.cache.sadd(
            f"data:autoreactionion_event:emojis:{ctx.guild.id}",
            b64encode(str(reaction).encode())
        )

        return await ctx.success(f"Successfully **added** {reaction} as a reaction for emojis.")
    
    
    @autoreaction_add.command(
        name="stickers",
        usage="<reaction>",
        example=":zzz:"
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_add_stickers(self: "Servers", ctx: Context, reaction: Emoji):
        """
        Add a reaction for stickers
        """
        
        if reaction is None:
            raise CommandError("I couldn't find that emoji.")

        if b64encode(str(reaction).encode()) in self.bot.cache.smembers(f"data:autoreaction_event:{ctx.guild.id}:stickers"):
            raise CommandError("That is **already** an **auto-reaction** for stickers.")
            
        if len(self.bot.cache.smembers(f"data:autoreaction_event:{ctx.guild.id}:stickers")) > 15:
            raise CommandError("There are too many reactions for that trigger.")
            
        await self.bot.db.execute(
            "INSERT INTO autoreact_event (guild_id, event, reaction) VALUES (%s, %s, %s);",
            ctx.guild.id, "stickers", b64encode(str(reaction).encode())
        )

        self.bot.cache.sadd(
            f"data:autoreactionion_event:{ctx.guild.id}:stickers",
            b64encode(str(reaction).encode())
        )

        return await ctx.success(f"Successfully **added** {reaction} as a reaction for stickers.")
    
        
    @autoreaction.group(
        name="remove",
        usage="<trigger>",
        example="50DollaLemonade",
        invoke_without_command=True
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_remove(self: "Servers", ctx: Context, trigger: str, reaction: Emoji):
        """
        Remove a reaction from an auto-react trigger
        """
        
        if reaction not in self.bot.cache.smembers(f"data:autoreaction_event:{ctx.guild.id}"):
            raise CommandError("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact WHERE keyword = %s AND reaction = %s;",
            trigger, b64encode(str(reaction).encode())
        )

        self.bot.cache.autoreply[ctx.guild.id][trigger].remove(b64encode(str(reaction).encode()))
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
        
        
    @autoreaction_remove.command(
        name="images",
        usage="<reaction>",
        example=":smash:"
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_remove_images(self: "Servers", ctx: Context, reaction: Emoji):
        """
        Remove a reaction for images
        """
        
        if reaction not in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("images", TUPLE):
            raise CommandError("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact_event WHERE guild_id = %s AND event = %s AND reaction = %s;",
            ctx.guild.id, "images", b64encode(str(reaction).encode())
        )

        self.bot.cache.autoreact_event[ctx.guild.id]["images"].remove(b64encode(str(reaction).encode()))
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
    
    
    @autoreaction_remove.command(
        name="spoilers",
        usage="<reaction>",
        example=":hushed_face:"
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_remove_spoilers(self: "Servers", ctx: Context, reaction: Emoji):
        """
        Remove a reaction for spoilers
        """
        
        if reaction not in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("spoilers", TUPLE):
            raise CommandError("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact_event WHERE guild_id = %s AND event = %s AND reaction = %s;",
            ctx.guild.id, "spoilers", b64encode(str(reaction).encode())
        )

        self.bot.cache.autoreact_event[ctx.guild.id]["spoilers"].remove(b64encode(str(reaction).encode()))
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
    
    
    @autoreaction_remove.command(
        name="emojis",
        usage="<reaction>",
        example=":wave:"
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_remove_emojis(self: "Servers", ctx: Context, reaction: Emoji):
        """
        Remove a reaction for emojis
        """
        
        if reaction not in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("emojis", TUPLE):
            raise CommandError("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact_event WHERE guild_id = %s AND event = %s AND reaction = %s;",
            ctx.guild.id, "emojis", b64encode(str(reaction).encode())
        )

        self.bot.cache.autoreact_event[ctx.guild.id]["emojis"].remove(b64encode(str(reaction).encode()))
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
    
    
    @autoreaction_remove.command(
        name="stickers",
        usage="<reaction>",
        example=":zzz:"
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_remove_stickers(self: "Servers", ctx: Context, reaction: Emoji):
        """
        Remove a reaction for stickers
        """
        
        if reaction not in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).get("stickers", TUPLE):
            raise CommandError("There **isn't** an **auto-reaction** like that.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact_event WHERE guild_id = %s AND event = %s AND reaction = %s;",
            ctx.guild.id, "stickers", b64encode(str(reaction).encode())
        )

        self.bot.cache.autoreact_event[ctx.guild.id]["stickers"].remove(b64encode(str(reaction).encode()))
        return await ctx.success(f"Successfully **removed** that **auto-reaction**.")
    
        
    @autoreaction.command(
        name="clear"
    )
    async def autoreaction_clear(self: "Servers", ctx: Context, type: Optional[str] = None):
        """
        Clear every auto-react trigger in this server
        """
        
        if ctx.guild.id not in self.bot.cache.autoreact and ctx.guild.id not in self.bot.cache.autoreact_event:
            raise CommandError("There **aren't** any **auto-react triggers** in this server.")
            
        if type is not None:
            if type.lower() not in ("images", "spoilers", "emojis", "stickers"):
                raise CommandError("There **isn't** an **auto-react event** like that.")
                
            if ctx.guild.id not in self.bot.cache.autoreact_event:
                raise CommandError("There **aren't** any **auto-react events** in this server.")
                
            if type.lower() not in self.bot.cache.autoreact_event[ctx.guild.id]:
                raise CommandError("There **isn't** an **auto-react event** like that in this server.")
            
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
        
        
    @autoreaction.command(
        name="removeall",
        aliases=("deleteall",)
    )
    @has_permissions(manage_emojis=True)
    async def autoreaction_removeall(self: "Servers", ctx: Context, trigger: str):
        """
        Clear every auto-reaction from a trigger
        """
        
        if trigger not in self.bot.cache.autoreact.get(ctx.guild.id, DICT):
            raise CommandError("There **aren't** any **auto-reactions** for that trigger.")
            
        await self.bot.db.execute(
            "DELETE FROM autoreact WHERE guild_id = %s AND trigger = %s;",
            ctx.guild.id, trigger
        )
        del self.bot.cache.autoreact[ctx.guild.id][trigger]
            
        return await ctx.success("Successfully **cleared** every **auto-reaction** belonging to that trigger.")
        
        
    @autoreaction.command(
        name="list",
        aliases=("view", "show"),
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
    @has_permissions(manage_emojis=True)
    async def autoreaction_list(self: "Servers", ctx: Context):
        """
        View every auto-react trigger
        """
        
        if ctx.parameters.get("extras") is True:
            rows, embed = [ ], Embed(
                color=self.bot.color,
                title=f"Auto-Reaction Extras in '{ctx.guild.name}'"
            )
            
            for event, reactions in self.bot.cache.autoreact_event.get(ctx.guild.id, DICT).items():
                rows.append(f"{event}\n{self.bot.reply} **Reactions:** {', '.join(b64decode(reaction.encode()).decode() for reaction in reactions)}")
                
            return await ctx.paginate((embed, rows))
        
        if not self.bot.cache.autoreact.get(ctx.guild.id, DICT):
            raise CommandError("There **aren't** any **auto-reaction triggers** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Auto-React Triggers in '{ctx.guild.name}'"
        )

        for keyword, reactions in self.bot.cache.autoreact[ctx.guild.id].items():
            rows.append(f"{keyword}\n{self.bot.reply} **Reactions:** {', '.join(b64decode(reaction.encode()).decode() for reaction in reactions)}")
                
        return await ctx.paginate((embed, rows))

        
    @Group(
        name="disable",
        aliases=("d",),
        usage="<sub command>",
        example="module lastfm",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def disable(self: "Servers", ctx: Context):
        """
        Disable a feature
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @disable.command(
        name="module",
        aliases=("category",),
        usage="<module>",
        example="lastfm"
    )
    async def disable_module(self: "Servers", ctx: Context, module: str):
        """
        Disable a module
        """
        
        if module.lower() not in list(map(lambda c: c.replace("LastFM Integration", "LastFM").lower(), self.bot.cogs.keys())) or module.lower() == "developer":
            raise CommandError("Please provide a **valid** module.")
            
        if module.lower() in self.bot.cache.disabled_module.get(ctx.guild.id, TUPLE):
            raise CommandError("That module is **already disabled**.")
            
        if module.lower() == "servers":
            raise CommandError("You can't **disable** that module.")
            
        await self.bot.db.execute(
            "INSERT INTO disabled_feature (guild_id, name, type) VALUES (%s, %s, 'module');",
            ctx.guild.id, module
        )

        self.bot.cache.sadd(
            f"data:disabled_feature:{ctx.guild.id}", orjson.dumps(dict(
                name=module,
                type="module"
            ))
        )

        return await ctx.success(f"Successfully **disabled** the module `{module}`.")
        
        
    @disable.command(
        name="command",
        aliases=("cmd",),
        usage="<command>",
        example="image"
    )
    async def disable_command(self: "Servers", ctx: Context, *, command: str):
        """
        Disable a command
        """
        
        if not (cmd := self.bot.get_command(command.lower())) or cmd.cog_name == "Developer":
            raise CommandError("Please provide a **valid** command.")
            
        if cmd.qualified_name in tuple(record.name for record in self.bot.cache.smembers(f"data:disabled_feature:{ctx.guild.id}")):
            raise CommandError("That command is **already disabled**.")
            
        if (cmd.root_parent or cmd).qualified_name in ("disable", "enable"):
            raise CommandError("You can't **disable** that command.")
            
        await self.bot.db.execute(
            "INSERT INTO disabled_feature (guild_id, name, type) VALUES (%s, %s, 'command');",
            ctx.guild.id, cmd.qualified_name
        )

        self.bot.cache.sadd(
            f"data:disabled_feature:{ctx.guild.id}", orjson.dumps(dict(
                name=cmd.qualified_name,
                type="command"
            ))
        )

        return await ctx.success(f"Successfully **disabled** the command `{cmd.qualified_name}`.")
    
    
    @disable.command(
        name="list",
        aliases=("view", "show")
    )
    @has_permissions(manage_channels=True)
    async def disable_list(self: "Servers", ctx: Context):
        """
        View every disabled feature
        """
        
        if not (self.bot.cache.disabled_module.get(ctx.guild.id, [ ]) + self.bot.cache.disabled_command.get(ctx.guild.id, TUPLE)):
            raise CommandError("There **aren't** any **disabled features** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Disabled Features in '{ctx.guild.name}'"
        )
        
        # I don't store the types in cache so a db query is necessary
        for name, type in await self.bot.db.execute("SELECT name, type FROM disabled_feature WHERE guild_id = %s;", ctx.guild.id):
            rows.append(f"{name}\n{self.bot.reply} **type:** {type}")
            
        return await ctx.paginate((embed, rows))
        
    
    @Group(
        name="pagination",
        aliases=("paginate",),
        usage="<sub command>",
        example="list",
        invoke_without_command=True
    )
    @has_permissions(manage_messages=True)
    async def pagination(self: "Servers", ctx: Context):
        """
        Set up multiple embeds on one message
        """

        return await ctx.send_help(ctx.command.qualified_name)
    
    
    @pagination.command(
        name="add",
        usage="<message> <embed code>",
        example="1115893655962665071 ..."
    )
    @has_permissions(manage_messages=True)
    async def pagination_add(self: "Servers", ctx: Context, message: Message, *, code: str):
        """
        Add a page to a pagination embed
        """
        
        if message.author != ctx.guild.me:
            raise CommandError("The message be sent by me.")
            
        if len(code) > 1024:
            raise CommandError("Please provide a **valid** embed script under 1024 characters.")
            
        await self.bot.db.execute(
            """
            INSERT IGNORE INTO pagination (guild_id, channel_id, message_id, current_page) VALUES (%s, %s, %s, %s);
            INSERT INTO pagination_pages (guild_id, channel_id, message_id, page, page_number) VALUES (%s, %s, %s, %s, %s);
            """,
            ctx.guild.id, message.channel.id, message.id, 1,
            ctx.guild.id, message.channel.id, message.id, code, len(self.bot.cache.pagination_pages.get(ctx.guild.id, DICT).get(message.id, TUPLE))+1
        )
        
        if ctx.guild.id not in self.bot.cache.pagination:
            self.bot.cache.pagination[ctx.guild.id] = { }
            
        if ctx.guild.id not in self.bot.cache.pagination_pages:
            self.bot.cache.pagination_pages[ctx.guild.id] = { }
            
        if message.id not in self.bot.cache.pagination[ctx.guild.id]:
            self.bot.cache.pagination[ctx.guild.id][message.id] = 1
            
        else:
            self.bot.cache.pagination[ctx.guild.id][message.id] = self.bot.cache.pagination[ctx.guild.id][message.id]+1

        if message.id not in self.bot.cache.pagination_pages[ctx.guild.id]:
            self.bot.cache.pagination_pages[ctx.guild.id][message.id] = [ ]
            
        self.bot.cache.pagination_pages[ctx.guild.id][message.id].append((code, len(self.bot.cache.pagination_pages[ctx.guild.id][message.id])+1))
        
        script = EmbedScript(await pagination_replacement(
            code, 
            ctx.guild, 
            len(self.bot.cache.pagination_pages[ctx.guild.id][message.id]), 
            self.bot.cache.pagination[ctx.guild.id][message.id]
        ))

        await script.parse()
        del script.objects["files"]
        await message.edit(**script.objects)

        await self.bot.db.execute(
            "UPDATE pagination SET current_page = %s WHERE message_id = %s",
            self.bot.cache.pagination[ctx.guild.id][message.id], message.id
        )
                    
        gather(*(
            message.add_reaction("<:v_left_page:1067034010624200714>"),
            message.add_reaction("<:v_right_page:1067034017108607076>")
        ))

        return await ctx.success(f"Successfully **added** a page to the pagination embed with this script:\n```{code}```")
        
        
    @pagination.command(
        name="update",
        aliases=("edit",),
        usage="<message> <id> <embed code>",
        example="1115893655962665071 2 ..."
    )
    @has_permissions(manage_messages=True)
    async def pagination_update(self: "Servers", ctx: Context, message: Message, id: int, *, code: str):
        """
        Update an existing page on pagination embed
        """
        
        if message.id not in self.bot.cache.pagination_pages.get(ctx.guild.id, DICT):
            raise CommandError("That **isn't** a pagination embed.")
            
        page = next(filter(lambda page: page[1] == id, self.bot.cache.pagination_pages[ctx.guild.id][message.id]), None)
        if page is None:
            raise CommandError("Please provide a **valid** page ID for that pagination embed.")
            
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
    @has_permissions(manage_messages=True)
    async def pagination_delete(self: "Servers", ctx: Context, message: Message):
        """
        Delete a pagination embed entirely
        """
        
        if message.id not in self.bot.cache.pagination_pages.get(ctx.guild.id, DICT):
            raise CommandError("That **isn't** a pagination embed.")
            
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
    @has_permissions(manage_messages=True)
    async def pagination_remove(self: "Servers", ctx: Context, message: Message, id: int):
        """
        Remove a page from a pagination embed
        """
        
        if message.id not in self.bot.cache.pagination_pages.get(ctx.guild.id, DICT):
            raise CommandError("That **isn't** a pagination embed.")
            
        page = next(filter(lambda page: page[1] == id, self.bot.cache.pagination_pages[ctx.guild.id][message.id]), None)
        if page is None:
            raise CommandError("Please provide a **valid** page ID for that pagination embed.")
            
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
    @has_permissions(manage_messages=True)
    async def pagination_restorereactions(self: "Servers", ctx: Context, message: Message):
        """
        Restore reactions to an existing pagination embed
        """
        
        if message.id not in self.bot.cache.pagination_pages.get(ctx.guild.id, DICT):
            raise CommandError("That **isn't** a pagination embed.")
            
        gather(*(
            message.add_reaction("<:v_left_page:1067034010624200714>"),
            message.add_reaction("<:v_right_page:1067034017108607076>")
        ))
        
        return await ctx.success("Successfully **restored** that pagination embed's reactions.")
        
        
    @pagination.command(name="reset")
    @has_permissions(manage_messages=True)
    async def pagination_reset(self: "Servers", ctx: Context):
        """
        Remove every existing pagination embed
        """
        
        if ctx.guild.id not in self.bot.cache.pagination_pages:
            raise CommandError("That **aren't** any **pagination embeds** in this server.")
            
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
        name="list",
        aliases=("view", "show")
    )
    @has_permissions(manage_guild=True)
    async def pagination_list(self: "Servers", ctx: Context):
        """
        View all existing pagination embeds
        """
        
        if ctx.guild.id not in self.bot.cache.pagination:
            raise CommandError("There **aren't** any **pagination embeds** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Pagination Embeds in '{ctx.guild.name}'"
        )
        for channel_id, message_id in await self.bot.db.execute("SELECT channel_id, message_id FROM pagination_pages WHERE guild_id = %s", ctx.guild.id):
            rows.append(f"[**{message_id}**](https://com/channels/{ctx.guild.id}/{channel_id}/{message_id})")
                
        return await ctx.paginate((embed, rows))
    
        
    @Group(
        name="enable",
        usage="<sub command>",
        example="module lastfm",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def enable(self: "Servers", ctx: Context):
        """
        Enable a feature
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @enable.command(
        name="module",
        aliases=("category",),
        usage="<module>",
        example="lastfm"
    )
    async def enable_module(self: "Servers", ctx: Context, module: str):
        """
        Enable a module
        """
        
        if module.lower() not in list(map(lambda c: c.replace("LastFM Integration", "LastFM").lower(), self.bot.cogs.keys())) or module.lower() == "developer":
            raise CommandError("Please provide a **valid** module.")
            
        if module.lower() not in self.bot.cache.disabled_module.get(ctx.guild.id, TUPLE):
            raise CommandError("That module is **already enabled**.")
            
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
    async def enable_command(self: "Servers", ctx: Context, *, command: str):
        """
        Enable a command
        """
        
        if not (cmd := self.bot.get_command(command.lower())) or cmd.cog_name == "Developer":
            raise CommandError("Please provide a **valid** command.")
            
        if cmd.qualified_name not in self.bot.cache.disabled_command.get(ctx.guild.id, TUPLE):
            raise CommandError("That command is **already enabled**.")
            
        await self.bot.db.execute(
            "DELETE FROM disabled_feature WHERE guild_id = %s AND name = %s AND type = 'command';",
            ctx.guild.id, cmd.qualified_name
        )
        self.bot.cache.disabled_command[ctx.guild.id].remove(cmd.qualified_name)
        
        return await ctx.success(f"Successfully **enabled** the command `{cmd.qualified_name}`.")
        
        
    @Group(
        name="ignore",
        usage="<member or channel or role>",
        example="@trey#0006",
        invoke_without_command=True
    )
    @has_permissions(administrator=True)
    async def ignore(
        self: "Servers", 
        ctx: Context, 
        *, 
        source: Union[ Member, TextChannel, Role ]
    ):
        """
        Ignore commands from a member or channel or role
        """
        
        if isinstance(source, Member) and await ctx.can_moderate(source, "ignore") is not None:
            return
        
        if source.id in self.bot.cache.smembers(f"data:ignore:{ctx.guild.id}"):
            await self.bot.db.execute(
                "DELETE FROM ignore_object WHERE object_id = %s;",
                source.id
            )

            self.bot.cache.srem(f"data:ignore:{ctx.guild.id}", source.id)
            return await ctx.success(f"No longer **ignoring commands** from {source.mention}.")
            
        if isinstance(source, Member):
            _type = "member"
        
        elif isinstance(source, TextChannel):
            _type = "channel"
            
        elif isinstance(source, Role):
            _type = "role"
            
        await self.bot.db.execute(
            "INSERT INTO ignore_object (guild_id, object_id, type) VALUES (%s, %s, %s);",
            ctx.guild.id, source.id, _type
        )

        self.bot.cache.sadd(f"data:ignore:{ctx.guild.id}", source.id)
        return await ctx.success(f"Commands from {source.mention} will now be **ignored**.")
        
        
    @ignore.command(
        name="list",
        aliases=("view", "show")
    )
    @has_permissions(manage_channels=True)
    async def ignore_list(self: "Servers", ctx: Context):
        """
        View every ignored member or channel or role
        """
        
        if not self.bot.cache.keys(pattern=f"data:ignore:{ctx.guild.id}"):
            raise CommandError("There aren't any **ignored members or channels or roles** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Ignored Objects in '{ctx.guild.name}'"
        )
        
        # I dont store the types in cache, so a database pull is necessary.
        for object_id, type in await self.bot.db.execute(
            "SELECT object_id, type FROM ignore_object WHERE guild_id = %s;", 
            ctx.guild.id
        ):
            if (object := ctx.guild.get_member(object_id) or ctx.guild.get_channel(object_id) or ctx.guild.get_role(object_id)):
                rows.append(f"{object.mention}\n{self.bot.reply} **Type:** {type}")
            
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="set",
        usage="<sub command>",
        example="icon ...",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def _set(self: "Servers", ctx: Context):
        """
        Set the new server icon or splash or banner
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @_set.command(
        name="icon",
        usage="[link or attachment]",
        example="..."
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def set_icon(
        self: "Servers",
        ctx: Context, 
        image: Attachment = parameter(
            converter=Attachment,
            default=Attachment.search
        )
    ):
        """
        Set the new server icon
        """

        try:
            await ctx.guild.edit(icon=await self.bot.proxied_session.read(image))
        
        except Exception:
            if not ctx.message.attachments or image != ctx.message.attachments[0].url:
                if self.bot.cache.ratelimited(f"globalrl:suspicious_urls{image}", 3, 86400):
                    return await self.bot.blacklist(ctx.author.id, _type=1)
                    
            raise CommandError("Please provide a **valid** image.")
            
        return await ctx.success(f"Successfully **set** the new [**server icon**]({ctx.guild.icon.url}).")
    
    
    @_set.command(
        name="splash",
        usage="[link or attachment]",
        example="..."
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def set_splash(
        self: "Servers", 
        ctx: Context, 
        image: Attachment = parameter(
            converter=Attachment,
            default=Attachment.search
        )
    ):
        """
        Set the new server splash
        """
        
        if ctx.guild.premium_tier < 1:
            raise CommandError("This server doesn't reach the **boost requirement** for a **splash background**.")
        
        try:
            await ctx.guild.edit(icon=await self.bot.proxied_session.read(image))
            
        except Exception:
            if not ctx.message.attachments or image != ctx.message.attachments[0].url:
                if self.bot.cache.ratelimited(f"globalrl:suspicious_urls{image}", 3, 86400):
                    return await self.bot.blacklist(ctx.author.id, _type=1)
                    
            raise CommandError("Please provide a **valid** image.")
            
        return await ctx.success(f"Successfully **set** the new [**server splash background**]({ctx.guild.icon.url}).")
    
    
    @_set.command(
        name="banner",
        usage="[image attachment]",
        example="..."
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def set_banner(
        self: "Servers", 
        ctx: Context,
        image: Attachment = parameter(
            converter=Attachment,
            default=Attachment.search
        )
    ):
        """
        Set the new server banner
        """
        
        if ctx.guild.premium_tier < 2:
            raise CommandError("This server doesn't reach the **boost requirement** for a **banner**.")
            
        try:
            await ctx.guild.edit(icon=await self.bot.proxied_session.read(image))
            
        except Exception:
            if not ctx.message.attachments or image != ctx.message.attachments[0].url:
                if self.bot.cache.ratelimited(f"globalrl:suspicious_urls{image}", 3, 86400):
                    return await self.bot.blacklist(ctx.author.id, _type=1)
                    
            raise CommandError("Please provide a **valid** image.")
            
        return await ctx.success(f"Successfully **set** the new [**server banner**]({ctx.guild.banner.url}).")
        
    
    @Group(
        name="unset",
        usage="<sub command>",
        example="icon",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def unset(self: "Servers", ctx: Context):
        """
        Unset the new server icon or splash or banner
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @unset.command(
        name="icon"
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def unset_icon(self: "Servers", ctx: Context):
        """
        Unset the server icon
        """
        
        if ctx.guild.banner is None:
            raise CommandError("This server **doesn't have** an **icon**")
            
        await ctx.guild.edit(icon=None)
        return await ctx.success(f"Successfully **unset** the **server icon**.")
    
    
    @unset.command(
        name="splash"
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def unset_splash(self: "Servers", ctx: Context):
        """
        Unset the server splash
        """
        
        if ctx.guild.banner is None:
            raise CommandError("This server **doesn't have** a **splash**")
            
        await ctx.guild.edit(splasy=None)
        return await ctx.success(f"Successfully **unset** the **server splash**.")
    
    
    @unset.command(
        name="banner"
    )
    @bot_has_permissions(manage_guild=True)
    @has_permissions(manage_guild=True)
    async def unset_banner(self: "Servers", ctx: Context):
        """
        Unset the server banner
        """
        
        if ctx.guild.banner is None:
            raise CommandError("This server **doesn't have** a **banner**")
            
        await ctx.guild.edit(banner=None)
        return await ctx.success(f"Successfully **unset** the **server banner**.")
        
        
    @Command(
        name="pin",
        usage="[message or reply]",
        example="..."
    )
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def pin(self: "Servers", ctx: Context, message: Optional[Message] = None):
        """
        Pin the provided or most recent message
        """
        
        if not message:
            if reference := ctx.message.reference:
                message = reference.resolved
            else:
                async for message in ctx.channel.history(limit=2):
                    message = message
                
                if not message:
                    return await ctx.send_help(ctx.command.qualified_name)
                
        if len(await ctx.channel.pins()) == 50:
            raise CommandError("This channel exceeds the **50 pin limit**.")
            
        await message.pin()
        return await ctx.success(f"Successfully **pinned** the [**provided message**]({message.jump_url}).")
        
        
    @Command(
        name="unpin",
        usage="[message or reply]",
        example="..."
    )
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def unpin(self: "Servers", ctx: Context, message: Optional[Message] = None):
        """
        Unpin the provided or most recent message
        """
        
        if not message:
            if reference := ctx.message.reference:
                message = reference.resolved
            else:
                async for message in ctx.channel.history(limit=2):
                    message = message
                
                if not message:
                    return await ctx.send_help(ctx.command.qualified_name)
                
        if message.pinned is False:
            raise CommandError("That message **isn't pinned**.")
            
        await message.unpin()
        return await ctx.success(f"Successfully **unpinned** the [**provided message**]({message.jump_url}).")
        

    @Command(
        name="firstmessage",
        aliases=("firstmsg",),
        usage="[channel]",
        example="..."
    )
    async def firstmessage(self: "Servers", ctx: Context, *, channel: Optional[TextChannel] = None):
        """
        Get a link for the first message in a channel
        """
        
        channel = channel or ctx.channel
        async for message in channel.history(limit=1, oldest_first=True):
            return await ctx.reply(view=View().add_item(
                Button(
                    label="First Message",
                    style=ButtonStyle.link,
                    url=message.jump_url
                )
            ))
            
            
    @Group(
        name="pins",
        aliases=("pinarchive",),
        usage="<sub command>",
        example="archive",
        invoke_without_command=True
    )
    @has_permissions(manage_guild=True)
    async def pins(self: "Servers", ctx: Context):
        """
        Setup the pin archival system
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @pins.command(
        name="archive",
        usage="[channel]",
        example="#chat"
    )
    @max_concurrency(1, BucketType.guild, wait=False)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_guild=True)
    async def pins_archive(self: "Servers", ctx: Context, *, channel: Optional[TextChannel] = None):
        """
        Archive the pins in a channel
        """
        
        channel = channel or ctx.channel
        if (config := self.bot.cache.get(f"data:pins:{ctx.guild.id}")) is None or (archive_channel := ctx.guild.get_channel(config.channel_id)) is None:
            raise CommandError("The pin archival system **is not set up** in this server.")
              
        if not (pins := await channel.pins()):
            raise CommandError("There aren't any pins in that channel.")
            
        to_delete = await ctx.success(f"Archiving {channel.mention}'s pins...")

        async def do_pinarchive():
            for pin in pins:
                if pin.author.bot:
                    continue
                    
                embed = (
                    Embed(
                        color=pin.author.color, 
                        description=pin.content + ("\n" + "\n".join(attachment.url for attachment in pin.attachments) if pin.attachments else ""),
                        timestamp=pin.created_at
                    )
                    .set_author(name=pin.author, icon_url=pin.author.display_avatar)
                    .set_footer(text=f"Pin archived from #{channel.name}")
                )

                if pin.attachments:
                    embed.set_image(url=pin.attachments[0].url)
                        
                try:
                    await archive_channel.send(
                        embed=embed,
                        view=View().add_item(
                            Button(
                                label="Jump to Message",
                                style=ButtonStyle.link,
                                url=pin.jump_url
                            )
                        )
                    )

                    await pin.unpin()
                    await sleep(1.25)

                except Exception:
                    continue
                
        await do_pinarchive()
        await to_delete.delete()

        return await ctx.success(f"Successfully **archived** this channel's pins! You can now find them in {archive_channel.mention}.")
        
        
    @pins.command(
        name="channel",
        usage="<channel>",
        example="#pins"
    )
    @has_permissions(manage_guild=True)
    async def pins_channel(self: "Servers", ctx: Context, *, channel: TextChannel):
        """
        Set the pin archival channel
        """
        
        if (config := self.bot.cache.get(f"data:pins:{ctx.guild.id}")) and channel.id == config.channel_id:
            raise CommandError("That is **already** the **current pin archive channel**.")
            
        await self.bot.db.execute(
            "INSERT INTO pin_archive (guild_id, channel_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id);",
            ctx.guild.id, channel.id
        )

        self.bot.cache.set(
            f"data:pins:{ctx.guild.id}", Munch(
                channel_id=channel.id,
                is_enabled=config.is_enabled if config else 1
            )
        )
            
        return await ctx.success(f"Successfully **binded** {channel.mention} as the pin archive channel.")
        
        
    @pins.command(
        name="toggle",
        usage="<state>",
        example="true"
    )
    async def pins_toggle(self: "Servers", ctx: Context, state: bool):
        """
        Toggle the pin archival system
        """
        
        if not (data := self.bot.cache.get(f"data:pins:{ctx.guild.id}")):
            raise CommandError(f"The pin archival system **isn't setup** in this server! Please set the archive channel using `{ctx.prefix}pins channel #channel`.")

        if state == data.is_enabled:
            raise CommandError("That is already the current state.")
            
        await self.bot.db.execute(
            "UPDATE pin_archive SET is_enabled = %s WHERE guild_id = %s;",
            state, ctx.guild.id
        )

        data["is_enabled"] = state
        
        self.bot.cache.set(f"data:pins:{ctx.guild.id}", data)
        return await ctx.success(f"Successfully **{'enabled' if state else 'disabled'}** the pin archival system.")
        
        
    @pins.command(name="reset")
    @has_permissions(manage_guild=True)
    async def pins_reset(self: "Servers", ctx: Context):
        """
        Reset the pin archival system configuration
        """
        
        if not self.bot.cache.keys(pattern=f"data:pins:{ctx.guild.id}"):
            raise CommandError("The pin archival system **isn't setup** in this server. ")
            
        await self.bot.db.execute(
            "DELETE FROM pin_archive WHERE guild_id = %s;",
            ctx.guild.id
        )

        self.bot.cache.delete(f"data:pins:{ctx.guild.id}")
        return await ctx.success("Successfully **reset** the **pin archival system configuration**.")
        
        
    @Group(
        name="webhook",
        aliases=("webhooks",),
        usage="<sub command>",
        example="create #rules --name Server Rules --avatar ...",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_webhooks=True)
    @has_permissions(manage_webhooks=True)
    async def webhook(self: "Servers", ctx: Context):
        """
        Set up webhooks in your server
        """

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
    @bot_has_permissions(manage_webhooks=True)
    @has_permissions(manage_webhooks=True)
    async def webhook_create(self: "Servers", ctx: Context, channel: Optional[TextChannel] = None):
        """
        Create a webhook to forward messages to
        """
        
        channel = channel or ctx.channel

        if len(self.bot.cache.keys(pattern=f"data:webhooks:{ctx.guild.id}:*")) > 10:
            raise CommandError(f"This server exceeds {self.bot.user.name.title()}'s **maximum webhook limit** of 10.")
            
        avatar = ctx.parameters.get("avatar") or ctx.author.display_avatar.url
        
        try:
            webhook = await ctx.channel.create_webhook(
                name=ctx.parameters.get("name", "Captain Hook"),
                avatar=await self.bot.proxied_session.read(url=avatar),
                reason=f"Webhook Create [{ctx.author}]"
            )

        except HTTPException as error:
            if error.endswith("Maximum number of webhooks reached (15)"):
                raise CommandError("You have exceeded the **maximum number of webhooks** in this channel (15).")
            
            raise CommandError("Couldn't create a webhook using the provided flags.")
        
        except ValueError as err:
            if str(err) == "Unsupported image type given":
                raise CommandError(f"Unsupported image type given.")
            
            raise

        await self.bot.db.execute(
            "INSERT INTO webhooks (guild_id, identifier, webhook_url, channel_id) VALUES (%s, %s, %s, %s);",
            ctx.guild.id, identifier := hash(webhook.url), webhook.url, channel.id
        )

        self.bot.cache.set(
            f"data:webhooks:{ctx.guild.id}:{identifier}", Munch(
                webhook_url=webhook.url,
                channel_id=channel.id
            )
        )

        return await ctx.success(f"Successfully **created** a **webhook** with the identifier `{identifier}`.")
        
        
    @webhook.command(
        name="delete",
        usage="<identifier>",
        example="6110f4be8664323d"
    )
    @bot_has_permissions(manage_webhooks=True)
    @has_permissions(manage_webhooks=True)
    async def webhook_delete(self: "Servers", ctx: Context, identifier: str):
        """
        Delete a webhook using it's identifier
        """
        
        if not (webhooks := tuple(record.split(":")[-1] for record in self.bot.cache.keys(pattern=f"data:webhooks:{ctx.guild.id}:*"))):
            raise CommandError(f"This server doesn't have any webhooks.\n**NOTE:** Webhooks must be created using the `{ctx.prefix}webhook create` command.")
            
        if identifier not in webhooks:
            raise CommandError("Please provide a **valid** webhook.")
        
        data = self.bot.cache.get(f"data:webhooks:{ctx.guild.id}:{identifier}")

        await Webhook.from_url(
            data.webhook_url,
            client=self.bot
        ).delete()
            
        await self.bot.db.execute(
            "DELETE FROM webhooks WHERE identifier = %s;",
            identifier
        )

        self.bot.cache.delete(f"data:webhooks:{ctx.guild.id}:{identifier}")
        return await ctx.success(f"Successfully **deleted** webhook with identifier `{identifier}`.")
        
        
    @webhook.command(
        name="list",
        aliases=("view", "show")
    )
    @has_permissions(manage_webhooks=True)
    async def webhook_list(self: "Servers", ctx: Context):
        """
        View very available webhook
        """
        
        if not (records := tuple(record.split(":")[-1] for record in self.bot.cache.keys(pattern=f"data:webhooks:{ctx.guild.id}:*"))):
            raise CommandError(f"This server doesn't have any webhooks.\n**NOTE:** Webhooks must be created using the `{ctx.prefix}webhook create` command.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Available Webhooks in '{ctx.guild.name}'"
        )

        for record in records:
            identifier = record
            data = self.bot.cache.get(f"data:webhooks:{ctx.guild.id}:{identifier}")
            
            if channel := ctx.guild.get_channel(data.channel_id):
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
    @has_permissions(manage_webhooks=True)
    async def webhook_send(
        self: "Servers", 
        ctx: Context, 
        identifier: str, 
        *, 
        script: EmbedScript
    ):
        """
        Send a message using an existing webhook
        """
        
        if not self.bot.cache.keys(pattern=f"data:webhooks:{ctx.guild.id}:*"):
            raise CommandError(f"This server doesn't have any webhooks.\n**NOTE:** Webhooks must be created using the `{ctx.prefix}webhook create` command.")
            
        if identifier not in (webhooks := tuple(record.split(":")[-1] for record in self.bot.cache.keys(pattern=f"data:webhooks:{ctx.guild.id}:*"))):
            raise CommandError("That isn't an existing webhook.")
            
        data = self.bot.cache.get(f"data:webhooks:{ctx.guild.id}:{identifier}")
        
        webhook = Webhook.from_url(
            data.webhook_url,
            client=self.bot,
            bot_token=self.bot.http.token
        )

        try:
            webhook = await webhook.fetch()

        except NotFound:
            await self.bot.db.execute(
                "DELETE FROM webhooks WHERE identifier = %s;",
                identifier
            )
            
            self.bot.cache.delete(f"data:webhooks:{ctx.guild.id}:{identifier}")
            raise CommandError("That webhook has been **deleted**.")
        
        webhook_message = await script.send(
            webhook,
            context=ctx,
            strip_text_of_flags=True,
            guild=ctx.guild,
            user=ctx.author,
            extras={
                "username": ctx.parameters.get("username", webhook.name),
                "wait": True
            }
        )

        return await ctx.success(f"Successfully **sent** a message using webhook with identifier `{identifier}`.")
        
        
    @Group(
        name="fakepermissions",
        aliases=("fp", "fakeperm", "fakeperms",),
        usage="<sub command>",
        example="add @Moderator moderate_members",
        extras={
            "permissions": "Server Owner"
        },
        invoke_without_command=True
    )
    @is_guild_owner()
    async def fakepermissions(self: "Servers", ctx: Context):
        """
        Set up fake permissions for a role using Vile
        """
        
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
    @is_guild_owner()
    async def fakepermissions_add(self: "Servers", ctx: Context, role: Role, *, permission: str):
        """
        Grant a fake permission to a role
        """
        
        permission = permission.replace(" ", "_").lower()
        if permission not in Permissions.VALID_FLAGS:
            raise CommandError("Please provide a **valid** permission.")
    
        if permission in self.bot.cache.fake_permissions.get(ctx.guild.id, DICT).get(role.id, TUPLE):
            raise CommandError("That fake permission **already exists** for that role.")
            
        await self.bot.db.execute(
            "INSERT INTO fake_permissions (guild_id, role_id, permission) VALUES (%s, %s, %s);",
            ctx.guild.id, role.id, permission
        )
        
        if ctx.guild.id not in self.bot.cache.fake_permissions:
            self.bot.cache.fake_permissions[ctx.guild.id] = { }
            
        if role.id not in self.bot.cache.fake_permissions[ctx.guild.id]:
            self.bot.cache.fake_permissions[ctx.guild.id][role.id] = [ ]
            
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
    @is_guild_owner()
    async def fakepermissions_remove(self: "Servers", ctx: Context, role: Role, *, permission: str):
        """
        Remove a fake permission from a role
        """
        
        permission = permission.replace(" ", "_").lower()
        if permission not in Permissions.VALID_FLAGS:
            raise CommandError("Please provide a **valid** permission.")
    
        if permission not in self.bot.cache.fake_permissions.get(ctx.guild.id, DICT).get(role.id, TUPLE):
            raise CommandError("That fake permission **does not exist** for that role.")
            
        await self.bot.db.execute(
            "DELETE FROM fake_permissions WHERE role_id = %s AND permission = %s;",
            role.id, permission
        )
        self.bot.cache.fake_permissions[ctx.guild.id][role.id].remove(permission)
        
        return await ctx.success(f"Successfully **removed** fake permission `{permission}` from {role.mention}.")
        
        
    @fakepermissions.command(
        name="list",
        aliases=("view", "show"),
        extras={
            "permissions": "Server Owner"
        }
    )
    @is_guild_owner()
    async def fakepermissions_list(self: "Servers", ctx: Context):
        """
        View very fake permission
        """
        
        if not self.bot.cache.fake_permissions.get(ctx.guild.id, DICT):
            raise CommandError("There **aren't** any **fake permissions** in this server.")
            
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Fake Permissions in '{ctx.guild.name}'"
        )

        for role_id, permissions in self.bot.cache.fake_permissions[ctx.guild.id].items():
            if permissions and (role := ctx.guild.get_role(role_id)):
                rows.append(f"{role.mention}\n{self.bot.reply} **Permissions:** {', '.join(permission.replace('_', ' ').title() for permission in permissions)}")
            
        return await ctx.paginate((embed, rows))
        
        
    @Group(
        name="extract",
        aliases=("export",),
        usage="<sub command>",
        example="stickers",
        invoke_without_command=True
    )
    @has_permissions(administrator=True)
    async def extract(self: "Servers", ctx: Context):
        """
        Sends all of an object in a ZIP file
        """

        return await ctx.send_help(ctx.command.qualified_name)
        
        
    @extract.command(
        name="stickers"
    )
    @has_permissions(administrator=True)
    async def extract_stickers(self: "Servers", ctx: Context):
        """
        Sends all of your server's stickers in a ZIP file
        """
        
        if not ctx.guild.stickers:
            raise CommandError("This server doesn't have any stickers.")
            
        stickers = await gather(*(s.read() for s in ctx.guild.stickers))
        with NamedTemporaryFile(suffix=".zip") as zip_file:
            with ZipFile(zip_file.name, "w") as zip_obj:
                for bytes, sticker in zip(stickers, ctx.guild.stickers):
                    filename = f"{sticker.name}.{sticker.format.name}"
                    zip_obj.writestr(filename, bytes)
            
            return await ctx.reply(file=File(zip_file.name, f"stickers_export_{ctx.guild.id}.zip"))
        
        
    @extract.command(
        name="emojis"
    )
    @has_permissions(administrator=True)
    async def extract_emojis(self: "Servers", ctx: Context):
        """
        Sends all of your server's emojis in a ZIP file
        """
        
        if not ctx.guild.emojis:
            raise CommandError("This server doesn't have any emojis.")
            
        emojis = await gather(*(e.read() for e in ctx.guild.emojis))
        with NamedTemporaryFile(suffix=".zip") as zip_file:
            with ZipFile(zip_file.name, "w") as zip_obj:
                for bytes, emoji in zip(emojis, ctx.guild.emojis):
                    filename = f"{emoji.name}.{'gif' if emoji.animated else 'png'}"
                    zip_obj.writestr(filename, bytes)
            
            return await ctx.reply(file=File(zip_file.name, f"emojis_export_{ctx.guild.id}.zip"))
        

    @Group(
        name="sticker",
        usage="<sub command>",
        example="tag",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_emojis_and_stickers=True)
    @has_permissions(manage_emojis_and_stickers=True)
    async def sticker(self: "Servers", ctx: Context):
        """
        Manage the server stickers
        """

        return await ctx.send_help(ctx.command.qualified_name)
    

    @sticker.command(
        name="add",
        aliases=("create",),
        usage="[image attachment] <name>",
        example="... doggo"
    )
    @bot_has_permissions(manage_emojis_and_stickers=True)
    @has_permissions(manage_emojis_and_stickers=True)
    async def sticker_add(
        self: "Servers", 
        ctx: Context,  
        *, 
        name: str
    ):
        """
        Create a new sticker
        """

        if len(ctx.guild.stickers) == ctx.guild.sticker_limit:
            raise CommandError("This server exceeds the **sticker limit**.")
        
        if len(name) < 2 or len(name) > 30:
            raise CommandError("Please provide a **valid** name between 2 and 30 characters.")
        
            
        image = await Attachment.search(ctx)
       
        image_bytes = await self.bot.session.read(image)
            
        try:
            sticker = await ctx.guild.create_sticker(
                name=name,
                description="...",
                emoji=":neutral_face:",
                file=File(BytesIO(image_bytes)),
                reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]"
            )

        except Exception:
            raise CommandError(f"I couldn't create a sticker using [**this image**]({image}).")
            
        return await ctx.success(f"Successfully **created** the sticker [**{sticker.name}**]({sticker.url}).")
    

    @sticker.command(
        name="remove",
        aliases=("delete",),
        usage="<sticker>",
        example="sad"
    )
    @bot_has_permissions(manage_emojis_and_stickers=True)
    @has_permissions(manage_emojis_and_stickers=True)
    async def sticker_remove(
        self: "Servers", 
        ctx: Context, 
        *, 
        sticker: Sticker
    ):
        """
        Delete an existing sticker
        """

        await sticker.delete(reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]")
        raise CommandError(f"Successfully **deleted** that sticker.")
    

    @sticker.command(
        name="rename",
        aliases=("name",),
        usage="<sticker>",
        example="sad lol"
    )
    @bot_has_permissions(manage_emojis_and_stickers=True)
    @has_permissions(manage_emojis_and_stickers=True)
    async def sticker_rename(
        self: "Servers", 
        ctx: Context, 
        sticker: Sticker, 
        *, 
        name: str
    ):
        """
        Rename an existing sticker
        """

        if len(name) < 2 or len(name) > 30:
            raise CommandError("Please provide a **valid** name between 2 and 30 characters.")
        
        await sticker.edit(
            name=name, 
            reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]"
        )

        raise CommandError(f"Successfully **renamed** that sticker to: \n```{name}```")
    

    @sticker.command(
        name="clean",
        aliases=("strip",)
    )
    @bot_has_permissions(manage_emojis_and_stickers=True)
    @has_permissions(manage_emojis_and_stickers=True)
    async def sticker_clean(self: "Servers", ctx: Context):
        """
        Remove vanity links from every sticker name
        """

        if not ctx.guild.stickers:
            raise CommandError(f"There aren't any **stickers** in this server.")
        
        async def clean_sticker(sticker):
            
            if "/" not in sticker.name:
                return
            
            name = multi_replace(sticker.name, {
                **{word: "" for word in sticker.name.split() if "/" in word}
            })

            if len(name) < 2:
                return
            
            return await sticker.edit(
                name=name.strip(),
                reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]"
            )
        
        cleaned = tuple(filter(lambda s: s, await gather(*(
            clean_sticker(sticker)
            for sticker in ctx.guild.stickers
        ))))

        return await ctx.success(f"Successfully **cleaned** `{len(cleaned)}` stickers.")
    

    @sticker.command(
        name="tag"
    )
    @bot_has_permissions(manage_emojis_and_stickers=True)
    @has_permissions(manage_emojis_and_stickers=True)
    @guild_has_vanity()
    async def sticker_tag(self: "Servers", ctx: Context):
        """
        Add your vanity link to every sticker name
        """

        if not ctx.guild.stickers:
            raise CommandError("There aren't any **stickers** in this server.")
        
        async def tag_sticker(sticker):
            
            if f".gg/{ctx.guild.vanity_url_code}" in sticker.name:
                return
            
            return await sticker.edit(
                name=sticker.name[:30-len(f" .gg/{ctx.guild.vanity_url_code}")] + f" .gg/{ctx.guild.vanity_url_code}".strip(),
                reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]"
            )
        
        tagged = tuple(filter(lambda s: s, await gather(*(
            tag_sticker(sticker)
            for sticker in ctx.guild.stickers
        ))))

        return await ctx.success(f"Successfully **tagged** `{len(tagged)}` stickers.")
    

    @Group(
        name="emoji",
        usage="<sub command>",
        example="removeduplicates",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_emojis=True)
    @has_permissions(manage_emojis=True)
    async def emoji(self: "Servers", ctx: Context):
        """
        Manage the server emojis
        """
        
        return await ctx.send_help(ctx.command.qualified_name)
    

    @emoji.command(
        name="add",
        aliases=("create",),
        usage="[image attachment] <name>",
        example="... doggo"
    )
    @bot_has_permissions(manage_emojis=True)
    @has_permissions(manage_emojis=True)
    async def emoji_add(
        self: "Servers", 
        ctx: Context,
        *, 
        name: str
    ):
        """
        Create a new emoji
        """

        if len(ctx.guild.emojis) == ctx.guild.emoji_limit*2:
            raise CommandError("This server exceeds the **emoji limit**.")
        
        if len(name) < 2 or len(name) > 30:
            raise CommandError("Please provide a **valid** name between 2 and 30 characters.")
        
        if not (image := await Attachment.search(ctx)):
            raise CommandError("I couldn't fetch any recent images from this channel.")
            
        try:
            emoji = await ctx.guild.create_custom_emoji(
                name=name,
                image=await self.bot.session.read(image),
                reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]"
            )
            
        except HTTPException as error:
            if "(error code: 30008)" in str(error):
                raise CommandError("This server doesn't have enough **emoji slots**.")

            raise CommandError("Please provide a **valid** image.")
            
        return await ctx.success(f"Successfully **created** the emoji [**{emoji.name}**]({emoji.url}).")
    

    @emoji.command(
        name="addmultiple",
        aliases=("addmany",),
        usage="<emojis>",
        example="..."
    )
    @bot_has_permissions(manage_emojis=True)
    @has_permissions(manage_emojis=True)
    async def emoji_addmultiple(
        self: "Servers", 
        ctx: Context, 
        emojis: Greedy[Union[ PartialEmoji, Emoji ]], 
    ):
        """
        Create multiple emojis
        """

        if len(ctx.guild.emojis) == ctx.guild.emoji_limit*2:
            raise CommandError("This server exceeds the **emoji limit**.")
        
        # I can't gather this without doing something stupid
        
        created = 0

        for emoji in emojis[:(ctx.guild.emoji_limit * 2)-len(ctx.guild.emojis)]:
            await sleep(1e-3)
            
            try:
                await ctx.guild.create_custom_emoji(
                    name=emoji.name,
                    image=await emoji.read(),
                    reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]"
                )
                
                created += 1

            except Exception:
                continue

        if created == 0:
            raise CommandError("I couldn't add any emojis.")

        if created != len(emojis):
            return await ctx.success(f"Successfully **created** `{created}` emojis, unable to add more.")
        
        return await ctx.success(f"Successfully **created** `{created}` emojis.")
    

    @emoji.command(
        name="addfromattachments",
        aliases=("fromattachments", "fromfiles")
    )
    @bot_has_permissions(manage_emojis=True)
    @has_permissions( manage_emojis=True)
    async def emoji_addfromattachments(self: "Servers", ctx: Context):
        """
        Create emojis from attachments
        """

        if len(ctx.guild.emojis) == ctx.guild.emoji_limit*2:
            raise CommandError("This server exceeds the **emoji limit**.")
        
        if not ctx.message.attachments:
            raise CommandError("This message doesn't have any attachments.")
        
        # I can't gather this without doing something stupid
        
        created = 0

        for attachment in ctx.message.attachments[:(ctx.guild.emoji_limit * 2)-len(ctx.guild.emojis)]:
            await sleep(1e-3)
            
            try:
                await ctx.guild.create_custom_emoji(
                    name=attachment.filename.replace(".", "").replace("png", "").replace("jpg", "").replace("gif", ""),
                    image=await attachment.read(),
                    reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]"
                )

                created += 1

            except Exception:
                continue

        if created == 0:
            raise CommandError("I couldn't add any emojis.")

        if created != len(ctx.message.attachments):
            return await ctx.success(f"Successfully **created** `{created}` emojis, unable to add more.")
        
        return await ctx.success(f"Successfully **created** `{created}` emojis.")
    

    @emoji.command(
        name="remove",
        aliases=("delete",),
        usage="<emoji>",
        example="sad"
    )
    @bot_has_permissions(manage_emojis=True)
    @has_permissions(manage_emojis=True)
    async def emoji_remove(
        self: "Servers", 
        ctx: Context, 
        *, 
        emoji: Emoji
    ):
        """
        Delete an existing emoji
        """

        await emoji.delete(reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]")
        return await ctx.success(f"Successfully **deleted** that emoji.")
    

    @emoji.command(
        name="rename",
        aliases=("name",),
        usage="<emoji>",
        example="sad lol"
    )
    @bot_has_permissions(manage_emojis=True)
    @has_permissions(manage_emojis=True)
    async def emoji_rename(
        self: "Servers", 
        ctx: Context, 
        emoji: Emoji, 
        *, 
        name: str
    ):
        """
        Rename an existing emoji
        """

        if len(name) < 2 or len(name) > 30:
            raise CommandError("Please provide a **valid** name between 2 and 30 characters.")
        
        await emoji.edit(
            name=name, 
            reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]"
        )

        return await ctx.success(f"Successfully **renamed** that emoji to: \n```{name}```")
    

    @emoji.command(
        name="removeduplicates"
    )
    @bot_has_permissions(manage_emojis=True)
    @has_permissions(manage_emojis=True)
    async def emoji_removeduplicates(self: "Servers", ctx: Context):
        """
        Delete duplicate emojis
        """

        if not ctx.guild.emojis:
            raise CommandError(f"There aren't any **emojis** in this server.")
            
        duplicates = set()
        seen = set()
        emojis_bytes = await gather(*(
            emoji.read()
            for emoji in ctx.guild.emojis
        ))

        for emoji, emoji_bytes in zip(ctx.guild.emojis, emojis_bytes):
            if emoji_bytes in seen:
                duplicates.add(emoji)

            else:
                seen.add(emoji_bytes)

        removed = await gather(*(
            duplicate.delete(reason=f"{self.bot.user.name.title()} Utilities [{ctx.author}]: Duplicate emoji")
            for duplicate in duplicates
        ))

        return await ctx.success(f"Successfully **removed** `{len(removed)}` duplicate emojis.")
    

    @Command(
        name="embed",
        aliases=("parser", "parse", "createembed"),
        usage="<script>",
        example="{embed} {title: hi} {description: lol}"
    )
    async def embed(
        self: "Servers",
        ctx: Context,
        *,
        script: EmbedScript
    ):
        """
        Send a message using the embed parser
        """

        return await script.send(
            ctx,
            guild=ctx.guild,
            user=ctx.author
        )
    

    @Group(
        name="rank",
        usage="<role> or <sub command>",
        example="@Intermediate",
        invoke_without_command=True
    )
    @bot_has_permissions(manage_roles=True)
    async def rank(
        self: "Servers",
        ctx: Context,
        *,
        role: Role
    ):
        """
        Join/leave a rank
        """

        if role.id not in await self.bot.db.fetch("SELECT role_id FROM ranks WHERE guild_id = %s", ctx.guild.id):
            raise CommandError("That role is not a joinable rank.")
        
        if not role.is_assignable():
            raise CommandError("I can't assign that role.")
        
        if role.is_dangerous():
            raise CommandError("That role has **dangerous** permissions.")
        
        if role in ctx.author.roles:
            await ctx.author.remove_roles(
                role, 
                reason=f"{self.bot.user.name.title()} Rank Roles"
            )

            return await ctx.success(f"Successfully **left** the {role.mention} rank.")
        
        await ctx.author.add_roles(
            role, 
            reason=f"{self.bot.user.name.title()} Rank Roles"
        )

        return await ctx.success(f"Successfully **joined** the {role.mention} rank.")
    

    @rank.command(
        name="add",
        usage="<role>",
        example="@Intermediate"
    )
    @has_permissions(manage_roles=True)
    async def rank_add(
        self: "Servers",
        ctx: Context,
        *,
        role: Role
    ):
        """
        Add a new rank for members to join
        """
        
        if role.id in await self.bot.db.fetch("SELECT role_id FROM ranks WHERE guild_id = %s", ctx.guild.id):
            raise CommandError("That role is already a joinable rank.")
        
        if role.is_dangerous():
            raise CommandError("That role has **dangerous** permissions.")
        
        await self.bot.db.execute(
            "INSERT INTO ranks (guild_id, role_id) VALUES (%s, %s);",
            ctx.guild.id, role.id
        )
        
        return await ctx.success(f"Successfully **added** {role.mention} as a joinable rank.")
    

    @rank.command(
        name="remove",
        usage="<role>",
        example="@Intermediate"
    )
    @has_permissions(manage_roles=True)
    async def rank_remove(
        self: "Servers",
        ctx: Context,
        *,
        role: Role
    ):
        """
        Remove an existing rank
        """
        
        if role.id not in await self.bot.db.fetch("SELECT role_id FROM ranks WHERE guild_id = %s", ctx.guild.id):
            raise CommandError("That role is not a joinable rank.")
        
        await self.bot.db.execute(
            "DELETE FROM ranks WHERE guild_id = %s AND role_id = %s;",
            ctx.guild.id, role.id
        )
        
        return await ctx.success(f"Successfully **removed** {role.mention} from the joinable ranks.")
    

    @rank.command(
        name="list",
        aliases=("view", "show")
    )
    async def rank_list(
        self: "Servers",
        ctx: Context
    ):
        """
        List all joinable ranks
        """
        
        if not (roles := await self.bot.db.fetch("SELECT role_id FROM ranks WHERE guild_id = %s", ctx.guild.id)):
            raise CommandError("There aren't any joinable ranks in this server.")
        
        rows, embed = [ ], Embed(
            color=self.bot.color,
            title=f"Joinable Ranks in '{ctx.guild.name}'"
        )

        for role_id in roles:
            if role := ctx.guild.get_role(role_id):
                rows.append(f"{role.mention}")
            
        return await ctx.paginate((embed, rows))
        
        
async def setup(bot: VileBot) -> NoReturn:
    """
    Add the Servers cog to the bot.

    Parameters:
        bot (VileBot): An instance of the VileBot class.
    """

    await bot.add_cog(Servers(bot))