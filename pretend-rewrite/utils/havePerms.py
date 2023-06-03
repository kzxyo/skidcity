from discord.ext import commands

def havePerms(perms = []):
    async def predicate(ctx):
        # if ctx.author.id in ctx.bot.owner_ids:
        #     return True
        if ctx.author.guild_permissions.administrator:
            return True
        command = ctx.command.name
        if ctx.command.parent:
            command = ctx.command.parent.name
        guild_id = ctx.guild.id
        role_ids = [role.id for role in ctx.author.roles]
        custom_perms = await ctx.bot.db.fetchrow(
            "SELECT allowed FROM guild_perms WHERE guild_id = $1 AND role_id = ANY($2) AND command = $3",
            guild_id,
            role_ids,
            str(command)
        )
        if custom_perms is None:
            custom_perms = []
        else:
            custom_perms = custom_perms["allowed"]
        if len(custom_perms) == 0:
            for perm in perms:
                if ctx.author.guild_permissions.__getattribute__(perm):
                    return True
        else:
            for perm in custom_perms:
                if perm in perms:
                    return True
        allowed = str(command) in custom_perms
        if not allowed:
            raise commands.MissingPermissions(perms)
        else:
            return True
    return commands.check(predicate)