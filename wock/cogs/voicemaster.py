from contextlib import suppress

import discord

from discord.ext import commands

from helpers import checks, wock


class voicemaster(commands.Cog, name="VoiceMaster Integration"):
    def __init__(self, bot):
        self.bot: wock.wockSuper = bot
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 8, commands.BucketType.member)
        self.cd_mapping_global = commands.CooldownMapping.from_cooldown(2, 4, commands.BucketType.guild)

    async def cog_load(self):
        """Cleanup empty voice channels"""

        await self.bot.wait_until_ready()

        async for voicemaster_channel in self.bot.db.fetchiter("SELECT channel_id FROM voicemaster"):
            if channel := self.bot.get_channel(voicemaster_channel.get("channel_id")):
                if list(filter(lambda member: not member.bot, channel.members)):
                    continue

                try:
                    await channel.delete(reason="VoiceMaster Channel Cleanup")
                except discord.HTTPException:
                    pass

            await self.bot.db.execute(
                "DELETE FROM voicemaster WHERE channel_id = $1",
                voicemaster_channel.get("channel_id"),
            )

    @commands.Cog.listener("on_voice_state_update")
    async def voicemaster_creation(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Create the temporary voice channel"""

        if not after.channel or getattr(before.channel, "id", None) == getattr(after.channel, "id", None):
            return

        configuration = await self.bot.db.fetch_config(member.guild.id, "voicemaster")
        if not configuration:
            return

        if after.channel.id != configuration.get("channel_id"):
            return

        _bucket_global = self.cd_mapping_global.get_bucket(member)
        if retry_after := _bucket_global.update_rate_limit():
            return

        _bucket = self.cd_mapping.get_bucket(member)
        if retry_after := _bucket.update_rate_limit():
            try:
                await member.disconnect(reason=f"VoiceMaster Creation Cooldown: {retry_after:.2f} seconds")
            except discord.HTTPException:
                pass
            return

        category = member.guild.get_channel(configuration.get("category_id")) or after.channel.category
        if bitrate := configuration.get("default_bitrate"):
            if bitrate > int(member.guild.bitrate_limit):
                bitrate = int(member.guild.bitrate_limit)
        else:
            bitrate = int(member.guild.bitrate_limit)
        channel = await member.guild.create_voice_channel(
            name=(
                await wock.EmbedScript(configuration.get("default_name")).resolve_variables(
                    guild=member.guild,
                    user=member,
                )
                if configuration.get("default_name")
                else f"{member.name}'s channel"
            ),
            category=category,
            bitrate=bitrate,
            rtc_region=configuration.get("default_region"),
            reason=f"VoiceMaster Creation: {member}",
        )

        await channel.edit(sync_permissions=True)
        try:
            await member.move_to(channel, reason=f"VoiceMaster Creation: {member}")
        except discord.HTTPException:
            try:
                await channel.delete(reason=f"VoiceMaster Creation Failure: {member}")
            except discord.HTTPException:
                pass
            return

        await self.bot.db.execute(
            "INSERT INTO voicemaster (guild_id, owner_id, channel_id) VALUES ($1, $2, $3)",
            member.guild.id,
            member.id,
            channel.id,
        )

        if default_role := member.guild.get_role(configuration.get("default_role")):
            if default_role not in member.roles and default_role.is_assignable():
                try:
                    await member.add_roles(default_role, reason=f"VoiceMaster Default Role: {member}")
                except discord.HTTPException:
                    pass

    @commands.Cog.listener("on_voice_state_update")
    async def voicemaster_deletion(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Delete the temporary voice channel"""

        if not before.channel or getattr(before.channel, "id", None) == getattr(after.channel, "id", None):
            return

        voicemaster_channel = await self.bot.db.fetchrow(
            "SELECT * FROM voicemaster WHERE guild_id = $1 AND channel_id = $2",
            member.guild.id,
            before.channel.id,
        )
        if not voicemaster_channel:
            return

        configuration = await self.bot.db.fetch_config(member.guild.id, "voicemaster")

        if default_role := member.guild.get_role(configuration.get("default_role")):
            if default_role in member.roles and default_role.is_assignable():
                try:
                    await member.remove_roles(default_role, reason=f"VoiceMaster Default Role: {member}")
                except discord.HTTPException:
                    pass

        if list(filter(lambda member: not member.bot, before.channel.members)):
            return

        voicemaster_channel = await self.bot.db.fetchrow(
            "SELECT * FROM voicemaster WHERE guild_id = $1 AND channel_id = $2",
            member.guild.id,
            before.channel.id,
        )
        if not voicemaster_channel:
            return

        try:
            await before.channel.delete(reason="VoiceMaster Deletion")
        except discord.HTTPException:
            pass

        await self.bot.db.execute(
            "DELETE FROM voicemaster WHERE guild_id = $1 AND channel_id = $2",
            member.guild.id,
            before.channel.id,
        )

    @commands.group(
        name="voicemaster",
        usage="(subcommand) <args>",
        example="setup",
        aliases=["voice", "vm", "vc"],
        invoke_without_command=True,
    )
    async def voicemaster(self, ctx: wock.Context):
        """Make temporary voice channels"""

        await ctx.send_help()

    @voicemaster.command(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def voicemaster_setup(self, ctx: wock.Context):
        """Setup the VoiceMaster configuration"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "voicemaster") or {}
        if ctx.guild.get_channel(configuration.get("channel_id")):
            return await ctx.warn(f"The **VoiceMaster** channels are already setup\n> Use `{ctx.prefix}voicemaster reset` to reset the configuration")

        category = await ctx.guild.create_category(name="Voice Channels")
        channel = await ctx.guild.create_voice_channel(name="Join to Create", category=category)

        await category.set_permissions(
            ctx.guild.default_role,
            connect=True,
            speak=True,
            view_channel=True,
            stream=True,
        )
        await channel.edit(sync_permissions=True)

        await self.bot.db.update_config(
            ctx.guild.id,
            "voicemaster",
            {
                "category_id": category.id,
                "channel_id": channel.id,
                "interface_id": None,
            },
        )
        await ctx.approve("Finished creating the **VoiceMaster** channels\n> You can move or rename them as you wish")

    @voicemaster.command(name="reset")
    @commands.has_permissions(manage_guild=True)
    async def voicemaster_reset(self, ctx: wock.Context):
        """Reset the VoiceMaster configuration"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "voicemaster")
        if not configuration:
            return await ctx.warn(f"The **VoiceMaster** channels are not setup\n> Use `{ctx.prefix}voicemaster setup` to setup the configuration")

        category = ctx.guild.get_channel(configuration.get("category_id"))
        channel = ctx.guild.get_channel(configuration.get("channel_id"))
        interface = ctx.guild.get_channel(configuration.get("interface_id"))

        if category:
            try:
                await category.delete()
            except:
                pass  # The category likely got deleted
        if channel:
            try:
                await channel.delete()
            except:
                pass  # The channel lieky got deleted
        if interface:
            try:
                await interface.delete()
            except:
                pass  # The interface likely got deleted

        await self.bot.db.update_config(ctx.guild.id, "voicemaster", {})
        await ctx.approve("Reset the **VoiceMaster** configuration")

    @voicemaster.command(name="category", usage="(category)", example="Voice Channels", aliases=["redirect"])
    @commands.has_permissions(manage_guild=True)
    async def voicemaster_category(self, ctx: wock.Context, category: discord.CategoryChannel):
        """Set the category for VoiceMaster channels"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "voicemaster")
        if not configuration:
            return await ctx.warn(f"The **VoiceMaster** channels are not setup\n> Use `{ctx.prefix}voicemaster setup` to setup the configuration")

        configuration["category_id"] = category.id
        await self.bot.db.update_config(ctx.guild.id, "voicemaster", configuration)
        await ctx.approve(f"Now redirecting **VoiceMaster** channels to **#{category.name}**")

    @voicemaster.group(
        name="default",
        usage="(subcommand) <args>",
        example="bitrate 64kbps",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    async def voicemaster_default(self, ctx: wock.Context):
        """Set the default settings for VoiceMaster channels"""

        await ctx.send_help()

    @voicemaster_default.command(name="bitrate", usage="(bitrate)", example="64kbps")
    @commands.has_permissions(manage_guild=True)
    async def voicemaster_default_bitrate(self, ctx: wock.Context, bitrate: wock.Bitrate):
        """Set the default bitrate for VoiceMaster channels"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "voicemaster")
        if not configuration:
            return await ctx.warn(f"The **VoiceMaster** channels are not setup\n> Use `{ctx.prefix}voicemaster setup` to setup the configuration")

        configuration["default_bitrate"] = bitrate * 1000
        await self.bot.db.update_config(ctx.guild.id, "voicemaster", configuration)
        await ctx.approve(f"Set the **default bitrate** to `{bitrate}kbps`")

    @voicemaster_default.command(
        name="role",
        usage="(role)",
        example="@VoiceMaster",
    )
    @commands.has_permissions(manage_guild=True, manage_roles=True)
    async def voicemaster_default_role(self, ctx: wock.Context, *, role: wock.Role):
        """Set the default role for VoiceMaster owners"""

        await wock.Role().manageable(ctx, role)
        await wock.Role().dangerous(ctx, role, "assign")

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "voicemaster")
        if not configuration:
            return await ctx.warn(f"The **VoiceMaster** channels are not setup\n> Use `{ctx.prefix}voicemaster setup` to setup the configuration")

        configuration["default_role"] = role.id
        await self.bot.db.update_config(ctx.guild.id, "voicemaster", configuration)
        await ctx.approve(f"Set the **default role** to {role.mention}")

    @voicemaster_default.command(
        name="region",
        usage="(region)",
        example="Sydney",
    )
    @commands.has_permissions(manage_guild=True)
    async def voicemaster_default_region(self, ctx: wock.Context, *, region: wock.Region):
        """Set the default region for VoiceMaster channels"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "voicemaster")
        if not configuration:
            return await ctx.warn(f"The **VoiceMaster** channels are not setup\n> Use `{ctx.prefix}voicemaster setup` to setup the configuration")

        configuration["default_region"] = region
        await self.bot.db.update_config(ctx.guild.id, "voicemaster", configuration)
        await ctx.approve(f"Set the **default region** to `{(region or 'Automatic').replace('-', ' ').title().replace('Us', 'US')}`")

    @voicemaster_default.command(
        name="name",
        usage="(text)",
        example="{user.name}'s trap house",
    )
    @commands.has_permissions(manage_guild=True)
    async def voicemaster_default_name(self, ctx: wock.Context, *, text: str):
        """Set the default name for VoiceMaster channels"""

        configuration = await self.bot.db.fetch_config(ctx.guild.id, "voicemaster")
        if not configuration:
            return await ctx.warn(f"The **VoiceMaster** channels are not setup\n> Use `{ctx.prefix}voicemaster setup` to setup the configuration")

        configuration["default_name"] = text
        await self.bot.db.update_config(ctx.guild.id, "voicemaster", configuration)
        await ctx.approve(f"Set the **default name** to `{text}`")

    @voicemaster.command(
        name="name",
        usage="(new name)",
        example="club house",
        aliases=["rename"],
    )
    @checks.voicemaster_channel()
    async def voicemaster_name(self, ctx: wock.Context, *, new_name: str):
        """Rename your voice channel"""

        try:
            await ctx.author.voice.channel.edit(name=new_name[:32], reason=f"VoiceMaster Rename: {ctx.author}")
        except discord.RateLimited:
            await ctx.warn("You're renaming your **voice channel** too fast")
        else:
            await ctx.approve(f"Renamed your **voice channel** to `{new_name}`")

    @voicemaster.command(name="bitrate", usage="(bitrate)", example="64kbps")
    @checks.voicemaster_channel()
    async def voicemaster_bitrate(self, ctx: wock.Context, bitrate: wock.Bitrate):
        """Set the bitrate for your voice channel"""

        await ctx.author.voice.channel.edit(bitrate=bitrate * 1000, reason=f"VoiceMaster Bitrate: {ctx.author}")
        await ctx.approve(f"Set the **bitrate** of your **voice channel** to `{bitrate}kbps`")

    @voicemaster.command(name="region", usage="(region)", example="Sydney")
    @checks.voicemaster_channel()
    async def voicemaster_region(self, ctx: wock.Context, *, region: wock.Region):
        """Set the region for your voice channel"""

        await ctx.author.voice.channel.edit(rtc_region=region, reason=f"VoiceMaster Region: {ctx.author}")
        await ctx.approve(
            f"Set the **region** of your **voice channel** to `{(region or 'Automatic').replace('-', ' ').title().replace('Us', 'US')}`"
        )

    @voicemaster.command(name="limit", usage="(user limit)", example="10", aliases=["max"])
    @checks.voicemaster_channel()
    async def voicemaster_limit(self, ctx: wock.Context, limit: int = 0):
        """Set the user limit for your voice channel"""

        if limit < 0 or limit > 99:
            return await ctx.warn("The **user limit** must be between `0` and `99`")

        await ctx.author.voice.channel.edit(user_limit=limit, reason=f"VoiceMaster Limit: {ctx.author}")
        await ctx.approve(f"Set the **user limit** of your **voice channel** to `{limit or 'unlimited'}`")

    @voicemaster.command(name="lock")
    @checks.voicemaster_channel()
    async def voicemaster_lock(self, ctx: wock.Context):
        """Prevent members from joining your voice channel"""

        if ctx.author.voice.channel.overwrites_for(ctx.guild.default_role).connect is False:
            return await ctx.warn("Your **voice channel** is already **locked**")

        overwrite = ctx.author.voice.channel.overwrites_for(ctx.guild.default_role)
        overwrite.connect = False
        overwrite.send_messages = True
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.approve("Your **voice channel** is now **locked**")

    @voicemaster.command(name="unlock")
    @checks.voicemaster_channel()
    async def voicemaster_unlock(self, ctx: wock.Context):
        """Allow members to join your voice channel"""

        if ctx.author.voice.channel.overwrites_for(ctx.guild.default_role).connect:
            return await ctx.warn("Your **voice channel** is already **unlocked**")

        overwrite = ctx.author.voice.channel.overwrites_for(ctx.guild.default_role)
        overwrite.connect = None
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.approve("Your **voice channel** is now **unlocked**")

    @voicemaster.command(name="hide", aliases=["private", "ghost"])
    @checks.voicemaster_channel()
    async def voicemaster_hide(self, ctx: wock.Context):
        """Hide your voice channel from members"""

        if ctx.author.voice.channel.overwrites_for(ctx.guild.default_role).view_channel is False:
            return await ctx.warn("Your **voice channel** is already **hidden**")

        overwrite = ctx.author.voice.channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = False
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.approve("Your **voice channel** is now **hidden**")

    @voicemaster.command(name="reveal", aliases=["visible", "unhide", "unghost"])
    @checks.voicemaster_channel()
    async def voicemaster_reveal(self, ctx: wock.Context):
        """Reveal your voice channel to members"""

        if ctx.author.voice.channel.overwrites_for(ctx.guild.default_role).view_channel is not False:
            return await ctx.warn("Your **voice channel** is already **visible**")

        overwrite = ctx.author.voice.channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = None
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.approve("Your **voice channel** is now **visible**")

    @voicemaster.command(
        name="permit",
        usage="(member or role)",
        example="rx#1337",
        aliases=["allow", "grant"],
    )
    @checks.voicemaster_channel()
    async def voicemaster_permit(self, ctx: wock.Context, *, target: wock.Member | wock.Role):
        """Allow a member or role to join your voice channel"""

        if ctx.author.voice.channel.overwrites_for(target).connect is True:
            return await ctx.warn(f"**{target}** is already permitted to join your **voice channel**")

        overwrite = ctx.author.voice.channel.overwrites_for(target)
        overwrite.connect = True
        overwrite.view_channel = True
        await ctx.author.voice.channel.set_permissions(target, overwrite=overwrite)
        await ctx.approve(f"Permitted {target.mention} access to your **voice channel**")

    @voicemaster.command(
        name="reject",
        usage="(member or role)",
        example="rx#1337",
        aliases=["deny", "unpermit", "unallow", "ungrant"],
    )
    @checks.voicemaster_channel()
    async def voicemaster_reject(self, ctx: wock.Context, *, target: wock.Member | wock.Role):
        """Disallow a member or role from joining your voice channel"""

        if ctx.author.voice.channel.overwrites_for(target).connect is False or ctx.author.voice.channel.overwrites_for(target).view_channel is False:
            return await ctx.warn(f"**{target}** is already rejected from joining your **voice channel**")

        overwrite = ctx.author.voice.channel.overwrites_for(target)
        overwrite.connect = False
        overwrite.view_channel = None
        await ctx.author.voice.channel.set_permissions(target, overwrite=overwrite)
        await ctx.approve(f"Rejected {target.mention} access to your **voice channel**")

        if isinstance(target, discord.Member) and target in ctx.author.voice.channel.members:
            with suppress(discord.HTTPException):
                await target.move_to(None)

    @voicemaster.command(name="claim", aliases=["steal"])
    async def voicemaster_claim(self, ctx: wock.Context):
        """Claim an unowned voice channel"""

        owner_id = await checks.voicemaster_channel().predicate(ctx, claim=True)
        if owner_id in (member.id for member in ctx.author.voice.channel.members):
            return await ctx.warn("This **voice channel** is already **claimed**")

        await self.bot.db.execute(
            "UPDATE voicemaster SET owner_id = $3 WHERE guild_id = $1 AND channel_id = $2",
            ctx.guild.id,
            ctx.author.voice.channel.id,
            ctx.author.id,
        )
        await ctx.approve(f"You're now the **owner** of this **voice channel**")

    @voicemaster.command(name="transfer", usage="(member)", example="rx#1337")
    @checks.voicemaster_channel()
    async def voicemaster_transfer(self, ctx: wock.Context, *, member: wock.Member):
        """Transfer ownership of your voice channel to another member"""

        if member.id == ctx.author.id:
            return await ctx.warn("You can't transfer **ownership** to yourself")
        if member.id not in (member.id for member in ctx.author.voice.channel.members):
            return await ctx.warn(f"**{member}** is not in this **voice channel**")

        await self.bot.db.execute(
            "UPDATE voicemaster SET owner_id = $3 WHERE guild_id = $1 AND channel_id = $2",
            ctx.guild.id,
            ctx.author.voice.channel.id,
            member.id,
        )
        await ctx.approve(f"Transferred **ownership** of this **voice channel** to {member.mention}")


async def setup(bot: wock.wockSuper):
    await bot.add_cog(voicemaster(bot))
