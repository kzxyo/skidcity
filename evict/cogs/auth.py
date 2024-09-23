import discord, datetime
from discord.ext import commands
from typing import Union
from patches.permissions import Permissions

class auth(commands.Cog): 
    def __init__(self, bot: commands.Bot): 
        self.bot = bot

    @commands.command()
    @Permissions.authorize()
    async def authorize(self, ctx: commands.Context, guild: int, buyer: Union[discord.Member, discord.User]): 
     
     channel = self.bot.get_channel(1268645258288435346)
     
     check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1", guild)
     if check is not None: return await ctx.warning("This server is **already** whitelisted.")

     embed = discord.Embed(color=self.bot.color, description="The following server has been authorized", title="Authorization", timestamp=datetime.datetime.now())
     
     embed.add_field(name="Server ID", value=f"{guild}", inline=False)
     embed.add_field(name="Buyer Mention", value=f"{buyer.mention}", inline=False)
     embed.add_field(name="Buyer ID", value=f"{buyer.id}", inline=False)
     embed.add_field(name="Staff Mention", value=f"{ctx.author.mention}", inline=False)
     embed.add_field(name="Staff ID", value=f"{ctx.author.id}", inline=False)

     embed.set_thumbnail(url=ctx.author.avatar.url)

     await channel.send(embed=embed)
     await self.bot.db.execute("INSERT INTO authorize VALUES ($1,$2)", guild, buyer.id)
     await ctx.success(f"I have **added** the guild ID **{guild}** as an authorized server to {buyer}.")
     
     view = discord.ui.View()
     view.add_item(discord.ui.Button(label="invite", url=discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions.all())))
     
     try: await buyer.send(f"Your server **{guild}** has been authorized. Invite me below.", view=view)
     except: pass
     
    @commands.command()
    @commands.is_owner()
    async def authorizeall(self, ctx: commands.Context): 
        
        for g in self.bot.guilds:
            await self.bot.db.execute("INSERT INTO authorize values ($1, $2) ON CONFLICT (guild_id) DO NOTHING", g.id, g.owner.id)
        
        embed = discord.Embed(color=self.bot.color, description=f"{ctx.author.mention}: authorizing **all** servers.")
        message = await ctx.reply(embed=embed)
        
        await message.edit(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: authorized **all** servers."))
     
    @commands.command()
    @Permissions.authorize()
    async def getauth(self, ctx: commands.Context, *, member: discord.User): 
     
     results = await self.bot.db.fetch("SELECT * FROM authorize WHERE buyer = $1", member.id)
     if len(results) == 0: return await ctx.warning("There is no server authorized for **{}**.".format(member))

     await ctx.paginate([f"{f'**{str(self.bot.get_guild(m[0]))}** `{m[0]}`' if self.bot.get_guild(m[0]) else f'`{m[0]}`'}" for m in results],
            f"Authorized guilds ({len(results)})",
            {"name": member.name, "icon_url": member.display_avatar.url})

    @commands.command()
    @commands.is_owner()
    async def unauthorize(self, ctx: commands.Context, id:int=None, *, reason: str='No Reason Provided'): 

        channel = self.bot.get_channel(1268645258288435346)
        
        check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1", id)
        if check is None: return await ctx.warning(f"I am **unable** to find this server.")

        embed = discord.Embed(color=self.bot.color, description="The following server has been unauthorized", title="Unauthorization", timestamp=datetime.datetime.now())
     
        embed.add_field(name="Server ID", value=f"{id}", inline=False)
        embed.add_field(name="Staff Mention", value=f"{ctx.author.mention}", inline=False)
        embed.add_field(name="Staff ID", value=f"{ctx.author.id}", inline=False)

        embed.set_thumbnail(url=ctx.author.avatar.url)
        
        await channel.send(embed=embed)
        await self.bot.db.execute("DELETE FROM authorize WHERE guild_id = $1", id)
        await ctx.success(f"I have **removed** the authorization for **{id}**.")

async def setup(bot): 
    await bot.add_cog(auth(bot))    
