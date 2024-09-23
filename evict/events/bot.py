import discord, datetime, aiohttp, logging, asyncio, contextlib, io
from collections import defaultdict
from discord.ext import commands, tasks
from discord import Embed
from asyncio import log
from patches import functions

log = logging.getLogger(__name__)

@tasks.loop(seconds=60)
async def shard_stats(self):
    log.info("Collecting shard stats")
    shards = []
    for shard_id, shard in self.bot.shards.items():
      guilds = [g for g in self.bot.guilds if g.shard_id == shard_id]
      users = len(self.bot.users)
      shard_info = {
                "shard_id": shard_id,
                "shard_name": f"Shard {shard_id}",
                "shard_ping": round(shard.latency * 1000),  # Kept in milliseconds for internal use
                "shard_guild_count": f"{len(guilds):,}",
                "shard_user_count": f"{users:,}",
                "shard_guilds": [str(g.id) for g in guilds],
                "server_count": len(guilds),  # Added field
                "member_count": users,  # Added field
                "uptime": str(self.bot.ext.uptime),  # Replace with actual uptime if available
                "latency": round(shard.latency * 1000) / 1000,  # Converted to seconds
                "last_updated": datetime.datetime.utcnow().isoformat()  # Current timestamp in ISO format
            }
      shards.append(shard_info)

      shard_data = {
            "bot": "Evict",  # Replace with your bot's name or identifier
            "shards": shards
        }

      try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://kure.pl/shards/post",  # Updated FastAPI server URL
                    json=shard_data,
                    headers={"api-key": "58ZCTj0fTkai"}  # Replace with your actual API key
                ) as response:
                    if response.status == 200:
                        log.info("Shard data successfully sent to the API")
                    else:
                        log.error(f"Failed to send shard data: {response.status} - {await response.text()}")
                        log.debug(f"Response headers: {response.headers}")
                        log.debug(f"Request payload: {shard_data}")
      except aiohttp.ClientConnectorError as e:
            log.error(f"Connection error occurred while sending shard data: {e}")
      except aiohttp.ClientResponseError as e:
            log.error(f"Response error occurred while sending shard data: {e}")
      except Exception as e:
            log.error(f"Exception occurred while sending shard data: {e}")

@tasks.loop(seconds=5)
async def servers_check(bot: commands.Bot):
    return [await guild.leave() for guild in bot.guilds if guild.id not in [x['guild_id'] for x in await bot.db.fetch("SELECT guild_id FROM authorize")]]

