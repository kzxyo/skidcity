import discord, humanfriendly, datetime
from discord.ext import commands
import asyncio

class donor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.group(
        help="manage donors",
        usage="donor",
        aliases=["dono"],
        hidden=True
    )
    @commands.is_owner()
    async def donor(self, ctx):
        if ctx.invoked_subcommand is None:
            donors = await self.db.fetch("SELECT * FROM donors")
            if not donors:
                return await ctx.reply("no donors found")


            pages = []
            for i in range(0, len(donors), 10):
                embed = discord.Embed(
                    color=self.bot.color,
                    title=f"donors • {len(donors)}"
                )
                page = ""
                for donor in donors[i:i+10]:
                    expires = f"in {humanfriendly.format_timespan(int((donor['time_expires'] - datetime.datetime.utcnow()).total_seconds()))}"
                    page += f"<@{donor['user_id']}> • {expires}\n"
                embed.description = page
                pages.append(embed)
            await self.bot.paginator(ctx, pages)
            
    @commands.Cog.listener()
    async def on_ready(self):
        # every 3 seconds check for donors
        while True:
            donors = await self.db.fetch("SELECT * FROM donors")
            if not donors:
                await asyncio.sleep(300)
                continue

            for donor in donors:
                if donor['time_expires'] < datetime.datetime.utcnow():
                    await self.db.execute("DELETE FROM donors WHERE user_id = $1", donor['user_id'])
                    user = self.bot.get_user(donor['user_id'])
                    if not user:
                        continue
                    try:
                        await user.send(f"your donor has expired")
                    except:
                        pass

            await asyncio.sleep(300)

    @donor.command(
        help="add donor",
        usage="donor add <user> <time>",
        aliases=["a"],
        hidden=True
    )
    @commands.is_owner()
    async def add(self, ctx, user: discord.User, time: str = "7d"):
        try:
            time = str(humanfriendly.parse_timespan(time))
        except:
            return await ctx.reply("invalid time format")

        donor = await self.db.fetchrow("SELECT * FROM donors WHERE user_id = $1", user.id)
        if donor:
            return await ctx.reply("user is already a donor")

        time_expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(float(time)))
        await self.db.execute("INSERT INTO donors (user_id, time_expires, added_by) VALUES ($1, $2, $3)", user.id, time_expires, ctx.author.id)
        duration_seconds = int((time_expires - datetime.datetime.utcnow()).total_seconds())
        formatted_duration = humanfriendly.format_timespan(duration_seconds)
        await ctx.reply(f"added user as donor until {formatted_duration}")


    @donor.command(
        help="remove donor",
        usage="donor remove <user>",
        aliases=["r"],
        hidden=True
    )
    @commands.is_owner()
    async def remove(self, ctx, user: discord.User):
        donor = await self.db.fetchrow("SELECT * FROM donors WHERE user_id = $1", user.id)
        if not donor:
            return await ctx.reply("user is not a donor")

        await self.db.execute("DELETE FROM donors WHERE user_id = $1", user.id)
        await ctx.reply("user removed as donor")

    @donor.command(
        help="check if user is a donor",
        usage="donor check <user>",
        aliases=["c"],
        hidden=True
    )
    @commands.is_owner()
    async def check(self, ctx, user: discord.User):
        donor = await self.db.fetchrow("SELECT * FROM donors WHERE user_id = $1", user.id)
        if not donor:
            return await ctx.reply("user is not a donor")
        else:
            await ctx.reply(f"user is a donor and expires <t:{int(donor['time_expires'].timestamp())}:R>\nadded by: <@{donor['added_by']}> (<t:{int(donor['time_added'].timestamp())}:R>)")


async def setup(bot):
    await bot.add_cog(donor(bot))