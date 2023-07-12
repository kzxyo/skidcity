from discord import Guild, HTTPException
import discord
import orjson
import time
from utilities.lair import Lair
from utilities.managers import Wrench
from discord import User
from utilities.general.utils import image_hash
import contextlib

class UserEvent(Wrench):

    @Wrench.listener(name='on_user_update')
    async def avatar_scraper(self, before: User, after: User):
        if before.display_avatar != after.display_avatar:
            channel = self.bot.get_channel(1126445318825848832)
            if before.display_avatar:
                image = await before.avatar.read()
                hash = await image_hash(image)
                file = await before.display_avatar.to_file(filename=f'{before.id}.{"png" if not before.display_avatar.is_animated() else "gif"}')
                tim = round(time.time())
                with contextlib.suppress(HTTPException, discord.errors.NotFound):
                    message = await channel.send(file=file)
                await self.bot.db.execute('INSERT INTO avatars (user_id, username, avatar, time, hash) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (user_id, hash) DO NOTHING', before.id, before.name, message.attachments[0].url, tim, hash)


async def setup(bot: Lair) -> None:
    await bot.add_cog(UserEvent(bot=bot))