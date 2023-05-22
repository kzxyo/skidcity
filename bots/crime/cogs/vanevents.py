import discord ; from discord.ext import commands ; from cogs.modules import utils 

class vanevents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


@commands.Cog.listener()
async def on_presence_update(self, before: discord.Member, after: discord.Member):

    user = after
    guild = after.guild
    try:
        db = utils.read_json('vanity')
        vanity = db[str(after.guild.id)]['vanity']
        try: ba = str(before.activity.name).lower()
        except: ba = 'none'
        try: aa = str(after.activity.name).lower()
        except: aa = 'none'
        if ba == aa: return
        if db[str(after.guild.id)]['vanity'] in aa and db[str(after.guild.id)]['vanity'] not in ba:
            try:
                x = after.guild.get_role(db[str(after.guild.id)]['role'])
                await after.add_roles(x, reason='crime vanity: vanity in status')
            except: pass
            try:
                z = await after.guild.fetch_channel(db[str(after.guild.id)]['channel'])
                await z.send(embed=discord.Embed(color=0x2f3136, description=f"{db[str(after.guild.id)]['message'].format(user=user, guild=guild, vanity=vanity)}"))
            except: pass
        elif db[str(after.guild.id)]['vanity'] not in aa and db[str(after.guild.id)]['vanity'] in ba:
            try:
                x = after.guild.get_role(db[str(after.guild.id)]['role'])
                await after.remove_roles(x, reason='crime vanity: vanity removed from status')
            except: pass

    except:
        pass

async def setup(bot):
    await bot.add_cog(vanevents(bot))             
