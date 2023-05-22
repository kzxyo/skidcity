import discord, aiohttp, random, json, time, asyncio, os, dateutil.parser
from discord.ext import commands
from tools.utils import Pack
from random import randrange
from typing import List
from io import BytesIO

class RockPaperScissors(discord.ui.View): 
  def __init__(self, ctx: commands.Context):
    self.ctx = ctx   
    self.get_emoji = {"rock": "🪨", "paper": "📰", "scissors": "✂️"} 
    self.status = False 
    super().__init__(timeout=10)
  
  async def disable_buttons(self): 
   for item in self.children: 
    item.disabled = True 

   await self.message.edit(view=self)   

  async def action(self, interaction: discord.Interaction, selection: str): 
    if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "This is not your game", ephemeral=True)
    botselection = random.choice(["rock", "paper, scissors"])

    def getwinner(): 
     if botselection == "rock" and selection == "scissors": return interaction.client.user.id
     elif botselection == "rock" and selection == "paper": return interaction.user.id
     elif botselection == "paper" and selection == "rock": return interaction.client.user.id
     elif botselection == "paper" and selection == "scissors": return interaction.user.id
     elif botselection == "scissors" and selection == "rock": return interaction.user.id 
     elif botselection == "scissors" and selection == "paper": return interaction.client.user.id 
     else: return "tie"           
    
    if getwinner() == "tie": await interaction.response.edit_message(embed=discord.Embed(color=interaction.client.color, title="Tie!", description=f"You both picked {self.get_emoji.get(selection)}"))
    elif getwinner() == interaction.user.id: await interaction.response.edit_message(embed=discord.Embed(color=interaction.client.color, title="You won!", description=f"You picked {self.get_emoji.get(selection)} and the bot picked {self.get_emoji.get(botselection)}")) 
    else: await interaction.response.edit_message(embed=discord.Embed(color=interaction.client.color, title="Bot won!", description=f"You picked {self.get_emoji.get(selection)} and the bot picked {self.get_emoji.get(botselection)}"))
    await self.disable_buttons()
    self.status = True 

  @discord.ui.button(emoji="🪨")
  async def rock(self, interaction: discord.Interaction, button: discord.ui.Button): 
    return await self.action(interaction, "rock")
  
  @discord.ui.button(emoji="📰")
  async def paper(self, interaction: discord.Interaction, button: discord.ui.Button): 
   return await self.action(interaction, "paper")

  @discord.ui.button(emoji="✂️")
  async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button): 
   return await self.action(interaction, "scissors") 
  
  async def on_timeout(self): 
   if self.status == False: await self.disable_buttons()


class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int, player1: discord.Member, player2: discord.Member):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y
        self.player1 = player1
        self.player2 = player2

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            if interaction.user != self.player1: return await interaction.response.send_message("you can't interact with this button", ephemeral=True)
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now **{self.player2.name}**'s turn"
        else:
            if interaction.user != self.player2: return await interaction.response.send_message("you can't interact with this button", ephemeral=True)
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now **{self.player1.name}'s** turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f'**{self.player1.name}** won!'
            elif winner == view.O:
                content = '**{}** won!'.format(self.player2.name)
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, player1: discord.Member, player2: discord.Member):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y, player1, player2))

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X
        
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None
    
    async def on_timeout(self) -> None:
      for item in self.children: item.disabled = True 
      await self.message.edit(view=self.view)  

class BlackTea: 
    """BlackTea backend variables"""
    MatchStart = {}
    lifes = {}
    
    async def get_string(): 
      lis = await BlackTea.get_words()
      word = random.choice([l for l in lis if len(l) > 3])
      return word[:3]

    async def get_words(): 
      async with aiohttp.ClientSession() as cs: 
       async with cs.get("https://www.mit.edu/~ecprice/wordlist.100000") as r: 
        byte = await r.read()
        data = str(byte, 'utf-8')
        return data.splitlines()

