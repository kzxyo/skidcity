import discord, datetime
from discord.ext import commands
from tools.utils.checks import Perms
from tools.utils.utils import Whitelist

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.Cog.listener('on_message_edit')
    async def invite_edit(self, before, after: discord.Message): 
     if after.content == before.content: return   
     message = after   
     if not message.guild: return 
     if isinstance(message.author, discord.User): return 
     if message.author.bot: return 
     if await Perms.has_perms(await self.bot.get_context(message), "manage_guild"): return 
     invites = ["discord.gg/", ".gg/", "discord.com/invite/"]
     if any(invite in message.content for invite in invites):
        check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = $1", message.guild.id)        
        if check is not None: 
          res1 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "antiinvite", message.channel.id, "channel")
          if res1: return 
          res2 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "antiinvite", message.author.id, "user")             
          if res2: return
          if "discord.gg/" in message.content:
            spl_word = "discord.gg/"
          elif ".gg/" in message.content:  
            spl_word = ".gg/"
          elif "discord.com/invite/" in message.content:
            spl_word = "discord.com/invite/"

          try:
           await message.delete()
           await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=1), reason="AutoMod: Sending invites")
           await message.channel.send(embed=discord.Embed(color=self.bot.color, title="vilan AutoMod", description=f"{self.bot.warning} {message.author.mention}: You have been muted for **1 minute** for sending discord invites links"))
          except KeyError: pass  
    
    @commands.Cog.listener('on_message')
    async def invite_send(self, message: discord.Message):   
     if not message.guild: return 
     if isinstance(message.author, discord.User): return 
     if message.author.bot: return 
     if await Perms.has_perms(await self.bot.get_context(message), "manage_guild"): return 
     invites = ["discord.gg/", ".gg/", "discord.com/invite/"]
     if any(invite in message.content for invite in invites):
        check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = $1", message.guild.id)        
        if check is not None: 
          res1 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "antiinvite", message.channel.id, "channel")
          if res1: return 
          res2 = await self.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", message.guild.id, "antiinvite", message.author.id, "user")             
          if res2: return
          if "discord.gg/" in message.content:
            spl_word = "discord.gg/"
          elif ".gg/" in message.content:  
            spl_word = ".gg/"
          elif "discord.com/invite/" in message.content:
            spl_word = "discord.com/invite/"

          try:
           await message.delete()
           await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=5), reason="AudoMod: Sending invites")
           await message.channel.send(embed=discord.Embed(color=self.bot.color, title="vilan AutoMod", description=f"{self.bot.warning} {message.author.mention}: You have been muted for **5 minutes** for sending discord invites links"))
          except KeyError: pass  
    
    @commands.group(name="anti-invite", invoke_without_command=True, aliases=["antilink", "anti-link"])
    async def anti_invite(self, ctx: commands.Context): 
     await ctx.create_pages()

    @anti_invite.command(name="enable", description="enable anti invite", aliases=["e"], help="automod", brief="manage guild") 
    @Perms.get_perms("manage_guild")
    async def antiinvite_enable(self, ctx: commands.Context):      
        check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = {}".format(ctx.guild.id))        
        if check: return await ctx.send_error("Anti-invite is **already** enabled")
        await self.bot.db.execute("INSERT INTO antiinvite VALUES ($1)", ctx.guild.id)
        return await ctx.send_success("Enabled anti-invite")
    
    @anti_invite.command(name="disable", description="disable anti invite", aliases=["d"], help="automod") 
    @Perms.get_perms("manage_guild")
    async def antiinvite_disable(self, ctx: commands.Context): 
        check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = {}".format(ctx.guild.id))        
        if not check: return await ctx.send_error("Anti-invite is **not** enabled")
        await self.bot.db.execute("DELETE FROM antiinvite WHERE guild_id = $1", ctx.guild.id)
        return await ctx.send_success("Disabled anti-invite")
    
    @anti_invite.group(name="whitelist", description="manage whitelist for anti invite", help="automod", aliases=["wl"])
    async def antiinvite_whitelist(self, ctx: commands.Context): 
      await ctx.create_pages()

    @antiinvite_whitelist.command(brief="manage guild", description="whitelist a channel from anti invite", help="automod", name="channel")
    @Perms.get_perms("manage_guild")  
    async def antiinvite_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
     await Whitelist.whitelist_things(ctx, "antiinvite", channel)    

    @antiinvite_whitelist.command(brief="manage guild", description="whitelist an user from antiinvite", help="automod", name="user")
    @Perms.get_perms("manage_guild")  
    async def antiinvite_user(self, ctx: commands.Context, *, member: discord.Member): 
      await Whitelist.whitelist_things(ctx, "antiinvite", member)
    
    @anti_invite.group(name="unwhitelist", description="remove channels or users from antilink whitelist", help="automod", aliases=["uwl"])
    async def antiinvite_unwhitelist(self, ctx): 
      await ctx.create_pages()
    
    @antiinvite_unwhitelist.command(help="automod", name="channel", description="unwhitelist a channel from antiinvite", brief="manage guild")
    @Perms.get_perms("manage_guild")
    async def unwhitelist_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
     await Whitelist.unwhitelist_things(ctx, "antiinvite", channel)
    
    @antiinvite_unwhitelist.command(help="automod", name="user", description="unwhitelist an user from antiinvite", brief="manage guild")
    @Perms.get_perms("manage_guild")
    async def unwhitelist_user(self, ctx: commands.Context, *, channel: discord.Member):
     await Whitelist.unwhitelist_things(ctx, "antiinvite", channel)     
    
    @anti_invite.group(name="whitelisted", description="returns a list of whitelisted channels or users", help="automod")
    async def antiinvite_whitelisted(self, ctx: commands.Context): 
      await ctx.create_pages()

    @antiinvite_whitelisted.command(name="channels", help="automod", description="return a list of whitelisted channels")
    async def whitelisted_channels(self, ctx: commands.Context): 
     await Whitelist.whitelisted_things(ctx, "antiinvite", "channel") 

    @antiinvite_whitelisted.command(name="users", description="return a list of whitelisted users", help="automod")
    async def whitelisted_users(self, ctx: commands.Context): 
      await Whitelist.whitelisted_things(ctx, "antiinvite", "user")
    
async def setup(bot):
    await bot.add_cog(AutoMod(bot))