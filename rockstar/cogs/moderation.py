import discord, aiohttp, button_paginator as pg
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote


class moderation(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
# Moderation Listeners

# Moderation Commands

    @commands.command(aliases=['yeet', 'vanish'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ban(self, ctx, member: Union[ discord.Member, discord.User]=None, reason = None):
        if (not ctx.author.guild_permissions.ban_members):
            embed = discord.Embed(colour=hex.warning, description=f"{emote.warning} {ctx.author.mention} **You do not have the required permissions: `ban_members`**")
            await ctx.reply(embed=embed)
            return
        if member is None:
            embed = discord.Embed(colour=hex.warning, description=f"{ctx.author.mention} **You need to mention a user!**")
            await ctx.reply(embed=embed)
            return
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
            embed = discord.Embed(colour=hex.warning, description=f"{ctx.author.mention}: you can't ban {member.mention}!")
            await ctx.reply(embed=embed)
            return
        if isinstance(member, discord.Member):
            if member == ctx.message.author:
                embed = discord.Embed(colour=hex.warning, description=f"{ctx.author.mention}: you cannot ban yourself!")
                await ctx.reply(embed=embed)
                return
        if reason == None:
            await member.ban(reason = "No reason provided.")
            embed = discord.Embed(colour=hex.normal, description=f"**Banned** {member.mention} **Reason:** `No reason provided`")
            await ctx.reply(embed=embed)
            return
        await member.ban(reason = reason)
        embed = discord.Embed(colour=hex.normal, description=f"**Banned** {member.mention} **Reason:** `{reason}`")
        await ctx.reply(embed=embed)
    
    @commands.command(aliases=['boot', 'bye'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def kick( self, ctx, member: Union[discord.Member, discord.User]=None, reason = None):
        if (not ctx.author.guild_permissions.kick_members):
            embed = discord.Embed(colour=hex.warning, description=f"{emote.warning} {ctx.auhtor.mention}** You do not have the required permissions: `kick_members`**")
            await ctx.reply(embed=embed)
            return
        if member is None:
            embed = discord.Embed(colour=hex.warning, description=f"{ctx.author.mention} **You need to mention a user!**")
            await ctx.reply(embed=embed)
            return
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
            embed = discord.Embed(colour=hex.warning, description=f"{ctx.author.mention}: you can't kick {member.mention}!")
            await ctx.reply(embed=embed)
            return
        if isinstance(member, discord.Member):
            if member == ctx.message.author:
                embed = discord.Embed(colour=hex.warning, description=f"{ctx.author.mention}: you cannot kick yourself!")
                await ctx.reply(embed=embed)
                return
        if reason == None:
            await member.kick(reason="No reason provided.")
            embed = discord.Embed(colour=hex.normal, description=f"**Kicked** {member.mention} **Reason:** `No reason provided.`")
            await ctx.reply(embed=embed)
            return
        await member.kick(reason="No reason provided.")
        embed = discord.Embed(colour=hex.normal, description=f"**Kicked** {member.mention} **Reason:** `No reason provided.`")
        await ctx.reply(embed=embed)
        
        
    @commands.command(aliases=['clear', 'delete'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def purge(self, ctx, *, amount: int = None):
        if (not ctx.author.guild_permissions.manage_messages):
            await ctx.reply("You do not have permission.")
            return
        if amount is None:
            await ctx.reply("You must input a number between 1 to 500")
            return
        if amount <= 0:
            await ctx.reply("You must input a number between 1 to 500")
            return
        amount = int(amount)
        await ctx.channel.purge(limit=amount)
        await ctx.reply(f"Deleted {amount} messages")
        
        
    @commands.command(aliases=['chperms'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def channelperms(self, ctx, *, channel: discord.TextChannel = None):
        channeloverwrite = channel.overwrites
        await ctx.reply(channeloverwrite)
        
            
            
    
async def setup(bot):
    await bot.add_cog(moderation(bot))