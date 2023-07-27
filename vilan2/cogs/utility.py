from discord import Embed, Member, User, Spotify, Role, TextChannel, Color
from discord.ext.commands import Context, command, Cog, Author, is_owner, group, AutoShardedBot as Bot
import discord, uwuipy, datetime, io, arrow, aiogtts, os
from tools.utils.checks import Perms
from typing import Union
from discord.ui import View, Button
from discord.ext import tasks
from io import BytesIO
from aiogtts import aiogTTS
from handlers.lastfmhandler import Handler

DISCORD_API_LINK = "https://discord.com/api/invite/"

@tasks.loop(seconds=10)
async def bday_task(bot: Bot): 
  results = await bot.db.fetch("SELECT * FROM birthday") 
  for result in results:
   if arrow.get(result['bday']).day == arrow.utcnow().day and arrow.get(result['bday']).month == arrow.utcnow().month:
    if result['state'] == "false":  
     member = await bot.fetch_user(result['user_id'])
     if member: 
      try: 
        await member.send(f"🎂 Happy birthday <@{member.id}>!!")
        await bot.db.execute("UPDATE birthday SET state = $1 WHERE user_id = $2", "true", result['user_id'])
      except: continue   
   else: 
     if result['state'] == "true": await bot.db.execute("UPDATE birthday SET state = $1 WHERE user_id = $2", "false", result['user_id'])

