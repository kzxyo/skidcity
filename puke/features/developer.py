import time

from puke import Puke
from puke.managers import Context

from discord import Embed
from discord.ext.commands import Cog, command

from aiohttp import ClientSession

class Developer(Cog):
    def __init__(self, bot):
        self.bot: Puke = bot

    async def cog_check(
        self: "Developer", 
        ctx: Context
    ) -> bool:
        return await self.bot.is_owner(ctx.author)
    
    @command(
        name="reload",
        aliases=['rl']
    )
    async def reload(
        self: "Developer",
        ctx: Context
    ):
        """
        Reload all functions
        """

        reloaded = list()

        for feature in list(self.bot.extensions):
            try:
                await self.bot.reload_extension(feature)
            except:
                return await ctx.warn(f"Failed to reload `{feature}`!")
            
            reloaded.append(feature)

        return await ctx.approve(f"Successfully reloaded `{len(reloaded)}` features!")
        
        
        

    @command(
        name="botavatar",
        aliases=['ba', 'setpfp', 'pfp']
    )
    async def botavatar(
        self: "Developer", 
        ctx: Context, 
        image: str = None
    ):
        """
        Sets bot's profile picture
        """
        if not image:
            image = ctx.message.attachments[0].url



        async with ClientSession() as session:
            async with session.get(image) as response:
                if response.status != 200:
                    raise ValueError("image unfuckingreadable.")

                img = await response.read()

        await self.bot.user.edit(avatar=img)

        embed = Embed(description=f"{self.bot.user.name} Avatar changed to")
        embed.set_image(url=image)
        await ctx.reply(embed=embed)
        

    @command(
      name="botname",
      aliases=["bn", "changename"]
      )
    async def botname(self: "Developer", ctx: Context, new_name: str): 
        """
        changes bot's name
        """
        await ctx.guild.me.edit(nick=new_name)
        await ctx.approve(f"Changed my display name to `{new_name}`")

    @command(
      name="selfpurge",
      aliases=[
          "self",
               "clean"]
      )
    async def selfpurge(self: "Developer", ctx: Context, limit: int = 100):
        """
        self purges the owner's messages
        """
        deleted = await ctx.message.channel.purge(limit=limit, check=lambda msg: msg.author == ctx.author)
        m = await ctx.approve(f"> Deleted `{len(deleted)}` messages from {ctx.author.mention}.")
        time.sleep(0.2)
        await m.delete()


async def setup(bot: Puke):
    await bot.add_cog(Developer(bot))