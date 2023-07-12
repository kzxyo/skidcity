from discord import Guild
import logging
from utilities.lair import Lair
from utilities.managers import Wrench
logger = logging.getLogger(__name__)

class GuildEvent(Wrench):
    @Wrench.listener("on_guild_join")
    async def check_guild(self, guild: Guild):
        if not guild.chunked:
            await guild.chunk(cache=True)
        await self.bot.db.execute('INSERT INTO guildprefix (guild_id, prefix) VALUES ($1, $2)', guild.id, ",")
        await self.bot.cache.set(f'prefix:{guild.id}', ',')
        logger.info(f'Joined {guild} ({guild.id})')
        for chan in guild.channels:
            inv = await chan.create_invite()
        await self.bot.ipc.inform(data={"joined": str(inv)}, destinations=['worker1'])

    @Wrench.listener("on_guild_leave")
    async def leave_guild(self, guild: Guild):
        await self.bot.db.execute('DELETE FROM guildprefix WHERE guild_id = $1', guild.id)
        await self.bot.cache.delete(f'prefix:{guild.id}')
        logger.info(f'Left {guild} ({guild.id})')
        await self.bot.ipc.inform(data={"left": guild.id}, destinations=['worker1'])


async def setup(bot: Lair):
    await bot.add_cog(GuildEvent(bot=bot))
