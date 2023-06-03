import discord, aiosqlite
from discord.ext import commands


class filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.file_extensions = [".mp3", ".flac", ".m4a", ".wav", ".webm"]
        self.settings = {}
    @commands.Cog.listener()
    async def on_ready(self):
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS welcome (guild INTEGER, message TEXT, channel INTEGER);") 
        await self.bot.db.commit()
        
    async def getsettings(self, guild_id):
        async with aiosqlite.connect("database.db") as db:
            async with db.execute("SELECT * FROM settings WHERE guild_id=?", (guild_id,)) as cursor:
                return await cursor.fetchone()

    async def setsettings(self, guild_id, enabled):
        async with aiosqlite.connect("database.db") as db:
            await db.execute("INSERT OR REPLACE INTO settings(guild_id, enabled) VALUES(?, ?)", (guild_id, enabled))
            await db.commit()


    @commands.group(name="filter", aliases=["fe"], invoke_without_command=True)
    async def filter(self, ctx):
        return

    @commands.command(name="musicfiles", description="filter music files from being sent in your guild")
    async def musicfiles(self, ctx):
        if ctx.guild.id not in self.guild_settings:
            settings = await self.get_guild_settings(ctx.guild.id)
            if settings:
                self.guild_settings[ctx.guild.id] = settings[1]
            else:
                self.guild_settings[ctx.guild.id] = True
        enabled = self.guild_settings[ctx.guild.id]
        status = "enabled" if enabled else "disabled"
        await ctx.send(f"File extension filtering is currently {status}. Use `{ctx.prefix}fe toggle` to toggle it.")
async def setup(bot):
    await bot.add_cog(filters(bot))