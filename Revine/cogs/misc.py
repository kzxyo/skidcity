# This source code is 100% original, any contents will be credited in revine's credits command. Created by fsb#1337 & report#0001

import discord, datetime, time, asyncio, random, aiohttp, io
from discord.ext import commands
from typing import Union
from discord.ui import View, Button
from classes import Emotes, Colors, Images

start_time = time.time()


class misc(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot


# --------------------------------------------------------------------------------------- Ping Command

    @commands.command(aliases=["latency"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        button1 = Button(label="Support", url="https://discord.gg/revine")
        button2 = Button(label="Invite", url="https://discord.com/api/oauth2/authorize?client_id=1075704083853357117&permissions=8&scope=bot%20applications.commands")
        bot_latency = round(self.bot.latency * 1000)
        embed = discord.Embed(color=Colors.normal, description=f"Current Latency: **{bot_latency}ms**")
        embed.set_author(icon_url=self.bot.user.display_avatar, name="Revine's Latency")
        view = View()
        view.add_item(button1)
        view.add_item(button2)
        await ctx.reply(embed=embed, view=view)

# --------------------------------------------------------------------------------------- Invite Command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        button1 = Button(label="Invite", url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands")
        embed = discord.Embed(description=f"Use the button below to invite revine.", color=Colors.normal)
        embed.set_author(name=f"Revine", icon_url=f"{Images.revine_pfp}", url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands")
        view = View()
        view.add_item(button1)
        await ctx.reply(embed=embed, view=view)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def poll(self, ctx, *, text):
        p = discord.Embed(description=f"{text}", color=Colors.normal)
        p.set_author(name=f"{ctx.author.display_name}#{ctx.author.discriminator}", icon_url=f"{ctx.author.avatar}", url=f"https://discord.com/users/{ctx.author.id}")
        p = await ctx.send(embed=p)
        await p.add_reaction(f"👍")
        await p.add_reaction(f"👎")

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`administrator`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def say(self, ctx, *, text):
        s = discord.Embed(description=f"{text}", color=Colors.normal)
        s.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=s)

    @commands.command(aliases=["cn", "changenick"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator = True)
    async def changenickname(self, ctx, member: discord.Member, nick = None):
        if nick == None:
            await member.edit(nick=nick)
            embed = discord.Embed(description=f"{member.mention} Nickname was set to **Default**", color=Colors.normal)
            await ctx.send(embed=embed)
            return 
        await member.edit(nick=nick)
        embed = discord.Embed(description=f"{member.mention} Nickname was set to **{nick}**", color=Colors.normal)
        embed.set_footer(text="category: misc・revine ©️ 2023")
        await ctx.send(embed=embed)

    @changenickname.error
    async def changenickname_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`Manage Nicknames`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed)

    @commands.command(aliases=["firstmsg", "fmsg"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def firstmessage(self, ctx):
        async for message in ctx.channel.history(limit=1, oldest_first=True):
            button1 = Button(label="First Message", url=message.jump_url, emoji=f"{Emotes.search_emote}")
            view= View()
            view.add_item(button1)
            await ctx.reply(view=view)
            
    @commands.command(aliases=["serverleave", "leaveserver"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.is_owner()
    async def leave(self, ctx):
        await ctx.send("I'm leaving the server...")
        await ctx.guild.leave()

        
        
async def setup(bot) -> None:
    await bot.add_cog(misc(bot))