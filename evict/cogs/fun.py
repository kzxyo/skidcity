import discord, random, json, asyncio, aiohttp
from discord.ext import commands
from patches.fun import Pack
from random import randrange
from io import BytesIO
from patches.permissions import Permissions
from kureAPI import API
from bot.headers import Session
from patches.fun import RockPaperScissors, BlackTea, TicTacToe

api = API("58ZCTj0fTkai")

class fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = Session()

    @commands.command(name="choose", description="choose between options", usage="[choices separated by a command]")
    async def choose_cmd(self, ctx: commands.Context, *, choice: str): 
     choices = choice.split(", ")
     if len(choices) == 1: return await ctx.reply("please put a `,` between your choices")
     final = random.choice(choices)
     await ctx.reply(embed=discord.Embed(color=self.bot.color, description=final))

    @Permissions.has_permission(manage_messages=True)
    @commands.command(name="poll", description="start a quick poll", help="fun", brief="manage messages")
    async def poll(self, ctx: commands.Context, *, question: str): 
      message = await ctx.send(embed=discord.Embed(color=self.bot.color, description=question).set_author(name=f"{ctx.author} asked"))
      await message.add_reaction("👍")
      await message.add_reaction("👎")

    @commands.command(description="flip a coin", help="fun")
    async def coinflip(self, ctx: commands.Context): 
     await ctx.reply(random.choice(["heads", "tails"]))  
    
    @commands.command(aliases=["rps"], description="play rock paper scissors with the bot", help="fun")
    async def rockpaperscisssors(self, ctx: commands.Context): 
      view = RockPaperScissors(ctx)
      embed = discord.Embed(color=self.bot.color, title="Rock Paper Scissors!", description="Click a button to play!")
      view.message = await ctx.reply(embed=embed, view=view)    
    
    @commands.group(invoke_without_command=True)
    async def clock(self, ctx): 
      return await ctx.create_pages()
    
    @clock.command(name="in", help="fun", description="clock in")
    async def clock_in(self, ctx: commands.Context): 
      return await ctx.reply(f"🕰️ {ctx.author.mention}: clocks in...")
    
    @clock.command(name="out", help="fun", description="clock out")
    async def clock_out(self, ctx: commands.Context): 
      return await ctx.reply(f"🕰️ {ctx.author.mention}: clocks out...")
    
    @commands.command(description="retard rate an user", help="fun", usage="<member>")
    async def howretarded(self, ctx, member: discord.Member=commands.Author):
     if member.id in self.bot.owner_ids: await ctx.reply(embed=discord.Embed(color=self.bot.color, title="how retarded", description=f"{member.mention} is `0%` retarded <a:dumbass:1265487107196190802>"))
     else: await ctx.reply(embed=discord.Embed(color=self.bot.color, title="how retarded", description=f"{member.mention} is `{randrange(100)}%` retarded <a:dumbass:1265487107196190802>"))

    @commands.command(description="gay rate an user", help="fun", usage="<member>")
    async def howgay(self, ctx, member: discord.Member=commands.Author):
     if member.id in self.bot.owner_ids: return await ctx.reply(embed=discord.Embed(color=self.bot.color, title="gay r8", description=f"{member.mention} is `0%` gay 🏳️‍🌈"))
     else:await ctx.reply(embed=discord.Embed(color=self.bot.color, title="gay r8", description=f"{member.mention} is `{randrange(100)}%` gay 🏳️‍🌈"))
    
    @commands.command(description="cool rate an user", help="fun", usage="<member>")
    async def howcool(self, ctx, member: discord.Member=commands.Author):
     if member.id in self.bot.owner_ids: return
     else: await ctx.reply(embed=discord.Embed(color=self.bot.color, title="cool r8", description=f"{member.mention} is `{randrange(100)}%` cool 😎"))

    @commands.command(description="check an user's iq", help="fun", usage="<member>")
    async def iq(self, ctx, member: discord.Member=commands.Author):
     if member.id in self.bot.owner_ids: return await ctx.reply(embed=discord.Embed(color=self.bot.color, title="iq test", description=f"{member.mention} has `3000` iq 🧠"))
     else: await ctx.reply(embed=discord.Embed(color=self.bot.color, title="iq test", description=f"{member.mention} has `{randrange(100)}` iq 🧠"))

    @commands.command(description="hot rate an user", help="fun", usage="<member>")
    async def hot(self, ctx, member: discord.Member=commands.Author):
     if member.id in self.bot.owner_ids: return
     else: await ctx.reply(embed=discord.Embed(color=self.bot.color, title="hot r8", description=f"{member.mention} is `{randrange(100)}%` hot 🥵"))     
    
    @commands.command()
    async def pp(self, ctx:commands.Context, *, member: discord.Member=commands.Author):
      lol = "===================="
      embed = discord.Embed(color=self.bot.color, description=f"{member.name}'s penis\n\n8{lol[random.randint(1, 20):]}D")
      if member.id in self.bot.owner_ids:
            embed = discord.Embed(color=self.bot.color, description=f"{member.name}'s penis\n\n8==============================D")
      await ctx.reply(embed=embed)  
    
    @commands.command(description="check how many bitches an user has", help="fun", usage="<member>")
    async def bitches(self, ctx: commands.Context, *, user: discord.Member=commands.Author):
      choices = ["regular", "still regular", "lol", "xd", "id", "zero", "infinite"]
      if random.choice(choices) == "infinite": result = "∞" 
      elif random.choice(choices) == "zero": result = "0"
      else: result = random.randint(0, 100)
      embed = discord.Embed(color=self.bot.color, description=f"{user.mention} has `{result}` bitches")
      if user.id in self.bot.owner_ids:
            embed = discord.Embed(color=self.bot.color, description=f"{user.mention} has `1000000000000` bitches")
      await ctx.reply(embed=embed)

    @commands.command(description="send a random bird image", help="fun")
    async def bird(self, ctx): 
      data = await self.bot.session.json("https://api.alexflipnote.dev/birb")
      await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['file'])), filename="bird.png"))

    @commands.command(description="send a random dog image", help="fun")
    async def dog(self, ctx):
        data = await self.bot.session.json("https://random.dog/woof.json")
        await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['url'])), filename=f"dog{data['url'][-4:]}"))

    @commands.command(description="send a random cat image", help="fun")
    async def cat(self, ctx):
        data = (await self.bot.session.json("https://api.thecatapi.com/v1/images/search"))[0]
        await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['url'])), filename="cat.png"))
    
    @commands.command(description="send a random capybara image", help="fun")
    async def capybara(self, ctx):
      data = await self.bot.session.json('https://api.capy.lol/v1/capybara?json=true')
      await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['data']['url'])), filename="cat.png"))
    
    @commands.command(description="return an useless fact", help="fun", aliases=["fact", "uf"])
    async def uselessfact(self, ctx):
      data = (await self.bot.session.json("https://uselessfacts.jsph.pl/random.json?language=en"))['text']
      await ctx.reply(data) 

    @commands.command(description='screenshot a website', usage='[url]', help='fun', aliases=['ss', 'screen'])
    async def screenshot(self, ctx: commands.Context, url: str):
        async with ctx.typing():
          if not url.startswith(("https://", "http://")):
            url = f"https://{url}"
        try:      
          data = await api.screenshot(f"{url}")
          embed = discord.Embed(color=self.bot.color)
          embed.set_image(url=data.image_url)
          await ctx.reply(embed=embed)
        except Exception: return await ctx.warning(f"This site **does not** appear to be valid.")

    @commands.command(description='grab info on a snapchat profile', usage='[username]', help='fun')
    async def snapchat(self, ctx: commands.Context, *, username: str):
      try:
        results = await self.bot.session.json("https://kure.pl/snapstory", headers=self.bot.resent_api, params={"username": username})
        if results.get('detail'):
          return await ctx.error(results['detail'])
        await ctx.paginate(list(map(lambda s: s['url'], results['stories'])))
      except Exception: return await ctx.warning(f"{username} **does not** appear to be valid.")

    @commands.command(description='get a random TikTok video', aliases=["foryou", "foryoupage"])
    async def fyp(self, ctx: commands.Context):

        async with ctx.typing():
            recommended = await self.session.get_json(url="https://www.tiktok.com/api/recommend/item_list/?WebIdLastTime=1709562791&aid=1988&app_language=en&app_name=tiktok_web&browser_language=en-US&browser_name=Mozilla&browser_online=true&browser_platform=Win32&browser_version=5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F124.0.0.0%20Safari%2F537.36&channel=tiktok_web&clientABVersions=70508271%2C72097972%2C72118536%2C72139452%2C72142433%2C72147654%2C72156694%2C72157773%2C72174908%2C72183344%2C72191581%2C72191933%2C72203590%2C72211002%2C70405643%2C71057832%2C71200802%2C71957976&cookie_enabled=true&count=9&coverFormat=2&device_id=7342516164603889184&device_platform=web_pc&device_type=web_h264&focus_state=true&from_page=fyp&history_len=3&isNonPersonalized=false&is_fullscreen=false&is_page_visible=true&language=en&odinId=7342800074206741537&os=windows&priority_region=&pullType=1&referer=&region=BA&screen_height=1440&screen_width=2560&showAboutThisAd=true&showAds=false&tz_name=Europe%2FLondon&watchLiveLastTime=1713523355360&webcast_language=en&msToken=W3zoVLSFi9M0BsPE6uC63GCdeoVC7hmjRNelZIe-7FP7x-1LRee6WYHYfpWXg3NYPoreJf_dMxfRWTZprVN8UU70_IaHnBMNirtZIRNp2QuR1nBivJgnetgiM-XTh7_KGbNswVs=&X-Bogus=DFSzswVOmtvANegtt2bDG-OckgSu&_signature=_02B4Z6wo00001BozSvQAAIDBhqj5OL8769AaM05AAGCne")
            recommended = recommended['itemList'][0]
            embed = discord.Embed(color=self.bot.color)
            embed.description = f'[{recommended["desc"]}](https://tiktok.com/@{recommended["author"]["uniqueId"]}/video/{recommended["id"]})'

            embed.set_author(
                name="@" + recommended["author"]["uniqueId"],
                icon_url=recommended["author"]["avatarLarger"],
            )
            embed.set_footer(
                text=f"❤️ {self.session.human_format(recommended['stats']['diggCount'])} 💬 {self.session.human_format(recommended['stats']['commentCount'])} 🔗 {self.session.human_format(recommended['stats']['shareCount'])} ({self.session.human_format(recommended['stats']['playCount'])} views)"
            )
            
            final = await self.session.get_json("https://tikwm.com/api/", params={"url": f'https://tiktok.com/@{recommended["author"]["uniqueId"]}/video/{recommended["id"]}'})
            await ctx.reply(
                embed=embed,
                file=discord.File(fp=await self.session.getbyte(url=final['data']['play']), filename='resenttiktok.mp4')
            )
            try: await ctx.message.delete()
            except: pass

    @commands.command(description='grab info on a roblox profile', usage='[username]', help='fun')
    async def roblox(self, ctx: commands.Context, profile: str):
      try:
        data = await api.get_roblox_user(f"{profile}")
        url = data.url
        embed = discord.Embed(color=self.bot.color, description=f'{data.bio}', title=f'{data.username}', url=f'{url}')
        embed.add_field(name='friends:', value=f'{data.friends}', inline=True)
        embed.add_field(name='following:', value=f'{data.followings}', inline=True)
        embed.add_field(name='followers:', value=f'{data.followers}', inline=True)
        embed.set_thumbnail(url=data.avatar_url)
        embed.set_footer(text='Roblox', icon_url='https://cdn.resent.dev/roblox.jpg')
        await ctx.reply(embed=embed)
      except Exception: return await ctx.warning(f"{profile} **does not** appear to be valid.")  

    @commands.command(description='grab info on a snapchat profile', usage='[username]', help='fun')
    async def snapchatuser(self, ctx: commands.Context, profile: str):
      try:  
        data = await api.get_snapchat_user(f"{profile}")
        embed = discord.Embed(color=self.bot.color, description=f'{data.bio}')
        embed.set_author(name=f'{data.username}', icon_url=f'{data.avatar}')
        embed.set_image(url=data.snapcode)
        embed.set_thumbnail(url=data.avatar)
        embed.set_footer(text='Snapchat', icon_url='https://cdn.resent.dev/snapchat.jpg')
        await ctx.reply(embed=embed)
      except Exception: return await ctx.warning(f"{profile} **does not** appear to be valid.")  

    @commands.command(description='grab info on a tiktok profile', usage='[username]', help='fun')
    async def tiktok(self, ctx: commands.Context, profile: str):
      try:
        data = await api.get_tiktok_user(f"{profile}")
        url = data.url
        embed = discord.Embed(color=self.bot.color, description=f'{data.bio}', title=f'{data.username}', url=f'{url}')
        embed.set_author(name=f'{data.username}', icon_url=f'{data.avatar}')
        embed.add_field(name='friends:', value=f'{data.friends}', inline=True)
        embed.add_field(name='followers:', value=f'{data.followers}', inline=True)
        embed.add_field(name='following:', value=f'{data.following}', inline=True)
        embed.add_field(name='likes:', value=f'{data.hearts}', inline=True)
        if data.verified: embed.add_field(name='verified:', value=f'{data.verified}', inline=True)
        if data.private: embed.add_field(name='private:', value=f'{data.private}')
        embed.set_thumbnail(url=data.avatar)
        embed.set_footer(text='TikTok', icon_url='https://cdn.resent.dev/tiktok.png')
        await ctx.reply(embed=embed)
      except Exception: return await ctx.warning(f"{profile} **does not** appear to be valid.")  

    @commands.command(description='grab info on a instagram profile', usage='[username]', help='fun')
    async def instagram(self, ctx: commands.Context, profile: str):
      try:  
        data = await api.get_instagram_user(f"{profile}")
        url = data.url
        embed = discord.Embed(color=self.bot.color, description=f'{data.bio}', title=f'{data.full_name}', url=f'{url}')
        embed.set_author(name=f'{data.username}', icon_url=f'{data.profile_pic}')
        embed.add_field(name='followers:', value=f'{data.followers}', inline=True)
        embed.add_field(name='following:', value=f'{data.following}', inline=True)
        embed.add_field(name='posts:', value=f'{data.posts}', inline=True)
        embed.add_field(name='highlights:', value=f'{data.highlights}', inline=True)
        embed.set_thumbnail(url=data.profile_pic)
        embed.set_footer(text='Instagram', icon_url='https://cdn.resent.dev/instagram.png')
        await ctx.reply(embed=embed)
      except Exception: return await ctx.warning(f"{profile} **does not** appear to be valid.")  

    @commands.command(description='ask chatgpt a question', usage='text', help='fun')
    async def chatgpt(self, ctx: commands.Context, *, text: str):
      try:  
        data = await api.ask_chatgpt(f"{text}")
        await ctx.reply(data)
      except Exception: return await ctx.warning(f"API is either down or I have no ChatGPT credits. Please join https://discord.gg/evict and report this.")  

    @commands.command(description="ship rate an user", help="fun", usage="[member]")
    async def ship(self, ctx, member: discord.Member):
     return await ctx.reply(f"**{ctx.author.name}** 💞 **{member.name}** = **{randrange(101)}%**")

    @commands.command(description="sends a random advice", help="fun")
    async def advice(self, ctx: commands.Context):
     byte = await self.bot.session.read("https://api.adviceslip.com/advice")
     data = str(byte, 'utf-8')
     data = data.replace("[", "").replace("]", "")
     js = json.loads(data) 
     return await ctx.reply(js['slip']['advice'])                              
    
    @commands.command(description="pack someone", help="fun", usage="[user]")
    async def pack(self, ctx: commands.Context, *, member: discord.Member): 
     if member == ctx.author: return await ctx.warning("You **cannot** pack yourself. I don't know why you would want to either.")
     await ctx.send(f"{member.mention} {random.choice(Pack.scripts)}") 

    @commands.command(aliases=["ttt"], description="play tictactoe with your friends", help="fun", usage="[member]")
    async def tictactoe(self, ctx: commands.Context, *, member: discord.Member):
      if member is ctx.author: return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.author.mention}: You can't play with yourself. It's ridiculous"))
      if member.bot: return await ctx.reply("bots can't play")      
      vi = TicTacToe(ctx.author, member)
      vi.message = await ctx.send(content=f'{member.mention}\n**{member.name}** vs **{ctx.author.name}**\n\nTic Tac Toe: **{ctx.author.name}** Is First', embed=None, view=vi, allowed_mentions=discord.AllowedMentions(users=[member]))  

    @commands.command(description="play blacktea with your friends", help="fun")
    async def blacktea(self, ctx: commands.Context): 
     try:
      if BlackTea.MatchStart[ctx.guild.id] is True: 
       return await ctx.reply("somebody in this server is already playing blacktea")
     except KeyError: pass 

     BlackTea.MatchStart[ctx.guild.id] = True 
     embed = discord.Embed(color=self.bot.color, title="BlackTea Matchmaking", description=f"⏰ Waiting for players to join. To join react with 🍵.\nThe game will begin in **20 seconds**")
     embed.add_field(name="goal", value="You have **10 seconds** to say a word containing the given group of **3 letters.**\nIf failed to do so, you will lose a life. Each player has **2 lifes**")
     embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)  
     mes = await ctx.send(embed=embed)
     await mes.add_reaction("🍵")
     await asyncio.sleep(20)
     me = await ctx.channel.fetch_message(mes.id)
     players = [user.id async for user in me.reactions[0].users()]
     leaderboard = []
     players.remove(self.bot.user.id)

     if len(players) < 2:
      BlackTea.MatchStart[ctx.guild.id] = False
      return await ctx.send("😦 {}, not enough players joined to start blacktea".format(ctx.author.mention), allowed_mentions=discord.AllowedMentions(users=True)) 
  
     while len(players) > 1: 
      for player in players: 
       strin = await BlackTea.get_string()
       await ctx.send(f"⏰ <@{player}>, type a word containing **{strin.upper()}** in **10 seconds**", allowed_mentions=discord.AllowedMentions(users=True))
      
       def is_correct(msg): 
        return msg.author.id == player
      
       try: 
        message = await self.bot.wait_for('message', timeout=10, check=is_correct)
       except asyncio.TimeoutError: 
          try: 
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
            if BlackTea.lifes[player] == 3: 
              await ctx.send(f" <@{player}>, you're eliminated ☠️", allowed_mentions=discord.AllowedMentions(users=True))
              BlackTea.lifes[player] = 0
              players.remove(player)
              leaderboard.append(player)
              continue 
          except KeyError:  
            BlackTea.lifes[player] = 0   
          await ctx.send(f"💥 <@{player}>, you didn't reply on time! **{2-BlackTea.lifes[player]}** lifes remaining", allowed_mentions=discord.AllowedMentions(users=True))    
          continue
       i=0
       for word in await BlackTea.get_words(): 
         if strin.lower() in message.content.lower() and message.content.lower() == word.lower(): 
            i+=1
            pass 
       if i == 0:   
          try: 
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
            if BlackTea.lifes[player] == 3: 
              await ctx.send(f" <@{player}>, you're eliminated ☠️", allowed_mentions=discord.AllowedMentions(users=True))
              BlackTea.lifes[player] = 0
              players.remove(player)
              leaderboard.append(player)
              continue 
          except KeyError:  
            BlackTea.lifes[player] = 0 
          await ctx.send(f"💥 <@{player}>, incorrect word! **{2-BlackTea.lifes[player]}** lifes remaining", allowed_mentions=discord.AllowedMentions(users=True))
       else: 
         await message.add_reaction("✅") 
         i=0 
     
     leaderboard.append(players[0])
     le = 1
     auto = ""
     for leader in leaderboard[::-1]: 
      auto += f"{'<a:crown:1021829752782323762>' if le == 1 else f'`{le}`'} **{ctx.guild.get_member(leader) or leader}**\n"
      if le == 10: break
      le += 1
     e = discord.Embed(color=self.bot.color, title=f"leaderboard for blacktea", description=auto).set_footer(text=f"top {'10' if len(leaderboard) > 9 else len(leaderboard)} players")     
     await ctx.send(embed=e)
     BlackTea.lifes[players[0]] = 0
     BlackTea.MatchStart[ctx.guild.id] = False 

    @commands.command(name="8ball", description="answers to your question", usage="[question]", help="fun")
    async def mtball(self, ctx: commands.Context, *, arg):      
     rand = ['**Yes**', '**No**', '**definitely yes**', '**Of course not**', '**Maybe**', '**Never**', '**Yes, dummy**', '**No wtf**']
     e = discord.Embed(color=self.bot.color, description=f"You asked: {arg}\nAnswer: {random.choice(rand)}")
     await ctx.reply(embed=e)
    
    @commands.command(aliases=['img'])
    async def image(
      self, ctx: commands.Context, *, query: str
    ):
      try:
        async with aiohttp.ClientSession() as session:
          async with session.post("https://api.rival.rocks/google/image", data=query, params={"safe": "true"}, headers={"api-key": self.bot.rival_api}) as response:
            response = await response.json()
            embeds = [discord.Embed(title=res.get('title', 'Untitled'), url="https://" + res.get('domain', ''), color=res.get('color', discord.Color.default())).set_image(url=res.get('url', '')) for res in response]
          # if len(embeds) == 0: return await ctx.warning("Nothing found.")
          return await ctx.paginate(embeds=embeds)
      except Exception:
        return await ctx.warning(f"Could not find anything with this query")

    @commands.command(name='search', description='search for something on google', usage='[query]', aliases=['google'])
    async def search(self, ctx: commands.Context, *, query: str):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://vile.bot/api/browser/search", data=query) as response:
                response = await response.json()

        chunks = [response[i:i + 5] for i in range(0, len(response), 5)]

        embeds = []
        for page, chunk in enumerate(chunks):
            embed = discord.Embed(color=self.bot.color, title='Search Results').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url).set_footer(text=f"Page {page+1}/{len(chunks)} Of Google Pages", icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/1200px-Google_%22G%22_logo.svg.png')
            for res in chunk:
                embed.add_field(name=f"Google", value=f"[**{res.get('title')}**](https://{res.get('domain')})\n{(res.get('description'))}", inline=False)
            embeds.append(embed)

        return await ctx.paginate(embeds=embeds)

async def setup(bot) -> None:
    await bot.add_cog(fun(bot))     