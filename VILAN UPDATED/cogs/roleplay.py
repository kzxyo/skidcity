import discord, asyncio, random
from discord.ext import commands
from tools.utils.checks import Perms, Pot

class RolePlay(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.pot_emoji = "🍃"
        self.pot_color = 0x57D657
        self.smoke = "🌬"
    
    async def pot_send(self, ctx: commands.Context, message: str) -> discord.Message:
      return await ctx.reply(embed=discord.Embed(color=self.pot_color, description=f"{self.pot_emoji} {ctx.author.mention}: {message}"))

    async def smoke_send(self, ctx: commands.Context, message: str) -> discord.Message:
      return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: {message}"))
    
    @commands.group(name="pot", invoke_without_command=True)
    async def potcmd(self, ctx):
      await ctx.create_pages()
    
    @potcmd.command(name="toggle", help="roleplay", description="toggle the server pot")
    @Perms.get_perms("manage_guild")
    async def pot_toggle(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM pot WHERE guild_id = {}".format(ctx.guild.id)) 
     if not check: 
      await self.bot.db.execute("INSERT INTO pot VALUES ($1,$2,$3)", ctx.guild.id, 0, ctx.author.id)
      return await self.pot_send(ctx, "The pot is **yours**")
     await self.bot.db.execute("DELETE FROM pot WHERE guild_id = $1", ctx.guild.id)
     return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: Lost the server's pot")) 
    
    @potcmd.command(name="stats", help="roleplay", description="check pot stats", aliases=["status", "settings"])
    @Pot.check_pot()
    async def pot_stats(self, ctx: commands.Context):      
      check = await self.bot.db.fetchrow("SELECT * FROM pot WHERE guild_id = $1", ctx.guild.id)
      embed = discord.Embed(color=self.pot_color, description=f"{self.smoke} hits: **{check['hits']}**\n{self.pot_emoji} holder: <@{check['holder']}>")      
      embed.set_author(icon_url=ctx.guild.icon, name=f"{ctx.guild.name}'s pot")
      return await ctx.reply(embed=embed)

    @potcmd.command(name="hit", help="roleplay", description="hit the server pot")
    @Pot.check_pot()
    @Pot.pot_owner()
    async def pot_hit(self, ctx: commands.Context): 
      mes = await self.pot_send(ctx, "Hitting the **pot**....")
      await asyncio.sleep(2)
      check = await self.bot.db.fetchrow("SELECT * FROM pot WHERE guild_id = $1", ctx.guild.id)
      newhits = int(check["hits"]+1)
      embed = discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: You just hit the **pot**. This server has now a total of **{newhits}** hits!")
      await mes.edit(embed=embed)
      await self.bot.db.execute("UPDATE pot SET hits = $1 WHERE guild_id = $2", newhits, ctx.guild.id)
    
    @pot_hit.error 
    async def on_error(self, ctx: commands.Context, error: Exception): 
     if isinstance(error, commands.CommandOnCooldown): return await self.pot_send(ctx, "Slow down g, You are getting too high")
    
    @potcmd.command(name="pass", help="roleplay", description="pass the pot to someone else", usage="[member]")
    @Pot.check_pot()
    @Pot.pot_owner()
    async def pot_pass(self, ctx: commands.Context, *, member: discord.Member):
     if member.id == self.bot.user.id: return await ctx.reply("I don't smoke thanks")
     elif member.bot: return await ctx.send_warning("Bots don't smoke")
     elif member.id == ctx.author.id: return await ctx.send_warning("You already have the **pot**")
     await self.bot.db.execute("UPDATE pot SET holder = $1 WHERE guild_id = $2", member.id, ctx.guild.id)
     await self.pot_send(ctx, f"**Pot** passed to **{member.name}**")
    
    @potcmd.command(name="steal", help="roleplay", description="steal the server's pot")
    @Pot.check_pot()
    async def pot_steal(self, ctx: commands.Context): 
     check = await self.bot.db.fetchrow("SELECT * FROM pot WHERE guild_id = $1", ctx.guild.id)
     if check["holder"] == ctx.author.id: return await self.joint_send(ctx, "You already have the **pot**")
     chances = ["yes", "yes", "yes", "no", "no"]
     if random.choice(chances) == "no": return await self.smoke_send(ctx, f"You tried to steal the **pot** and **{(await self.bot.fetch_user(int(check['holder']))).name}** hit you")
     await self.bot.db.execute("UPDATE pot SET holder = $1 WHERE guild_id = $2", ctx.author.id, ctx.guild.id)
     return await self.pot_send(ctx, "You got the server **pot**")
    
    @commands.command(description="kiss an user", usage="[member]", help="roleplay")
    async def kiss(self, ctx: commands.Context, *, member: discord.Member):
     lol = await self.bot.session.json("http://api.nekos.fun:8080/api/kiss")
     embed = discord.Embed(color=self.bot.color, description=f"*Aww how cute!* **{ctx.author.name}** kissed **{member.name}**")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.command(description="cuddle an user", usage="[member]", help="roleplay")
    async def cuddle(self, ctx, *, member: discord.Member):
     lol = await self.bot.session.json("http://api.nekos.fun:8080/api/cuddle")
     embed = discord.Embed(color=self.bot.color, description=f"*Aww how cute!* **{ctx.author.name}** cuddled **{member.name}**")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.command(description="hug an user", usage="[member]", help="roleplay")
    async def hug(self, ctx: commands.Context, *, member: discord.Member): 
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"*Aww how cute!* **{ctx.author.name}** hugged **{member.name}**")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.command(description="pat an user", usage="[member]", help="roleplay")
    async def pat(self, ctx, *, member: discord.Member):
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"*Aww how cute!* **{ctx.author.name}** pats **{member.name}**")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.command(description="slap an user", usage="[member]", help="roleplay")
    async def slap(self, ctx, *, member: discord.Member): 
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** slaps **{member.name}***")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.command(description="start laughing", help="roleplay")
    async def laugh(self, ctx): 
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** laughs")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

    @commands.command(description="start crying", help="roleplay")
    async def cry(self, ctx):
     lol = await self.bot.session.json(f"http://api.nekos.fun:8080/api/{ctx.command.name}")
     embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** cries")
     embed.set_image(url=lol["image"])
     return await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(RolePlay(bot))