import discord, aiohttp, button_paginator as pg, datetime, time
from discord.ext import commands
from typing import Union
from io import BytesIO
from classes import hex, emote

start = time.time()

class info(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.command(aliases = ['bi', 'binfo', 'rockstar', 'about', 'aboutrockstar'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botinfo(self, ctx):
        avatar_url = self.bot.user.avatar.url
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - start))))
        members = 0
        for guild in self.bot.guilds:
            members += guild.member_count - 1
        embed = discord.Embed(color=hex.normal, description="**[Rockstar](https://discord.gg/rockstarbot), multipurpose & useful.**")
        embed.set_thumbnail(url=f'{avatar_url}')
        embed.set_author(name=f"{self.bot.user.name}", icon_url=self.bot.user.display_avatar)
        embed.add_field(name="", value=f"> **Guilds:** " + " ** "f"` {len(self.bot.guilds)} `" + "**\n> **Users:** " + f"` {members} `" + " \n> **D.py Version:** " + f" ` {discord.__version__} `\n> **Ping:** " +f"` {round(self.bot.latency * 1000)}ms `\n" +f"> **Uptime:** ` {uptime} `")
        await ctx.reply(embed=embed, mention_author=False)
        
# Uptime Command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def uptime(self, ctx):
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - start))))
        e = discord.Embed(colour=0x2f3136, description=f"**` {uptime} `**")
        await ctx.reply(embed=e, mention_author=False)
            
