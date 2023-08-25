import discord
import aiohttp
from discord.ext import commands


class snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.NUM_TO_STORE = 3
        self.snipes = {}
        self.warn = ""
        self.deleted_msgs = {}
        self.edited_msgs = {}
        self.reactions = {}
        self.snipe_limit = self.NUM_TO_STORE

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        ch_id = before.channel.id
        if not before.author.bot:
            if before.content and after.content:
                if ch_id not in self.edited_msgs:
                    self.edited_msgs[ch_id] = []
                self.edited_msgs[ch_id].append((before, after))
            else:
                if ch_id not in self.edited_msgs:
                    self.edited_msgs[ch_id] = []
                self.edited_msgs[ch_id].append((before, after))
            try:
                if len(self.edited_msgs[ch_id]) > self.snipe_limit:
                    self.edited_msgs[ch_id].pop(0)
            except:
                pass

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        ch_id = message.channel.id
        try:
            if not message.author.bot:
                if message.content:
                    if ch_id not in self.deleted_msgs:
                        self.deleted_msgs[ch_id] = []
                    self.deleted_msgs[ch_id].append(message)
                else:
                    if ch_id not in self.deleted_msgs:
                        self.deleted_msgs[ch_id] = []
                    self.deleted_msgs[ch_id].append(message)
                if len(self.deleted_msgs[ch_id]) > self.snipe_limit:
                    self.deleted_msgs[ch_id].pop(0)
        except:
            pass

    @commands.command(
        name="snipe",
        aliases=["s"],
        description="See recently deleted messages in the current channel",
        brief="int",
    )
    async def snipe(self, ctx: commands.Context, limit: int = 1):
        if limit > self.snipe_limit:
            return await ctx.send(
                delete_after=5,
                embed=discord.Embed(
                    color=0x303135,
                    description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {self.snipe_limit}**",
                ),
            )
        try:
            msgs: list[discord.Message] = self.deleted_msgs[ctx.channel.id][::-1][
                :limit
            ]
            for msg in msgs:
                if msg == "Snipe Has Been Removed":
                    return await ctx.reply(
                        delete_after=10,
                        embed=discord.Embed(description=f"**{msg}**", color=0x303135),
                    )
                snipe_embed = (
                    discord.Embed(color=0x303135, timestamp=msg.created_at)
                    .set_author(name=msg.author, icon_url=msg.author.display_avatar)
                    .set_footer(
                        text=f"{limit}/{len(self.deleted_msgs[ctx.channel.id])}"
                    )
                )
                if msg.content:
                    snipe_embed.description = msg.content
                if msg.attachments:
                    snipe_embed.set_image(url=msg.attachments[0].proxy_url)
            await ctx.send(embed=snipe_embed)

        except:
            await ctx.send(
                delete_after=5,
                embed=discord.Embed(
                    color=0x303135,
                    description=f"{self.warn} {ctx.author.mention}: **<:warn:1138340198661505096> there is nothing to snipe**",
                ),
            )

    @commands.command(name="embed", description="create an embed", brief="embedcode")
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, *, embedcode: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.rival.rocks/embed", params={"code": embedcode}
            ) as f:
                data = await f.json()
        return await ctx.send(**data)

    @commands.command(
        name="editsnipe",
        aliases=["es"],
        description="See recently edited messages in the current channel",
        brief="int",
    )
    async def editsnipe(self, ctx: commands.Context, limit: int = 1):
        if limit > self.snipe_limit:
            return await ctx.send(
                delete_after=5,
                embed=discord.Embed(
                    color=0x303135,
                    description=f"{self.warn} {ctx.author.mention}: **current snipe limit is {self.snipe_limit}**",
                ),
            )
        try:
            msgs = self.edited_msgs[ctx.channel.id][::-1][:limit]
            for msg in msgs:
                if msg == "Snipe Has Been Removed":
                    return await ctx.reply(
                        delete_after=10,
                        embed=discord.Embed(description=f"**{msg}**", color=0x303135),
                    )
                editsnipe_embed = (
                    discord.Embed(color=0x303135, timestamp=msg[0].edited_at)
                    .set_author(
                        name=msg[0].author, icon_url=msg[0].author.display_avatar
                    )
                    .set_footer(text=f"{limit}/{len(self.edited_msgs[ctx.channel.id])}")
                )
                if msg[0].content:
                    editsnipe_embed.description = msg[0].content
                if msg[0].attachments:
                    editsnipe_embed.set_image(url=msg[0].attachments[0].proxy_url)
            await ctx.send(embed=editsnipe_embed)

        except KeyError:
            await ctx.send(
                delete_after=5,
                embed=discord.Embed(
                    color=0x303135,
                    description=f"{self.warn} {ctx.author.mention}: **<:warn:1138340198661505096> there is nothing to snipe**",
                ),
            )

    @commands.command(
        name="clearsnipes",
        description="Clear the stored sniped messages.",
        aliases=["cs"],
    )
    @commands.has_permissions(manage_messages=True)
    async def clear_snipes(self, ctx):
        self.deleted_msgs.clear()
        await ctx.message.add_reaction("👍🏾")


async def setup(bot):
    await bot.add_cog(snipe(bot))
