import discord, uwuipy
from discord.ext import commands
from tools.utils.checks import Perms, Mod
from typing import Union
from tools.utils.utils import NoStaff

valid = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

def key(s):
  return s[2]

def checkusername(table: str) -> bool: 
  if len(table) > 10: return False
  for i in table: 
    if not i in valid: return False 
  return True 

async def uwushit(bot, text: str) -> str:
    uwu = uwuipy.uwuipy()
    return uwu.uwuify(text)

def premium():
  async def predicate(ctx: commands.Context):
    check = await ctx.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = $1", ctx.author.id)
    if check is None:
      await ctx.send_warning("You are not a donor. Boost the [**support server**](https://discord.gg/kQcYeuDjvN) to get donor perks")
      return False
    return True
  return commands.check(predicate)

async def get_usernames(bot, type, username):   
    if type == "str": 
      results = await bot.db.fetch("SELECT * FROM oldusernames WHERE username = $1", username)      
      data = [r for r in results] 
    data.sort(key=key, reverse=True)
    return data

class donor(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.Cog.listener("on_message")
    async def uwuwebhook(self, message: discord.Message):
      if not message.guild: return
      if isinstance(message.author, discord.User): return
      check = await self.bot.db.fetchrow("SELECT * FROM uwulock WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)
      if check:
        try: 
            await message.delete()
            uwumsg = await uwushit(self.bot, message.clean_content)
            webhooks = await message.channel.webhooks()
            if len(webhooks) == 0: webhook = await message.channel.create_webhook(name="vilan - uwulock", reason="uwulock")
            else: webhook = webhooks[0] 
            await webhook.send(content=uwumsg, username=message.author.name, avatar_url=message.author.display_avatar.url)
        except: pass 
    
    @commands.command(description="remove the hardban from an user", help="donor", usage="[user]")
    @Perms.get_perms("ban_members")
    @premium()
    async def unhardban(self, ctx: commands.Context, *, member: discord.User):
      check = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = $1 AND banned = $2", ctx.guild.id, member.id)
      if not check: return await ctx.send_warning(f"**{member}** is not hardbanned")
      await self.bot.db.execute("DELETE FROM hardban WHERE guild_id = $1 AND banned = $2", ctx.guild.id, member.id)
      await ctx.guild.unban(member, reason="unhardbanned by {}".format(ctx.author))
      await ctx.message.add_reaction("<:catthumbsup:1081227675462533161>")
    
    @commands.command(description="hardban an user from the server", help="donor", usage="[user]")
    @Perms.get_perms("ban_members")
    @premium()
    async def hardban(self, ctx: commands.Context, *, member: Union[discord.Member, discord.User]):
      if isinstance(member, discord.Member):
        if member.id == ctx.author.id: return await ctx.send_warning("You cannot hardban yourself")
        if member.id == self.bot.user.id: return await ctx.reply("im invicible")
        if await Mod.check_hieracy(ctx, member):
         che = await self.bot.db.fetchrow("SELECT * FROM hardban WHERE guild_id = $1 AND banned = $2", ctx.guild.id, member.id)
         if che: return await ctx.send_success(f"**{member}** has been hardbanned by **{await self.bot.fetch_user(che['author'])}**")
         await ctx.guild.ban(member, reason="hardbanned by {}".format(ctx.author))
         await self.bot.db.execute("INSERT INTO hardban VALUES ($1,$2,$3)", ctx.guild.id, member.id, ctx.author.id)
         await ctx.message.add_reaction("<:catthumbsup:1081227675462533161>")
    
    @commands.command(description="uwuify a person's messages", help="donor", usage="[member]", brief="administrator")
    @Perms.get_perms("administrator")
    @premium()
    async def uwulock(self, ctx: commands.Context, *, member: NoStaff): 
      if member.bot: return await ctx.send_warning("You cannot **uwulock** a bot")
      check = await self.bot.db.fetchrow("SELECT user_id FROM uwulock WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))    
      if check is None: await self.bot.db.execute("INSERT INTO uwulock VALUES ($1,$2)", ctx.guild.id, member.id)
      else: await self.bot.db.execute("DELETE FROM uwulock WHERE user_id = {} AND guild_id = {}".format(member.id, ctx.guild.id))    
      return await ctx.message.add_reaction("<:catthumbsup:1081227675462533161>")    
    
    commands.command(description="find names with certain discriminators" ,help="donor", aliases=["pomelo"])
    @premium()
    async def lookup(self, ctx, name: str=None):
                t = str(name) 
                type = "str"
                data = await get_usernames(self.bot, type, name)
                i=0
                k=1
                l=0
                number = []
                messages = []
                num = 0
                auto = ""  
                if data:
                    for table in data:                   
                        username = table[0]
                        if checkusername(username) is False: continue
                        num += 1
                        auto += f"\n`{num}` @{username}: <t:{int(table[2])}:R> "
                        k+=1
                        l+=1
                        if l == 10:
                          messages.append(auto)
                          number.append(discord.Embed(color=self.bot.color, title="Searches by name", description=auto).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar))
                          i+=1
                          auto = ""
                          l=0
                    messages.append(auto)
                    embed = discord.Embed(color=self.bot.color, title="Searches by name", description=auto).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                    number.append(embed)
                    await ctx.paginator(number) 
                else: return await ctx.send_warning(f"No names available") 
    
    @commands.command(description="purge an amount of messages sent by you", help="donor", usage="[amount]")
    @premium()
    async def selfpurge(self, ctx: commands.Context, amount: int):
      mes = []
      async for message in ctx.channel.history():
       if (len(mes) == amount +1): break
       if message.author == ctx.author: mes.append(message)
            
      await ctx.channel.delete_messages(mes)
    
    @commands.command(description="check the premium perks", help="donor")
    async def perks(self, ctx: commands.Context): 
      embed = discord.Embed(color=self.bot.color, title="donator perks", description="Boost **1** time the [**support server**](https://discord.gg/kQcYeuDjvN) to get access to these perks.")
      embed.add_field(name="commands", value='\n'.join([f"**{command.name}** - {command.description}" for command in set(ctx.cog.walk_commands()) if not command.name in [ctx.command.name, 'donate']]), inline=False) 
      return await ctx.reply(embed=embed) 
    
    @commands.command(description="see how can you become a donator", help="donor", aliases=["payment"])
    async def donate(self, ctx: commands.Context): 
      embed = discord.Embed(color=self.bot.color, title="donate method", description=f"<:boosts:1079296391605661886> - [`support server`](https://discord.gg/kQcYeuDjvN)\nBoosting will get you access to premium perks.")
      boost = discord.ui.Button(emoji="<:boosts:1079296391605661886>")
      view = discord.ui.View(timeout=None)

      async def boost_callback(interaction: discord.Interaction): 
        await interaction.response.send_message("boost https://discord.gg/kQcYeuDjvN for perks", ephemeral=True)
    
      boost.callback = boost_callback
    
      view.add_item(boost)
      await ctx.reply(embed=embed, view=view, mention_author=False)
    
async def setup(bot):
    await bot.add_cog(donor(bot))