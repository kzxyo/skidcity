# This source code is 100% original, any contents will be credited in revine's credits command. Created by fsb#1337 & report#0001

import discord, time, datetime, psutil
from discord.ext import commands
from typing import Union
from discord.utils import format_dt
from discord.ui import View, Button, Select
from classes import Colors, Emotes

class info(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

# --------------------------------------------------------------------------------------- Avatar Command

    @commands.command(aliases=["av", "pfp"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def avatar(self, ctx: commands.Context, *,member: discord.User = None):
        if member == None:member = ctx.author
        user = await self.bot.fetch_user(member.id)
        if user.avatar == None:
            em = discord.Embed(color=Colors.normal,description=f"{member.mention}")
            await ctx.reply(embed=em, mention_author=False)
        else:
            avatar_url = user.avatar.url
            button1 = Button(label="Avatar", url=avatar_url, emoji=Emotes.link_emote)
            e = discord.Embed(color=Colors.normal, url=user.avatar.url)
            e.set_author(name=f"{member.display_name}#{member.discriminator}", icon_url=f"{member.avatar}", url=f"https://discord.com/users/{member.id}")
            e.set_image(url=avatar_url)
            e.set_footer(text="category: info・revine ©️ 2023")
            view = View()
            view.add_item(button1)
            await ctx.reply(embed=e, view=view, mention_author=False)

# --------------------------------------------------------------------------------------- Banner Command

    @commands.command(aliases=["bnr"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def banner(self, ctx: commands.Context, *, member: discord.User = None):
        if member == None:member = ctx.author
        user = await self.bot.fetch_user(member.id)
        if user.banner == None:
            em = discord.Embed(color=Colors.normal, description=f"{Emotes.warning_emote} {member.mention} doesn't have a banner on the profile")
            await ctx.reply(embed=em, mention_author=False)
        else:
            banner_url = user.banner.url
            button1 = Button(label="Banner", url=banner_url, emoji=Emotes.link_emote)
            e = discord.Embed(color=Colors.normal)
            e.set_author(name=f"{member.display_name}#{member.discriminator}", icon_url=f"{member.avatar}", url=f"https://discord.com/users/{member.id}")
            e.set_image(url=banner_url)
            e.set_footer(text="category: info・revine ©️ 2023")
            view = View()
            view.add_item(button1)
            await ctx.reply(embed=e, view=view, mention_author=False)

# On Banner Error

    @banner.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            e = discord.Embed(color=Colors.normal, description=f"{ctx.author.mention} {error}")
            await ctx.reply(embed=e, mention_author=False)


# --------------------------------------------------------------------------------------- Profile Icon Command

    @commands.command(aliases=["pi"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def profileicon(self, ctx: commands.Context, *, member: discord.User = None):
        if member == None:member = ctx.author
        user = await self.bot.fetch_user(member.id)
        if user.banner == None:
            em = discord.Embed(
                color=Colors.normal,
                description=f"{Emotes.warning_emote} {member.mention}: doesn't have a profile I can display.")
            await ctx.reply(embed=em, mention_author=False)
        else:
            banner_url = user.banner.url
            avatar_url = user.avatar.url
            button1 = Button(label="Icon", url=avatar_url)
            button2 = Button(label="Banner", url=banner_url)
            e = discord.Embed(color=Colors.normal, description=f'*Here are the icon and banner for [**{member.display_name}#{member.discriminator}**](https://discord.com/users/{member.id})*')
            e.set_author(name=f"{member.display_name}#{member.discriminator}", icon_url=f"{member.avatar}", url=f"https://discord.com/users/{member.id}")
            e.set_image(url=f"{banner_url}")
            e.set_thumbnail(url=f"{avatar_url}")
            e.set_footer(text="category: info・revine ©️ 2023")
            view = View()
            view.add_item(button1)
            view.add_item(button2)
            await ctx.reply(embed=e, view=view, mention_author=False)

# --------------------------------------------------------------------------------------- Userinfo Command

    @commands.command(aliases=['ui', 'uinfo', 'whois'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx: commands.Context, *, user:discord.Member = None):
        if user == None:user = ctx.author
        if len(user.roles) > 1:role_string = ' '.join([r.mention for r in user.roles][1:])
        date_format = "%a, %d %b %Y %I:%M %p"
        userbanner = user.banner
        if user.banner == None:
            bannernull = discord.Embed(description=f"**Created:** {user.created_at.strftime(date_format)}\n**Joined:** {user.joined_at.strftime(date_format)}", colour=Colors.normal)
            bannernull.set_author(name=f"{user.display_name}#{user.discriminator}", url=f"https://discord.com/users/{user.id}", icon_url=f"{user.display_avatar}")
            bannernull.add_field(name="Roles: ` {} `".format(len(user.roles)-1), value=role_string, inline=True)
            bannernull.add_field(name="Misc:", value=f"[**` Avatar `**]({user.display_avatar})\n[**` Profile `**](https://discord.com/users/{user.id})", inline=True)
            bannernull.set_thumbnail(url=f"{user.avatar}")
            bannernull.set_footer(text="category: info・revine ©️ 2023")
            iconurl = Button(label="Icon", url=user.avatar.url)
            profileurl = Button(label="Profile", url=f"https://discord.com/users/{user.id}")
            view = View()
            view.add_item(iconurl)
            view.add_item(profileurl)
            await ctx.reply(embed=bannernull, view=view, mention_author=False)
            
# --------------------------------------------------------------------------------------- Revine's Information
            
    @commands.command(aliases=['bi', 'binfo', 'about'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botinfo(self, ctx):
        botinfo = discord.Embed(description=f"> - *Visit revine's [**Support Server**](https://discord.gg/revine) for more information.*\n> - *Revine's Global Prefix: **` ; `***", color=Colors.normal)
        botinfo.add_field(name=f"Stats", value=f"test", inline=True)
        botinfo.set_author(name="Revine's Information", icon_url=f"{self.bot.user.display_avatar}", url="https://discord.gg/revine")
        botinfo.set_footer(text="category: info・revine ©️ 2023")
        await ctx.reply(embed=botinfo)
        
# --------------------------------------------------------------------------------------- Get Guildbanner command
        
    @commands.command(aliases=["sbanner", "sb", "sbnr"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverbanner(self, ctx):
        if ctx.guild.banner is None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: **{ctx.guild.name}** does not have a banner", color=Colors.normal)
            await ctx.reply(embed=embed)
            return
        e = discord.Embed(color=Colors.normal)
        e.set_author(name=f"{ctx.guild.name}'s server banner", icon_url=f"{ctx.guild.icon.url}")
        e.set_image(url=f"{ctx.guild.banner.url}")
        button = Button(label="Download", url=f"{ctx.guild.banner.url}", emoji=f"{Emotes.link_emote}")
        view = View()
        view.add_item(button)
        await ctx.send(view=view, embed=e)
        
# --------------------------------------------------------------------------------------- Get Guildicon command

    @commands.command(aliases=["sicon", "si", "sico", "savi"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def servericon(self, ctx):
        if ctx.guild.icon is None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: **{ctx.guild.name}** does not have a icon", color=Colors.normal)
            await ctx.reply(embed=embed)
            return
        e = discord.Embed(color=Colors.normal)
        e.set_author(name=f"{ctx.guild.name}'s server icon", icon_url=f"{ctx.guild.icon.url}")
        e.set_image(url=f"{ctx.guild.icon.url}")
        avatar = Button(label="Download", url=f"{ctx.guild.icon.url}", emoji=f"{Emotes.link_emote}")
        view = View()
        view.add_item(avatar)
        await ctx.send(embed=e, view=view)
        
# --------------------------------------------------------------------------------------- Get Guildsplash command

    @commands.command(aliases=["ssplash", "sspl"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serversplash(self, ctx):
        if ctx.guild.splash is None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: **{ctx.guild.name}** does not have a splash banner", color=Colors.normal)
            await ctx.reply(embed=embed)
            return
        e = discord.Embed(color=Colors.normal)
        e.set_author(name=f"{ctx.guild.name}'s server splash", icon_url=f"{ctx.guild.icon.url}")
        e.set_image(url=f"{ctx.guild.splash.url}")
        splash = Button(label="Download", url=f"{ctx.guild.splash.url}", emoji=f"{Emotes.link_emote}")
        view = View()
        view.add_item(splash)
        await ctx.send(embed=e, view=view)
        
async def setup(bot) -> None:
    await bot.add_cog(info(bot))