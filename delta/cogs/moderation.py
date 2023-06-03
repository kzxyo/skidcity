import discord  
from discord.ext import commands 
from discord.ui import View, Button

class moderation(commands.Cog):
   def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot 
        
   @commands.command()
   @commands.cooldown(1, 3, commands.BucketType.user)
   async def ban(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
    if (not ctx.author.guild_permissions.ban_members):
     e = discord.Embed(color=discord.Color.yellow(), description=f"> {ctx.author.mention} You need __`ban_members` permission__ to use this command")
     await ctx.reply(embed=e, mention_author=False)
     return  

    if member == None:
       e = discord.Embed(color=0x2f3136, title="**ban**", description="> __bans member from the server__")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="**category**", value="> __moderation__", inline=True)
       e.add_field(name="**permissions**", value="> __ban_members__", inline=True)
       e.add_field(name="**usage**", value=f"`usage: ban [member] <reason>`", inline=False)
       e.add_field(name="**aliases**", value="> __none__")
       await ctx.reply(embed=e, mention_author=False)  
       return 

    if member == None or member == ctx.message.author:
        e = discord.Embed(color=0x2f3136, description=f"> <:emoji_7:1048996990706524322> {ctx.author.mention}: you cannot ban __yourself__")
        await ctx.reply(embed=e, mention_author=False)
        return
    
    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=0x2f3136, description=f"> <:emoji_7:1048996990706524322> {ctx.author.mention}: __you can't ban {member.mention}__")
       await ctx.reply(embed=nope, mention_author=False)
       return

    if reason == None:
        reason = "No reason provided"

    if ctx.guild.premium_subscriber_role in member.roles:
     button1 = Button(label="accept", style=discord.ButtonStyle.green)
     button2 = Button(label="refuse", style=discord.ButtonStyle.red)
     embed = discord.Embed(color=0x2f3136, description=f"> *are you sure you want to ban {member.mention}?** __they are a server booster__")
     async def button1_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=0x2f3136, description=f"> {interaction.user.mention} this is not your __message__")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        
        try: 
          await member.ban(reason=f"> kicked by __{ctx.author}__ - __{reason}__")
          embe = discord.Embed(color=0x2f3136, description=f"> <:icons_banhammer:1049360132766711880> {member.mention} got banned whit the reason __{reason}__")
          await interaction.response.edit_message(embed=embe, view=None)
          try:
           banned = discord.Embed(color=0x2f3136, title="**ban case**", description=f"> __you have been banned from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin__")
           banned.set_thumbnail(url=ctx.guild.icon.url)
           banned.add_field(name="**moderator**", value=ctx.author)
           banned.add_field(name="**reason**", value=reason)
           banned.set_footer(text=f"> __id: {ctx.guild.id}__")  
           await member.send(embed=banned)
          except:
           pass   
        except:
         no = discord.Embed(color=0x2f3136, description=f"> <:emoji_7:1048996990706524322> {ctx.author.mention}: __i don't have enough permissions to do this__")
         await interaction.response.edit_message(embed=no, mention_author=False)
     button1.callback = button1_callback

     async def button2_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=0x2f3136, description=f"> __{interaction.user.mention} this is not your message__")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return

        embe = discord.Embed(color=0x2f3136, description=f"> __alright you changed your mind!__")
        await interaction.response.edit_message(embed=embe, view=None)

     button2.callback = button2_callback

     view = View()
     view.add_item(button1)
     view.add_item(button2)
     await ctx.reply(embed=embed, view=view, mention_author=False)        

    else:    
     try: 
      await member.ban(reason=f"> banned by __{ctx.author}__ - __{reason}__")
      embed = discord.Embed(color=0x2f3136, description=f"> <:icons_banhammer:1049360132766711880> __{member.mention} got banned whit the reason {reason}__")
      await ctx.reply(embed=embed, mention_author=False)
      try: 
         banned = discord.Embed(color=0x2f3136, title="**ban case**", description=f"> __you have been banned from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin__")
         banned.set_thumbnail(url=ctx.guild.icon.url)
         banned.add_field(name="**moderator**", value=ctx.author)
         banned.add_field(name="**reason**", value=reason)
         banned.set_footer(text=f"> __id: {ctx.guild.id}__")   
         await member.send(embed=banned)
      except: 
         pass 
     except:
        no = discord.Embed(color=0x2f3136, description=f"> <:emoji_7:1048996990706524322> __{ctx.author.mention}: i don't have enough permissions to do this__")
        await ctx.reply(embed=no, mention_author=False)

   @ban.error
   async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(color=0xff0000, description=f"> {ctx.author.mention}: __{error}__")
        await ctx.reply(embed=embed, mention_author=False)

   
   @commands.command()
   @commands.cooldown(1, 3, commands.BucketType.user)
   async def unban(self, ctx: commands.Context, *, member: discord.User=None):
    if (not ctx.author.guild_permissions.ban_members):
     e = discord.Embed(color=discord.Color.yellow(), description=f"> {ctx.author.mention} You need `ban_members` __permission__ to use this command")
     await ctx.reply(embed=e, mention_author=False)
     return   

    if member == None:
       e = discord.Embed(color=0x2f3136, title="**unban**", description="> __unbans member from server__")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="**category**", value="> __moderation__", inline=True)
       e.add_field(name="**permissions**", value="> __ban_members__", inline=True)
       e.add_field(name="**usage**", value=f"`usage: unban [member]`", inline=False)
       e.add_field(name="**aliases**", value="> __none__")
       await ctx.reply(embed=e, mention_author=False)  
       return 
  
    try: 
     guild = ctx.guild
     embed = discord.Embed(color=0x2f3136, description=f"> {member} __has been unbanned__")
     await guild.unban(user=member)
     await ctx.reply(embed=embed, mention_author=False)
    except:
       emb = discord.Embed(color=discord.Color.yellow(), description=f"> __{ctx.author.mention} couldn't unban this member__")
       await ctx.reply(embed=emb, mention_author=False)  
   
   @commands.command()
   @commands.cooldown(1, 3, commands.BucketType.user)
   async def kick(self, ctx: commands.Context, member: discord.Member=None, *, reason=None):
    if (not ctx.author.guild_permissions.kick_members):
     e = discord.Embed(color=discord.Color.yellow(), description=f"> {ctx.author.mention} You need `kick_members` __permission__ to use this commnad")
     await ctx.reply(embed=e, mention_author=False)
     return   

    if member == None:
       e = discord.Embed(color=0x2f3136, title="**kick**", description="> __kicks member from server__")
       e.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
       e.add_field(name="**category**", value="> __moderation__", inline=True)
       e.add_field(name="**permissions**", value="> __kick_members__", inline=True)
       e.add_field(name="**usage**", value=f"`usage: kick [member] <reason>\nexample: kick {ctx.author.mention} test`", inline=False)
       e.add_field(name="**aliases**", value="> __none__")
       await ctx.reply(embed=e, mention_author=False) 
       return  

    if member == ctx.author:
     e = discord.Embed(color=discord.Color.yellow(), description=f"> <:emoji_7:1048996990706524322> __{ctx.author.mention}: you can't kick yourserlf__")
     await ctx.reply(embed=e, mention_author=False)
     return

    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner.id:
       nope = discord.Embed(color=0xFFEE00, description=f"> <:emoji_7:1048996990706524322> __{ctx.author.mention}: you can't kick {member.mention}__")
       await ctx.reply(embed=nope, mention_author=False)
       return   
 
    if reason == None:
        reason = "No reason provided"

    if ctx.guild.premium_subscriber_role in member.roles:
     button1 = Button(label="accept", style=discord.ButtonStyle.green)
     button2 = Button(label="refuse", style=discord.ButtonStyle.red)
     embed = discord.Embed(color=0x2f3136, description=f"> are you sure you want to kick __{member.mention}?__ **they are a server booster**")
     async def button1_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=0xff0000, description=f"> {interaction.user.mention} this is not your __message__")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return
        
        try: 
          await member.kick(reason=f"> kicked by __{ctx.author}__ - __{reason}__")
          embe = discord.Embed(color=0x2f3136, description=f"> <:icons_banhammer:1049360132766711880> __{member.mention} got kicked whit the reason {reason}__")
          await interaction.response.edit_message(embed=embe, view=None)
          try:
           banned = discord.Embed(color=0x2f3136, title="**kick case**", description=f"> __you have been kicked from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin__")
           banned.set_thumbnail(url=ctx.guild.icon.url)
           banned.add_field(name="**moderator**", value=ctx.author)
           banned.add_field(name="**reason**", value=reason)
           banned.set_footer(text=f"> __id: {ctx.guild.id}__")  
           await member.send(embed=banned)
          except:
           print('cant dm')    
        except:
         no = discord.Embed(color=0xFFEE00, description=f"> <:emoji_7:1048996990706524322> __{ctx.author.mention}: i don't have enough permissions to do this__")
         await interaction.response.edit_message(embed=no, mention_author=False)
     button1.callback = button1_callback

     async def button2_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            em = discord.Embed(color=0xff0000, description=f"> __{interaction.user.mention}__ this is not your message")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return

        embe = discord.Embed(color=0x2f3136, description=f"> __alright you changed your mind!__")
        await interaction.response.edit_message(embed=embe, view=None)

     button2.callback = button2_callback

     view = View()
     view.add_item(button1)
     view.add_item(button2)
     await ctx.reply(embed=embed, view=view, mention_author=False)        

    else:
     try: 
      await member.kick(reason=f"> kicked by __{ctx.author}__ - __{reason}__")
      embed = discord.Embed(color=0x2f3136, description=f"> <:icons_banhammer:1049360132766711880> __{member.mention} got kicked whit the reason {reason}__")
      await ctx.reply(embed=embed, mention_author=False)
      try:
           banned = discord.Embed(color=0x2f3136,    title="**kick case**", description=f"> __you have been kicked from {ctx.guild.name}\nIf you want to dispute this situation, contact an admin__")
           banned.set_thumbnail(url=ctx.guild.icon.url)
           banned.add_field(name="**moderator**", value=ctx.author)
           banned.add_field(name="**reason**", value=reason)
           banned.set_footer(text=f"> __id: {ctx.guild.id}__")  
           await member.send(embed=banned)
      except:
           pass   
     except:
        no = discord.Embed(color=0xFFEE00, description=f"> <:emoji_7:1048996990706524322> __{ctx.author.mention}: i don't have enough permissions to do this__")
        await ctx.reply(embed=no, mention_author=False)       

   @kick.error
   async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(color=0xff0000, description=f"{ctx.author.mention}: {error}")
        await ctx.reply(embed=embed, mention_author=False)
             
async def setup(bot) -> None: 
    await bot.add_cog(moderation(bot))
  