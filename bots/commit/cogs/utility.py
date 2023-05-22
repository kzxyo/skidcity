import discord, aiohttp
from discord.ext import commands 
from discord.ext.commands import has_permissions 
from io import BytesIO
from cogs.events import commandhelp
from typing import Union

check = "<:x_approve:1030181005656596551>"
wrong = "<:x_denied:1030181108916174848>"
Warning = "<:check_warning:1030180956985892895>"

class utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True) 
    async def guildedit(self, ctx):
       embed = discord.Embed(color=0x2f3136, title="guildedit", description="edit a part of the guild")
       embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       embed.add_field(name="category", value="config")
       embed.add_field(name="commands", value="guildedit icon - edits server's icon\nguildedit splash - edits server's invite background link\nguildedit banner - edits server's banner\nguildedit name - edits server's name\nguildedit description - edits server's description", inline=False)
       embed.add_field(name="usage", value=f"```guildedit [guild part] [string]```", inline=False)
       embed.add_field(name="aliases", value="none")
       await ctx.reply(embed=embed, mention_author=False) 

    @guildedit.command(help="edit server's icon", description="config", usage="[icon url / attachment]")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def icon(self, ctx: commands.Context, icon=None):
        if not ctx.author.guild_permissions.manage_guild:
         await ctx.reply("you need `manage_guild` permission to use this command")
         return 
        if icon == None:
           if not ctx.message.attachments: 
            await commandhelp(self, ctx, "guildedit" + " " + ctx.command.name)
           else:
            icon = ctx.message.attachments[0].url  
        
        link = icon
        async with aiohttp.ClientSession() as ses: 
          async with ses.get(link) as r:
           try:
            if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await ctx.guild.edit(icon=bytes)
                emb = discord.Embed(color=0x2f3136, description=f"{ctx.author.mention} changed server's icon to")
                emb.set_image(url=link)
                await ctx.reply(embed=emb, mention_author=False)
                return
           except Exception as e:
            e = discord.Embed(color=0xff0000, description=f"{wrong} {ctx.author.mention} unable to change server's icon {e}")
            await ctx.reply(embed=e, mention_author=False)
            return   

    @guildedit.command(help="edit server's banner", description="config", usage="[banner url / attachment]")
    @commands.cooldown(1, 4, commands.BucketType.user) 
    async def banner(self, ctx: commands.Context, icon=None):
        if not ctx.author.guild_permissions.manage_guild:
         await ctx.reply("you need `manage_guild` permission to use this command")
         return 
        if ctx.guild.premium_subscription_count <  7:
            e = discord.Embed(color=0xffff00, description=f"{wrong} {ctx.author.mention} this server hasn't banners feature unlocked")
            await ctx.reply(embed=e, mention_author=False)
            return  
        if icon == None:
           if not ctx.message.attachments: 
            await commandhelp(self, ctx, "guildedit" + " " + ctx.command.name)
           else:
            icon = ctx.message.attachments[0].url
        
        link = icon
        async with aiohttp.ClientSession() as ses: 
          async with ses.get(link) as r:
           try:
            if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await ctx.guild.edit(banner=bytes)
                emb = discord.Embed(color=0x2f3136, description=f"{check} {ctx.author.mention} changed server's banner to")
                emb.set_image(url=link)
                await ctx.reply(embed=emb, mention_author=False)
                return
           except Exception as e:
            e = discord.Embed(color=0xff0000, description=f"{wrong} {ctx.author.mention} unable to change server's banner {e}")
            await ctx.reply(embed=e, mention_author=False)
            return   

    @guildedit.command(help="edit server's splash", description="config", usage="[splash url / attachment]")
    @commands.cooldown(1, 4, commands.BucketType.user) 
    async def splash(self, ctx: commands.Context, icon=None):
        if not ctx.author.guild_permissions.manage_guild:
         await ctx.reply("you need `manage_guild` permission to use this command")
         return 
        if ctx.guild.premium_subscription_count <  2:
            e = discord.Embed(color=0xffff00, description=f"{wrong} {ctx.author.mention} this server hasn't splash feature unlocked")
            await ctx.reply(embed=e, mention_author=False)
            return  
        if icon == None:
           if not ctx.message.attachments: 
            await commandhelp(self, ctx, "guildedit" + " " + ctx.command.name)
           else:
            icon = ctx.message.attachments[0].url
        
        link = icon
        async with aiohttp.ClientSession() as ses: 
          async with ses.get(link) as r:
           try:
            if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await ctx.guild.edit(splash=bytes)
                emb = discord.Embed(color=0x2f3136, description=f"{check} {ctx.author.mention} changed server's banner to")
                emb.set_image(url=link)
                await ctx.reply(embed=emb, mention_author=False)
                return
           except Exception as e:
            e = discord.Embed(color=0xff0000, description=f"{wrong} {ctx.author.mention} unable to change server's banner {e}")
            await ctx.reply(embed=e, mention_author=False)
            return

    @commands.command(help="sets an icon for a role", description="config", usage="[emoji] [role]")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def roleicon(self, ctx: commands.Context, emoji: Union[discord.PartialEmoji, str]=None, *, role: discord.Role=None):
      botuser = ctx.guild.get_member(self.bot.user.id)  
      if not ctx.author.guild_permissions.manage_roles:
        await ctx.reply("You are missing `manage_roles` permission")
        return
      if ctx.guild.premium_tier < 2:
        embed = discord.Embed(color=0xffff00, description=f"{wrong} {ctx.author.mention} the server needs to have at least 7 boosts to change role icons")
        await ctx.reply(embed=embed, mention_author=False)
        return   
      if role == None or emoji==None:
        await commandhelp(self, ctx, ctx.command.name)
        return
      if role.position >= botuser.top_role.position:
        embed = discord.Embed(color=0xff0000, description=f"{wrong} {ctx.author.mention} i can't edit a role that's higher than mine")
        await ctx.reply(embed=embed, mention_author=False)
        return    
      if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner.id:
        embed = discord.Embed(color=0xff0000, description=f"{wrong} {ctx.author.mention} i can't edit a role that's higher than yours")
        await ctx.reply(embed=embed, mention_author=False)
        return     
      if isinstance(emoji, discord.PartialEmoji):  
       url = emoji.url  
       async with aiohttp.ClientSession() as ses: 
        async with ses.get(url) as r:
         try:
            if r.status in range (200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await role.edit(display_icon=bytes, reason=f"role icon changed by {ctx.author}")
                embed = discord.Embed(color=0x2f3136, description=f"{check} {ctx.author.mention} changed role icon for {role.mention}")
                await ctx.reply(embed=embed, mention_author=False)
                return
         except discord.HTTPException:
            await ctx.send(f'oh no! i was unable to change the role icon')  
            return
      elif isinstance(emoji, str):      
        ordinal = ord(emoji)
        async with aiohttp.ClientSession() as cs:
          async with cs.get(f"https://twemoji.maxcdn.com/v/latest/72x72/{ordinal:x}.png") as r:
            try:
              if r.status in range(200, 299):
                img = BytesIO(await r.read())
                bytes = img.getvalue()
                await role.edit(display_icon=bytes, reason=f"role icon changed by {ctx.author}")
                embed = discord.Embed(color=0x2f3136, description=f"{check} {ctx.author.mention} changed role icon for {role.mention}")
                await ctx.reply(embed=embed, mention_author=False) 
            except discord.HTTPException:
             await ctx.send(f'oh no! i was unable to change the role icon')    

async def setup(bot):
    await bot.add_cog(utility(bot))
