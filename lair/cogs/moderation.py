from utilities.managers import Context, Wrench
from utilities.lair import Lair
from discord import User, Member, Embed, BanEntry, Forbidden
from utilities.general.converters import cMember, Reason, FetchBannedUser, Roles
from utilities.scripting import EmbedBuilder
from discord.ext.commands import command, has_permissions, group
from typing import Annotated, Optional, List, Union
from discord.abc import Snowflake


class Moderation(Wrench):

    async def ban_response(self, ctx: Context, member: cMember | Member | User):
        response = await self.bot.db.fetchval('SELECT response FROM custom_ban_response WHERE guild_id = $1', ctx.guild.id)
        if response:
            builder = EmbedBuilder(ctx, member)
            embed = await builder.build_embed(response['response'])
            return await ctx.send(embed)
        else:
            return await ctx.done(f'{member.mention} has been **banned**.')
            
    async def kick_response(self, ctx: Context, member: cMember | Member | User):
        response = await self.bot.db.fetchval('SELECT response FROM custom_kick_response WHERE guild_id = $1', ctx.guild.id)
        if response:
            builder = EmbedBuilder(ctx, member)
            embed = await builder.build_embed(response['response'])
            return await ctx.send(embed)
        else:
            return await ctx.done(f'{member.mention} has been **kicked**.')
        
    @command(name='ban', aliases=['b'], brief='Bans a member from the server.')
    @has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: Context,
        member: Annotated[Snowflake, cMember] | Member | User,
        *,
        reason: Annotated[Optional[str], Reason] = None
    ) -> Embed:
        if member.premium_since:
            msg = await ctx.error(
                f'{member.mention} is a booster, are you sure you want to ban them?'
            )
            conf = await ctx.confirm(ctx, msg)
            if conf:
                await ctx.guild.ban(member, reason=reason)
                return await self.ban_response(ctx, member)
            else:
                return await msg.edit(content='Cancelled.')
            
        else:
            await ctx.guild.ban(member, reason=reason)
            return await self.ban_response(ctx, member)
        
    @command(name='kick', aliases=['boot'], brief='Kicks a member from the server.')
    @has_permissions(kick_members=True)
    async def kick(
        self,
        ctx: Context,
        member: Annotated[Snowflake, cMember] | Member | User,
        *,
        reason: Annotated[Optional[str], Reason] = None
    ) -> Embed:
        if member.premium_since:
            msg = await ctx.error(
                f'{member.mention} is a booster, are you sure you want to kick them?'
            )
            conf = await ctx.confirm(ctx, msg)
            if conf:
                await ctx.guild.ban(member, reason=reason)
                return await self.kick_response(ctx, member)
            else:
                return await msg.edit(content='Cancelled.')
            
        else:
            await ctx.guild.ban(member, reason=reason)
            return await self.kick_response(ctx, member)
        
    @command(name="unban", brief="Unban a member from the current guild.")
    @has_permissions(ban_members=True)
    async def unban(
        self,
        ctx: Context,
        member: Annotated[BanEntry, FetchBannedUser],
        *,
        reason: Annotated[Optional[str], Reason] = None,
    ):
        if reason is None:
            reason = f"Unbanned by {ctx.author} ({ctx.author.id})"
        await ctx.guild.unban(member.user, reason=reason)
        if member.reason:
            await ctx.done(
                f"**{member.user}** has been unbanned, Previously banned for: {member.reason}"
            )
        else:
            return await ctx.success(
                f"**{member.user}** has been unbanned."
            )
        

    @command(name="role", brief="Add/Remove a role from a user.")
    @has_permissions(manage_roles=True)
    async def role(
        self,
        ctx: Context,
        member: cMember | Member,
        *roles: Roles
    ):
        added, removed, total = [], [], []

        for role in roles:
            if role in member.roles:
                removed.append(role)
            else:
                added.append(role)

        if added:
            await member.add_roles(*added, atomic=False)
            total.extend(f'**{role.name}**' for role in added)

        if removed:
            await member.remove_roles(*removed, atomic=False)
            total.extend(f'**{role.name}**' for role in removed)

        if total:
            if len(total) > 1:
                await ctx.send(f'Added the roles {", ".join(total)} to {member.mention}')
            elif added:
                await ctx.send(f'Added the role {" ".join(total)} to {member.mention}')
            else:
                await ctx.send(f'Removed the role {" ".join(total)} from {member.mention}')





async def setup(bot: Lair):
    await bot.add_cog(Moderation(bot))