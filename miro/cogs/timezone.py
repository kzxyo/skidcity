import discord
import pytz


from data.database import Async
from discord import Embed, Member
from discord.ext.commands import command, Cog, group


class timezone(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.color = 0x4c5264
        self.db = Async.db

    @group(
        name="timezone",
        description= "See user's timezone",
        usage="timezone <member>",
        help="timezone @Claqz",
        aliases=["time", "tz"],
        invoke_without_command=True,
    )
    async def timezone(self, ctx, *, member: Member = None):
        member = member or ctx.author

        location = await self.db.find_one({"guild_id": str(ctx.guild.id), "user_id": str(member.id)})
        if not location:
            return await ctx.send(embed=discord.Embed(
                description="Your **timezone** has not yet been set\n> Use {}timezone set (location) to set it!".format(
                    ctx.prefix
                )
                if member == ctx.author
                else "**{}** has not yet set up their **timezone**".format(member.mention),
                color=self.color,
            ))

        timezone_id = location.get("timezone")
        try:
            timezone_info = pytz.timezone(timezone_id)
            timestamp = discord.utils.utcnow().astimezone(timezone_info)
        except pytz.UnknownTimeZoneError:
            return await ctx.send(f"Unknown timezone: {timezone_id}")

        embed = discord.Embed(
            description="Your current time is **{}**".format(
                timestamp.strftime("%b %d, %I:%M %p")
            )
            if member == ctx.author
            else "**{}**'s current time is **{}**".format(
                member.mention, timestamp.strftime("%b %d, %I:%M %p")
            ),
            color=self.color,
        )
        await ctx.send(embed=embed)

    @timezone.command(
        name="set",
        usage="timezone set (country)",
        example="france"
    )
    async def timezone_set(self, ctx, location, state=None):
        country_codes = pytz.country_names
        lowercase_location = location.lower()
        matching_codes = [
            code
            for code, country_name in country_codes.items()
            if lowercase_location in country_name.lower()
        ]

        if not matching_codes:
            return await ctx.send(f"No timezones found for {location}")

        country_code = matching_codes[0]
        timezones = pytz.country_timezones.get(country_code, [])

        if not timezones:
            return await ctx.send(f"No timezones found for {location}")

        if state:
            location_query = f"{state}, {country_code}"
        else:
            location_query = country_code

        timezone_id = None
        for tz in timezones:
            if state and state.lower() in tz.lower():
                timezone_id = tz
                break
            elif not state and location.lower() in tz.lower():
                timezone_id = tz
                break

        if not timezone_id:
            return await ctx.send(f"No timezones found for {location} ({state})")

        await self.db.update_one(
            {"guild_id": str(ctx.guild.id), "user_id": str(ctx.author.id)},
            {"$set": {"timezone": timezone_id}},
            upsert=True
        )
        await ctx.send(
            embed=Embed(
                description=f"Your **timezone** has been set to `{timezone_id}`, mate!",
                color=self.color
            )
        )

    @timezone.command(name="list", aliases=["all"])
    async def timezone_list(self, ctx):
        locations = await self.db.find({"guild_id": str(ctx.guild.id)}).to_list(length=None)
        if not locations:
            return await ctx.send("No **timezones** have been set")

        timezone_entries = []
        for location in locations:
            member = ctx.guild.get_member(int(location["user_id"]))
            if member:
                timezone_id = location["timezone"]
                try:
                    timezone_info = pytz.timezone(timezone_id)
                    timestamp = discord.utils.utcnow().astimezone(timezone_info)
                    timezone_entry = f"{member.mention} (`{timezone_id}`): {timestamp.strftime('%b %d, %I:%M %p')}"
                    timezone_entries.append(timezone_entry)
                except pytz.UnknownTimeZoneError:
                    continue

        chunks = [timezone_entries[i:i + 10] for i in range(0, len(timezone_entries), 10)]

        for chunk in chunks:
            embed = discord.Embed(
                title="Member Timezones",
                description="\n".join(chunk),
                color=self.color
            )
            await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(timezone(bot))