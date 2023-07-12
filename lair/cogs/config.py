import datetime
from typing import Literal
from discord.ext.commands import command, group
from discord import Embed
from utilities.lair import Lair
from utilities.managers import Wrench, Context
from utilities.patch import has_permissions
from utilities.general import Role
from utilities import config


class Configuration(Wrench):
    @command(
        name="guildprefix", aliases=["gp"], brief="Change lairs prefix in the server."
    )
    @has_permissions(manage_guild=True)
    async def guildprefix(self, ctx: Context, prefix: str):
        if len(prefix) > 20:
            return await ctx.error("**Prefix** length exceeded limit **20**.")
        await self.bot.db.execute(
            """
                INSERT INTO guildprefix (guild_id, prefix)
                VALUES ($1, $2)
                ON CONFLICT (guild_id)
                DO UPDATE SET prefix = excluded.prefix
            """,
            ctx.guild.id,
            prefix,
        )
        await self.bot.cache.set(f"prefix:{ctx.guild.id}", prefix)
        return await ctx.done(f"Changed the **guildprefix** to **{prefix}**")

    @group(
        name='fakepermissions', aliases=['fake', 'fakeperms'], brief='Configure fake permissions in the server'
    )
    async def fakeperms(self, ctx: Context):
        return
    
    @fakeperms.command(name='add', aliases=['append'], brief='Add a role with fake permissions in the server.')
    async def fakeperms_add(self, ctx: Context, role: Role, *, permission: str):
        permission = permission.replace(" ", "_").lower()
        if not permission in dict(ctx.author.guild_permissions):
            return await ctx.warn(f"**{permission}** is not a valid permission.")
        try:
            await self.bot.db.execute('INSERT INTO fakepermissions (guild_id, role_id, permission) VALUES ($1, $2, $3)', ctx.guild.id, role.id, permission, raise_exceptions=True)
            return await ctx.done(f'Assigned the fake permission **{permission}** to role {role.mention}')
        except:
            return await ctx.error(f'{role.mention} is already registered as a fake permission role.')
    
    @fakeperms.command(name='remove', aliases=['delete', 'revoke', 'boot'], brief='Remove a fake permission from a role.')
    async def fakeperms_remove(self, ctx: Context, role: Role, *, permission: str):
        permission = permission.replace(" ", "_").lower()
        if not permission in dict(ctx.author.guild_permissions):
            return await ctx.warn(f"**{permission}** is not a valid permission.")
        try:
            await self.bot.db.execute('DELETE FROM fakepermissions WHERE role_id = $1 AND guild_id = $2', role.id, ctx.guild.id, raise_exceptions=True)
            return await ctx.done(f'Removed the fake permission **{permission}** from role {role.mention}')
        except:
            return await ctx.error(f'{role.mention} is already registered as a fake permission role.')
        
    @fakeperms.command(name='list', aliases=['view', 'show'], brief="View a list of fake permissions in the server.")
    async def fakeperms_view(self, ctx: Context):
        roles = []
        embeds = []
        num = 0

        async for row in self.bot.db.fetchiter(
            "SELECT role_id, array_agg(permission) AS permissions FROM fakepermissions WHERE guild_id = $1 GROUP BY role_id",
            ctx.guild.id,
        ):
            if (role := ctx.guild.get_role(row["role_id"])) and (permissions := row["permissions"]):
                role_permissions = ", ".join([f"`{permission.replace('_', ' ').title()}`" for permission in permissions])
                roles.append(f'{role.mention} - {role_permissions}')

        if not roles:
            return await ctx.warn('There are no registered fake permissions in this server.')

        for page in ctx.as_chunks(roles, 10):
            num += 1
            embeds.append(
                Embed(
                    description="\n".join(page),
                    color=config.Color.main,
                    timestamp=datetime.datetime.now()
                )
                .set_footer(
                    text=f"Page {num}/{len(list(ctx.as_chunks(roles, 10)))}  ({len(roles)} entries)"
                )
                .set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
            )

        return await ctx.paginate(embeds)

    @group(name='theme', aliases=['themes'], brief='Configure bot theme in the server.')
    async def theme(self, ctx: Context):
        return


    @theme.command(name='embeds', aliases=['embed'], brief='Enable/Disable embed responses in the server.')
    async def theme_embeds(self, ctx: Context, *, option: Literal["on", "off"]):
        if option == 'on':
            await self.bot.db.execute('INSERT INTO theme (guild_id, embeds) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET embeds = excluded.embeds', ctx.guild.id, True)
            return await ctx.done('Enabled embed responses in this server.')
        elif option == 'off':
            await self.bot.db.execute('INSERT INTO theme (guild_id, embeds) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET embeds = excluded.embeds', ctx.guild.id, False)
            return await ctx.done('Disabled embed responses in this server.')



async def setup(bot: Lair):
    await bot.add_cog(Configuration(bot=bot))