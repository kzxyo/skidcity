
import discord, typing, difflib
from discord import Embed
from discord.ext import commands 
from .utils.util import Colors, Emojis
from cogs.utilevents import blacklist, commandhelp, noperms, sendmsg
class roles(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot


    @commands.command(invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @blacklist()
    async def role(self, ctx):
            embed = discord.Embed(color=Colors.default, title="roles", description="manage roles with crime")
            embed.add_field(name="usage", value="```role [subcommand] [target] [other]```", inline=False)
            embed.add_field(name="commands", value="> role create - creates a role\n> role delete - deletes a role\n> role give - gives a user a role\n> role take - takes a role from a user\n> role rename - renames a role\n> role info - gets info on a role", inline=False)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="powered by crime")
            await ctx.reply(embed=embed, mention_author=False)
    @commands.command(aliases=["rolemake"])
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @blacklist()
    async def rolecreate(self, ctx, *, role_name: str):
        guild = ctx.guild
        existing_role = discord.utils.get(guild.roles, name=role_name)
        if existing_role:
            embed = discord.Embed(
                title = "",
                description = f"{Emojis.warn} A role with the name **{role_name}** already exists.",
                color = 0xf7f9f8)
            await ctx.reply(embed=embed, mention_author=False)
            return
        await guild.create_role(name=role_name)
        embed = discord.Embed(
                title = "",
                description = f"{Emojis.check} A role with the name **{role_name}** has been made.",
                color = 0xf7f9f8)
        await ctx.reply(embed=embed, mention_author=False)
 

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @blacklist()
    async def roledelete(self, ctx, *, role_name: str):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            await role.delete()
            embed = discord.Embed(
                title = "",
                description = f"{Emojis.check} A role with the name *{role_name}* has been deleted.",
                color = 0xf7f9f8)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed = discord.Embed(
                title = "",
                description = f"{Emojis.warn} A role with the name *{role_name}* has not been found.",
                color = 0xf7f9f8)
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["roleadd"])
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @blacklist()
    async def rolegive(self, ctx, member: discord.Member, *, role: discord.Role):
        if role in member.roles:
            embed = discord.Embed(
                    title = "",
                    description = f"{Emojis.warn} member already has role {role.mention}",
                    color = 0xf7f9f8)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            await member.add_roles(role)
        embed = discord.Embed(
                title = "",
                description = f"{Emojis.check} {member.mention} has recieved the role {role.mention}.",
                color = 0xf7f9f8)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["roletake"])
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @blacklist()
    async def roleremove(self, ctx, member: discord.Member, *, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role)
        embed = discord.Embed(
                title = "",
                description = f"{Emojis.check} {member.mention} has lost the role {role.mention}.",
                color = 0xf7f9f8)
        await ctx.reply(embed=embed, mention_author=False)


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @blacklist()
    async def rolerename(self, ctx,  role: discord.Role, new_name: str):
            await role.edit(name=new_name)
            embed = discord.Embed(
                    title = "",
                    description = f"{Emojis.check} {role.mention} has been renamed to {new_name}.",
                    color = 0xf7f9f8)
            await ctx.reply(embed=embed, mention_author=False)        

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def rolecolor(self, ctx: commands.Context, role: discord.Role, colour: discord.Colour):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role.name)
        if not role:            
             return
        try:
            await role.edit(color=colour, reason=f"{ctx.author} ({ctx.author.id}) has modified the role {role.name} ({role.id}).")
        except discord.HTTPException:
                    embed = discord.Embed(
                    description=f"{Emojis.warn} I do not have permissions to change the role color of **`{role.mention}`**"
                    )
                    await ctx.reply(embed=embed, mention_author=False)		
        else:
                    embed = discord.Embed(
                    description=f"{Emojis.check} changed {role.mention}'s color to **`{colour}`**"
                    )
                    await ctx.reply(embed=embed, mention_author=False)


    @commands.command()
    async def roleinfo(self, ctx, role: typing.Union[ discord.Role, str]):
        if isinstance(role, discord.Role):
            role=role
            perms = []
            content = discord.Embed(title=f"@{role.name} | #{role.id}")
            content.colour = role.color
            if isinstance(role.icon, discord.Asset):
                content.set_thumbnail(url=role.display_icon)
            elif isinstance(role.icon, str):
                content.title = f"{role.icon} @{role.name} | #{role.id}"
            for perm, allow in iter(role.permissions):
                if allow:
                    perms.append(f"`{perm.upper()}`")
            if role.managed:
                if role.tags.is_bot_managed():
                    manager = ctx.guild.get_member(role.tags.bot_id)
                elif role.tags.is_integration():
                    manager = ctx.guild.get_member(role.tags.integration_id)
                elif role.tags.is_premium_subscriber():
                    manager = "Server boosting"
                else:
                    manager = "UNKNOWN"
            content.add_field(name="Hex Code", value=str(role.color).upper())
            content.add_field(name="Member", value=len(role.members))
            content.add_field(name="Created", value=discord.utils.format_dt(role.created_at, style="R"))
            content.add_field(name="Hoisted", value=str(role.hoist))
            content.add_field(name="Mentionable", value=role.mentionable)
            content.add_field(name="Mention", value=role.mention)
            return await ctx.reply(embed=content)


async def setup(bot):
    await bot.add_cog(roles(bot))             