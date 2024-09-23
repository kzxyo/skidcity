import discord
from discord.ext import commands 
from patches.permissions import Permissions, Whitelist

async def decrypt_message(content: str) -> str: 
  return content.lower().replace("1", "i").replace("4", "a").replace("3", "e").replace("0", "o").replace("@", "a") 

class automod(commands.Cog): 
    def __init__(self, bot: commands.Bot): 
      self.bot = bot 
      self.antispam_cache = {}
    
    @commands.group(aliases=["cf"], invoke_without_command=True)
    async def chatfilter(self, ctx): 
      await ctx.create_pages()

    @chatfilter.command(name="add", description="add a word to the chatfilter", brief="manage guild", usage="[word]")
    @Permissions.has_permission(manage_guild=True) 
    async def cf_add(self, ctx: commands.Context, *, word: str): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM chatfilter WHERE guild_id = $1 AND word = $2", ctx.guild.id, word.lower())
     if check: return await ctx.warning("This word is **already** added in the chatfilter list") 
     
     await self.bot.db.execute("INSERT INTO chatfilter VALUES ($1,$2)", ctx.message.guild.id, word.lower())
     await ctx.success(f"Added **{word}** as a filtered word")
    
    @chatfilter.command(name="remove", aliases=["delete"], description="remove a word from the chatfilter", brief="manage guild", usage="[word]")
    @Permissions.has_permission(manage_guild=True) 
    async def cf_remove(self, ctx: commands.Context, *, word: str): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM chatfilter WHERE guild_id = $1 AND word = $2", ctx.guild.id, word.lower())
     if not check: return await ctx.warning("This word is **not** added in the chatfilter list") 
     
     await self.bot.db.execute("DELETE FROM chatfilter WHERE guild_id = $1 AND word = $2", ctx.message.guild.id, word.lower())
     await ctx.success(f"removed **{word}** from the filtered word") 
     
    @chatfilter.command(name="list", description="returns a list of blacklisted words", brief="manage guild")
    async def cf_list(self, ctx: commands.Context):
      
      results = await self.bot.db.fetch("SELECT * FROM chatfilter WHERE guild_id = $1", ctx.guild.id)
      
      if len(results) == 0: return await ctx.warning("no **blacklisted** words found")
        
      cf_list = [
        f"``{index + 1}.`` {result['word']}" 
        for index, result in enumerate(results)]
            
      await ctx.paginate(cf_list, f"blacklisted words [{len(results)}]")  
    
    @chatfilter.group(name="whitelist", description="manage whitelist for chatfilter", aliases=["wl"], brief="manage guild")
    async def cf_whitelist(self, ctx: commands.Context): 
      await ctx.create_pages()

    @cf_whitelist.command(brief="manage guild", description="whitelist a channel from chatfilter", name="channel")
    @Permissions.has_permission(manage_guild=True) 
    async def cf_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
     await Whitelist.whitelist_things(ctx, "chatfilter", channel)    

    @cf_whitelist.command(brief="manage guild", description="whitelist an user from chatfilter", name="user")
    @Permissions.has_permission(manage_guild=True) 
    async def cf_user(self, ctx: commands.Context, *, member: discord.Member): 
      await Whitelist.whitelist_things(ctx, "chatfilter", member)
    
    @chatfilter.group(name="unwhitelist", description="remove channels or users from chatfilter whitelist", aliases=["uwl"], brief="manage guild")
    async def cf_unwhitelist(self, ctx): 
      await ctx.create_pages()
    
    @cf_unwhitelist.command(name="channel", description="unwhitelist a channel from chatfilter", brief="manage guild")
    @Permissions.has_permission(manage_guild=True) 
    async def cf_unwhitelist_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
     await Whitelist.unwhitelist_things(ctx, "chatfilter", channel)
    
    @cf_unwhitelist.command(name="user", description="unwhitelist an user from chatfilter", brief="manage guild")
    @Permissions.has_permission(manage_guild=True) 
    async def cf_unwhitelist_user(self, ctx: commands.Context, *, member: discord.Member):
     await Whitelist.unwhitelist_things(ctx, "chatfilter", member)     
    
    @chatfilter.group(name="whitelisted", description="returns a list of whitelisted channels or users", brief="manage guild")
    async def cf_whitelisted(self, ctx: commands.Context): 
      await ctx.create_pages()

    @cf_whitelisted.command(name="channels", description="return a list of whitelisted channels", brief="manage guild")
    async def cf_whitelisted_channels(self, ctx: commands.Context): 
     await Whitelist.whitelisted_things(ctx, "chatfilter", "channel") 

    @cf_whitelisted.command(name="users", description="return a list of whitelisted users", brief="manage guild")
    async def whitelisted_users(self, ctx: commands.Context): 
      await Whitelist.whitelisted_things(ctx, "chatfilter", "user")
    
    @commands.group(name="antispam", invoke_without_command=True, brief="manage guild")
    async def anti_spam(self, ctx): 
      return await ctx.create_pages() 

    @anti_spam.command(name="enable", description="enable anti spam", aliases=['e'], brief="manage guild")
    @Permissions.has_permission(manage_guild=True) 
    async def anti_spam_enable(self, ctx: commands.Context):       
        
        check = await self.bot.db.fetchrow("SELECT * FROM antispam WHERE guild_id = {}".format(ctx.guild.id))        
        if check: return await ctx.error("Anti-spam is **already** enabled")
        
        await self.bot.db.execute("INSERT INTO antispam VALUES ($1,$2,$3,$4)", ctx.guild.id, 5, 5, "mute")
        return await ctx.success("Anti-spam is now enabled")
    
    @anti_spam.command(name="disable", description="disable anti spam", brief="manage guild")
    @Permissions.has_permission(manage_guild=True) 
    async def anti_spam_disable(self, ctx: commands.Context):
      
      check = await self.bot.db.fetchrow("SELECT * FROM antispam WHERE guild_id = {}".format(ctx.guild.id))        
      if not check: return await ctx.error("Anti-spam is **not** enabled")
      
      await self.bot.db.execute("DELETE FROM antispam WHERE guild_id = $1", ctx.guild.id)
      return await ctx.success("Anti-spam is now disabled") 
    
    @anti_spam.command(name="punishment", description="set antispam punishment", brief="manage guild", usage="[punishment]")
    @Permissions.has_permission(manage_guild=True) 
    async def anti_spam_punishment(self, ctx: commands.Context, punishment: str): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM antispam WHERE guild_id = {}".format(ctx.guild.id))        
     
     if not check: return await ctx.error("Anti-spam is **not** enabled") 
     if not punishment in ["delete", "mute"]: return await ctx.warning(f"Punishment can be only **ban** or **mute**, not **{punishment}**") 
     
     await self.bot.db.execute("UPDATE antispam SET punishment = $1 WHERE guild_id = $2", punishment, ctx.guild.id)
     return await ctx.success(f"Anti-spam punishment set to **{punishment}**") 
    
    @anti_spam.command(name="seconds", description="set antispam's delay time", brief="manage guild", usage="[seconds]")
    @Permissions.has_permission(manage_guild=True) 
    async def anti_spam_seconds(self, ctx: commands.Context, second: int): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM antispam WHERE guild_id = {}".format(ctx.guild.id))        
     if not check: return await ctx.error("Anti-spam is **not** enabled") 
     
     if second < 1: return await ctx.warning(f"Anti-spam delay can't be lower than 1 second") 
     
     await self.bot.db.execute("UPDATE antispam SET seconds = $1 WHERE guild_id = $2", second, ctx.guild.id)
     return await ctx.success(f"Anti-spam delay set to **{second}**")  
    
    @anti_spam.command(name="limit", description="set antispam's limit", brief="manage guild", usage="[limit]")
    @Permissions.has_permission(manage_guild=True) 
    async def anti_spam_limit(self, ctx: commands.Context, second: int): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM antispam WHERE guild_id = {}".format(ctx.guild.id))        
     if not check: return await ctx.error("Anti-spam is **not** enabled") 
     
     if second < 1: return await ctx.warning(f"anti-spam limit can't be lower than 1 second") 
     
     await self.bot.db.execute("UPDATE antispam SET count = $1 WHERE guild_id = $2", second, ctx.guild.id)
     return await ctx.success(f"Anti-spam limit set to **{second}**")  
    
    @anti_spam.group(name="whitelist", description="manage whitelist for anti spam", aliases=["wl"], brief="manage guild")
    async def antispam_whitelist(self, ctx: commands.Context): 
      await ctx.create_pages()

    @antispam_whitelist.command(brief="manage guild", description="whitelist a channel from anti spam", name="channel")
    @Permissions.has_permission(manage_guild=True)   
    async def antispam_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
     await Whitelist.whitelist_things(ctx, "antispam", channel)    

    @antispam_whitelist.command(brief="manage guild", description="whitelist an user from anti spam", name="user")
    @Permissions.has_permission(manage_guild=True)   
    async def antispam_user(self, ctx: commands.Context, *, member: discord.Member): 
      await Whitelist.whitelist_things(ctx, "antispam", member)
    
    @anti_spam.group(name="unwhitelist", description="remove channels or users from antispam whitelist", aliases=["uwl"], brief="manage guild")
    async def antispam_unwhitelist(self, ctx): 
      await ctx.create_pages()
    
    @antispam_unwhitelist.command( name="channel", description="unwhitelist a channel from anti spam", brief="manage guild")
    @Permissions.has_permission(manage_guild=True) 
    async def as_unwhitelist_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
     await Whitelist.unwhitelist_things(ctx, "antispam", channel)
    
    @antispam_unwhitelist.command( name="user", description="unwhitelist an user from anti spam", brief="manage guild")
    @Permissions.has_permission(manage_guild=True) 
    async def as_unwhitelist_user(self, ctx: commands.Context, *, channel: discord.Member):
     await Whitelist.unwhitelist_things(ctx, "antispam", channel)     
    
    @anti_spam.group(name="whitelisted", description="returns a list of whitelisted channels or users")
    async def antispam_whitelisted(self, ctx: commands.Context): 
      await ctx.create_pages()

    @antispam_whitelisted.command(name="channels", description="return a list of whitelisted channels", brief="manage guild")
    async def as_whitelisted_channels(self, ctx: commands.Context): 
     await Whitelist.whitelisted_things(ctx, "antispam", "channel") 

    @antispam_whitelisted.command(name="users", description="return a list of whitelisted users", brief="manage guild")
    async def as_whitelisted_users(self, ctx: commands.Context): 
      await Whitelist.whitelisted_things(ctx, "antispam", "user")

    @commands.group(name="anti-invite", invoke_without_command=True, aliases=["antilink", "anti-link"], brief="manage guild")
    async def anti_invite(self, ctx: commands.Context): 
     await ctx.create_pages()

    @anti_invite.command(name="enable", description="enable anti invite", aliases=["e"], brief="manage guild") 
    @Permissions.has_permission(manage_guild=True) 
    async def antiinvite_enable(self, ctx: commands.Context):      
        
        check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = {}".format(ctx.guild.id))        
        if check: return await ctx.error("Anti-invite is **already** enabled")
        
        await self.bot.db.execute("INSERT INTO antiinvite VALUES ($1)", ctx.guild.id)
        return await ctx.success("Anti-invite is now enabled")
    
    @anti_invite.command(name="disable", description="disable anti invite", aliases=["d"]) 
    @Permissions.has_permission(manage_guild=True) 
    async def antiinvite_disable(self, ctx: commands.Context): 
        
        check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = {}".format(ctx.guild.id))        
        if not check: return await ctx.error("Anti-invite is **not** enabled")
        
        await self.bot.db.execute("DELETE FROM antiinvite WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success("Anti-invite is now disabled")
    
    @anti_invite.group(name="whitelist", description="manage whitelist for anti invite", aliases=["wl"], brief="manage guild")
    async def antiinvite_whitelist(self, ctx: commands.Context): 
      await ctx.create_pages()

    @antiinvite_whitelist.command(brief="manage guild", description="whitelist a channel from anti invite", name="channel")
    @Permissions.has_permission(manage_guild=True)   
    async def antiinvite_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
     await Whitelist.whitelist_things(ctx, "antiinvite", channel)    

    @antiinvite_whitelist.command(brief="manage guild", description="whitelist an user from antiinvite", name="user")
    @Permissions.has_permission(manage_guild=True)   
    async def antiinvite_user(self, ctx: commands.Context, *, member: discord.Member): 
      await Whitelist.whitelist_things(ctx, "antiinvite", member)
    
    @anti_invite.group(name="unwhitelist", description="remove channels or users from antilink whitelist", aliases=["uwl"], brief="manage guild")
    async def antiinvite_unwhitelist(self, ctx): 
      await ctx.create_pages()
    
    @antiinvite_unwhitelist.command(name="channel", description="unwhitelist a channel from antiinvite", brief="manage guild")
    @Permissions.has_permission(manage_guild=True) 
    async def unwhitelist_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
     await Whitelist.unwhitelist_things(ctx, "antiinvite", channel)
    
    @antiinvite_unwhitelist.command(name="user", description="unwhitelist an user from antiinvite", brief="manage guild")
    @Permissions.has_permission(manage_guild=True) 
    async def unwhitelist_user(self, ctx: commands.Context, *, channel: discord.Member):
     await Whitelist.unwhitelist_things(ctx, "antiinvite", channel)     
    
    @anti_invite.group(name="whitelisted", description="returns a list of whitelisted channels or users", brief="manage guild")
    async def antiinvite_whitelisted(self, ctx: commands.Context): 
      await ctx.create_pages()

    @antiinvite_whitelisted.command(name="channels", description="return a list of whitelisted channels", brief="manage guild")
    async def whitelisted_channels(self, ctx: commands.Context): 
     await Whitelist.whitelisted_things(ctx, "antiinvite", "channel") 

    @antiinvite_whitelisted.command(name="users", description="return a list of whitelisted users", brief="manage guild")
    async def whitelisted_users(self, ctx: commands.Context): 
      await Whitelist.whitelisted_things(ctx, "antiinvite", "user")

async def setup(bot): 
    await bot.add_cog(automod(bot))        