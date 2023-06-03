import discord 
from discord.ext import commands 
from utils.havePerms import havePerms

def find_role(ctx: commands.Context, argument: str) -> discord.Role | None: 
  for role in ctx.guild.roles:
    if role.name == "@everyone": 
      continue 
    if argument in role.name: 
      return role
  return None   

class NewRoleConverter(commands.Converter): 
  async def convert(self, ctx: commands.Context, argument: str): 
   try:
     role = await commands.RoleConverter().convert(ctx, argument)
   except commands.BadArgument: 
    role = find_role(ctx, argument)
    if role is None: 
      raise commands.BadArgument("Role not found")
   if not role.is_assignable(): raise commands.CommandError("The bot cannot manage this role") 
   if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id: raise commands.BadArgument("You cannot manage this role")
   return role

class RoleCommand(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
  
  @commands.command()
  @havePerms(["manage_roles"])
  async def role(self, ctx: commands.Context, member: discord.Member, *, role: NewRoleConverter):
   if not role in member.roles: 
    await member.add_roles(role, reason=f"{ctx.author} added the role")
    return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"Added role {role.mention} to {member.mention}"))  
   else: 
    await member.remove_roles(role, reason=f"{ctx.author} removed the role")
    return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"Removed role {role.mention} from {member.mention}"))
    
async def setup(bot: commands.Bot) -> None: 
  await bot.add_cog(RoleCommand(bot))      