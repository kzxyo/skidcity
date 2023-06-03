import discord
from discord.ext import commands
from utils.havePerms import havePerms
from utils.isDonor import isDonor

class uwulock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        prefixes = await self.bot.prefix(message)
        if message.content.startswith(tuple(prefixes)):
            return

        if message.author.bot:
            return
        if message.guild is None:
            return
        if message.attachments:
            return
        if message.content == "":
            return
        if len(message.content) > 1024:
            return

        data = await self.bot.db.fetchrow("SELECT * FROM user_uwulock WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)
        if data:
            webhook = discord.utils.get(await message.channel.webhooks(), name="uwulock")
            if webhook is None:
                webhook = await message.channel.create_webhook(name="uwulock")
            await webhook.send(
                content=message.content.replace("r", "w").replace("l", "w").replace("R", "W").replace("L", "W"),
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url
            )
            await message.delete()
        

    @commands.command(
        help="every message sent by locked user will be uwuified (by webhook)",
        usage="uwulock <user>",
        aliases=["uwul", "uwulify", "uwu"],
    )
    @havePerms(["manage_webhooks"])
    @isDonor()
    async def uwulock(self, ctx: commands.Context, user: discord.Member):
        data = await self.bot.db.fetchrow("SELECT * FROM user_uwulock WHERE user_id = $1 AND guild_id = $2", user.id, ctx.guild.id)
        em = discord.Embed(color=self.bot.color)
        if data:
            await self.bot.db.execute("DELETE FROM user_uwulock WHERE user_id = $1 AND guild_id = $2", user.id, ctx.guild.id)
            em.description = f"**{user}** has been removed from uwulock"
        else:
            await self.bot.db.execute("INSERT INTO user_uwulock (user_id, guild_id, added_by) VALUES ($1, $2, $3)", user.id, ctx.guild.id, ctx.author.id)
            em.description = f"**{user}** has been added to uwulock"

        await ctx.reply(embed=em)

async def setup(bot):
    await bot.add_cog(uwulock(bot))