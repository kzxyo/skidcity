import discord, os
from discord.ext import commands
from discord.ext.commands import Paginator

from tools.bot import DiscordBot
from tools.context import HarmContext

class Owner(commands.Cog):
    def __init__(self, bot: DiscordBot):
      self.bot = bot 
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if await self.bot.db.fetchrow("SELECT * FROM blacklisted WHERE user_id = $1", guild.id):
          return await guild.leave()
        
        if guild.member_count < 5:
            if guild.me.guild_permissions.view_audit_log:
                async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                    if entry.target.user.id == self.bot.user.id: 
                        embed = discord.Embed(
                          color=0xff0000,
                          description=f"I left **{guild.name}** because it has less than **5** members"
                        )
    
                        try: 
                           await entry.user.send(embed=embed)
                        except: 
                           pass 

            await guild.leave()            

    @commands.command(
        name="leave", 
        hidden=True
    )
    async def leave_guild(
       self, 
       ctx: HarmContext,
       *, guild: discord.Guild
    ):
       await guild.leave()
       await ctx.send(f"left {guild.name}")

    @commands.group(invoke_without_command=True)
    async def blacklist(self, ctx):
       return await ctx.send_help(ctx.command)

    @blacklist.command(
        name="user",
        hidden=True 
    )
    @commands.is_owner()
    async def blacklist_user(
       self,
       ctx: HarmContext,
       *, user: discord.User
    ):
        """blacklist an user from using the bot"""
        if await self.bot.db.fetchrow("SELECT * FROM blacklisted WHERE user_id = $1", user.id):
          await self.bot.db.execute("DELETE FROM blacklisted WHERE user_id = $1", user.id)
          return await ctx.success(f"User is now unblacklisted from {self.bot.user}")
        
        await self.bot.db.execute("INSERT INTO blacklisted VALUES ($1)", user.id)
        return await ctx.success(f"Blacklisted {user.mention} from {self.bot.user}")
    
    @blacklist.command(
       name="server", 
       aliases=['guild'],
       hidden=True
    )
    @commands.is_owner()
    async def blacklist_server(
       self,
       ctx: HarmContext, 
       id: int
    ):
        """blacklist a server from using the bot"""
        if await self.bot.db.fetchrow("SELECT * FROM blacklisted WHERE user_id = $1", id):
          await self.bot.db.execute("DELETE FROM blacklisted WHERE user_id = $1", id)
          return await ctx.success(f"Server is now unblacklisted from {self.bot.user}")
        
        await self.bot.db.execute("INSERT INTO blacklisted VALUES ($1)", id)

        if guild := self.bot.get_guild(id):
           guild_name = guild.name 
           await guild.leave()
        else: 
           guild_name = "server"   

        return await ctx.success(f"Blacklisted {guild_name} from {self.bot.user}")

    @commands.command()
    @commands.is_owner()
    async def custom(self, ctx):
       await self.bot.change_presence(activity=discord.CustomActivity(name="discord.gg/abkkQJyUDQ", state="discord.gg/abkkQJyUDQ"))

    @commands.command(aliases=['setbotpfp', 'setavatar'])
    @commands.is_owner()
    async def setbotav(self, ctx):
        if len(ctx.message.attachments) == 0:
            await ctx.msg("Please upload an image file.")
            return

        attachment = ctx.message.attachments[0]

        if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            await ctx.send("Please upload a valid image file (PNG, JPG, JPEG, GIF).")
            return

        try:
            
            attachment_filename = attachment.filename
            await attachment.save(attachment_filename)

            with open(attachment_filename, 'rb') as file:
                avatar_bytes = file.read()

            
            await self.bot.user.edit(avatar=avatar_bytes)

            
            os.remove(attachment_filename)

            await ctx.send("Bot avatar changed.")
        except Exception as e:
            await ctx.send(f"An error occurred while setting the bot avatar: {e}")

    @commands.command()
    @commands.is_owner()
    async def repeat(self, ctx, times: int, *, message: str):
        if times <= 0:
            await ctx.send("no")
            return

        for _ in range(times):
            await ctx.send(message)

    @commands.command()
    @commands.is_owner()
    async def me(self, ctx):
        member = ctx.author
        limit = 100

        async for message in ctx.channel.history(limit=limit):
            if message.author == member:
                await message.delete()

    @commands.command(name='sids')
    @commands.is_owner()
    async def sids(self, ctx):
      paginator = Paginator()

      for guild in self.bot.guilds:
          member_count = len(guild.members)
          paginator.add_line(f"{guild.name} - {guild.id} - {member_count}")

      for page in paginator.pages:
          await ctx.send(page)

async def setup(bot: DiscordBot) -> None:
   return await bot.add_cog(Owner(bot))      