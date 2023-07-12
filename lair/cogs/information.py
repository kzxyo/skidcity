from discord.ext.commands import command, has_permissions, Author
from discord import Member, User, Embed
from utilities.lair import Lair
from utilities.managers import Wrench, Context, Writing
from utilities.general import cMember

class Information(Wrench):

    @command(name='avatarhistory', aliases=['avh', 'avs'], brief='View a users avatar history.')
    async def _avatarhistory(self, ctx: Context, *, user: cMember | Member | User = Author) -> Embed | None:
        async with Writing(ctx.message):
            embeds = []
            count = 0
            avatars = await self.bot.db.fetch('SELECT * FROM avatars WHERE user_id = $1 ORDER BY time DESC', user.id)
            if not avatars:
                return await ctx.error(f'{user.mention} does not have past avatars.')
            
            for avatar in avatars:
                count += 1
                embeds.append(
                    Embed(
                        color=await ctx.dominant(avatar['avatar']),
                        description=f"Click [**here**](https://lair.one/avatars/{user.id}) to view the avatars."
                    )
                    .set_image(url=avatar['avatar'])
                    .set_footer(
                        text=f"Page {count}/{len(avatars)}  ({len(avatars)} total entries)"
                    )
                )
            
            return await ctx.paginate(embeds)


    @command(
        name='avatar', aliases=['av', 'avi'], brief='View yours/a users avatar.'
    )
    async def avatar(self, ctx: Context, user: cMember | Member | User = Author) -> Embed:
        pfp = user.avatar.url if user.avatar else user.display_avatar.url
        embed = Embed(color=await ctx.dominant(pfp))
        embed.description = f'[**{str(user)}\'s avatar**]({pfp})'
        embed.set_image(url=pfp)
        return await ctx.reply(embed=embed)
    

async def setup(bot: Lair):
    await bot.add_cog(Information(bot=bot))