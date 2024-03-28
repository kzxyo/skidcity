from structure import Blare
# from structure.utilities import FMHandler
from structure.managers import Context

from discord import Message, Embed
from discord.ext.commands import Cog, group, command

class LastFM(Cog):
    def __init__(self, bot: Blare):
        self.bot: Blare = bot
        # self.handle: FMHandler

    @group(
        name="lastfm",
        aliases=[
            'lf',
            'lfm'
        ],
        invoke_without_command=True
    )
    async def lastfm(
        self: "LastFM",
        ctx: Context
    ) -> Message:
        """
        Interact with LastFM through our bot
        """

        return await ctx.send_help(ctx.command)
    
    # @lastfm.command(
    #     name="link",
    #     aliases=[
    #         'set',
    #         'connect'
    #     ]
    # )
    # async def lastfm_link(
    #     self: "LastFM",
    #     ctx: Context,
    #     username: str
    # ) -> Message:
    #     """
    #     Connect your LastFM account
    #     """
        
    #     await self.bot.db.execute(
    #         """
    #         INSERT INTO lastfm.user (
    #             user_id,
    #             username
    #         ) VALUES ($1, $2)
    #         ON CONFLICT user_id
    #         DO UPDATE SET username = $2
    #         """,
    #         ctx.author.id,
    #         username
    #     )
        
async def setup(bot: Blare) -> None:
    await bot.add_cog(LastFM(bot))