class Utility(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.lastfmhandler = Handler("289e4e09a1126fd938c1e1deeed869c7")
        self.cake = "🎂"
    
    async def bday_send(self, ctx: Context, message: str) -> discord.Message:
      return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.cake} {ctx.author.mention}: {message}"))
    
    @Cog.listener()
    async def on_ready(self): 
      await self.bot.wait_until_ready()
      bday_task.start(self.bot)
    
    @command(description="gets the invite link with administrator permission of a bot", help="utility", usage="[bot id]")
    async def getbotinvite(self, ctx, id: User):   
      if not id.bot: return await ctx.send_error("This is not a bot")
      embed = Embed(color=self.bot.color, description=f"**[invite the bot](https://discord.com/api/oauth2/authorize?client_id={id.id}&permissions=8&scope=bot%20applications.commands)**")
      view = discord.ui.View()
      view.add_item(discord.ui.Button(label=f"invite {id.name}", url=f"https://discord.com/api/oauth2/authorize?client_id={id.id}&permissions=8&scope=bot%20applications.commands"))
      await ctx.reply(embed=embed, view=view)
    
    @command(description="get someone's instagram profile informations", help="utility", usage="[ig user]", aliases=["ig"])
    async def instagram(self, ctx: Context, *, name):
        data = await self.bot.session.json("https://api.pretend.space/instagram", params={"username": name}, headers={"Authorization": f"Bearer {self.bot.pretend_api}"})
        if data.get('detail'): return await ctx.send_warning("Account not found")
        embed = Embed(color=self.bot.color, description=f"**[@{name}]({data['url']})**\n{data['bio']}")
        embed.add_field(name="following", value=data["following"])
        embed.add_field(name="followers", value=data["followers"])
        embed.add_field(name="posts", value=data["posts"])
        embed.set_thumbnail(url=data["avatar"])
        await ctx.reply(embed=embed)
    
    @command(description="see a member past avatars", help="utility", usage="<member>", aliases=["avh"])
    async def avatarhistory(self, ctx: Context, *, member: Member=None):
      if not member: member = ctx.author
      check = await self.bot.db.fetchrow("SELECT * FROM avh WHERE user_id = $1", member.id)
      if not check: return await ctx.send_warning(f"**{member}** didn't change his avatar")
      await ctx.reply(embed=Embed(color=self.bot.color, description=f"see **{int(check['count'])}** of **{member}'s** past [avatars](https://api.pretend.space/avatars/{member.id})"))
    
    @command(aliases=["tts", "speech"], description="convert your message to mp3", help="utility", usage="[message]") 
    async def texttospeech(self, ctx: Context, *, txt: str): 
      lol=BytesIO()
      vc = aiogTTS()
      await vc.save(txt, 'tts.mp3', lang='en')
      await vc.write_to_fp(txt, lol, slow=False, lang='en') 
      await ctx.reply(file=discord.File(fp='tts.mp3', filename="tts.mp3"))
      return os.remove('tts.mp3')
    
    @command(description="search for images on google", help="utility", usage="[query]", aliases=["img", "google"])
    async def image(self, ctx: Context, *, query: str):
      embeds = []
      data = await self.bot.session.json("https://notsobot.com/api/search/google/images", params={"query": query, "safe": "True"})
      for item in data: embeds.append(Embed(color=self.bot.color, title=f"<:google:1122111636489125898> Search result for {query}", description=item['header'], url=item['url']).set_image(url=item['image']['url']).set_footer(text=f"1/{len(data)} (Safe Search active)").set_author(name=ctx.author.global_name if ctx.author.global_name else ctx.author.name, icon_url=ctx.author.display_avatar.url))
      await ctx.paginator(embeds)
    
    @command(description="translate a word in any language you want", help="utility", usage="[language] [text]", aliases=["tr"])
    async def translate(self, ctx: Context, lang: str, *, text: str):
        data = (await self.bot.session.json("https://api.pretend.space/translate", params={"language": lang, "text": text}, headers={"Authorization": f"Bearer {self.bot.pretend_api}"}))
        await ctx.reply(embed=Embed(color=self.bot.color, title=f"translated to {data['language']}", description=f"{data['translated']}", timestamp=datetime.datetime.now()))
    
    @command(description="show information about an invite", help="utility", usage="[invite code]", aliases=["ii"])
    async def inviteinfo(self, ctx: Context, code: str): 
        invite_code = code
        data = await self.bot.session.json(DISCORD_API_LINK + invite_code, proxy=self.bot.proxy_url, ssl=False)
        name = data["guild"]["name"]
        id = data['guild']['id']
        description = data["guild"]["description"]
        boosts = data["guild"]["premium_subscription_count"]
        avatar = f"https://cdn.discordapp.com/icons/{data['guild']['id']}/{data['guild']['icon']}.{'gif' if 'a_' in data['guild']['icon'] else 'png'}?size=1024"
        embed = Embed(color=self.bot.color, description=f"{description}")
        embed.add_field(name="info", value=f"<:boosts:1079296391605661886> **boosts:** {boosts}")
        embed.set_thumbnail(url=avatar)
        embed.set_author(name=f"{name}")
        embed.set_footer(text=f"ID: {id}")
        await ctx.reply(embed=embed)
    
    @command(description="get the first message from a channel", help="utility", usage="<channel>", aliases=["firstmsg"])
    async def firstmessage(self, ctx: Context, *, channel: TextChannel=None):
        channel = channel or ctx.channel
        messages = [mes async for mes in channel.history(oldest_first=True, limit=1)]
        message = messages[0]
        embed = Embed(color=self.bot.color, title="first message in {}".format(channel), description=message.content, timestamp=message.created_at)
        embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        view = View()
        view.add_item(Button(label="message", url=message.jump_url))
        await ctx.reply(embed=embed, view=view)
    
    @command(description="see informations about the server", help="utility", aliases=["si"])
    async def serverinfo(self, ctx):
        guild = ctx.guild
        owner = guild.owner.global_name if guild.owner.global_name else guild.owner.name
        desc = guild.description if guild.description else ""
        icon = f"[icon]({guild.icon})" if guild.icon else "N/A"
        banner = f"[banner]({guild.banner})" if guild.banner else "N/A"
        splash = f"[splash]({guild.splash})" if guild.splash else "N/A"
        embed = Embed(color=self.bot.color, title=f"{guild.name} • shard: {guild.shard_id}/{self.bot.shard_count-1}", description=f"created at <t:{int(guild.created_at.timestamp())}:R> owned by {owner}\n{desc}")
        embed.add_field(name=f"channels {len(guild.channels)}", value=f"**text:** **{len(guild.text_channels)}**\n**voice:** **{len(guild.voice_channels)}**\n**categories:** **{len(guild.categories)}**")
        embed.add_field(name="links", value=f"{icon}\n{banner}\n{splash}")
        embed.add_field(name="info", value=f"**boosts:** {guild.premium_subscription_count} (level {guild.premium_tier})\n**verification:** {guild.verification_level}\n**vanity:** {guild.vanity_url}")
        embed.set_thumbnail(url=guild.icon)
        embed.set_footer(text=f"ID: {guild.id}")
        await ctx.reply(embed=embed)
    
    @group(aliases=["guild"], invoke_without_command=True)
    async def server(self, ctx: Context):
        return await ctx.invoke(self.bot.get_command("serverinfo"))
    
    @server.command(description="show information about the server", help="utility")
    async def info(self, ctx: Context): 
      return await ctx.invoke(self.bot.get_command("serverinfo"))
    
    @command(description="get role informations", help="utility", usage="[role]", aliases=["ri"])
    async def roleinfo(self, ctx: Context, *, role: Union[Role, str]): 
      if isinstance(role, str): 
        role = ctx.find_role(role)
        if role is None: return await ctx.send_warning(f"**{role.name}** is not a valid role")
            
      embed = Embed(color=role.color, title="@{} - `{}`".format(role.name, role.id), timestamp=role.created_at)
      embed.set_thumbnail(url=role.display_icon if not isinstance(role.display_icon, str) else None)
      embed.add_field(name="stats", value=f"**hoist:** {str(role.hoist).lower()}\n**mentionable:** {str(role.mentionable).lower()}\n**members:** {str(len(role.members))}")
      await ctx.reply(embed=embed)
    
    @command(description="see when an user was last seen", help="utility", usage="[member]")
    async def seen(self, ctx, *, member: Member):
        check = await self.bot.db.fetchrow("SELECT * FROM seen WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, member.id))
        if check is None: return await ctx.send_warning( f"I did not see **{member}**")
        ts = check['time']
        await ctx.reply(embed=Embed(color=self.bot.color, description="{}: **{}** was last seen <t:{}:R>".format(ctx.author.mention, member, ts))) 
    
    @command(description="clear the snipes in the server", help="utility", aliases=["cs"])
    @Perms.get_perms("manage_messages")
    async def clearsnipes(self, ctx):
        lis = ["snipe"]
        for l in lis: await self.bot.db.execute(f"DELETE FROM {l} WHERE guild_id = $1", ctx.guild.id)
        await ctx.send_success("Cleared all snipes")
    
    @command(aliases=["s"], description="check the latest deleted message from a channel", help="utility")
    async def snipe(self, ctx: Context, *, number: int=1):
        check = await self.bot.db.fetch("SELECT * FROM snipe WHERE guild_id = {} AND channel_id = {}".format(ctx.guild.id, ctx.channel.id))
        if len(check) == 0: return await ctx.send_warning( "No deleted messages found in this channel") 
        if number > len(check): return await ctx.send_warning( f"snipe limit is **{len(check)}**".capitalize()) 
        sniped = check[::-1][number-1]
        em = Embed(color=self.bot.color, description=sniped['content'], timestamp=sniped['time'])
        em.set_author(name=sniped['author'], icon_url=sniped['avatar']) 
        em.set_footer(text="{}/{}".format(number, len(check)))
        if sniped['attachment'] != "none":
         if ".mp4" in sniped['attachment'] or ".mov" in sniped['attachment']:
          url = sniped['attachment']
          r = await self.bot.session.read(url)
          bytes_io = BytesIO(r)
          file = File(fp=bytes_io, filename="video.mp4")
          return await ctx.reply(embed=em, file=file)
         else:
           try: em.set_image(url=sniped['attachment'])
           except: pass 
        return await ctx.reply(embed=em)
    
    @command(description="let people know your away", help="utility", usage="<reason>")
    async def afk(self, ctx: Context, *, reason="AFK"):      
       ts = int(datetime.datetime.now().timestamp()) 
       result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id)) 
       if result is None:
        await self.bot.db.execute("INSERT INTO afk VALUES ($1,$2,$3,$4)", ctx.guild.id, ctx.author.id, reason, ts)
        await ctx.send_success(f"You're now AFK -  **{reason}**")
    
    @command(description="uwuify a message", help="utility", usage="[message]", aliases=["uwu"])
    async def uwuify(self, ctx: Context, *, message: str):
      uwu = uwuipy.uwuipy()
      uwu_message = uwu.uwuify(message)
      await ctx.reply(uwu_message)
    
    @command(description="delete your name history", help="utility")
    async def clearnames(self, ctx: Context):
        embed = Embed(color=self.bot.color, description="Are you sure you want to clear your usernames?")
        yes = discord.ui.Button(emoji=self.bot.yes)
        no = discord.ui.Button(emoji=self.bot.no)
        async def yes_callback(interaction: discord.Interaction): 
          if interaction.user.id != ctx.author.id: return await self.bot.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True) 
          await self.bot.db.execute("DELETE FROM oldusernames WHERE user_id = $1", ctx.author.id) 
          return await interaction.response.edit_message(view=None, embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {interaction.user.mention}: Your name history has been deleted"))
        
        async def no_callback(interaction: discord.Interaction): 
         if interaction.user.id != ctx.author.id: return await self.bot.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True) 
         return await interaction.response.edit_message(view=None, embed=discord.Embed(color=self.bot.color, description=f"aborting action..."))  
        
        yes.callback = yes_callback
        no.callback = no_callback
        view = discord.ui.View()
        view.add_item(yes)
        view.add_item(no)
        await ctx.reply(embed=embed, view=view)
    
    @command(description="see the old names for a user", help="utility", usage="<user>", aliases=["names"])
    async def usernames(self, ctx, member: User=None):
       if not member: member = ctx.author
       check = await self.bot.db.fetch("SELECT * FROM oldusernames WHERE user_id = $1", member.id)
       i=0
       k=1
       l=0
       num = 0
       mes = ""
       number = []
       messages = []
       if check:
         for chec in check[::-1]:
          username = chec['username']
          num += 1
          mes += f"\n`{num}` {username}"
          k+=1
          l+=1
          if l == 10:
            messages.append(mes)
            number.append(Embed(color=self.bot.color, description=mes).set_author(name=f"changed usernames for {member.name}", icon_url=member.display_avatar.url))
            i+=1
            mes = ""
            l=0
         messages.append(mes)
         number.append(Embed(color=self.bot.color, description=mes).set_author(name=f"changed usernames for {member.name}", icon_url=member.display_avatar.url))
         return await ctx.paginator( number)   
       else: return await ctx.send_warning( f"no changed usernames found for **{member}**".capitalize())
    
    @command(description="see all server boosters", help="utility")
    async def boosters(self, ctx: Context):
            if not ctx.guild.premium_subscriber_role or len(ctx.guild.premium_subscriber_role.members) == 0: return await ctx.send_warning( "this server does not have any boosters".capitalize())
            i=0
            k=1
            l=0
            mes = ""
            number = []
            messages = []
            for member in ctx.guild.premium_subscriber_role.members: 
              mes = f"{mes}`{k}` {member}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=self.bot.color, title=f"boosters [{len(ctx.guild.premium_subscriber_role.members)}]", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
            messages.append(mes)
            number.append(Embed(color=self.bot.color, title=f"boosters [{len(ctx.guild.premium_subscriber_role.members)}]", description=messages[i]))
            await ctx.paginator( number) 
    
    @command(description="see an user avatar", help="utility", usage="<member>", aliases=["av"])
    async def avatar(self, ctx: Context, member: Union[Member, User]=None):
      if member is None: member = ctx.author
      if isinstance(member, Member):
        embed = Embed(color=self.bot.color, title=f"{member.name}'s avatar", url=member.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        await ctx.reply(embed=embed)
      elif isinstance(member, User):
        embed = Embed(color=self.bot.color, title=f"{member.name}'s avatar", url=member.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=member.display_avatar.url)
        await ctx.reply(embed=embed)
    
    @command(description="check how many members does your guild has", help="utility", aliases=["mc"])
    async def membercount(self, ctx: Context):
      b=len(set(b for b in ctx.guild.members if b.bot))
      h=len(set(b for b in ctx.guild.members if not b.bot))
      embed = Embed(color=self.bot.color)
      embed.set_author(name=f"{ctx.guild.name}'s member count", icon_url=ctx.guild.icon)
      embed.add_field(name=f"members (+{len([m for m in ctx.guild.members if (datetime.datetime.now() - m.joined_at.replace(tzinfo=None)).total_seconds() < 3600*24 and not m.bot])})", value=h)
      embed.add_field(name="total", value=ctx.guild.member_count) 
      embed.add_field(name="bots", value=b)
      await ctx.reply(embed=embed)
    
    @command(description="see an user banner", help="utility")
    async def banner(self, ctx: Context, *, member: User=Author):
     user = await self.bot.fetch_user(member.id)
     if not user.banner: return await ctx.send_warning(f"**{user}** doesn't have a banner") 
     embed = discord.Embed(color=self.bot.color, title=f"{user.name}'s banner", url=user.banner.url)
     embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
     embed.set_image(url=user.banner.url)
     return await ctx.reply(embed=embed) 
    
    @command(description="see a list of server roles", help="utility")
    async def roles(self, ctx):
        i=0
        k=1
        l=0
        mes = ""
        number = []
        messages = []
        for role in ctx.guild.roles:
          mes = f"{mes}`{k}` <@&{role.id}> - {len(role.members)} members\n"
          k+=1
          l+=1
          if l == 10:
           messages.append(mes)
           number.append(Embed(color=self.bot.color, title=f"roles in {ctx.guild.name} [{len(ctx.guild.roles)}]", description=messages[i]))
           i+=1
           mes = ""
           l=0
        
        messages.append(mes)
        number.append(Embed(color=self.bot.color, title=f"roles in {ctx.guild.name} [{len(ctx.guild.roles)}]", description=messages[i]))
        await ctx.paginator( number)
    
    @command(description="see a list of the bots in your server", help="utility")
    async def bots(self, ctx):
        i=0
        k=1
        l=0
        mes = ""
        number = []
        messages = []
        b=len(set(b for b in ctx.guild.members if b.bot))
        for m in ctx.guild.members:
         if m.bot:
          mes = f"{mes}`{k}` {m.name} - {m.id}\n"
          k+=1
          l+=1
          if l == 10:
           messages.append(mes)
           number.append(Embed(color=self.bot.color, title=f"bots in {ctx.guild.name} [{b}]", description=messages[i]))
           i+=1
           mes = ""
           l=0
        
        messages.append(mes)
        number.append(Embed(color=self.bot.color, title=f"bots in {ctx.guild.name} [{b}]", description=messages[i]))
        await ctx.paginator( number)
    
    @command(description="show users information", help="utility", usage="<user>", aliases=["ui"])
    async def userinfo(self, ctx: Context, *, member: Union[Member, User]=None):
      if not member: member = ctx.author
      user = await self.bot.fetch_user(member.id)
      discrim = ["0001", "1337", "0002", "9999", "0666", "0888", "6969", "0069"]
      badges = []
      if user.public_flags.active_developer: 
       badges.append("<:activedev:1120024255506157639>")
      if user.public_flags.early_supporter:
       badges.append("<:early:1120024487262429194>")
      if user.public_flags.verified_bot_developer:
       badges.append("<:developer:1120024438956621834>")
      if user.public_flags.staff: 
       badges.append("<:staff:1120024392898973696>")
      if user.public_flags.bug_hunter:
       badges.append("<:bughunter:1120024676157100162>") 
      if user.public_flags.bug_hunter_level_2:
       badges.append("<:gold_bughunter:1120024742569726102>")   
      if user.public_flags.partner:
       badges.append("<:partener:1120024599040622725>")
      if user.public_flags.discord_certified_moderator:
       badges.append("<:moderator:1120024553662464050>")
      if user.public_flags.hypesquad_bravery:
       badges.append("<:hypesquad_bravery:1120024942503788635>")
      if user.public_flags.hypesquad_balance:
       badges.append("<:hypesquad_balance:1120024922010423317>")
      if user.public_flags.hypesquad_brilliance:
       badges.append("<:hypesquad_brilliance:1120024896106418236>")  
      if user.discriminator in discrim or user.display_avatar.is_animated() or user.banner is not None:
       badges.append("<:nitro:1119547617630748682>")
      if user.discriminator == "0":
       badges.append("<:pomelo:1119542969456934963>")

      for guild in self.bot.guilds: 
       mem = guild.get_member(user.id)
       if mem is not None:
        if mem.premium_since is not None:
         badges.append("<:boost:1120024840355721347>")
         break
      
      async def lf(mem: Union[Member, User]): 
        check = await self.bot.db.fetchrow("SELECT username FROM lastfm WHERE user_id = {}".format(mem.id))
        if check is not None: 
          u = str(check['username']) 
          if u != "error": 
            a = await self.lastfmhandler.get_tracks_recent(u, 1)
            return f"<:lastfm:1123217269397393479> Listening to [{a['recenttracks']['track'][0]['name']}]({a['recenttracks']['track'][0]['url']}) by **{a['recenttracks']['track'][0]['artist']['#text']}** on lastfm.."
      
        return ""
      
      e = Embed(color=self.bot.color, title="‎" + "".join(map(str, badges)))
      if isinstance(member, Member):
       e.description = f"{await lf(member)}"
       e.set_author(name=member.global_name if member.global_name else member.name, icon_url=member.display_avatar.url)
       e.set_thumbnail(url=member.display_avatar.url)
       e.add_field(name="dates", value=f"**joined:** <t:{int(member.joined_at.timestamp())}:R>\n**created:** <t:{int(member.created_at.timestamp())}:R>")
       roles = member.roles[1:][::-1]
       if len(roles) > 0: e.add_field(name=f"roles ({len(roles)})", value=' '.join([r.mention for r in roles]) if len(roles) < 5 else ' '.join([r.mention for r in roles[:4]]) + f" and {len(roles)-4} more")
       e.set_footer(text=f"ID: {str(member.id)}")
       await ctx.reply(embed=e)
       return
      if isinstance(member, User):
       e = Embed(color=self.bot.color)
       e.title = "‎" + "".join(map(str, badges))
       e.set_author(name=member.global_name if member.global_name else member.name, icon_url=member.display_avatar.url)
      
       e.set_thumbnail(url=member.display_avatar.url)
       e.add_field(name="dates", value=f"**created:** <t:{int(member.created_at.timestamp())}:R>")
       e.set_footer(text=f"ID: {str(member.id)}")
       await ctx.reply(embed=e)
    
    @group(invoke_without_command=True, description="show what an user is listening on spotify", help="utility", usage="<member>", aliases=["sp"])
    async def spotify(self, ctx: Context, *, member: Member=None):
      if not member: member = ctx.author
      a = next((a for a in member.activities if isinstance(a, Spotify)), None)
      if not a: return await ctx.send_warning("You are not listening to **spotify**")
      await ctx.reply(f"||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||https://open.spotify.com/track/{a.track_id}")
    
    @spotify.command(name="search", description="search for a song on spotify", help="utility", usage="[song]")
    async def spotify_search(self, ctx: Context, *, song: str=None):
        data = (await self.bot.session.json("https://api.pretend.space/spotify", params={"query": song}, headers={"Authorization": f"Bearer {self.bot.pretend_api}"}))['url']
        await ctx.reply(data)
    
    @group(invoke_without_command=True, help="utility", description="check member's birthday", aliases=['bday'])
    async def birthday(self, ctx: Context, *, member: Member=None): 
     if member is None: member = ctx.author 
     rocks = "'s"
     date = await self.bot.db.fetchrow("SELECT bday FROM birthday WHERE user_id = $1", member.id) 
     if not date: return await ctx.send_warning( f"**{'Your' if member == ctx.author else str(member) + rocks}** birthday is **not** set")
     date = date['bday']
     if "ago" in arrow.get(date).humanize(granularity='day'): date=date.replace(year=date.year+1)
     else: date = date
     if arrow.get(date).humanize(granularity='day') == "in 0 days":	date = "tomorrow" 
     elif arrow.get(date).day == arrow.utcnow().day and arrow.get(date).month == arrow.utcnow().month: date = "today"  
     else: date=arrow.get(date+datetime.timedelta(days=1)).humanize(granularity='day') 
     await self.bday_send(ctx, f"{'Your' if member == ctx.author else '**' + member.name + rocks + '**'} birthday is **{date}**")
    
    @birthday.command(name="set", help="utility", description="set your birthday", usage="[month] [day]")
    async def bday_set(self, ctx: Context, month: str, day: str): 
     try:
      if len(month)==1: mn="M"
      elif len(month)==2: mn="MM"
      elif len(month)==3: mn="MMM"
      else: mn="MMMM"
      if "th" in day: day=day.replace("th","")
      if "st" in day: day=day.replace("st","")
      if len(day)==1: dday="D"
      else: dday="DD"
      ts=f"{month} {day} {datetime.date.today().year}"
      if "ago" in arrow.get(ts, f'{mn} {dday} YYYY').humanize(granularity="day"): year=datetime.date.today().year+1
      else: year=datetime.date.today().year
      string=f"{month} {day} {year}"
      date=arrow.get(string, f'{mn} {dday} YYYY')
      check = await self.bot.db.fetchrow("SELECT * FROM birthday WHERE user_id = $1", ctx.author.id)
      if not check: await self.bot.db.execute("INSERT INTO birthday VALUES ($1,$2,$3)", ctx.author.id, date.datetime, "false")
      else: await self.bot.db.execute("UPDATE birthday SET bday = $1 WHERE user_id = $2", date.datetime, ctx.author.id)
      await self.bday_send(ctx, f"Your birthday has been set as **{month} {day}**")
     except: return await ctx.send_error(f"usage: `{ctx.clean_prefix}birthday set [month] [day]`") 
    
    @birthday.command(name="unset", help="utility", description="unset your birthday")
    async def bday_unset(self, ctx: Context):
      check = await self.bot.db.fetchrow("SELECT bday FROM birthday WHERE user_id = $1", ctx.author.id)
      if not check: return await ctx.send_warning( "Your birthday is **not** set")
      await self.bot.db.execute("DELETE FROM birthday WHERE user_id = $1", ctx.author.id)
      await ctx.send_warning( "Removed your birthday")
    
async def setup(bot):
    await bot.add_cog(Utility(bot))