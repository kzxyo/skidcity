from platform import python_version, python_version_tuple
import discord, requests, os, datetime, psutil, time, button_paginator as pg
from discord.ext import commands
from discord.utils import format_dt
from discord.ui import View, Button, Select
from utility import Emotes, Colours

start_time = time.time()

class info(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.command(aliases=['about', 'gov', 'info', 'binfo', 'bi'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botinfo(self, ctx):
        avatar_url = self.bot.user.avatar.url
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - start_time))))
        users = 0
        for guild in self.bot.guilds:
            users += guild.member_count - 1
        embed = discord.Embed(color=0x2f3136, description=f"**Global Prefix: `,`**")
        embed.set_thumbnail(url=f'{avatar_url}')
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar)
        embed.add_field(name=f"**{Emotes.replyemote} Global Stats**",value=f"> - **Guilds:** " + " `"f"{len(self.bot.guilds)}" + "`\n> - **Users:** " + f"`{users}" + f"` \n> - **{Emotes.discordpyemote}.py Version:** " + f" `{discord.__version__}`\n> - **Ping:** " +f"`{round(self.bot.latency * 1000)}ms`\n" +f"> - **Uptime:** `{uptime}`")
        await ctx.reply(embed=embed, mention_author=False)
        
        
    @commands.command(aliases=['uinfo', 'useri', 'whois', 'aboutuser', 'ui'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx, member: discord.User = None):
        if member == None:
            await ctx.send("User is not defined. You did not mention a user.")
            return
        await ctx.send(f"User is {member.mention}.")
        
    @commands.command(aliases=['avatar', 'av', 'avi', 'pfp', 'uicon'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def useravatar(self, ctx, member: discord.User = None):
        if member == None:
            useravatar = ctx.author.display_avatar
            embed = discord.Embed(color=Colours.standard)
            embed.set_author(name=f"{ctx.author.display_name}#{ctx.author.discriminator}'s avatar", icon_url=ctx.author.display_avatar, url=f"https://discord.com/users/{ctx.author.id}")
            embed.set_image(url=useravatar)
            await ctx.reply(embed=embed)
            return
        useravatar = member.display_avatar
        embed = discord.Embed(color=Colours.standard)
        embed.set_author(name=f"{member.display_name}#{member.discriminator}'s avatar", icon_url=member.display_avatar, url=f"https://discord.com/users/{member.id}")
        embed.set_image(url=useravatar)    
        await ctx.reply(embed=embed)
        
    @commands.command(aliases=["bnr"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def banner(self, ctx: commands.Context, *, member: discord.User = None):
        if member == None:member = ctx.author
        user = await self.bot.fetch_user(member.id)
        if user.banner == None:
            em = discord.Embed(color=Colours.standard, description=f"{Emotes.warning_emote} {member.mention} does not have a banner")
            await ctx.reply(embed=em, mention_author=False)
        else:
            banner_url = user.banner.url
            e = discord.Embed(color=Colours.standard)
            e.set_author(name=f"{member.display_name}#{member.discriminator}", icon_url=f"{member.avatar}", url=f"https://discord.com/users/{member.id}")
            e.set_image(url=banner_url)
            await ctx.reply(embed=e, mention_author=False)

    @banner.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            e = discord.Embed(color=Colours.warning, description=f"{ctx.author.mention} {error}")
            await ctx.reply(embed=e, mention_author=False)
                
                
    @commands.command(aliases=['sinfo', 'si', 'serveri', 'aboutserver', 'serverstats'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverinfo(self, ctx, guild: discord.Guild = None):
        if guild == None:
            embed = discord.Embed(description=f"**Guild Owner:** {ctx.guild.owner.mention}\n**Guild ID:** `{ctx.guild.id}`")
            embed.add_field(name="Total Users", value=f"**Member Count:** ` {len(ctx.guild.members)} `\n**Human Count:** ` {len([m for m in ctx.guild.members if not m.bot])} `\n**Bot Count:** ` {len([m for m in ctx.guild.members if m.bot])} `", inline=True)
            embed.add_field(name="Premium Stats", value=f"**Boosts:** ` {ctx.guild.premium_subscription_count} `\n**Boost Tier:** ` {ctx.guild.premium_tier} `")
            embed.set_author(name=f"{ctx.guild.name}", icon_url=f"{ctx.guild.icon}")
            embed.set_thumbnail(url=f"{ctx.guild.icon}")
            await ctx.reply(embed=embed)
            return
        await discord.Guild == guild
        embed = discord.Embed(description=f"**Guild Owner:** {guild.owner.mention}\n**Guild ID:** `{guild.id}`")
        embed.add_field(name="Total Users", value=f"**Member Count:** ` {len(guild.members)} `\n**Human Count:** ` {len([m for m in guild.members if not m.bot])} `\n**Bot Count:** ` {len([m for m in guild.members if m.bot])} `", inline=True)
        embed.add_field(name="Premium Stats", value=f"**Boosts:** ` {guild.premium_subscription_count} `\n**Boost Tier:** ` {guild.premium_tier} `")
        embed.set_author(name=f"{guild.name}", icon_url=f"{guild.icon}")
        embed.set_thumbnail(url=f"{guild.icon}")
        await ctx.reply(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(info(bot))