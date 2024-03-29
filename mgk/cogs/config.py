import discord
from discord.ext import commands
from modules.func import member

class config(commands.Cog, description = "see config commands"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener("on_guild_channel_create")
    async def channel_create(self, channel):
        c = self.bot.get_channel(channel.id)
        data = await self.bot.db.fetchone("SELECT role FROM muterole WHERE guild = %s", (c.guild.id,))
        if data is not None:
            role = c.guild.get_role(int(data['role']))
            await c.set_permissions(role, overwrite=discord.PermissionOverwrite(send_messages=False, add_reactions=False))
        
    @commands.command(extras={"Category": "Config"}, usage="selfprefix !prefix", help="Set your self prefix", aliases=["sprefix"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def selfprefix(self, ctx, prefix: str=None):
        if prefix is None: return await ctx.error("prefix is None")
        if len(prefix) > 8: return await ctx.error("the number of letters/numbers must be less than 9")
        result = await self.bot.db.fetchone("SELECT prefix FROM selfprefix WHERE user = %s", (ctx.author.id,))
        if result is None:
            await self.bot.db.execute("INSERT INTO selfprefix (user, prefix) VALUES (%s, %s)", (ctx.author.id, prefix,))
        else:
             await self.bot.db.execute("UPDATE selfprefix SET prefix = %s WHERE user = %s", (prefix, ctx.author.id))
        await ctx.succes(f"your selfprefix now is ``{prefix}``")
        
    @commands.command(extras={"Category": "Config"}, usage="prefix !prefix", help="Set guild prefix", aliases=["gprefix"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @member.has_perm("manage_guild")
    async def prefix(self, ctx, prefix: str=None):
        if prefix is None: return await ctx.error("prefix is None")
        if len(prefix) > 8: return await ctx.error("the number of letters/numbers must be less than 9")
        result = await self.bot.db.fetchone("SELECT prefix FROM prefix WHERE guild = %s", (ctx.guild.id,))
        if result is None:
            await self.bot.db.execute(f"INSERT INTO prefix (guild, prefix) VALUES (%s, %s)", (ctx.guild.id, prefix,))
        else:
             await self.bot.db.execute("UPDATE prefix SET prefix = %s WHERE guild = %s", (prefix, ctx.guild.id,))
        await ctx.succes(f"prefix on this guild now is ``{prefix}``")
        
    @commands.group(aliases=["mr"], invoke_without_command=True)
    async def muterole(self, ctx):
        await ctx.gcmd(self.bot, "muterole")
    
    @muterole.command(extras={"Category": "Config"}, usage="muterole setup", help="Setup mute role")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @member.has_perm("administrator")
    async def setup(self, ctx):
        data = await self.bot.db.fetchone("SELECT role FROM muterole WHERE guild = %s", (ctx.guild.id,))
        if data is not None:
            return await ctx.error("you have mute role seted if you want to set again use **muterole delete**")
        role = await ctx.guild.create_role(name="muted - mgk", permissions=discord.Permissions(send_messages=False, add_reactions=False))
        #await role.edit(position=ctx.guild.me.top_role.position - 1)
        await self.bot.db.execute(f"INSERT INTO muterole (guild, role) VALUES (%s, %s)", (ctx.guild.id, role.id,))
        perms = discord.PermissionOverwrite(send_messages=False, add_reactions=False)
        for c in ctx.guild.channels:
            await c.set_permissions(role, overwrite=perms)
        await ctx.succes(f"mute role was seted to {role.mention}")
        
    @muterole.command(extras={"Category": "Config"}, usage="muterole delete", help="Delete mute role")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @member.has_perm("administrator")
    async def delete(self, ctx):
        data = await self.bot.db.fetchone("SELECT role FROM muterole WHERE guild = %s", (ctx.guild.id,))
        if data is None:
            return await ctx.error("if you want to setup mute role use **muterole setup**")
        role = ctx.guild.get_role(int(data['role']))
        await role.delete()
        await self.bot.db.execute("DELETE FROM muterole WHERE guild = %s", (ctx.guild.id,))
        await ctx.succes("mute role was deleted")
        
async def setup(bot):
    await bot.add_cog(config(bot))