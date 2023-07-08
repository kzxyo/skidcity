import discord, asyncio, requests, os
from discord.ext import commands
from discord.ext.commands import has_permissions
from typing import Union
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps
from discord.ext.commands import Paginator
from typing import Literal, Optional, Union

class Emoji(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(
        description="delete an emoji",
        help="emoji",
        usage="deleteemoji [emoji]",
        brief="manage emojis",
        aliases=["delemoji"],
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @has_permissions(manage_emojis=True)
    async def deleteemoji(self, ctx: commands.Context, emoji: discord.Emoji):
        await emoji.delete()
        await ctx.reply("Deleted the emoji")

    @commands.command(
        description="add an emoji",
        help="emoji",
        usage="steal [emoji] <name>",
        brief="manage emojis",
        aliases=["steal"],
    )
    @commands.cooldown(1, 4, commands.BucketType.guild)
    @has_permissions(manage_emojis=True)
    async def addemoji(
        self,
        ctx: commands.Context,
        emoji: Union[discord.Emoji, discord.PartialEmoji],
        *,
        name: str = None,
    ):
        if not name:
            name = emoji.name
        try:
            emoji = await ctx.guild.create_custom_emoji(
                image=await emoji.read(), name=name
            )
            await ctx.reply(f"added emoji `{name}` | {emoji}".capitalize())
        except discord.HTTPException as e:
            return await ctx.reply(ctx, f"Unable to add the emoji | {e}")

    @commands.command(
        description="add multiple emojis",
        help="emoji",
        usage="addmultiple [emojis]",
        aliases=["am"],
        brief="manage emojis",
    )
    @commands.cooldown(1, 6, commands.BucketType.guild)
    @has_permissions(manage_emojis=True)
    async def addmultiple(
        self, ctx: commands.Context, *emoji: Union[discord.Emoji, discord.PartialEmoji]
    ):
        if len(emoji) == 0:
            return await ctx.reply("Please provide some emojis to add")
        emojis = []
        await ctx.channel.typing()
        for emo in emoji:
            try:
                emoj = await ctx.guild.create_custom_emoji(
                    image=await emo.read(), name=emo.name
                )
                emojis.append(f"{emoj}")
                await asyncio.sleep(0.5)
            except discord.HTTPException as e:
                return await ctx.reply(ctx, f"Unable to add the emoji | {e}")

        embed = discord.Embed(color=self.bot.color, title=f"added {len(emoji)} emojis")
        embed.description = "".join(map(str, emojis))
        return await ctx.reply(embed=embed)


    @commands.command(
        aliases=["ei"], description="show emoji info", help="emoji", usage="emojiinfo [emoji]"
    )
    async def emojiinfo(
        self,
        ctx: commands.Context,
        *,
        emoji: Union[discord.Emoji, discord.PartialEmoji],
    ):
        embed = discord.Embed(
            color=self.bot.color, title=emoji.name, timestamp=emoji.created_at
        ).set_footer(text=f"id: {emoji.id}")
        embed.set_thumbnail(url=emoji.url)
        embed.add_field(name="Animated", value=emoji.animated)
        embed.add_field(name="Link", value=f"[emoji]({emoji.url})")
        if isinstance(emoji, discord.Emoji):
            embed.add_field(name="Guild", value=emoji.guild.name)
            embed.add_field(name="Usable", value=emoji.is_usable())
            embed.add_field(name="Available", value=emoji.available)
            emo = await emoji.guild.fetch_emoji(emoji.id)
            embed.add_field(name="Created by", value=str(emo.user))
        return await ctx.reply(embed=embed)

    @commands.command(name="emojis", usage="emotes", description="View all server emotes", aliases=["emotes"])
    @has_permissions(manage_messages=True)
    @commands.cooldown(1, 8, commands.BucketType.guild)
    async def emojis(self, ctx):

        if not ctx.guild.emojis:
            return await ctx.reply("No emojis are in this **server**")

        paginator = Paginator(prefix='', suffix='', max_size=2000)

        for emoji in ctx.guild.emojis:
            paginator.add_line(f"{emoji} (`{emoji.id}`)")

        embeds = []
        for page in paginator.pages:
            embed = discord.Embed(title=f"Emojis in {ctx.guild.name}")
            embed.description = page
            embeds.append(embed)

        for embed in embeds:
            await ctx.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Emoji(bot))