class Bot(commands.Cog): 
    def __init__(self, bot: commands.Bot):
      self.bot = bot
      self.buckets: dict = dict(
            avatars=dict(
                lock=asyncio.Lock(),
                data=defaultdict(dict),
            )
      )

    @commands.Cog.listener()
    async def on_ready(self): 
        servers_check.start(self.bot)
        shard_stats.start(self)
        
    @commands.Cog.listener('on_ready')
    async def stats(self): 
            channel_id = 1264065200290529350
            channel = self.bot.get_channel(channel_id)
            embed = discord.Embed(color=self.bot.color, description=f"evict is now online with **{len(self.bot.guilds)}** guilds and **{len(self.bot.users)}** users.")
            try: await channel.send(embed=embed)
            except: return
        
    @commands.Cog.listener('on_guild_join')
    async def join_log(self, guild: discord.Guild):
            channel_id = 1262304011562782804
            channel = self.bot.get_channel(channel_id)
     
            icon= f"[icon]({guild.icon.url})" if guild.icon is not None else "N/A"
            splash=f"[splash]({guild.splash.url})" if guild.splash is not None else "N/A"
            banner=f"[banner]({guild.banner.url})" if guild.banner is not None else "N/A"   
            embed = discord.Embed(color=self.bot.color, timestamp=datetime.datetime.now(), description=f"evict has joined a guild.")   
            embed.set_thumbnail(url=guild.icon)
            embed.set_author(name=guild.name, url=guild.icon)
            embed.add_field(name="Owner", value=f"{guild.owner.mention}\n{guild.owner}")
            embed.add_field(name="Members", value=f"**Users:** {len(set(i for i in guild.members if not i.bot))} ({((len(set(i for i in guild.members if not i.bot)))/guild.member_count) * 100:.2f}%)\n**Bots:** {len(set(i for i in guild.members if i.bot))} ({(len(set(i for i in guild.members if i.bot))/guild.member_count) * 100:.2f}%)\n**Total:** {guild.member_count}")
            embed.add_field(name="Information", value=f"**Verification:** {guild.verification_level}\n**Boosts:** {guild.premium_subscription_count} (level {guild.premium_tier})\n**Large:** {'yes' if guild.large else 'no'}")
            embed.add_field(name="Design", value=f"{icon}\n{splash}\n{banner}")
            embed.add_field(name=f"Channels ({len(guild.channels)})", value=f"**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}\n**Categories** {len(guild.categories)}")
            embed.add_field(name="Counts", value=f"**Roles:** {len(guild.roles)}/250\n**Emojis:** {len(guild.emojis)}/{guild.emoji_limit*2}\n**Stickers:** {len(guild.stickers)}/{guild.sticker_limit}")
            embed.set_footer(text=f"Guild ID: {guild.id}")
            if guild.banner:
                embed.set_image(url=guild.banner)
            try: await channel.send(embed=embed)
            except: return

    @commands.Cog.listener('on_guild_remove')
    async def leave_log(self, guild: discord.Guild):
            channel_id = 1262304011562782804
            channel = self.bot.get_channel(channel_id)
     
            icon= f"[icon]({guild.icon.url})" if guild.icon is not None else "N/A"
            splash=f"[splash]({guild.splash.url})" if guild.splash is not None else "N/A"
            banner=f"[banner]({guild.banner.url})" if guild.banner is not None else "N/A"   
            embed = discord.Embed(color=self.bot.color, timestamp=datetime.datetime.now(), description=f"evict has left a guild.")   
            embed.set_thumbnail(url=guild.icon)
            embed.set_author(name=guild.name, url=guild.icon)
            embed.add_field(name="Owner", value=f"{guild.owner.mention}\n{guild.owner}")
            embed.add_field(name="Members", value=f"**Users:** {len(set(i for i in guild.members if not i.bot))} ({((len(set(i for i in guild.members if not i.bot)))/guild.member_count) * 100:.2f}%)\n**Bots:** {len(set(i for i in guild.members if i.bot))} ({(len(set(i for i in guild.members if i.bot))/guild.member_count) * 100:.2f}%)\n**Total:** {guild.member_count}")
            embed.add_field(name="Information", value=f"**Verification:** {guild.verification_level}\n**Boosts:** {guild.premium_subscription_count} (level {guild.premium_tier})\n**Large:** {'yes' if guild.large else 'no'}")
            embed.add_field(name="Design", value=f"{icon}\n{splash}\n{banner}")
            embed.add_field(name=f"Channels ({len(guild.channels)})", value=f"**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}\n**Categories** {len(guild.categories)}")
            embed.add_field(name="Counts", value=f"**Roles:** {len(guild.roles)}/250\n**Emojis:** {len(guild.emojis)}/{guild.emoji_limit*2}\n**Stickers:** {len(guild.stickers)}/{guild.sticker_limit}")
            embed.set_footer(text=f"Guild ID: {guild.id}")
            if guild.banner:
                embed.set_image(url=guild.banner)
            try: await channel.send(embed=embed)
            except: return
      
    @commands.Cog.listener('on_guild_join')
    async def join_message(self, guild: discord.Guild):
        
        check = await self.bot.db.fetchrow("SELECT * FROM gblacklist WHERE guild_id = {}".format(guild.id))
        check1 = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = {}".format(guild.id))
        
        if check1 is None: return
        if check: return
        
        if channel := discord.utils.find(
            lambda c: c.permissions_for(guild.me).embed_links, guild.text_channels
        ):
        
            
            embed = Embed(
                color=self.bot.color,
                title="Getting started with evict",
                description=(
                    "Hey! Thanks for your interest in **evict bot**. "
                    "The following will provide you with some tips on how to get started with your server!"
                ),
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar)

            embed.add_field(
                name="**Prefix 🤖**",
                value=(
                    "The most important thing is my prefix. "
                    f"It is set to `;` by default for this server and it is also customizable, "
                    "so if you don't like this prefix, you can always change it with `prefix` command!"
                ),
                inline=False,
            )
            embed.add_field(
                name="**Moderation System 🛡️**",
                value=(
                    "If you would like to use moderation commands, such as `jail`, `ban`, `kick` and so much more... "
                    "please run the `setmod` command to quickly set up the moderation system."
                ),
                inline=False,
            )
            embed.add_field(
                name="**Documentation and Help 📚**",
                value=(
                    "You can always visit our [documentation](https://docs.evict.cc)"
                    " and view the list of commands that are available [here](https://evict.cc/commands)"
                    " - and if that isn't enough, feel free to join our [Support Server](https://discord.gg/evict) for extra assistance!"
                ),
            )
            
            await channel.send(embed=embed)

    @commands.Cog.listener('on_guild_join')
    async def gblacklist_check(self, guild: discord.Guild):
        
        check = await self.bot.db.fetchrow("SELECT * FROM gblacklist WHERE guild_id = {}".format(guild.id))
        
        if check is not None:
            await guild.leave()
            
    @commands.Cog.listener('on_guild_join')
    async def authorization_check(self, guild: discord.Guild):
        
        check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = {}".format(guild.id))
        
        if check: return
        
        if channel := discord.utils.find(
            lambda c: c.permissions_for(guild.me).embed_links, guild.text_channels):
        
            if check is None:
                embed = Embed(
                color=self.bot.color,
                description=(
                    "Hey! Evict is authorization only, please join the [support server](https://discord.gg/evict)"
                    " and request a whitelist."))
        
            await channel.send(embed=embed)
            await guild.leave()

    @commands.Cog.listener("on_user_update")
    async def avatar_update(self, before: discord.User, after: discord.User):
        """Save past avatars to the upload bucket"""

        if not self.bot.is_ready() or not after.avatar or str(before.display_avatar) == str(after.display_avatar):
            return

        channel = self.bot.get_channel(1268454162006413385)
        if not channel:
            return

        try:
            image = await after.avatar.read()
        except:
            return  # asset too new

        image_hash = await functions.image_hash(image)

        with contextlib.suppress(discord.HTTPException):
            message = await channel.send(
                file=discord.File(
                    io.BytesIO(image),
                    filename=f"{image_hash}." + ("png" if not before.display_avatar.is_animated() else "gif"),
                )
            )

            await self.bot.db.execute(
                "INSERT INTO avatars (user_id, avatar, hash, timestamp) VALUES ($1, $2, $3, $4) ON CONFLICT (user_id, hash) DO NOTHING",
                before.id,
                message.attachments[0].url,
                image_hash,
                int(discord.utils.utcnow().timestamp()),
            )

async def setup(bot: commands.Bot) -> None: 
  await bot.add_cog(Bot(bot)) 