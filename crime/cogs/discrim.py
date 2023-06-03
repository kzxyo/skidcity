import discord, datetime
from discord.ext import commands
from .utils.util import Emojis
from cogs.utilevents import blacklist
from .utils.views import Views

class tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.available_tags = []
        
    @commands.Cog.listener()
    async def on_ready(self):
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS tracker (guild_id INTEGER, channel INTEGER)")
        await self.bot.db.commit()
    
    @commands.Cog.listener()
    async def on_available_tag(self, user:discord.User):
        self.available_tags.insert(0,
            {
                "user": user,
                "time": datetime.now()
            }
        )
        
    @commands.Cog.listener()
    async def on_user_update(self, before:discord.Member, after:discord.Member):
        if before.avatar == after.avatar:
            if before.discriminator == "0001":
                self.bot.dispatch('available_tag', before)
                for x in self.bot.guilds:
                    async with self.bot.db.cursor() as e:
                        await e.execute(f"SELECT * FROM tracker WHERE guild_id = {x.id}")
                        channel = await e.fetchone()
                        if channel is not None:
                            ch = self.bot.get_channel(int(channel[1]))
                            await ch.send(f"**new tag available**: {before}")
                

    @commands.group(
        name = "tracker",
        description = "Tracks #0001 Tags and sends it through a channel",
        aliases = ["track"],
        invoke_without_command = True
    )
    @blacklist()
    @commands.has_permissions(manage_channels=True)
    async def tracker(self, ctx):
        pass

    @tracker.command(
        name = "add",
        description = "Adds a channel to track #0001 tags"
    )
    @commands.has_permissions(manage_channels=True)
    @blacklist()
    async def add(self, ctx, channel=None):
        if channel == None:
            channel = ctx.channel.id
        try:
            if "<#" in channel:
                channel = channel.replace("<#", "")
            if ">" in channel:
                channel = channel.replace(">", "")
            async with self.bot.db.cursor() as c:
                await c.execute(f"SELECT * FROM tracker WHERE guild_id = ? AND channel = ?", (ctx.guild.id, channel,))
                check = await c.fetchone()
                if check is not None:
                    await c.execute("UPDATE tracker SET guild_id = ? AND channel = ?", (ctx.guild.id, channel,)) 
                    await self.bot.db.commit()
                elif check is None:
                    await c.execute("INSERT INTO tracker VALUES (?,?)", (ctx.guild.id, channel,))
                    await self.bot.db.commit()
                await ctx.reply(embed=discord.Embed(
                    description=f"{Emojis.check} Successfully **Added** the channel <#{channel}> to **track** discriminators",
                    color=0x2f3136), mention_author=False)
        except Exception as e:
            print(e)
            await ctx.reply(embed=discord.Embed(
                description=f"{Emojis.check} Successfully **Added** the channel <#{channel}> to **track** discriminators",
                color=0x2f3136), mention_author=False)
            
    @commands.command(name = "tags", 
             description="See available 0001 tags")
    @blacklist()
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def tags(self, ctx):
        async with ctx.typing():
            available_tags = self.available_tags.copy()
            if available_tags:
                max_tags = 10
                tags = tuple(available_tags[x:x + max_tags]  for x in range(0, len(available_tags), max_tags))
                pages = []

                i = 0
                for group in tags:
                    page = discord.Embed()
                    page.set_author(name=ctx.author.name,icon_url=ctx.author.display_avatar.url)
                    page.title = f"Recent Tag Changes"
                    page.description = '\n'.join([f"`{idx+1+i}` **-** {x['user']}: {discord.utils.format_dt(x['time'], style='R')}" for idx, x in enumerate(group)])
                    pages.append(page)
                    i += len(group) +1
                
                if len(pages) == 1:
                    await ctx.reply(embed=pages[0], mention_author=False)
                else:
                    paginator = Views.Paginator()
                    await paginator.start(ctx,pages)
            else:
                embed = discord.Embed()
                embed.description = "> There are no tags avaiilbieleeioe :skull:!"
                await ctx.reply(embed=embed, mention_author=False)
async def setup(bot):
    await bot.add_cog(tracker(bot))