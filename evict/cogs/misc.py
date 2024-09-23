import discord, random, string, asyncio, aiohttp
from discord.ext import commands 
from patches.permissions import Permissions
from patches.classes import Mod
from utils.utils import EmbedScript
from bot.helpers import EvictContext
from patches.classes import ValidWebhookCode
from bot.headers import Session

def is_detention(): 
 async def predicate(ctx: commands.Context): 
  
  check = await ctx.bot.db.fetchrow("SELECT * FROM naughtycorner WHERE guild_id = $1", ctx.guild.id)
  if not check: await ctx.warning("Naughty corner is not configured")
  
  return check is not None 
 return commands.check(predicate)
 
class misc(commands.Cog):
  def __init__(self, bot: commands.Bot): 
    self.bot = bot   
    self.headers = {
      "Content-Type": "application/json"
    }  
  
  async def webhook_channel(self, url) -> discord.TextChannel | None: 
   
   r = await self.bot.session.get(url)
   
   data = (await r.json())['channel_id'] 
   return self.bot.get_channel(int(data))

  @commands.Cog.listener()
  async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState): 
   
   naughty = await self.bot.db.fetchrow("SELECT * FROM naughtycorner_members WHERE guild_id = $1 AND user_id = $2", member.guild.id, member.id)
   
   if naughty: 
     check = await self.bot.db.fetchrow("SELECT * FROM naughtycorner WHERE guild_id = $1", member.guild.id)
     
     if check:
      channel = member.guild.get_channel(int(check['channel_id']))      
      
      if after.channel.id != channel.id: await member.move_to(channel=channel, reason=f"moved to the naughty corner")

  @commands.group(aliases=['detention', 'nc'], invoke_without_command=True)
  async def naughtycorner(self, ctx: commands.Context): 
    await ctx.create_pages()
    
  @naughtycorner.command( aliases=['configure', 'set'], brief="manage server", usage="[voice channel]", name="setup", description="configure naughty corner voice channel")
  @Permissions.has_permission(manage_guild=True)
  async def nc_setup(self, ctx: commands.Context, *, channel: discord.VoiceChannel): 
   
   check = await self.bot.db.fetchrow("SELECT * FROM naughtycorner WHERE guild_id = $1", ctx.guild.id)
   if check: await self.bot.db.execute("UPDATE naughtycorner SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id) 
   
   else: await self.bot.db.execute("INSERT INTO naughtycorner VALUES ($1,$2)", ctx.guild.id, channel.id)
   return await ctx.success(f"Naughty corner voice channel configured -> {channel.mention}")

  @naughtycorner.command( name="unsetup", brief="manage server", description="disable naughty corner feature in the server") 
  @Permissions.has_permission(manage_guild=True)
  @is_detention()
  async def nc_unsetup(self, ctx: commands.Context): 
   
   await self.bot.db.execute('DELETE FROM naughtycorner WHERE guild_id = $1', ctx.guild.id)
   return await ctx.success("Naughty corner is now disabled")
  
  @naughtycorner.command( name="add", brief="timeout members", description="add a member to the naughty corner", usage="[member]")
  @Permissions.has_permission(moderate_members=True)
  @is_detention()
  async def nc_add(self, ctx: commands.Context, *, member: discord.Member): 
   
   if await Mod.check_hieracy(ctx, member): 
    
    check = await self.bot.db.fetchrow("SELECT * FROM naughtycorner_members WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member.id)
    if check: return await ctx.warning("This member is **already** in the naughty corner")
    
    await self.bot.db.execute("INSERT INTO naughtycorner_members VALUES ($1,$2)", ctx.guild.id, member.id)
    
    res = await self.bot.db.fetchrow("SELECT channel_id FROM naughtycorner WHERE guild_id = $1", ctx.guild.id)
    channel = ctx.guild.get_channel(int(res['channel_id']))
    
    await member.move_to(channel=channel, reason=f"Moved to the naughty corner by {ctx.author}")
    return await ctx.success(f"Moved **{member}** to {channel.mention if channel else '**Naughty Corner**'}") 
  
  @naughtycorner.command( name="remove", brief="timeout emmbers", description="remove a member from the naughty corner", usage="[member]")
  @Permissions.has_permission(manage_guild=True)
  @is_detention()
  async def nc_remove(self, ctx: commands.Context, *, member: discord.Member): 
   
   if await Mod.check_hieracy(ctx, member): 
    check = await self.bot.db.fetchrow("SELECT * FROM naughtycorner_members WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member.id)
    
    if not check: return await ctx.warning("this member is **not** in the naughty corner")
    
    await self.bot.db.execute("DELETE FROM naughtycorner_members WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member.id)
    return await ctx.success(f"removed **{member}** from **naughty corner**") 
   
  @naughtycorner.command(name="members", aliases=['list'], description="returns members from the naughty corner")      
  @is_detention()
  async def nc_list(self, ctx: commands.Context):
      
      results = await self.bot.db.fetch("SELECT user_id FROM naughtycorner_members WHERE guild_id = $1", ctx.guild.id)
      if len(results) == 0: return await ctx.warning("no **whitelisted** members found")
      
      nc_list = [f"<@!{r['user_id']}>" for r in results]
      await ctx.paginate(nc_list, f"members in naughty corner [{len(results)}]")  

  @commands.group(name="webhook", invoke_without_command=True)
  async def webhook(self, ctx):
    await ctx.create_pages()

  @webhook.group(name="edit", invoke_without_command=True, description="edit a webhook")
  async def webhook_edit(self, ctx): 
    return await ctx.create_pages()

  @webhook_edit.command(name="name", description="edit a webhook's name",  usage="[code] [name]", brief="manage server") 
  @Permissions.has_permission(manage_guild=True)
  async def webhook_name(self, ctx: commands.Context, code: str, *, name: str): 
   
   check = await self.bot.db.fetchrow("SELECT * FROM webhook WHERE code = $1 AND guild_id = $2", code, ctx.guild.id)
   if not check: return ctx.error("No **webhook** associated with this code")
   
   webhook = discord.Webhook.from_url(check['url'], session=self.bot.session)
   
   if webhook: 
    
    await webhook.edit(name=name, reason=f"webhook edited by {ctx.author}") 
    return await ctx.success(f"Webhook name changed in **{name}**")
  
   else: return ctx.error(f"No **webhook** found")

  @webhook_edit.command(name="avatar", aliases=["icon"],  description="edit a webhook's avatar", usage="[code] [image url / attachment]", brief="manage server")
  @Permissions.has_permission(manage_guild=True)
  async def webhook_avatar(self, ctx: commands.Context, code: str, link: str=None): 
   
   check = await self.bot.db.fetchrow("SELECT * FROM webhook WHERE code = $1 AND guild_id = $2", code, ctx.guild.id)
   if not check: return ctx.error("There is no **webhook** associated with this code.")
   
   webhook = discord.Webhook.from_url(check['url'], session=self.bot.session)
   
   if webhook: 
    
    if link is None and len(ctx.message.attachments) == 0: return await self.bot.help_command.send_command_help(ctx.command)
    if link: link = link 
    
    elif not link and ctx.message.attachments: link = ctx.message.attachments[0].url
    
    avatar = await Session.get_bytes(self, url=link)
    await webhook.edit(avatar=avatar, reason=f"webhook avatar changed by {ctx.author}")
    
    return await ctx.success(f"webhook avatar changed")
   else: return ctx.error(f"no **webhook** found")   

  @webhook.command(name="create", aliases=['add'],  description="create a webhook in a channel", usage="[channel] <name>", brief="manage server")
  @Permissions.has_permission(manage_guild=True)
  async def webhook_create(self, ctx: commands.Context, channel: discord.TextChannel, *, name: str="evict"): 
   
   webhook = await channel.create_webhook(name=name, reason=f"webhook created by {ctx.author}") 
   code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) 
   
   await self.bot.db.execute("INSERT INTO webhook VALUES ($1,$2,$3,$4)", ctx.guild.id, channel.id, code, webhook.url)
   return await ctx.success(f"webhook created in {channel.mention} with the code `{code}`")
  
  @webhook.command(name="delete", aliases=['remove'], brief="manage server", description="delete a webhook from a channel", usage="[code]")
  @Permissions.has_permission(manage_guild=True)
  async def webhook_delete(self, ctx: commands.Context, code: str): 
   
   check = await self.bot.db.fetchrow("SELECT * FROM webhook WHERE code = $1 AND guild_id = $2", code, ctx.guild.id)
   if not check: return ctx.error("No **webhook** associated with this code")   
   
   webhook = discord.Webhook.from_url(check['url'], session=self.bot.session)
   
   if webhook: 
    
    try: await webhook.delete(reason=f"webhook deleted by {ctx.author}")
    except: pass  
   
   await self.bot.db.execute("DELETE FROM webhook WHERE code = $1 AND guild_id = $2", code, ctx.guild.id)
   await ctx.success(f"deleted the webhook ``{code}``.")
  
  @webhook.command(name="send", aliases=["post"], description="send a message via a webhook using a code", brief="manage server")
  @Permissions.has_permission(manage_guild=True)
  async def webhook_send(self, ctx: EvictContext, code: ValidWebhookCode, *, script: EmbedScript=None):
   check = await self.bot.db.fetchrow("SELECT * FROM webhook WHERE guild_id = $1 AND code = $2", ctx.guild.id, code)
   if script is None: 
      if ctx.message.attachments: 
        script = await self.embed_json(ctx.author, ctx.message.attachments[0])  
      else: 
        return await ctx.send_help(ctx.command) 

   async with aiohttp.ClientSession(headers=self.headers) as session: 
      webhook = discord.Webhook.from_url(url=check['url'], session=session)
      
      if not webhook: 
        return await ctx.error("no webhook found with this code")
      
      w = await self.bot.fetch_webhook(webhook.id)
      await w.send(**script)
      await ctx.success(f"sent webhook -> {w.channel.mention}")
   
  @webhook.command(name="list", brief="manage guild", description="shows a list of available webhooks in the server", aliases=['view']) 
  @Permissions.has_permission(manage_guild=True) 
  async def webhook_list(self, ctx: commands.Context): 
      
      results = await self.bot.db.fetch("SELECT * FROM webhook WHERE guild_id = $1", ctx.guild.id)
      
      if len(results) == 0: return await ctx.warning("there are no **webhooks** created by the bot in this server")
        
      webhook_list = [f"<#{results['channel_id']}> - `{results['code']}`"]
            
      await ctx.paginate(webhook_list, f"webhooks in server [{len(results)}]")  

  @commands.command(description='make a channel nsfw for 30 seconds', brief='manage channels', usage='[chan]')
  @commands.has_permissions(manage_channels=True)
  async def naughty(self, ctx):
        
        channel: discord.TextChannel = ctx.channel
        
        if channel.is_nsfw():
            return await ctx.warning("The channel is already marked as NSFW.")
        
        try:
            
            await channel.edit(nsfw=True, reason=f'requested by {ctx.author}')
            await ctx.success(f"The channel {channel.mention} has been marked as NSFW for 30 seconds.")
            
            await asyncio.sleep(30)
            
            await channel.edit(nsfw=False, reason=f'requested by {ctx.author}')
            await ctx.success(f"The channel {channel.mention} is no longer marked as NSFW.")
        
        except discord.Forbidden:
            await ctx.warning("I don't have the required permissions to manage channels.")
            
  @commands.command(description='pin a message by replying to it', brief='manage messages', usage='[message id]')
  @Permissions.has_permission(manage_messages=True)
  async def pin(self, ctx: commands.Context, message_id: int = None):
        
        if ctx.message.reference:
            message_id = ctx.message.reference.message_id
        
        if not message_id:
            await ctx.warning("You need to provide a **message ID** or **reply** to the message")
            return

        message = await ctx.channel.fetch_message(message_id)
        
        await message.pin()
        await ctx.success(f"pinned message.")
        
  @commands.command(description='unpin a message by replying to it', brief='manage messages', usage='[message id]')
  @Permissions.has_permission(manage_messages=True)
  async def unpin(self, ctx: commands.Context, message_id: int = None):
        
        if ctx.message.reference:
            message_id = ctx.message.reference.message_id
        
        if not message_id:
            await ctx.warning("You need to provide a **message ID** or **reply** to the message")
            return

        message = await ctx.channel.fetch_message(message_id)
        
        await message.unpin()
        await ctx.success(f"unpinned message.")

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(misc(bot))       