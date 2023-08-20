import discord, io, random, asyncio, aiohttp
from discord.ext import commands
from typing import List
from io import BytesIO

class BlackTea:
    """Backend variables for BlackTea"""
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
            if interaction.user != self.player1: return await interaction.client.ext.send_warning(interaction, "You cannot interact with this", ephemeral=True)
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now **{self.player2.name}**'s turn"
        else:
            if interaction.user != self.player2: return await interaction.client.ext.send_warning(interaction, "You cannot interact with this", ephemeral=True)
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now **{self.player1.name}**'s turn"
        
        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f"**{self.player1.name}** won!"
            elif winner == view.O:
                content = "**{}** won!".format(self.player2.name)
            else:
                content = "Its a **tie**!"
            
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

class fun(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @commands.command(description="pack a member", help="fun", usage="[member]")
    async def pack(self, ctx: commands.Context, member: discord.Member):
        data = await self.bot.session.json("https://evilinsult.com/generate_insult.php?lang=en&type=json")
        await ctx.send(f"{member.mention} {data['insult']}")
    
    @commands.command(name="no", description="just says yes", help="fun")
    async def no_cmd(self, ctx: commands.Context): 
     await ctx.reply("yes") 
    
    @commands.command(name="yes", description="just says no", help="fun")
    async def yes_cmd(self, ctx: commands.Context): 
     await ctx.reply("no") 
    
    @commands.command(description="send a random dog image", help="fun")
    async def dog(self, ctx):
        data = await self.bot.session.json("https://random.dog/woof.json")
        await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['url'])), filename=f"dog{data['url'][-4:]}"))

    @commands.command(description="send a random cat image", help="fun")
    async def cat(self, ctx):
        data = (await self.bot.session.json("https://api.thecatapi.com/v1/images/search"))[0]
        await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['url'])), filename="cat.png"))
    
    @commands.command(description="send a random bird image", help="fun")
    async def bird(self, ctx): 
      data = await self.bot.session.json("https://api.alexflipnote.dev/birb")
      await ctx.reply(file=discord.File(fp=BytesIO(await self.bot.session.read(data['file'])), filename="bird.png"))
    
    @commands.command(description="say a message", help="fun", usage="[message]")
    async def say(self, ctx, *, msg):
        await ctx.message.delete()
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"said by {ctx.author}", disabled=True))
        await ctx.send(content=msg, view=view)
    
    @commands.command(name="choose", description="choose between multiple options", help="fun", usage="[choices]\nexample: ;choose apple, samsung, lg")
    async def choose_mt(self, ctx: commands.Context, *, choice: str):
        choices = choice.split(",")
        if len(choices) == 1: return await ctx.reply("put a ',' between your choices")
        await ctx.reply(content=f"{random.choice(choices)}")
    
    @commands.command(aliases=["ttt"], description="play tictactoe with a friend", help="fun", usage="[member]")
    async def tictactoe(self, ctx: commands.Context, *, member: discord.Member):
      #if member is ctx.author: return await ctx.reply("you can't play with yourself")
      if member.bot: return await ctx.reply("bots can't play games")      
      embed = discord.Embed(color=self.bot.color, description=f"**{ctx.author.name}** wants to play **tictactoe** with you, do you accept?")
      style = discord.ButtonStyle.gray
      yes = discord.ui.Button(emoji=self.bot.yes, style=style)
      no = discord.ui.Button(emoji=self.bot.no, style=style)
      
      async def yes_callback(interaction: discord.Interaction): 
         if interaction.user != member:
           em = discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {interaction.user.mention}: You are not the author of this embed")
           return await interaction.response.send_message(embed=em, ephemeral=True)
         vi = TicTacToe(ctx.author, member)
         await interaction.message.delete()
         vi.message = await ctx.send(content=f'Its **{ctx.author.name}** turn', embed=None, view=vi)  
         
      async def no_callback(interaction: discord.Interaction): 
         if interaction.user != member:
           em = discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {interaction.user.mention}: You are not the author of this embed")
           return await interaction.response.send_message(embed=em, ephemeral=True)
         await interaction.response.edit_message(f"Looks like **{interaction.user.name}** doesn't want to play tictactoe right now", view=None, content=ctx.author.mention)

      yes.callback = yes_callback
      no.callback = no_callback  
      view = discord.ui.View()
      view.add_item(yes)
      view.add_item(no)
      await ctx.send(embed=embed, view=view, content=member.mention) 
    
    @commands.command(description="sends a definition of a word", help="fun", usage="[word]")
    async def urban(self, ctx, *, word):
      embeds = []
      try:
       data = await self.bot.session.json("http://api.urbandictionary.com/v0/define", params={"term": word})
       defs = data["list"]
       for defi in defs: 
        e = discord.Embed(color=self.bot.color, description=defi["definition"], timestamp=dateutil.parser.parse(defi["written_on"]))
        #e.set_author(name=word, url=defi["permalink"])
        e.add_field(name="example", value=defi["example"], inline=False) 
        e.set_footer(text=f"{defs.index(defi)+1}/{len(defs)}")
        embeds.append(e)
       return await ctx.paginator(embeds)
      except Exception as e: await ctx.send_warning("No definition found for **{}**".format(word))
    
    @commands.command(name="8ball", description="answers to your question", usage="[question]", help="fun")
    async def mtball(self, ctx: commands.Context, *, arg):      
     rand = ['**Yes**', '**No**', '**definitely yes**', '**Of course not**', '**Maybe**', '**Never**', '**Yes, dummy**', '**No wtf**']
     e = discord.Embed(color=self.bot.color, description=f"Question: {arg}\nAnswer: {random.choice(rand)}")
     await ctx.reply(embed=e)
    
    @commands.command(description="ask a question to ben", help="fun", usage="[question]")
    async def ben(self, ctx, *, question):   
     rand = ["./tools/videos/benhoho.mp4", "./tools/videos/benno.mp4", "./tools/videos/benuhh.mp4", "./tools/videos/benyes.mp4"]
     resp = random.choice(rand)
     await ctx.reply(file=discord.File(rf"{resp}"))
    
    @commands.command(description="check how many bitches an user has", help="fun", usage="<member>")
    async def bitches(self, ctx: commands.Context, *, user: discord.Member=commands.Author):
      choices = ["regular", "still regular", "lol", "xd", "id", "zero", "infinite"]
      if random.choice(choices) == "infinite": result = "∞" 
      elif random.choice(choices) == "zero": result = "0"
      else: result = random.randint(0, 100)
      await ctx.send_neutral(f"{user.mention} has `{result}` bitches")
    
    @commands.command(description="play blacktea with your friends", help="fun")
    async def blacktea(self, ctx: commands.Context):
     try:
      if BlackTea.MatchStart[ctx.guild.id] is True:
       return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.author.mention}: Someone is already playing blacktea in this server"))
     except KeyError: pass
    
     BlackTea.MatchStart[ctx.guild.id] = True
     embed = discord.Embed(color=self.bot.color, title="BlackTea MatchMaking", description="- Press 🍵 to join\n- Game starts in 20 seconds\n- The game need at least 2 players to start\n- Every player has 3 lifes\n- Say a word with the given letters")
     embed.set_author(name=ctx.author.global_name if ctx.author.global_name else ctx.author.name, icon_url=ctx.author.display_avatar.url)
     mes = await ctx.send(embed=embed)
     await mes.add_reaction("🍵")
     await asyncio.sleep(20)
     me = await ctx.channel.fetch_message(mes.id)
     players = [user.id async for user in me.reactions[0].users()]
     #players.remove(self.bot.user.id)
     
     if len(players) < 2:
      BlackTea.MatchStart[ctx.guild.id] = False
      return await ctx.send(embed=discord.Embed(color=self.bot.color, description="😦 {}, not enough players joined to start blacktea".format(ctx.author.mention)), allowed_mentions=discord.AllowedMentions(users=True))
     
     while len(players) > 1:
      for player in players:
       strin = await BlackTea.get_string()
       await ctx.send(embed=discord.Embed(color=self.bot.color, description=f"⏰ <@{player}>, type a word containing **{strin.upper()}** in **10 seconds**"))

       def is_correct(msg):
        return msg.author.id == player
     
       try:
        message = await self.bot.wait_for('message', timeout=10, check=is_correct)
       except asyncio.TimeoutError:
          try:
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1
            if BlackTea.lifes[player] == 3:
              await ctx.send(embed=discord.Embed(color=self.bot.color, description=f"☠ <@{player}>, you are eliminated"))
              BlackTea.lifes[player] = 0
              players.remove(player)
              continue
          except KeyError:
            BlackTea.lifes[player] = 0
          await ctx.send(embed=discord.Embed(color=self.bot.color, description=f"💥 <@{player}>, you didn't reply on time! **{2-BlackTea.lifes[player]}** lifes remaining"))
          continue
       i=0
       for word in await BlackTea.get_words():
         if strin.lower() in message.content.lower() and word.lower() in message.content.lower():
            i=1
            pass
       if i == 0:
          try:
            BlackTea.lifes[player] = BlackTea.lifes[player] + 1
            if BlackTea.lifes[player] == 3:
              await ctx.send(embed=discord.Embed(color=self.bot.color, description=f"☠ <@{player}>, you are eliminated"))
              BlackTea.lifes[player] = 0
              players.remove(player)
              continue
          except KeyError:
            BlackTea.lifes[player] = 0
          await ctx.send(embed=discord.Embed(color=self.bot.color, description=f"💥 <@{player}>, incorrect word! **{2-BlackTea.lifes[player]}** remaining"))
       else: 
         await message.add_reaction("✅")
         i=0
      
     await ctx.send(embed=discord.Embed(color=self.bot.color, description=f"👑 <@{players[0]}> won the game"))
     BlackTea.lifes[players[0]] = 0
     BlackTea.MatchStart[ctx.guild.id] = False
    
async def setup(bot):
    await bot.add_cog(fun(bot))