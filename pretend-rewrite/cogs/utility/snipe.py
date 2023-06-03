import discord
from discord.ext import commands

class snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
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
        
        async with self.bot.db.acquire() as conn:
            await conn.execute("INSERT INTO snipe (guild_id, channel_id, message_id, content, author_id) VALUES ($1, $2, $3, $4, $5)", message.guild.id, message.channel.id, message.id, message.content, message.author.id)
    """
    @commands.command(
        help="shows a user spotify activity",
        usage="spotify",
        aliases=["sp"]
    )
    async def spotify(self, ctx):
        embed = discord.Embed(color=self.bot.color, desctiption=f"** You are listen to __{spotify_result.title}__**\n**Artist its __{spotify_result.artist}__**")
        embed.set_thumbnail(url=f"{spotify_result.album_cover_url}")
        await ctx.reply(embed=embed)
    """
    @commands.command(aliases=['s'])
    async def snipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        async with self.bot.db.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM snipe WHERE guild_id = $1 AND channel_id = $2 ORDER BY time DESC", ctx.guild.id, channel.id)
            if row is None:
                return await ctx.send("There is nothing to snipe in this channel.")
            embed = discord.Embed(title=f"Sniped message in #{channel.name}", description=row["content"], color=self.bot.color, timestamp=row["time"])
            embed.set_author(name=ctx.guild.get_member(row["author_id"]).display_name, icon_url=ctx.guild.get_member(row["author_id"]).display_avatar.url)
            embed.set_author(
                name=ctx.guild.get_member(row["author_id"]).display_name,
                icon_url=ctx.guild.get_member(row["author_id"]).display_avatar.url
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(snipe(bot))