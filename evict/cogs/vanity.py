from typing import Optional
from discord import Member, Guild, Role
from dataclasses import dataclass
from discord.ext import commands

@dataclass
class Vanity:
	vanity: str
	role: Role
 
class vanity(commands.Cog):
	def __init__(self, bot):
	    self.bot = bot
  
 
@commands.command(name = 'vanityrole', usage = "[role]")
@commands.has_permissions(manage_guild = True)
async def vanityrole(self, ctx, *, role: Optional[Role] = None):
		vanity = ctx.guild.vanity_url_code
		if vanity == None:
			return await ctx.warning(f"you cannot use **vanity roles**")
		if role == None:
			await self.bot.db.execute("""DELETE FROM vanity_role WHERE guild_id = $1""", ctx.guild.id)
			try:
				self.cache.pop(ctx.guild.id)
			except:
				pass
			return await ctx.success(f"successfully **disabled** vanity roles")
		else:
			await self.bot.db.execute("""INSERT INTO vanity_role (guild_id, role_id) VALUES($1,$2) ON CONFLICT (guild_id) DO UPDATE SET role_id = excluded.role_id""", ctx.guild.id, role.id)
			self.cache[ctx.guild.id] = Vanity(vanity = vanity, role = role)
			return await ctx.success(f"successfully **enabled** vanity roles, vanity repping will now reward with {role.mention}")


async def setup(bot):
	    await bot.add_cog(vanity(bot))
