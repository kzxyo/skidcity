import discord 
from discord.ext import commands

class events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        embed = discord.Embed(color=0x2f3136, description=f"> Axie Join In  **{guild.name}** Owner **{guild.owner}** And **{guild.member_count}** members")
        embed.set_footer(text=f"ID: {guild.id}")
        await self.bot.get_channel(1048979715655991395).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
       embed = discord.Embed(color=0x2f3136, description=f"> Axie Left From**{guild.name}** Owner **{guild.owner}** And **{guild.member_count}** members")
       embed.set_footer(text=f"ID: {guild.id}")
       await self.bot.get_channel(1048979715655991395).send(embed=embed)
       
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
       if message.content == f"<@{self.bot.user.id}>": 
        await message.reply("My prefix is `.`")

async def commandhelp(self, ctx, cmd):
    try:
       command = self.bot.get_command(cmd)
       if command.usage is None:
        usage = ""
       else:
        usage = command.usage 

       embed = Embed(color=0x2f3136, title=command, description=command.help)
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="category", value=command.description)
       if command.brief:
        embed.add_field(name="commands", value=command.brief, inline=False)
       embed.add_field(name="usage", value=f"{await self.bot.command_prefix(self.bot, ctx.message)}{cmd} {usage}", inline=False)
       embed.add_field(name="aliases", value=', '.join(map(str, command.aliases)) or "none")
       await ctx.reply(embed=embed, mention_author=False)
    except:
       await ctx.reply(f"Can't find the `{cmd}` command", mention_author=False)

async def setup(bot) -> None: 
    await bot.add_cog(events(bot))        
