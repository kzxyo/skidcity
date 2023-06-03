import discord
from discord.ext import commands
import os
import random
import json
import sys

class roles(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
     
    @commands.command(pass_context=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.is_owner()
    async def roles(self, ctx, guild):
        guild = ctx.guild
        roles = [role for role in guild.roles if role != ctx.guild.default_role]
        embed = discord.Embed(title=f"Server Roles in {guild.name}",description=f"".join([role.mention for role in roles]),colour=0x2f3136)
        await ctx.send(embed=embed)
        
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator = True)
    async def addrole(self,ctx,member:discord.Member,role:discord.Role):
        await member.add_roles(role)
        e=discord.Embed(color=discord.Color.green(),description=f"Added **{role}** to {member.mention}.") 
        e.set_footer(text="Delta Role Add",icon_url="https://cdn.discordapp.com/emojis/1022917201663115307.png")
        await ctx.reply(embed=e, mention_author=False)
   
    @addrole.error
    async def addrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
            description = "This command requires `administrator` permission!",
             colour = 0xff0000
             )
            await ctx.send(embed=embed, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator = True)
    async def removerole(self,ctx,member:discord.Member,role:discord.Role):
        await member.remove_roles(role)
        e=discord.Embed(color=discord.Color.green(),description=f"Removed **{role}** from {member.mention}")
        e.set_footer(text="Delta role remove",icon_url="https://cdn.discordapp.com/emojis/1022917201663115307.png")
        await ctx.reply(embed=e, mention_author=False) 
        
    @removerole.error
    async def removerole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
            description = "This command requires `administrator` permission!",
             colour = 0xff0000
             )
            await ctx.send(embed=embed, mention_author=False)
        
    @commands.command(aliases=["rl"])
    async def role(self, ctx):
        embed=discord.Embed(title="Role",  color=0x2f3136)
        embed.add_field(
                name="Category",
                value=
                f"Moderation",
                inline=False)
        embed.add_field(
                name="Permisions",
                value=
                f"Administrator",
                inline=False)
        embed.add_field(
                name="Role Add Usage",
                value=
                f"`*addrole (user) <role>`",
                inline=False)
        embed.add_field(
                name="Role Remove Usage",
                value=
                f"`*removerole (user) <role>`",
                inline=False)
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(roles(bot))