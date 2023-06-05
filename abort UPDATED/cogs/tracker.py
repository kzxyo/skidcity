import discord, datetime, button_paginator as pg
from discord.ext import commands
from backend.classes import Emojis, Colors
from cogs.events import blacklist, sendmsg, noperms
from backend.views import Views
#from backend import views

from datetime import datetime
now =datetime.now

class tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.available_tags = []

    @commands.Cog.listener()
    async def on_available_tag(self, user: discord.User):
        self.available_tags.insert(0, {"user": user,"time": datetime.now()})

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.Member, after: discord.Member):
        if before.avatar == after.avatar:
            if before.discriminator == "0001":
                self.bot.dispatch('available_tag', before)
                for x in self.bot.guilds:
                    async with self.bot.db.cursor() as e:
                        await e.execute(f"SELECT * FROM tracker WHERE guild_id = {x.id}")
                        channel = await e.fetchone()
                        if channel is not None:
                            ch = self.bot.get_channel(int(channel[1]))
                            await ch.send(f"new tag available: **{before}**")

    @commands.group(aliases=["track"],invoke_without_command=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def tracker(self, ctx):
        e = discord.Embed(title="Command: tracker", description="Tracks #0001 Tags and sends it through a channel",color=Colors.default, timestamp=ctx.message.created_at)
        e.add_field(name="category", value="config")
        e.add_field(name="Arguments", value="<subcommand> [channel]")
        e.add_field(name="permissions", value="manage_channels", inline=True)
        e.add_field(name="Command Usage",value="```Syntax: ;tracker add #tags```", inline=False)
        await sendmsg(self, ctx, None, e, None, None, None, None)
        return

    @tracker.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def add(self, ctx, channel=None):
        if not ctx.author.guild_permissions.manage_channels: return await noperms(self, ctx, "manage_channels")   
        if channel == None:
            channel = ctx.channel.id
        try:
            if "<#" in channel:
                channel = channel.replace("<#", "")
            if ">" in channel:
                channel = channel.replace(">", "")
            async with self.bot.db.cursor() as c:
                await c.execute(f"SELECT * FROM tracker WHERE guild_id = ? AND channel = ?", (ctx.guild.id, channel,))
                check = await c.fetchone()
                if check is not None:
                    await c.execute("UPDATE tracker SET guild_id = ? AND channel = ?", (ctx.guild.id, channel,))
                    await self.bot.db.commit()
                elif check is None:
                    await c.execute("INSERT INTO tracker VALUES (?,?)", (ctx.guild.id, channel,))
                    await self.bot.db.commit()
                embed=discord.Embed(description=f"> {Emojis.check} {ctx.author.mention}: Successfully **Added** the channel <#{channel}> to **track** discriminators",color=Colors.default)
                await sendmsg(self, ctx, None, embed, None, None, None, None)

        except Exception as e:
            print(e)
            embed=discord.Embed(description=f"> {Emojis.check} {ctx.author.mention}: Successfully **Added** the channel <#{channel}> to **track** discriminators",color=Colors.default)
            await sendmsg(self, ctx, None, embed, None, None, None, None)
            
            
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @blacklist()
    async def tags(self, ctx):
        async with ctx.typing():
            available_tags = self.available_tags.copy()
            if available_tags:
                max_tags = 10
                tags = tuple(available_tags[x:x + max_tags]
                             for x in range(0, len(available_tags), max_tags))
                pages = []

                i = 0
                for group in tags:
                    page = discord.Embed(color = Colors.default)
                    page.set_author(name=ctx.author.name,icon_url=ctx.author.display_avatar.url)
                    page.title = f"Recent Tag Changes"
                    page.description = '\n'.join([f"`{idx+1+i}` {x['user']} - {discord.utils.format_dt(x['time'], style='R')}" for idx, x in enumerate(group)])
                    pages.append(page)
                    i += len(group) + 1
                if len(pages) == 1:
                    return await sendmsg(self, ctx, None, pages[0], None, None, None, None)
                else:
                    paginator = pg.Paginator(self.bot, pages, ctx, invoker=ctx.author.id)
                    paginator.add_button('prev', emoji='<:left:1100418278272290846>')
                    paginator.add_button('delete', emoji='<:stop:1018156487232720907>')
                    paginator.add_button('next', emoji='<:right:1100418264028426270>')
                    await paginator.start()
            else:
                embed = discord.Embed(color = Colors.default)
                embed.description = "> There are no tags available"
                await sendmsg(self, ctx, None, embed, None, None, None, None)


async def setup(bot) -> None:
    await bot.add_cog(tracker(bot))