class TypeRace:       
   """TypeRace backend variables"""    
   async def getanswer(): 
    async with aiohttp.ClientSession() as cs: 
      async with cs.get("https://www.mit.edu/~ecprice/wordlist.100000") as r: 
        byte = await r.read()
        data = str(byte, 'utf-8')
        data = data.splitlines()
        mes = ""
        for _ in range(10):
           mes = f"{mes}{random.choice(data)} " 

        return mes   

   def accurate(first: str, second: str):
    percentage = 0 
    i=0
    text1 = first.split()
    text2 = second.split()
    for t in text2: 
     try: 
       if t == text1[i]: 
        percentage+=10 
       i+=1 
     except: return percentage 

    return percentage        

class fun(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.command(aliases=["goodmorning"], help="fun", description="says good morning")
    async def gm(self, ctx: commands.Context): 
      await ctx.send(f"Good Morning {ctx.author.mention}!")

    @commands.command(help="fun", description="says good night")
    async def gn(self, ctx: commands.Context): 
      await ctx.send(f"💤 Good Night {ctx.author.mention}!")  

    @commands.command(name="choose", description="choose between options", usage="[choices separated by a comma]\nexample ;choose apple, pear, carrot")
    async def choose_cmd(self, ctx: commands.Context, *, choice: str): 
     choices = choice.split(", ")
     if len(choices) == 1: return await ctx.reply("please put a `,` between your choices")
     final = random.choice(choices)
     await ctx.reply(final)

    @commands.command(name="quickpoll", description="start a quick poll", help="fun")
    async def quickpoll_cmd(self, ctx: commands.Context, *, question: str): 
      message = await ctx.reply(embed=discord.Embed(color=self.bot.color, description=question).set_author(name=f"{ctx.author} asked"))
      await message.add_reaction("👍")
      await message.add_reaction("👎")

    @commands.command(name="no", description="just says yes", help="fun")
    async def no_cmd(self, ctx: commands.Context): 
     await ctx.reply("yes") 
    
    @commands.command(name="yes", description="just says no", help="fun")
    async def yes_cmd(self, ctx: commands.Context): 
     await ctx.reply("no") 

    @commands.command(description="flip a coin", help="fun")
    async def coinflip(self, ctx: commands.Context): 
     await ctx.reply(random.choice(["heads", "tails"]))  
    
    @commands.hybrid_command(aliases=["rps"], description="play rock paper scissors with the bot", help="fun")
    async def rockpaperscisssors(self, ctx: commands.Context): 
      view = RockPaperScissors(ctx)
      embed = discord.Embed(color=self.bot.color, title="Rock Paper Scissors!", description="Click a button to play!")
      view.message = await ctx.reply(embed=embed, view=view)

    @commands.command(help="fun", description="join vc and make some noise")
    async def esex(self, ctx: commands.Context): 
      if not ctx.author.voice: return await ctx.send_warning("You are **not** in a voice channel")
      if ctx.voice_client: return await ctx.send_warning("The bot is **already** in a voice channel")
      vc = await ctx.author.voice.channel.connect()
      vc.play(discord.FFmpegPCMAudio("./esex.mp3"), after=lambda e: print("done"))
      await ctx.message.add_reaction("🥵") 
      while vc.is_playing(): 
       await asyncio.sleep(10)
       if not ctx.voice_client: return
       await ctx.reply("I'm done, leaving vc")
       await ctx.voice_client.disconnect(force=True)      
    
    @commands.group(invoke_without_command=True)
    async def clock(self, ctx): 
      return await ctx.create_pages()
    
    @clock.command(name="in", help="fun", description="clock in")
    async def clock_in(self, ctx: commands.Context): 
      return await ctx.reply(f"🕰️ {ctx.author.mention}: clocks in...")
    
    @clock.command(name="out", help="fun", description="clock out")
    async def clock_out(self, ctx: commands.Context): 
      return await ctx.reply(f"🕰️ {ctx.author.mention}: clocks out...")

    @commands.hybrid_command(description="see someone's banner", help="utility", usage="<user>")
    async def banner(self, ctx: commands.Context, *, member: discord.User=commands.Author):
     user = await self.bot.fetch_user(member.id)
     if not user.banner: return await ctx.send_warning(f"**{user}** Doesn't have a banner") 
     embed = discord.Embed(color=self.bot.color, title=f"{user.name}'s banner", url=user.banner.url)
     embed.set_image(url=user.banner.url)
     return await ctx.reply(embed=embed) 
    
    @commands.hybrid_command(description="retard rate an user", help="fun", usage="<member>")
    async def howretarded(self, ctx, member: discord.Member=commands.Author):
     await ctx.reply(embed=discord.Embed(color=self.bot.color, title="how retarded", description=f"{member.mention} is {randrange(101)}% retarded <:blue_dumb:1092786568974049341>"))

    @commands.hybrid_command(description="gay rate an user", help="fun", usage="<member>")
    async def howgay(self, ctx, member: discord.Member=commands.Author):
     await ctx.reply(embed=discord.Embed(color=self.bot.color, title="gay r8", description=f"{member.mention} is {randrange(101)}% gay 🏳️‍🌈"))
    
    @commands.hybrid_command(description="cool rate an user", help="fun", usage="<member>")
    async def howcool(self, ctx, member: discord.Member=commands.Author):
     await ctx.reply(embed=discord.Embed(color=self.bot.color, title="cool r8", description=f"{member.mention} is {randrange(101)}% cool 😎"))

    @commands.hybrid_command(description="check an user's iq", help="fun", usage="<member>")
    async def iq(self, ctx, member: discord.Member=commands.Author):
     await ctx.reply(embed=discord.Embed(color=self.bot.color, title="iq test", description=f"{member.mention} has `{randrange(200)}` iq 🧠"))

    @commands.hybrid_command(description="hot rate an user", help="fun", usage="<member>")
    async def hot(self, ctx, member: discord.Member=commands.Author):
     await ctx.reply(embed=discord.Embed(color=self.bot.color, title="hot r8", description=f"{member.mention} is `{randrange(100)}%` hot 🥵"))     
    
    @commands.hybrid_command()
    async def pp(self, ctx:commands.Context, *, member: discord.Member=commands.Author):
      lol = "===================="
      embed = discord.Embed(color=self.bot.color, description=f"{member.name}'s penis\n\n8{lol[random.randint(1, 20):]}D")
      await ctx.reply(embed=embed)  
    
    @commands.command(description="check how many bitches an user has", help="fun", usage="<member>")
    async def bitches(self, ctx: commands.Context, *, user: discord.Member=commands.Author):
      choices = ["regular", "still regular", "lol", "xd", "id", "zero", "infinite"]
      if random.choice(choices) == "infinite": result = "∞" 
      elif random.choice(choices) == "zero": result = "0"
      else: result = random.randint(0, 100)
      embed = discord.Embed(color=self.bot.color, description=f"{user.mention} has `{result}` bitches")
      await ctx.reply(embed=embed)

    @commands.hybrid_command(description="sends a definition of a word", help="fun", usage="[word]")
    async def urban(self, ctx, *, word):
      embeds = []
      try:
       data = await self.bot.session.json("http://api.urbandictionary.com/v0/define", params={"term": word})
       defs = data["list"]
       for defi in defs: 
        e = discord.Embed(color=self.bot.color, description=defi["definition"], timestamp=dateutil.parser.parse(defi["written_on"]))
        e.set_author(name=word, url=defi["permalink"])
        e.add_field(name="example", value=defi["example"], inline=False) 
        e.set_footer(text=f"{defs.index(defi)+1}/{len(defs)}")
        embeds.append(e)
       return await ctx.paginator(embeds)
      except Exception as e: await ctx.reply("no definition found for **{}**".format(word))

    @commands.hybrid_command(description="send a random bird image", help="fun")
    async def bird(self, ctx): 
      data = await self.bot.session.json("https://api.alexflipnote.dev/birb")
      await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['file'])), filename="bird.png"))

    @commands.hybrid_command(description="send a random dog image", help="fun")
    async def dog(self, ctx):
        data = await self.bot.session.json("https://random.dog/woof.json")
        await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['url'])), filename=f"dog{data['url'][-4:]}"))

    @commands.hybrid_command(description="send a random cat image", help="fun")
    async def cat(self, ctx):
        data = (await self.bot.session.json("https://api.thecatapi.com/v1/images/search"))[0]
        await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['url'])), filename="cat.png"))
    
    @commands.hybrid_command(description="send a random capybara image", help="fun")
    async def capybara(self, ctx):
      data = await self.bot.session.json('https://api.capy.lol/v1/capybara?json=true')
      await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['data']['url'])), filename="cat.png"))
    
    @commands.hybrid_command(description="return an useless fact", help="fun", aliases=["fact", "uf"])
    async def uselessfact(self, ctx):
      data = (await self.bot.session.json("https://uselessfacts.jsph.pl/random.json?language=en"))['text']
      await ctx.reply(data) 

    @commands.hybrid_command(description="ask a question to ben", help="fun", usage="[question]")
    async def ben(self, ctx, *, question):   
     rand = ["./videos/benhoho.mp4", "./videos/benno.mp4", "./videos/benuhh.mp4", "./videos/benyes.mp4"]
     resp = random.choice(rand)
     await ctx.reply(content=f"*{question}*\nben's response - **{resp.replace('./videos/ben', '')[:-4]}**", file=discord.File(rf"{resp}"))

    @commands.hybrid_command(description="ship rate an user", help="fun", usage="[member]")
    async def ship(self, ctx, member: discord.Member):
     return await ctx.reply(f"**{ctx.author.name}** 💞 **{member.name}** = **{randrange(101)}%**")

    @commands.hybrid_command(description="say a message", help="fun", usage="[message]")
    async def say(self, ctx, *, arg):                    
     await ctx.message.delete()     
     view = discord.ui.View() 
     view.add_item(discord.ui.Button(label=f"said by {ctx.author}", disabled=True))
     await ctx.send(content=arg, view=view)

    @commands.hybrid_command(description="sends a random advice", help="fun")
    async def advice(self, ctx: commands.Context):
     byte = await self.bot.session.read("https://api.adviceslip.com/advice")
     data = str(byte, 'utf-8')
     data = data.replace("[", "").replace("]", "")
     js = json.loads(data) 
     return await ctx.reply(js['slip']['advice'])                              
    
    @commands.command(description="pack someone", help="fun", usage="[user]")
    async def pack(self, ctx: commands.Context, *, member: discord.Member): 
     if member == ctx.author: return await ctx.reply("Why do u wanna pack urself stupid boy?")
     await ctx.send(f"{member.mention} {random.choice(Pack.scripts)}") 

    @commands.hybrid_command(aliases=["ttt"], description="play tictactoe with your friends", help="fun", usage="[member]")
    async def tictactoe(self, ctx: commands.Context, *, member: discord.Member):
      if member is ctx.author: return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.author.mention}: You can't play with yourself. It's ridiculous"))
      if member.bot: return await ctx.reply("bots can't play")      
      embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** wants to play **tictactoe** with you. Do you accept?")
      style = discord.ButtonStyle.gray
      yes = discord.ui.Button(emoji=self.bot.yes, style=style)
      no = discord.ui.Button(emoji=self.bot.no, style=style)
      
      async def yes_callback(interaction: discord.Interaction): 
         if interaction.user != member:
           em = discord.Embed(color=self.bot.color, description=f"{self.bot.warning}: {interaction.user.mention} you are not the author of this embed")
           return await interaction.response.send_message(embed=em, ephemeral=True)
         vi = TicTacToe(ctx.author, member)
         await interaction.message.delete()
         vi.message = await ctx.send(content=f'Tic Tac Toe: **{ctx.author.name}** goes first', embed=None, view=vi)  
         
      async def no_callback(interaction: discord.Interaction): 
         if interaction.user != member:
           em = discord.Embed(color=self.bot.color, description=f"{self.bot.warning}: {interaction.user.mention} you are not the author of this embed")
           return await interaction.response.send_message(embed=em, ephemeral=True)
         await interaction.response.edit_message(embed=discord.Embed(color=self.bot.color, description=f"I'm sorry but **{interaction.user.name}** doesn't want to play with you right now"), view=None, content=ctx.author.mention)

      yes.callback = yes_callback
      no.callback = no_callback  
      view = discord.ui.View()
      view.add_item(yes)
      view.add_item(no)
      await ctx.send(embed=embed, view=view, content=member.mention) 

    @commands.hybrid_command(description="play blacktea with your friends", help="fun")
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
      
    @commands.hybrid_command(description="see how fast are you typing", help="fun")
    async def typerace(self, ctx: commands.Context):
     answer = await TypeRace.getanswer()
     mam = answer
     timer = 30 
     r = await self.bot.session.read("https://textoverimage.moesif.com/image", params={"image_url": "https://singlecolorimage.com/get/18191c/600x300", "text": answer, "text_color": "f2f1f4ff", "text_size": "32", "y_align": "middle", "x_align": "center"})
     await ctx.reply(content="You have to type the following text in **30 seconds**", file=discord.File(BytesIO(r)), filename="text.png")
     startTime = time.time()
     
     def is_correct(msg): 
        return msg.author == ctx.author

     try: guess = await self.bot.wait_for('message', check=is_correct, timeout=timer)
     except asyncio.TimeoutError: return await ctx.reply(embed=discord.Embed(color=self.bot.color, description="🙁 {} you took too long to reply".format(ctx.author.mention))) 
    
     if guess.content == mam: 
        fintime = time.time()
        total = fintime - startTime
        embed = discord.Embed(color=self.bot.color, title="Congratulations!", description=f"You typed the message perfectly (100% accuracy) in {total:.2f} seconds")
        return await guess.reply(embed=embed)
     else: 
      fintime = time.time()
      total = fintime - startTime  
      embed = discord.Embed(color=self.bot.color, description="You typed the sentence in **{}** seconds with an accuracy of **{}%**".format(f"{total:.2f}", TypeRace.accurate(guess.content, mam)))
      return await guess.reply(embed=embed)

    @commands.hybrid_command(description="returns a random bible versse", help="fun")
    async def bible(self, ctx: commands.Context): 
       byte = await self.bot.session.read("https://labs.bible.org/api/?passage=random&type=json")
       data = str(byte, 'utf-8')
       data = data.replace("[", "").replace("]", "")
       bible = json.loads(data) 
       embed = discord.Embed(color=self.bot.color, description=bible["text"]).set_author(name="{} {}:{}".format(bible["bookname"], bible["chapter"], bible["verse"]), icon_url="https://imgs.search.brave.com/gQ1kfK0nmHlQe2XrFIoLH9vtFloO3HRTDaCwY5oc0Ow/rs:fit:1200:960:1/g:ce/aHR0cDovL3d3dy5w/dWJsaWNkb21haW5w/aWN0dXJlcy5uZXQv/cGljdHVyZXMvMTAw/MDAvdmVsa2EvNzU3/LTEyMzI5MDY0MTlC/MkdwLmpwZw") 
       await ctx.reply(embed=embed)

    @commands.hybrid_command(name="8ball", description="answers to your question", usage="[question]", help="fun")
    async def mtball(self, ctx: commands.Context, *, arg):      
     rand = ['**Yes**', '**No**', '**definitely yes**', '**Of course not**', '**Maybe**', '**Never**', '**Yes, dummy**', '**No wtf**']
     e = discord.Embed(color=self.bot.color, description=f"You asked: {arg}\nAnswer: {random.choice(rand)}")
     await ctx.reply(embed=e)
  
    @commands.hybrid_command(help='fun', description="send a tweet image", usage="[messsage]")
    async def tweet(self, ctx: commands.Context, *, comment: str):
     r = await self.bot.session.read("https://some-random-api.ml/canvas/youtube-comment?", params={"username": str(ctx.author), "displayname": ctx.author.name, "comment": comment, "avatar": ctx.author.display_avatar.url})
     return await ctx.reply(file=discord.File(BytesIO(r), filename="tweet.png"))

    @commands.hybrid_command(help='fun', description="send an youtube comment image", usage="[messsage]")
    async def comment(self, ctx: commands.Context, *, comment: str):
     r = await self.bot.session.read("https://some-random-api.ml/canvas/youtube-comment?", params={"username": ctx.author.name, "comment": comment, "avatar": ctx.author.display_avatar.url})
     return await ctx.reply(file=discord.File(BytesIO(r), filename="comment.png"))

async def setup(bot) -> None:
    await bot.add_cog(fun(bot))        
