import discord 
import aiohttp
import asyncio 

from discord.ext import commands 

from tools.bot import DiscordBot
from tools.context import HarmContext

class Usernames(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_user_update(
        self, 
        before: discord.User,
        after: discord.User
    ):
        if before.__str__ != after.__str__:
            if not await self.bot.db.fetchrow("SELECT * FROM blacklisted WHERE user_id = $1", before.id):
                if results := await self.bot.db.fetchrow("SELECT webhook_url FROM usernames"):
                    content = f"New username available: **{before}**"
                    for result in results: 
                        async with aiohttp.ClientSession() as session:
                            try: 
                                webhook = discord.Webhook.from_url(
                                  result[0],
                                  session=session
                                )
                            except ValueError:
                                await self.bot.db.execute("DELETE FROM usernames WHERE webhook_url = $1", result[0])
                                continue 

                            await webhook.send(
                                content,
                                username="harm - usernames",
                                avatar=self.bot.user.display_avatar.url
                            )
                            await asyncio.sleep(0.8)    

    @commands.hybrid_group(invoke_without_command=True)
    async def usernames(self, ctx):
        return await ctx.send_help(ctx.command)
    
    @usernames.command(
        name = "remove",
        aliases = ['disable'],
        brief = "manage guild"
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def usernames_remove(self, ctx: HarmContext):
        """disable the username tracking"""
        if not await self.bot.db.fetchrow("SELECT * FROM usernames WHERE guild_id = $1", ctx.guild.id):
            return await ctx.error("There is no channel that tracks new usernames in this server")
        
        await self.bot.db.execute("DELETE FROM usernames WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success("Stopped tracking new available usernames")

    @usernames.command(
        name = "add",
        brief = "manage server",
        usage = "$usernames add #channel"
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_webhooks=True)
    async def usernames_add(
        self,
        ctx: HarmContext,
        *, channel: discord.TextChannel
    ):
        """add a channel to track new available usernames"""
        if await self.bot.db.fetchrow("SELECT * FROM usernames WHERE guild_id = $1", ctx.guild.id):
            return await ctx.error("There is **already** a channel configured to trace new available usernames")
        
        webhooks = [w for w in await channel.webhooks() if w.token]
        if len(webhooks) > 0: 
            webhook = webhooks[0]
        else: 
            webhook = await channel.create_webhook(
                name = "harm - usernames",
                avatar = await self.bot.user.display_avatar.read()
            )   

        await self.bot.db.execute("INSERT INTO usernames VALUES ($1,$2)", ctx.guild.id, webhook.url)
        return await ctx.success(f"Tracking new usernames in {channel.mention}")      
        
async def setup(bot: DiscordBot):
    return await bot.add_cog(Usernames(bot))       