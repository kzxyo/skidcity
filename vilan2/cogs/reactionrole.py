import discord 
from discord.ext import commands
from tools.utils.checks import Perms
from typing import Union 

class ReactionRoles(commands.Cog): 
  def __init__(self, bot: commands.AutoShardedBot): 
    self.bot = bot 

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent): 
    if payload.member.bot: return   
    if payload.emoji.is_custom_emoji():       
       check = await self.bot.db.fetchrow("SELECT role_id FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", payload.guild_id, payload.message_id, payload.channel_id, payload.emoji.id) 
       if check:
        roleid = check['role_id']
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(roleid)
        if not role in payload.member.roles: await payload.member.add_roles(role)
    elif payload.emoji.is_unicode_emoji():
      try:
       check = await self.bot.db.fetchrow("SELECT role_id FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", payload.guild_id, payload.message_id, payload.channel_id, ord(str(payload.emoji))) 
       if check:
         roleid = check["role_id"]
         guild = self.bot.get_guild(payload.guild_id)
         role = guild.get_role(roleid)
         if not role in payload.member.roles: await payload.member.add_roles(role)      
      except TypeError: pass 

  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent): 
   mem = self.bot.get_guild(payload.guild_id).get_member(payload.user_id)
   if not mem: return
   if mem.bot: return 
   if payload.emoji.is_custom_emoji(): 
    check = await self.bot.db.fetchrow("SELECT role_id FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", payload.guild_id, payload.message_id, payload.channel_id, payload.emoji.id) 
    if check: 
      roleid = check["role_id"]
      guild = self.bot.get_guild(payload.guild_id)
      member = guild.get_member(payload.user_id)
      role = guild.get_role(int(roleid))
      if role in member.roles: await member.remove_roles(role)
   elif payload.emoji.is_unicode_emoji(): 
    try: 
      check = await self.bot.db.fetchrow("SELECT role_id FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", payload.guild_id, payload.message_id, payload.channel_id, ord(str(payload.emoji)))
      if check: 
       roleid = check["role_id"]
       guild = self.bot.get_guild(payload.guild_id)
       member = guild.get_member(payload.user_id)
       role = guild.get_role(int(roleid))
       if role in member.roles: await member.remove_roles(role)
    except TypeError: pass   
  
  @commands.group(invoke_without_command=True, aliases=['rr'])
  async def reactionrole(self, ctx): 
   await ctx.create_pages()
  
  @reactionrole.command(name="add", description="add a reactionrole to a message", help="config", brief="manage roles", usage="[message id] [channel] [emoji] [role]")
  @Perms.get_perms("manage_roles")
  async def rr_add(self, ctx: commands.Context, messageid: int, channel: discord.TextChannel, emoji: Union[discord.Emoji, str], *, role: Union[discord.Role, str]): 
   try: message = await channel.fetch_message(messageid)
   except discord.NotFound: return await ctx.send_warning("Message not found")
   if isinstance(role, str): 
    role = ctx.find_role(role)
    if role is None: return await ctx.send_warning("Role not found")
   
   check = await self.bot.db.fetchrow("SELECT * FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", ctx.guild.id, message.id, channel.id, emoji.id if isinstance(emoji, discord.Emoji) else ord(str(emoji)))
   if check: return await ctx.send_warning("A reactionrole with the same arguments is already added")

   try: 
    await message.add_reaction(emoji)
    await self.bot.db.execute("INSERT INTO reactionrole VALUES ($1,$2,$3,$4,$5,$6)", ctx.guild.id, message.id, channel.id, role.id, emoji.id if isinstance(emoji, discord.Emoji) else ord(str(emoji)), str(emoji))   
    return await ctx.send_success(f"Added reaction role {emoji} for {role.mention}")
   except: return await ctx.send_error("Unable to add reaction role for this role")

  @reactionrole.command(name="remove", description="remove a reactionrole from a message", help="config", brief="manage roles", usage="[message id] [channel] [emoji]")
  @Perms.get_perms("manage_roles")
  async def rr_remove(self, ctx: commands.Context, messageid: int, channel: discord.TextChannel, emoji: Union[discord.Emoji, str]): 
   check = await self.bot.db.fetchrow("SELECT * FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", ctx.guild.id, messageid, channel.id, emoji.id if isinstance(emoji, discord.Emoji) else ord(str(emoji)))
   if not check: return await ctx.send_warning("Cannot find a reactionrole with the given arguments")
   await self.bot.db.execute("DELETE FROM reactionrole WHERE guild_id = $1 AND message_id = $2 AND channel_id = $3 AND emoji_id = $4", ctx.guild.id, messageid, channel.id, emoji.id if isinstance(emoji, discord.Emoji) else ord(str(emoji))) 
   await ctx.send_success("Reactionrole deleted") 

  @reactionrole.command(name="list", description="list all the reaction roles from the server", help="config") 
  async def rr_list(self, ctx: commands.Context):
   results = await self.bot.db.fetch("SELECT * FROM reactionrole WHERE guild_id = $1", ctx.guild.id)
   if len(results) == 0: return await ctx.send_warning("No **reactionroles** found")
   i=0
   k=1
   l=0
   mes = ""
   number = []
   messages = []
   for result in results:
       mes = f"{mes}`{k}` {result['emoji_text']} - {ctx.guild.get_role(int(result['role_id'])).mention if ctx.guild.get_role(int(result['role_id'])) else result['role_id']} [message link]({(await ctx.guild.get_channel(int(result['channel_id'])).fetch_message(int(result['message_id']))).jump_url or 'https://none.none'})\n"
       k+=1
       l+=1
       if l == 10:
         messages.append(mes)
         number.append(discord.Embed(color=self.bot.color, title=f"reaction roles ({len(results)})", description=messages[i]))
         i+=1
         mes = ""
         l=0

   messages.append(mes)          
   number.append(discord.Embed(color=self.bot.color, title=f"reaction roles ({len(results)})", description=messages[i]))
   await ctx.paginator(number)   

async def setup(bot: commands.AutoShardedBot) -> None: 
  await bot.add_cog(ReactionRoles(bot))      