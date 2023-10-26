import random
import discord 
import aiohttp 
import asyncio

from tools.converters import PfpFormat, Genre

from tools.context import HarmContext
from discord.ext import commands, tasks

@tasks.loop(minutes=1)
async def autopfp_loop(bot):
    if results := await bot.db.fetch("SELECT * FROM autopfp"):
        for result in results: 
            async with aiohttp.ClientSession() as session:
                try: 
                    webhook = discord.Webhook.from_url(
                      result['webhook_url'], 
                      session=session
                    )
                except ValueError:
                    await bot.db.execute("DELETE FROM autopfp WHERE webhook_url = $1", result['webhook_url']) 
                    continue 

                pfp = random.choice(bot.pfps.get(result['genre']))
                embed = discord.Embed(color=bot.color)
                embed.set_image(url=pfp)
                embed.set_footer(text="source: pinterest")
                await webhook.send(
                    username="harm - autopfp",
                    avatar_url=bot.user.display_avatar.url,
                    embed=embed,
                    silent=True
                )
                await asyncio.sleep(0.8)

class Autopfp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
    
    @commands.hybrid_group(invoke_without_command=True)
    async def autopfp(self, ctx):
        await ctx.send_help(ctx.command)
    
    @autopfp.command(name="help", aliases=['guide'])
    async def autopfp_help(self, ctx: HarmContext):
        """guide for autopfp commands"""
        embed = discord.Embed(color=self.bot.color)
        embed.add_field(
            name="genres", 
            value="male, female, anime",
            inline=False
        )

        embed.add_field(
            name="formats",
            value="png, gif",
            inline=False
        )

        await ctx.send(embed=embed)

    @autopfp.command(
        name="add",
        brief="manage server",
        usage="$autopfp add male png #male-pfps"
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_webhooks=True)
    async def autopfp_add(
        self,
        ctx: HarmContext,
        genre: Genre, 
        format: PfpFormat, 
        *,
        channel: discord.TextChannel
    ):
        """add a channel for autopfp"""
        if await self.bot.db.fetchrow("SELECT * FROM autopfp WHERE genre = $1 AND guild_id = $2", f"{genre}_{format}", ctx.guild.id):
            return await ctx.error(f"There is a channel active for {genre} {format}s")
        
        webhooks = [w for w in await channel.webhooks() if w.token]
        if len(webhooks) > 0:
            webhook = webhooks[0]
        else: 
            webhook = await channel.create_webhook(
                name = "harm - autopfp",
                avatar = await self.bot.user.display_avatar.read(),
                reason = "Creating webhook for autopfp sending"
            )

        await self.bot.db.execute(
            """INSERT INTO autopfp
            VALUES ($1,$2,$3)""",
            ctx.guild.id, 
            webhook.url,
            f"{genre}_{format}"
        )        

        return await ctx.success(f"Added {channel.mention} for {genre} {format}s posting")
    
    @autopfp.command(
        name = "remove",
        brief = "manage server",
        usage = "$autopfp remove male pfp"
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def autopfp_remove(
        self,
        ctx: HarmContext,
        genre: Genre,
        format: PfpFormat
    ):
        """remove a genre from autopfp"""
        if not await self.bot.db.fetchrow("SELECT * FROM autopfp WHERE guild_id = $1 AND genre = $2", ctx.guild.id, f"{genre}_{format}"):
            return await ctx.error(f"There is no **autopfp** channel active for **{genre} {format}s**")
        
        await self.bot.db.execute("DELETE FROM autopfp WHERE guild_id = $1 AND genre = $2", ctx.guild.id, f"{genre}_{format}")
        return await ctx.success(f"Stopped sending **{genre} {format}s**")
    
    @autopfp.command(name = "list")
    async def autopfp_list(self, ctx: HarmContext):
        """get a list of the active autopfp genres in this server"""
        if results := await self.bot.db.fetch("SELECT genre FROM autopfp WHERE guild_id = $1", ctx.guild.id):
            channels = list(
                map(
                    lambda result: result['genre'].replace("_", " "), 
                    results
                )
            )
            return await ctx.paginate(
                channels,
                f"Autopfp ({len(channels)})",
                {"name": ctx.guild.name, "icon_url": ctx.guild.icon}
            )
        
        return await ctx.error("There are no active autopfp channels")

async def setup(bot) -> None: 
    return await bot.add_cog(Autopfp(bot))