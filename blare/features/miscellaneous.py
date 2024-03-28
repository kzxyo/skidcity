from structure import Blare
from structure.utilities import dump, Snipe
from structure.managers import Context

from discord import Message, Embed
from discord.ext.commands import Cog, command, has_permissions

from xxhash import xxh32_hexdigest

class Miscellaneous(Cog):
    def __init__(self, bot: Blare):
        self.bot: Blare = bot

    @Cog.listener()
    async def on_message_delete(
        self: "Miscellaneous",
        message: Message
    ):
        try:
            await self.bot.cache.sadd(
                f"snipe:{xxh32_hexdigest(str(message.channel.id))}", 
                dump(message),
            )
        except Exception as e:
            print(e)


    @command(
        name="ping",
        aliases=["latency"],
    )
    async def ping(
        self: "Miscellaneous", 
        ctx: Context
    ) -> Message:
        """
        Get the bot's latency
        """

        return await ctx.send(f"{round(self.bot.latency * 1000)}ms")
 

    @command(
        name="snipe",
        aliases=['s']
    )
    async def snipe(
        self: "Miscellaneous",
        ctx: Context,
        index: int = 1
    ) -> Message:
        """
        Snipe a recently deleted message
        """

        snipes = await self.bot.cache.get(f"snipe:{xxh32_hexdigest(str(ctx.channel.id))}")
        try:
            message = Snipe(**snipes[index - 1][0])
        except IndexError:
            return await ctx.alert("That is out of my range!")
        
        embed = Embed(
            description=message.content or "Message has embed or attachment only!!"
        )
        embed.set_author(
            name=message.author.name,
            icon_url=message.author.avatar
        )
        embed.set_footer(
            text=f"{ctx.author.name} \u2022 {index:,} / {len(snipes)} ",
        )
        if message.attachments:
            embed.set_image(url=message.attachments[0])

        elif message.stickers:
            embed.set_image(url=message.stickers[0])
        
        return await ctx.send(
            embeds=[
                embed,
                *[
                    Embed.from_dict(embed) 
                    for embed in message.embeds
                ],
            ],
        )

    @command(
        name="clearsnipes",
        aliases=['cs']
    )
    @has_permissions(manage_messages=True)
    async def clearsnipes(
        self: "Miscellaneous",
        ctx: Context
    ) -> Message:
        """
        Clear the snipe cache
        """
        await self.bot.cache.remove(f"snipe:{xxh32_hexdigest(str(ctx.channel.id))}")
        return await ctx.message.add_reaction("👍")

    @command(
        name="test"
    )
    async def test(
        self: "Miscellaneous",
        ctx: Context
    ) -> Message:
        await ctx.send(embed = Embed(
            description=f"### **[how u feel?](https://last.fm)**\nby **Destroy Lonely**\non **If Looks Could Kill**",
            url="https://last.fm"
        ).set_thumbnail(url="https://media.pitchfork.com/photos/6453ab5e575213cbefca6d9a/master/w_1280%2Cc_limit/Destroy-Lonely-If-Looks-Could-Kill.jpg").set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        )   

async def setup(bot: Blare) -> None:
    await bot.add_cog(Miscellaneous(bot))
