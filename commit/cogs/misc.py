import discord, aiohttp
from discord import app_commands
from discord.ext import commands
from typing import Union
from cogs.events import commandhelp

DISCORD_API_LINK = "https://discord.com/api/invite/"
check = "<:x_approve:1030181005656596551>"
wrong = "<:x_denied:1030181108916174848>"
Warning = "<:check_warning:1030180956985892895>"


class misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(help="shows someone's avatar", usage="<member>", aliases=["av"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def avatar(self, ctx: commands.Context, *, member: Union[discord.Member, discord.User]=None): 
      if member is None:
        member = ctx.author 

      embed = discord.Embed(color=0x2f3136, title=f"{member.name}'s avatar", url=member.avatar.url)
      if isinstance(member, discord.Member):
       if not member.avatar: 
        embed = discord.Embed(color=0x2f3136, title=f"{member.name}'s avatar", url=member.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
       else:
        embed = discord.Embed(color=0x2f3136, title=f"{member.name}'s avatar", url=member.avatar.url)
        embed.set_image(url=member.avatar.url)

       await ctx.reply(embed=embed, mention_author=False)  

      elif isinstance(member, discord.User):
       embed = discord.Embed(color=0x2f3136, title=f"{member.name}'s avatar", url=member.display_avatar.url)
       embed.set_image(url=member.display_avatar.url)  
       await ctx.reply(embed=embed, mention_author=False)    

    @commands.command(help="shows someone's banner", usage="<member>")
    @commands.cooldown(1, 3, commands.BucketType.user)   
    async def banner(self, ctx: commands.Context, *, member: Union[discord.Member, discord.User]=None):
      if member is None:
        member = ctx.author 

      user = await self.bot.fetch_user(member.id)
      if not user.banner:
        e = discord.Embed(color=0xff0000, description=f"{wrong} {ctx.author.mention} this user doesn't have a banner")
        await ctx.reply(embed=e, mention_author=False)
        return 

      embed = discord.Embed(color=0x2f3136, title=f"{user.name}'s banner", url=user.banner.url)
      embed.set_image(url=user.banner.url)
      await ctx.reply(embed=embed, mention_author=False)   
    
    @commands.command(aliases=["ui", "whois", "user"], usage="<user>", help="shows user info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx, member: discord.Member = None):
        if not member:  # if member is no mentioned
            member = ctx.author  # set member as the author
            
        embed = discord.Embed(color=0x2f3136)
        embed.set_thumbnail(url= member.display_avatar)
        embed.set_author(name=f"{member}", icon_url= member.display_avatar)
        embed.set_footer(text= f"ID: {member.id}")
        embed.add_field(name="joined", value=f"<:t{int(member.joined_at.timestamp())}:R>")
        embed.add_field(name= "registered", value=f"<:t{int(member.created_at.timestamp())}:R>"),
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        embed.add_field(name="join position", value=str(members.index(member)+1))
        embed.add_field(name='status', value=member.status)
        embed.add_field(name='activity', value=member.activity)
        if len(member.roles) > 1:
            role_string = ' '.join([r.mention for r in member.roles][1:])
            embed.add_field(name="roles [{}]".format(len(member.roles)-1), value=role_string)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="shows server's banner", aliases=["guildbanner"])
    @commands.cooldown(1, 3, commands.BucketType.user)   
    async def serverbanner(self, ctx: commands.Context):    
     if not ctx.guild.banner:
        e = discord.Embed(color=0xff0000, description=f"{wrong} {ctx.author.mention} this server doesn't have a banner")
        await ctx.reply(embed=e, mention_author=False)
        return    
     
     embed = discord.Embed(color=0x2f3136, title=f"{ctx.guild.name}'s banner", url=ctx.guild.banner.url)
     embed.set_image(url=ctx.guild.banner.url)
     await ctx.reply(embed=embed, mention_author=False)    

    @commands.command(help="shows server's avatar", aliases=["guildavatar", "servericon", "guildicon"])
    @commands.cooldown(1, 3, commands.BucketType.user)   
    async def serveravatar(self, ctx: commands.Context):    
     if not ctx.guild.icon:
        e = discord.Embed(color=0xff0000, description=f"{wrong} {ctx.author.mention}: this server doesn't have an avatar")
        await ctx.reply(embed=e, mention_author=False)
        return    
     
     embed = discord.Embed(color=0x2f3136, title=f"{ctx.guild.name}'s avatar", url=ctx.guild.icon.url)
     embed.set_image(url=ctx.guild.icon.url)
     await ctx.reply(embed=embed, mention_author=False)       

    @commands.command(aliases=["si"], help="shows server info")
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def serverinfo(self, ctx: commands.Context):
        owner = ctx.guild.owner_id
        member = ctx.author
        channels = len(ctx.message.guild.categories)
        text = len(ctx.message.guild.text_channels)
        voice = len(ctx.message.guild.voice_channels)
        total = len(ctx.message.guild.members)
        server_id = ctx.guild.id
        roles = len(ctx.message.guild.roles)
        verify = len(ctx.message.guild.verification_level)
        stickers = len(ctx.guild.stickers)
        emoji = len(ctx.guild.emojis)
        
        users = len([m for m in ctx.guild.members if not m.bot])
        online = 0
        bots = 0
        for member in ctx.guild.members:
            if str(member.status) == 'online' or str(member.status) == 'idle' or str(member.status) == 'dnd':
                    online += 1
            if member.bot:
                bots += 1
        
        embed=discord.Embed(color=0x2f3136)
        embed.add_field(name= "Created", value=f"<t:{int(ctx.guild.created_at.timestamp())}:R>", inline=False)
        embed.add_field(name= "Server owner:", value=f"<@{owner}>", inline=False)
        embed.add_field(name= "members", value=f"**users:** {users}\n**online:** {online}\n**bots:** {bots}\n**total:** {total}", inline=False)
        embed.add_field(name= "channels", value=f"**categories:** {channels}\n**text:** {text}\n**voice:** {voice}", inline=False)
        embed.add_field(name= "info", value=f"**verification:** {verify}\n**roles:** {roles}\n**stickers:** {stickers}\n**emoji:** {emoji}", inline=False)
        embed.set_author(name= ctx.guild.name)
        embed.set_footer(text= f"ID: {server_id}")
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=["mc"], help="shows guilds membercount")
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def membercount(self, ctx):
        
        members = len([m for m in ctx.guild.members if not m.bot])
        bots = 0
        
        for member in ctx.guild.members:
            if member.bot:
                bots += 1
        embed = discord.Embed(color=0x2f3136)
        embed.set_author(name=f"{ctx.guild.name}'s statistics", icon_url=ctx.guild.icon.url)
        embed.add_field(name="total", value=f"{len(ctx.guild.members)}")
        embed.add_field(name="members", value=f"{members}")
        embed.add_field(name="bots", value=f"{bots}")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="get a server's banner based on it's invite code", usage="[invite code]")
    async def sbanner(self, ctx, *, link=None):
     if link == None:
      await commandhelp(self, ctx, ctx.command.name)
      return

     invite_code = link
     async with aiohttp.ClientSession() as cs:
      async with cs.get(DISCORD_API_LINK + invite_code) as r:
       data = await r.json()

     try: 
      format = ""
      if "a_" in data["guild"]["banner"]:
        format = ".gif"
      else:
        format = ".png"

      embed = discord.Embed(color=0x2f3136, title=data["guild"]["name"] + "'s banner")
      embed.set_image(url="https://cdn.discordapp.com/banners/" + data["guild"]["id"] + "/" + data["guild"]["banner"] + f"{format}?size=1024")
      await ctx.reply(embed=embed, mention_author=False)
     except:
      e = discord.Embed(color=discord.Color.red(), description=f"{wrong} {ctx.author.mention} Couldn't get **" + data["guild"]["name"] + "'s** banner")
      await ctx.reply(embed=e, mention_author=False)

    @commands.command(help="get a server's splash based on it's invite code", usage="[invite code]")
    async def splash(self, ctx, *, link=None):
      if link == None:
       await commandhelp(self, ctx, ctx.command.name)
       return 

      try: 
       invite_code = link
       async with aiohttp.ClientSession() as cs:
        async with cs.get(DISCORD_API_LINK + invite_code) as r:
         data = await r.json()

       embed = discord.Embed(color=0x2f3136, title=data["guild"]["name"] + "'s splash")
       embed.set_image(url="https://cdn.discordapp.com/splashes/" + data["guild"]["id"] + "/" + data["guild"]["splash"] + ".png?size=1024")
       await ctx.reply(embed=embed, mention_author=False)
      except:
        e = discord.Embed(color=discord.Color.red(), description=f"{wrong} {ctx.author.mention}: Couldn't get **" + data["guild"]["name"] + "'s** splash image")
        await ctx.reply(embed=e, mention_author=False) 

    @commands.command(help="get a server's icon based on it's invite code", usage="[invite code]")
    async def sicon(self, ctx, *, link=None):
     if link == None:
       await commandhelp(self, ctx, ctx.command.name)
       return

     invite_code = link
     async with aiohttp.ClientSession() as cs:
      async with cs.get(DISCORD_API_LINK + invite_code) as r:
       data = await r.json()

     try: 
      format = ""
      if "a_" in data["guild"]["icon"]:
        format = ".gif"
      else:
        format = ".png"
          
      embed = discord.Embed(color=0x2f3136, title=data["guild"]["name"] + "'s icon")
      embed.set_image(url="https://cdn.discordapp.com/icons/" + data["guild"]["id"] + "/" + data["guild"]["icon"] + f"{format}?size=1024")
      await ctx.reply(embed=embed, mention_author=False)
     except:
      e = discord.Embed(color=discord.Color.red(), description=f"{wrong} {ctx.author.mention}: Couldn't get **" + data["guild"]["name"] + "'s** icon")
      await ctx.reply(embed=e, mention_author=False)   

async def setup(bot):
    await bot.add_cog(misc(bot))