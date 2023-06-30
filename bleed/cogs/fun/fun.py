from discord import Embed, Message
from discord.ext.commands import Cog, command

from helpers.bleed import Bleed
from helpers.managers import Context


class Fun(Cog):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot

    @command(
        name="image",
        usage="(search)",
        example="Playboi Carti",
        aliases=[
            "im",
            "img",
        ],
    )
    async def image(self, ctx: Context, *, search: str) -> Message:
        """
        Search Google for an image
        """

        async with ctx.typing():
            data = await self.bot.session.request(
                "GET",
                "https://notsobot.com/api/search/google/images",
                params={
                    "query": search,
                    "safe": str(not ctx.channel.is_nsfw()),
                },
            )
            if not data:
                return await ctx.warn(f"No results were found for **{search}**")

        return await ctx.paginate(
            [
                Embed(
                    color=item.color,
                    url=item.url,
                    title=item.header,
                    description=item.description,
                )
                .set_image(url=item.image.url)
                .set_footer(icon_url="https://cdn.notsobot.com/brands/google-go.png")
                for item in data
                if not item.header in ("TikTok")
            ],
            of_text=(
                "Google Images Results "
                + ("(Safe)" if not ctx.channel.is_nsfw() else "")
            ),
        )
