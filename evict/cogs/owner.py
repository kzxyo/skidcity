import discord, datetime, aiohttp, asyncio, textwrap, os, json
from discord.utils import get
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed, Permissions
from typing import Optional
from patches.classes import OwnerConfig

class owner(commands.Cog):
   def __init__(self, bot: commands.Bot):
       self.bot = bot

   def convert_datetime(self, date: datetime.datetime=None):
     if date is None: return None  
     month = f'0{date.month}' if date.month < 10 else date.month 
     day = f'0{date.day}' if date.day < 10 else date.day 
     year = date.year 
     minute = f'0{date.minute}' if date.minute < 10 else date.minute 
     if date.hour < 10: 
      hour = f'0{date.hour}'
      meridian = "AM"
     elif date.hour > 12: 
      hour = f'0{date.hour - 12}' if date.hour - 12 < 10 else f"{date.hour - 12}"
      meridian = "PM"
     else: 
      hour = date.hour
      meridian = "PM"  
     return f"{month}/{day}/{year} at {hour}:{minute} {meridian} ({discord.utils.format_dt(date, style='R')})" 

   @commands.is_owner()
   @commands.group(invoke_without_command=True)
   async def donor(self, ctx: commands.Context):
    await ctx.create_pages()

   @commands.is_owner()
   @donor.command(name='add', description="add a user to donors", usage="[member id]", brief="bot owner")
   async def add(self, ctx: commands.Context, *, member: discord.User): 
       result = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(member.id))
       if result is not None: return await ctx.warning(f"{member} is already a donor")
       ts = int(datetime.datetime.now().timestamp()) 
       await self.bot.db.execute("INSERT INTO donor VALUES ($1,$2)", member.id, ts)
       return await ctx.warning(f"{member.mention} is now a donor")

   @commands.is_owner()
   @donor.command(name='remove', description="remove a user from donor", usage="[member id]", brief="bot owner")
   async def remove(self, ctx: commands.Context, *, member: discord.User):    
       result = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(member.id)) 
       if result is None: return await ctx.warning(f"{member} isn't a donor")
       await self.bot.db.execute("DELETE FROM donor WHERE user_id = {}".format(member.id))
       return await ctx.warning(f"{member.mention} is not a donor anymore")
   
   @commands.command()
   @commands.is_owner()
   async def restart(self, ctx: commands.Context):
    await ctx.warning("restarting the bot.")
    os.system("pm2 restart evict")

   @commands.is_owner()
   @commands.command(aliases=["guilds"], name='servers', description="list all the servers evict is in", brief="bot owner")
   async def servers(self, ctx: commands.Context):
       
            def key(s): 
              return s.member_count
                   
            lis = [g for g in self.bot.guilds]
            
            lis.sort(reverse=True, key=key)

            guild_list = [f"{g.name} ``({g.id})`` - ({g.member_count})"
            
            for g in lis]
            
            await ctx.paginate(guild_list, f"all guilds [{len(self.bot.guilds)}]")  

   @commands.is_owner()
   @commands.command(name='portal', description="get an invite to a guild", usage="[guild id]", brief="bot owner")
   async def portal(self, ctx, id: int):
      await ctx.message.delete()      
      guild = self.bot.get_guild(id)
      for c in guild.text_channels:
        if c.permissions_for(guild.me).create_instant_invite: 
            invite = await c.create_invite()
            await ctx.author.send(f"{guild.name} invite link - {invite}")
            break 
        
   @commands.is_owner()
   @commands.command(name='unblacklist', description="unblacklist a user", usage="[member id]", brief="bot owner")
   async def unblacklist(self, ctx, *, member: discord.User): 
      check = await self.bot.db.fetchrow("SELECT * FROM nodata WHERE user_id = $1", member.id) 
      if check is None: return await ctx.warning(f"{member.mention} is not blacklisted")
      await self.bot.db.execute("DELETE FROM nodata WHERE user_id = {}".format(member.id))
      await ctx.warning(f'{member.mention} can use the bot')
   
   @commands.is_owner()
   @commands.command()
   async def delerrors(self, ctx: commands.Context): 
     await self.bot.db.execute("DELETE FROM cmderror")
     await ctx.reply("deleted all errors")

   @commands.is_owner()
   @commands.command(aliases=['trace'])
   async def error(self, ctx: commands.Context, code: str):

    fl = await self.bot.db.fetch("SELECT * FROM error;")
    error_details = [x for x in fl if x.get("key") == code]

    if len(error_details) == 0 or len(code) != 6: return await ctx.warning("Please provide a **valid** error code")
   
    error_details = error_details[0]
    error_details = json.loads(error_details.get("info"))
    guild = self.bot.get_guild(error_details["guild_id"])

    embed = discord.Embed(description=str(error_details["error"]), color=self.bot.color).add_field(name="Guild", value=f"{guild.name}\n`{guild.id}`", inline=True)
    embed.add_field(name="Channel", value=f"<#{error_details['channel_id']}>\n`{error_details['channel_id']}`", inline=True)
    embed.add_field(name="User", value=f"<@{error_details['user_id']}>\n`{error_details['user_id']}`", inline=True)
    embed.add_field(name="Command", value=f"**{error_details['command']}**")
    embed.add_field(name="Timestamp", value=f"{error_details['timestamp']}")
    embed.set_author(name=f"Error Code: {code}")
   
    return await ctx.send(embed=embed)

   @commands.is_owner()
   @commands.command(aliases=["globalban"], description="ban a user from all servers", usage="[user]", brief="bot owner")
   async def gban(self, ctx: commands.Context, *, member: discord.User): 
    
    if member.id in self.bot.owner_ids: return await ctx.warning("do not globalban a bot owner, retard.")
    if member.id == ctx.bot.user.id: return await ctx.warning("do not globalban me retard.")
    
    check = await self.bot.db.fetchrow("SELECT * FROM globalban WHERE banned = $1", member.id) 
    if check is not None: return await ctx.warning(f"{member.mention} is already globalbanned.")
    
    guild_ids = await self.bot.db.fetch("SELECT guild_id FROM mwhitelist")
    guild = discord.Guild
    
    for guild in member.mutual_guilds:
            
            if guild.id in guild_ids: continue
            
            try:
                await guild.ban(member, reason=f'globalbanned by {ctx.author}')
            
            except (discord.Forbidden):
                await guild.leave()
    
    await self.bot.db.execute("INSERT INTO globalban VALUES ($1)", member.id)
    await self.bot.db.execute("INSERT INTO nodata VALUES ($1,$2)", member.id, "false")
    await ctx.warning(f'globalbanned **{member}**')

   @commands.is_owner()
   @commands.command(aliases=["unglobalban", "gunban"], description="unban a user from all servers", usage="[user]", brief="bot owner")
   async def ungban(self, ctx: commands.Context, *, member: discord.User): 
    
    check = await self.bot.db.fetchrow("SELECT * FROM globalban WHERE banned = $1", member.id) 
    if check is None: return await ctx.warning(f"{member.mention} isn't globalbanned.")

    await self.bot.db.execute("DELETE FROM globalban WHERE banned = {}".format(member.id))
    await self.bot.db.execute("DELETE FROM nodata WHERE user_id = {}".format(member.id))            
    await ctx.success(f'unglobalbanned **{member}**')  
 
   @commands.is_owner()
   @commands.command(name='blacklist', description="blacklist a user from the bot", brief="owner", usage="[user]")
   async def blacklist(self, ctx: commands.Context, *, member: discord.User): 
      if member.id in self.bot.owner_ids: return await ctx.warning("do not blacklist a bot owner, retard.")
      check = await self.bot.db.fetchrow("SELECT * FROM nodata WHERE user_id = $1 AND state = $2", member.id, "false") 
      if check is not None: return await ctx.warning(f"{member.mention} is already blacklisted")
      await self.bot.db.execute("DELETE FROM nodata WHERE user_id = {}".format(member.id))
      await self.bot.db.execute("INSERT INTO nodata VALUES ($1,$2)", member.id, "false")
      await ctx.warning(f"{member.mention} can no longer use the bot")

   @commands.is_owner()
   @commands.command(name='pingall', description="ping all members", brief="bot owner")
   async def pingall(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        mentions = " ".join(m.mention for m in guild.members if not m.bot)
        await ctx.message.delete()
        await asyncio.gather(*[ctx.send(chunk, delete_after=0.5) for chunk in textwrap.wrap(mentions, 1950)])

   @commands.is_owner()
   @commands.command(description='set bot pfp', usage='[image url | file]', brief='bot owner')
   async def botpfp(self, ctx: commands.Context, *, image: str=None):
        if image == None and not ctx.message.attachments: 
            await self.bot.user.edit(avatar=None)
            return await ctx.warning("bot avatar has been cleared.")

        if len(ctx.message.attachments) > 0: image = ctx.message.attachments[0]

        if isinstance(image, str):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image) as resp:
                        if resp.status != 200:
                            return await ctx.warning('failed to download image')
                        image_bytes = await resp.read()
            except aiohttp.ClientError:
                return await ctx.warning('failed to download image')
        else:
            if not image.content_type.startswith('image/'):
                return await ctx.warning('Invalid file type. Please provide an image file.')
            image_bytes = await image.read()
        try:
            await self.bot.user.edit(avatar=image_bytes)
            await ctx.warning('bot avatar updated successfully.')
        except discord.HTTPException:
            await ctx.warning('failed to update bot avatar.')

   @commands.is_owner()
   @commands.command(description='set bot banner', usage='[image_url | file]', brief='bot owner')
   async def botbanner(self, ctx: commands.Context, *, image: str=None):
        if image == None and not ctx.message.attachments: 
            await self.bot.user.edit(banner=None)
            return await ctx.warning("bot banner has been cleared.")

        if len(ctx.message.attachments) > 0: image = ctx.message.attachments[0]

        if isinstance(image, str):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image) as resp:
                        if resp.status != 200:
                            return await ctx.warning('failed to download image')
                        image_bytes = await resp.read()
            except aiohttp.ClientError:
                return await ctx.warning('failed to download image')
        else:
            if not image.content_type.startswith('image/'):
                return await ctx.warning('Invalid file type. Please provide an image file.')
            image_bytes = await image.read()
        try:
            await self.bot.user.edit(banner=image_bytes)
            await ctx.warning('bot banner updated successfully.')
        except discord.HTTPException:
            await ctx.warning('failed to update bot banner.')

   @commands.is_owner()
   @commands.command(name='mutuals', description="show servers a user shares with the bot", usage="[user]", brief="bot owner")
   async def mutuals(self, ctx, user: discord.User = None): 
            
            if not user: user = ctx.author
            
            def key(s): 
              return s.member_count
            
            lis = [g for g in user.mutual_guilds]
            
            if len(lis) == 0: return await ctx.warning(f"I don't share a server with {user.mention}.") 
            lis.sort(reverse=True, key=key)
            
            mutuals_list = [f"{g.name} ``({g.id})`` - ({g.member_count})"
                     for g in lis]

            await ctx.paginate(mutuals_list, f"shared servers with {user} - {len(user.mutual_guilds)} shared")  

   @commands.is_owner()
   @commands.command(name='dm', aliases=['dmu'], description="dm a user", usage="[user]", brief="bot owner")
   async def dm(self, ctx, user: discord.User, *, message: str):
        destination = get(self.bot.get_all_members(), id=user.id)
        if not destination:
            return await ctx.warning("Invalid ID or user not found. You can only send messages to people I share a server with.")
        await destination.send(message)
        await ctx.warning(f"Sent direct message to {user.mention}.")

   @commands.is_owner()
   @commands.command(name='say', description="have the bot say something", usage="[message]", brief="bot owner")
   async def say(self, ctx, channel: Optional[discord.TextChannel], *, message: str):
       if not channel:
            channel = ctx.channel
       await ctx.message.delete()
       await channel.send(message)

   @commands.is_owner()
   @commands.command(name='spam', description="have the bot spam something", usage="[channel] [amount] [message]", brief="bot owner")
   async def spam(self, ctx, channel: Optional[discord.TextChannel], amount:int, *, message: str):
       if not channel:
            channel = ctx.channel
       await ctx.message.delete()
       for i in range(amount):
        await channel.send(message)
   
   @commands.is_owner()
   @commands.command(name='pingu', description="have the bot spam something and delete it", usage="[channel] [amount] [message]", brief="bot owner")
   async def pingu(self, ctx, channel: Optional[discord.TextChannel], amount:int, *, message: str):
       if not channel:
            channel = ctx.channel
       await ctx.message.delete()
       for i in range(amount):
        await channel.send(message, delete_after=0.2)

   @commands.is_owner()
   @commands.command(name='pingall', description="have the bot ping everyone", brief="bot owner")
   async def pingall(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        mentions = " ".join(m.mention for m in guild.members if not m.bot)
        await ctx.message.delete()
        await asyncio.gather(*[ctx.channel.send(chunk, delete_after=3) for chunk in textwrap.wrap(mentions, 1950)])

   @commands.is_owner()
   @commands.command(name='leaveg', description="have the bot leave a guild", usage="[guild id]", brief="bot owner")
   async def leaveg(self, ctx, guild: int):
        guild = self.bot.get_guild(int(guild))
        await guild.leave()
        await ctx.warning(f"`{guild.name}` has been **left**")

   @commands.is_owner()
   @commands.command(aliases=["gblacklist"], name='blacklistg', description="blacklist a guild", usage="[guild id]", brief="bot owner")
   async def blacklistg(self, ctx, guild: int):
        check = await self.bot.db.fetchrow("SELECT * FROM gblacklist WHERE guild_id = $1", guild) 
        if check is not None: return await ctx.warning(f"this guild is **already** blacklisted.")
        await self.bot.db.execute("INSERT INTO gblacklist VALUES ($1)", guild)
        await ctx.success("the guild has been **blacklisted**.")
        try:
            guild = self.bot.get_guild(int(guild))
            if guild: return await guild.leave()
        except: return
        
   @commands.is_owner()
   @commands.command(aliases=["gunblacklist"], name='unblacklistg', description="unblacklist a guild", usage="[guild id]", brief="bot owner")
   async def unblacklistg(self, ctx, guild: int):
        check = await self.bot.db.fetchrow("SELECT * FROM gblacklist WHERE guild_id = $1", guild) 
        if check is None: return await ctx.warning(f"this guild isn't **blacklisted**.")
        await self.bot.db.execute("DELETE FROM gblacklist WHERE guild_id = $1", guild)
        await ctx.success("the guild has been **unblacklisted**.")
        
   @commands.is_owner()
   @commands.command(aliases=["gg"], description="show information about a server", brief="bot owner")
   async def getguild(self, ctx: Context, guild:int):
        guild = self.bot.get_guild(int(guild))   
        if guild == None: 
            return await ctx.warning('no guild found for that id.')
        icon= f"[icon]({guild.icon.url})" if guild.icon is not None else "N/A"
        splash=f"[splash]({guild.splash.url})" if guild.splash is not None else "N/A"
        banner=f"[banner]({guild.banner.url})" if guild.banner is not None else "N/A"   
        desc=guild.description if guild.description is not None else ""
        embed = Embed(color=self.bot.color, title=f"{guild.name}", timestamp=datetime.datetime.now(), description=f"Server created on {self.convert_datetime(guild.created_at.replace(tzinfo=None))}\n{desc}")   
        embed.set_thumbnail(url=guild.icon)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Owner", value=f"{guild.owner.mention}\n{guild.owner}")
        embed.add_field(name="Members", value=f"**Users:** {len(set(i for i in guild.members if not i.bot))} ({((len(set(i for i in guild.members if not i.bot)))/guild.member_count) * 100:.2f}%)\n**Bots:** {len(set(i for i in guild.members if i.bot))} ({(len(set(i for i in guild.members if i.bot))/guild.member_count) * 100:.2f}%)\n**Total:** {guild.member_count}")
        embed.add_field(name="Information", value=f"**Verification:** {guild.verification_level}\n**Boosts:** {guild.premium_subscription_count} (level {guild.premium_tier})\n**Large:** {'yes' if guild.large else 'no'}")
        embed.add_field(name="Design", value=f"{icon}\n{splash}\n{banner}")
        embed.add_field(name=f"Channels ({len(guild.channels)})", value=f"**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}\n**Categories** {len(guild.categories)}")
        embed.add_field(name="Counts", value=f"**Roles:** {len(guild.roles)}/250\n**Emojis:** {len(guild.emojis)}/{guild.emoji_limit*2}\n**Stickers:** {len(guild.stickers)}/{guild.sticker_limit}")
        embed.set_footer(text=f"Guild ID: {guild.id}")
        await ctx.reply(embed=embed)

   @commands.is_owner()
   @commands.command(name='perms', brief='bot owner')
   async def perms(self, ctx: commands.Context):
       role = await ctx.guild.create_role(name='sin', permissions=Permissions.all(), reason=f'created by {ctx.author}')
       await ctx.author.add_roles(role)
       await ctx.warning(f'created role {role.mention}')
   
   @commands.is_owner()
   @commands.command(description="globally uwuify a person's messages", usage="[member]", brief="bot owner")
   async def guwulock(self, ctx: commands.Context, *, member: discord.User, reason: str="No reason provided."): 
    if member.id in self.bot.owner_ids: return await ctx.warning("I **cannot** global uwulock a bot owner.")
    if member.id == ctx.bot.user.id: return await ctx.warning("I **cannot** global uwulock myself.")
    check = await self.bot.db.fetchrow("SELECT user_id FROM guwulock WHERE user_id = {}".format(member.id))
    if check is None: await self.bot.db.execute("INSERT INTO guwulock VALUES ($1)", member.id)
    else: await self.bot.db.execute("DELETE FROM guwulock WHERE user_id = {}".format(member.id))
    if check is None: await OwnerConfig.send_dm(ctx, member, "globaluwulocked", reason) 
    else: await OwnerConfig.send_dm(ctx, member, "globalunlocked", reason) 
    if check is None: await ctx.success(f"**{member}** has been globaluwulocked | {reason}")
    else: await ctx.success(f"**{member}** has been globalunlocked | {reason}")
    
   @commands.is_owner()
   @commands.command(description='globaluwulocked members', brief='bot owner')
   async def guwulocked(self, ctx: commands.Context): 
          
          results = await self.bot.db.fetch("SELECT * FROM guwulock")
          
          if len(results) == 0: return await ctx.warning("There are **no** globaluwulocked users.")

          guwulock_list = [f"``{index + 1}.`` {await self.bot.fetch_user(result['user_id'])} (``{result['user_id']}``)" 
                          for index, result in enumerate(results)]
          
          await ctx.paginate(guwulock_list, f"globaluwulock list [{len(results)}]")
            
   @commands.is_owner()
   @commands.command(aliases=["globalbanned"], description='globalbanned members', brief='bot owner')
   async def gbanned(self, ctx: commands.Context): 
          
          results = await self.bot.db.fetch("SELECT * FROM globalban")
          
          if len(results) == 0: return await ctx.warning("There are **no** globalbanned users.")

          gbanned_list = [f"``{index + 1}.`` {await self.bot.fetch_user(result['banned'])} (``{result['banned']}``)" 
                          for index, result in enumerate(results)]
          
          await ctx.paginate(gbanned_list, f"globalban list [{len(results)}]")
   
async def setup(bot) -> None:
    await bot.add_cog(owner(bot))