# Avatar Command

    @commands.command(aliases=['ava', 'pfp', 'av', 'avi', 'uico', 'uicon'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def avatar(self, ctx: commands.Context, *, member: discord.User = None):
        if member == None:member = ctx.author
        user = await self.bot.fetch_user(member.id)
        if user.display_avatar == None:
            em = discord.Embed(color=hex.normal, description=f"{emote.warning} {member.mention} does not have a avatar.")
            await ctx.send(embed=em, mention_author=False)
        else:
            avatar_url = user.display_avatar
            e = discord.Embed(color=hex.normal)
            e.set_author(name=f"{member.name}#{member.discriminator}'s avatar", icon_url=f"{member.avatar}", url=f"https://discord.com/users/{member.id}")
            e.set_image(url=avatar_url)
            await ctx.reply(embed=e, mention_author=False)
            
# Banner Command
 
    @commands.command(aliases=["bnr"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def banner(self, ctx: commands.Context, *, member: discord.User = None):
        if member == None:member = ctx.author
        user = await self.bot.fetch_user(member.id)
        if user.banner == None:
            em = discord.Embed(color=hex.normal, description=f"{emote.warning} {member.mention} **does not have a banner.**")
            await ctx.send(embed=em, mention_author=False)
        else:
            banner_url = user.banner.url
            e = discord.Embed(color=hex.normal)
            e.set_author(name=f"{member.display_name}#{member.discriminator}'s banner", icon_url=f"{member.avatar}", url=f"https://discord.com/users/{member.id}")
            e.set_image(url=banner_url)
            await ctx.reply(embed=e, mention_author=False)
            
# Member Server Avatar Command

    @commands.command(aliases=["sava"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def usavatar(self, ctx, member: discord.User = None):
        if member == None:member = ctx.author
        if member.guild_avatar == None:
            em = discord.Embed(color=hex.normal, description=f"{emote.warning} {member.mention} **does not have a server avatar.**")
            await ctx.send(embed=em, mention_author=False)
        else:
            avatar_url = member.guild_avatar
            e = discord.Embed(color=hex.normal)
            e.set_author(name=f"{member.name}#{member.discriminator}'s server avatar", icon_url=f"{member.avatar}", url=f"https://discord.com/users/{member.id}")
            e.set_image(url=avatar_url)
            await ctx.reply(embed=e, mention_author=False)
        
# Server Banner Command

    @commands.command(aliases=['sb', 'sbanner', 'sbnr'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverbanner(self, ctx, *, invite = "developedbyasf"):
        if invite == "developedbyasf":
            banner = ctx.guild.banner
            if banner == None:
                embed = discord.Embed(description=f"**{emote.warning} {ctx.author.mention}: This guild has no banner.**" ,color=hex.normal)
                await ctx.send(embed=embed)
                return
            embed = discord.Embed(title=f"{ctx.guild.name}'s banner", color=hex.normal)
            embed.set_image(url=f"{ctx.guild.banner}")
            await ctx.reply(embed=embed, mention_author=False) 
            return
        invite = await self.bot.fetch_invite(url = f"https://discord.gg/{invite}")
        if invite.guild.banner is None:
            embed = discord.Embed(description=f"{ctx.author.mention}: {invite.guild.name} has no banner" ,color=hex.normal)
            await ctx.send(embed=embed)
            return
        await ctx.channel.typing()
        embed = discord.Embed(title=f"{invite.guild.name}'s banner", url=f"{invite}", color=hex.normal)
        embed.set_image(url=invite.guild.banner.url)
        await ctx.send(embed=embed)

# Server Icon Command

    @commands.command(aliases=['sico', 'sicon', 'spfp'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def servericon(self, ctx, *, invite = "developedbyasf"):
        if invite == "developedbyasf":
            embed = discord.Embed(title=f"{ctx.guild.name}'s icon",color=hex.normal)
            embed.set_image(url=f"{ctx.guild.icon}")
            await ctx.reply(embed=embed, mention_author=False) 
            return
        invite = await self.bot.fetch_invite(url = f"https://discord.gg/{invite}")
        if invite.guild.icon is None:
            embed = discord.Embed(description=f"{ctx.author.mention}: {invite.guild.name} has no icon" ,color=hex.warning)
            await ctx.send(embed=embed)
            return
        await ctx.channel.typing()
        embed = discord.Embed(title=f"{invite.guild.name}'s icon",color=hex.normal)
        embed.set_image(url=invite.guild.icon)
        await ctx.send(embed=embed)
            
# Server Splash Command

    @commands.command(aliases=['sspl', 'ssplash', 'ssp', 'splash'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serversplash(self, ctx, *, invite = "developedbyasf"):
        if invite == "developedbyasf":
            embed = discord.Embed(title=f"{ctx.guild.name}'s splash", color=hex.normal)
            embed.set_image(url=f"{ctx.guild.splash}")
            await ctx.reply(embed=embed, mention_author=False) 
            return
        invite = await self.bot.fetch_invite(url = f"https://discord.gg/{invite}")
        if invite.guild.splash is None:
            embed = discord.Embed(description=f"{ctx.author.mention}: {invite.guild.name} has no splash" ,color=hex.warning)
            await ctx.send(embed=embed)
            return
        await ctx.channel.typing()
        embed = discord.Embed(title=f"{invite.guild.name}'s splash",color=hex.normal)
        embed.set_image(url=invite.guild.splash)
        await ctx.send(embed=embed)

# Server Member Count Command

    @commands.command(aliases=['mc', 'totaluser', 'totalmembers'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def membercount(self, ctx, *, invite = "developedbyasf"):
        if invite == "developedbyasf":
            embed = discord.Embed(description=f"Total Members: ` {len(ctx.guild.members)} `", color=hex.normal)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            await ctx.reply(embed=embed, mention_author=False) 
            return
        invite = await self.bot.fetch_invite(url = f"https://discord.gg/{invite}")
        if invite.approximate_member_count < 0:
            embed = discord.Embed(description=f"{ctx.author.mention}: Couldn't get the current member count of that guild." ,color=hex.warning)
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(description=f"Total Members: ` {invite.approximate_member_count} `", color=hex.normal)
        embed.set_author(name=invite.guild.name, icon_url=invite.guild.icon)
        await ctx.send(embed=embed)

# Server Bot Count Command

    @commands.command(aliases=['bc', 'totalbots', 'totalclients'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botcount(self, ctx, *, invite = "developedbyasf"):
        if invite == "developedbyasf":
            embed = discord.Embed(description=f"Total Bots: ` {len([m for m in ctx.guild.members if m.bot])} `", color=hex.normal)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            await ctx.reply(embed=embed, mention_author=False) 
            return
        invite = await self.bot.fetch_invite(url = f"https://discord.gg/{invite}")
        if {len([m for m in invite.approximate_member_count if m.bot])} is None:
            embed = discord.Embed(description=f"{ctx.author.mention}: There is no bots in that server." ,color=hex.normal)
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(description=f"Total Bots: ` {len([m for m in invite.approximate_member_count if m.bot])} `", color=hex.normal)
        embed.set_author(name=invite.guild.name, icon_url=invite.guild.icon)
        await ctx.send(embed=embed)
            
            
async def setup(bot) -> None:
    await bot.add_cog(info(bot))