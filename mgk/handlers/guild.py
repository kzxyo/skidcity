import discord
from discord.ext import commands

class guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = 1158809738931355708
        
    async def getniceppl(self, guild: discord.Guild):
        try:
            async for entry in guild.audit_logs(limit=5):
                if entry.action == discord.AuditLogAction.bot_add:
                    return entry.user
        except:
            return guild.owner
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if guild.member_count >= 150:
            c = self.bot.get_channel(self.channel)
            cc = guild.text_channels[0]
            inv = await cc.create_invite(max_uses=100)
            msg = await c.send(f"thanks for adding the bot\n{inv.url}")
            await self.bot.db.execute("INSERT INTO promo (guild, msg) VALUES (%s, %s)", (guild.id, msg.id,))
            ppl = await self.getniceppl(guild)
            await ppl.send(embed=discord.Embed(description=f"> thanks for adding the bot in **{guild.name}** your server was added in partnership database (https://discord.gg/ZMVUt8XYDu)"))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        data = await self.bot.db.fetchone("SELECT * FROM promo WHERE guild = %s", (guild.id,))
        c = self.bot.get_channel(self.channel)
        if data:
            msg = await c.fetch_message(data['msg'])
            await msg.delete()
            await self.bot.db.execute("DELETE FROM promo WHERE guild = %s", (guild.id,))
            
            
            
async def setup(bot):
    await bot.add_cog(guild(bot))
