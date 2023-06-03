import discord  
from discord.ext import commands 
from discord.ui import View, Button

class moderation(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
    

    #-----BAN-----#
   @commands.command()
   async def ban(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
    if (not ctx.author.guild_permissions.ban_members):
     e = discord.Embed(color=discord.Color.yellow(), description=f"{ctx.author.mention}: you are missing permissions `ban_members`")
     await ctx.reply(embed=e, mention_author=False)
     return  

    if member == None:
       e = discord.Embed(color=0xffffff, title="ban", description="bans member from the server")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="category", value="moderation", inline=True)
       e.add_field(name="permissions", value="ban_members", inline=True)
       e.add_field(name="usage", value=f"```usage: ban [member] <reason>```", inline=False)
       e.add_field(name="aliases", value="none")
       await ctx.reply(embed=e, mention_author=False)  
       return 
 
    if member == None or member == ctx.message.author:
        e = discord.Embed(color=0xffffff, description=f"<:check_warning:956780930066964500> {ctx.author.mention}: you cannot ban yourself")
        await ctx.reply(embed=e, mention_author=False)
        return
    
    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=0xffffff, description=f"<:check_warning:956780930066964500> {ctx.author.mention}: you can't ban {member.mention}")
       await ctx.reply(embed=nope, mention_author=False)
       return

    if reason == None:
        reason = "No reason provided"

    if ctx.guild.premium_subscriber_role in member.roles:
     button1 = Button(label="yes", style=discord.ButtonStyle.green)
     button2 = Button(label="no", style=discord.ButtonStyle.red)
     embed = discord.Embed(color=0xffffff, description=f"are you sure you want to ban {member.mention}? they are a server booster")
     async def button1_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=0xffffff, description=f"{interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        
        try: 
          await member.ban(reason=f"kicked by {ctx.author} - {reason}")
          embe = discord.Embed(color=0xffffff, description=f"<:icons_hammer:976525276186038312> {member.mention} got banned | {reason}")
          await interaction.response.edit_message(embed=embe, view=None)
          try:
           banned = discord.Embed(color=0xffffff, title="ban case", description=f"you have been banned from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
           banned.set_thumbnail(url=ctx.guild.icon.url)
           banned.add_field(name="moderator", value=ctx.author)
           banned.add_field(name="reason", value=reason)
           banned.set_footer(text=f"id: {ctx.guild.id}")  
           await member.send(embed=banned)
          except:
           pass   
        except:
         no = discord.Embed(color=0xffffff, description=f"<:check_warning:956780930066964500> {ctx.author.mention}: i don't have enough permissions to do this")
         await interaction.response.edit_message(embed=no, mention_author=False)
     button1.callback = button1_callback

     async def button2_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=0xffffff, description=f"{interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return

        embe = discord.Embed(color=0xffffff, description=f"alright you changed your mind!")
        await interaction.response.edit_message(embed=embe, view=None)

     button2.callback = button2_callback

     view = View()
     view.add_item(button1)
     view.add_item(button2)
     await ctx.reply(embed=embed, view=view, mention_author=False)        

    else:    
     try: 
      await member.ban(reason=f"banned by {ctx.author} - {reason}")
      embed = discord.Embed(color=0xffffff, description=f"<:icons_hammer:976525276186038312> {member.mention} got banned | {reason}")
      await ctx.reply(embed=embed, mention_author=False)
      try: 
         banned = discord.Embed(color=0xffffff, title="ban case", description=f"you have been banned from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
         banned.set_thumbnail(url=ctx.guild.icon.url)
         banned.add_field(name="moderator", value=ctx.author)
         banned.add_field(name="reason", value=reason)
         banned.set_footer(text=f"id: {ctx.guild.id}")   
         await member.send(embed=banned)
      except: 
         pass 
     except:
        no = discord.Embed(color=0xffffff, description=f"<:check_warning:956780930066964500> {ctx.author.mention}: i don't have enough permissions to do this")
        await ctx.reply(embed=no, mention_author=False)

   @ban.error
   async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(color=0xffffff, description=f"{ctx.author.mention}: {error}")
        await ctx.reply(embed=embed, mention_author=False)

#-----UNBAN-----#

   @commands.command()
   async def unban(self, ctx: commands.Context, *, member: discord.User=None):
    if (not ctx.author.guild_permissions.ban_members):
     e = discord.Embed(color=discord.Color.yellow(), description=f"{ctx.author.mention}: you are missing permissions `ban_members`")
     await ctx.reply(embed=e, mention_author=False)
     return   

    if member == None:
       e = discord.Embed(color=0xffffff, title="unban", description="unbans member from server")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="category", value="moderation", inline=True)
       e.add_field(name="permissions", value="ban_members", inline=True)
       e.add_field(name="usage", value=f"```usage: unban [member]```", inline=False)
       e.add_field(name="aliases", value="none")
       await ctx.reply(embed=e, mention_author=False)  
       return 
  
    try: 
     guild = ctx.guild
     embed = discord.Embed(color=0xffffff, description=f"{member} has been unbanned")
     await guild.unban(user=member)
     await ctx.reply(embed=embed, mention_author=False)
    except:
       emb = discord.Embed(color=discord.Color.yellow(), description=f"{ctx.author.mention} couldn't unban this member")
       await ctx.reply(embed=emb, mention_author=False)  
   
#-----KICK-----#

   @commands.command()
   async def kick(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
    if (not ctx.author.guild_permissions.kick_members):
     e = discord.Embed(color=discord.Color.yellow(), description=f"{ctx.author.mention}: you are missing permissions `kick_members`")
     await ctx.reply(embed=e, mention_author=False)
     return   

    if member == None:
       e = discord.Embed(color=0xffffff, title="kick", description="kicks member from server")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="category", value="moderation", inline=True)
       e.add_field(name="permissions", value="kick_members", inline=True)
       e.add_field(name="usage", value=f"```usage: kick [member] <reason>\nexample: kick {ctx.author.mention} test```", inline=False)
       e.add_field(name="aliases", value="none")
       await ctx.reply(embed=e, mention_author=False) 
       return  

    if member == ctx.author:
     e = discord.Embed(color=discord.Color.yellow(), description=f"<:check_warning:956780930066964500> {ctx.author.mention}: you can't kick yourserlf")
     await ctx.reply(embed=e, mention_author=False)
     return

    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=0xffffff, description=f"<:check_warning:956780930066964500> {ctx.author.mention}: you can't kick {member.mention}")
       await ctx.reply(embed=nope, mention_author=False)
       return   
 
    if reason == None:
        reason = "No reason provided"

    if ctx.guild.premium_subscriber_role in member.roles:
     button1 = Button(label="yes", style=discord.ButtonStyle.green)
     button2 = Button(label="no", style=discord.ButtonStyle.red)
     embed = discord.Embed(color=0xffffff, description=f"are you sure you want to kick {member.mention}? they are a server booster")
     async def button1_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=0xffffff, description=f"{interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        
        try: 
          await member.kick(reason=f"kicked by {ctx.author} - {reason}")
          embe = discord.Embed(color=0xffffff, description=f"<:icons_hammer:976525276186038312> {member.mention} got kicked | {reason}")
          await interaction.response.edit_message(embed=embe, view=None)
          try:
           banned = discord.Embed(color=0xffffff, title="kick case", description=f"you have been kicked from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
           banned.set_thumbnail(url=ctx.guild.icon.url)
           banned.add_field(name="moderator", value=ctx.author)
           banned.add_field(name="reason", value=reason)
           banned.set_footer(text=f"id: {ctx.guild.id}")  
           await member.send(embed=banned)
          except:
           print('cant dm')    
        except:
         no = discord.Embed(color=0xffffff, description=f"<:check_warning:956780930066964500> {ctx.author.mention}: i don't have enough permissions to do this")
         await interaction.response.edit_message(embed=no, mention_author=False)
     button1.callback = button1_callback

     async def button2_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=0xffffff, description=f"{interaction.user.mention} this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return

        embe = discord.Embed(color=0xffffff, description=f"alright you changed your mind!")
        await interaction.response.edit_message(embed=embe, view=None)

     button2.callback = button2_callback

     view = View()
     view.add_item(button1)
     view.add_item(button2)
     await ctx.reply(embed=embed, view=view, mention_author=False)        

    else:
     try: 
      await member.kick(reason=f"kicked by {ctx.author} - {reason}")
      embed = discord.Embed(color=0xffffff, description=f"<:icons_hammer:976525276186038312> {member.mention} got kicked | {reason}")
      await ctx.reply(embed=embed, mention_author=False)
      try:
           banned = discord.Embed(color=0xffffff, title="kick case", description=f"you have been kicked from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin")
           banned.set_thumbnail(url=ctx.guild.icon.url)
           banned.add_field(name="moderator", value=ctx.author)
           banned.add_field(name="reason", value=reason)
           banned.set_footer(text=f"id: {ctx.guild.id}")  
           await member.send(embed=banned)
      except:
           pass   
     except:
        no = discord.Embed(color=0xffffff, description=f"<:check_warning:956780930066964500> {ctx.author.mention}: i don't have enough permissions to do this")
        await ctx.reply(embed=no, mention_author=False)       

   @kick.error
   async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(color=0xffffff, description=f"{ctx.author.mention}: {error}")
        await ctx.reply(embed=embed, mention_author=False)

async def setup(bot) -> None: 
    await bot.add_cog(moderation(bot))  