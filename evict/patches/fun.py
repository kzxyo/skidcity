import random, discord, aiohttp, datetime
from typing import List
from discord.ext import commands

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

    
class RockPaperScissors(discord.ui.View): 
  def __init__(self, ctx: commands.Context):
    self.ctx = ctx   
    self.get_emoji = {"rock": "🪨", "paper": "📰", "scissors": "✂️"} 
    self.status = False 
    super().__init__(timeout=10)

  async def action(self, interaction: discord.Interaction, selection: str): 
        if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.warning(interaction, "This is not your game", ephemeral=True)
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

    async def disable_buttons(self): 
        for item in self.children: 
            item.disabled = True 
        await self.message.edit(view=self)   
        
        
class MarryView(discord.ui.View): 
   def __init__(self, ctx: commands.Context, member: discord.Member): 
    super().__init__() 
    self.ctx = ctx 
    self.member = member
    self.status = False 

   @discord.ui.button(emoji="<:check:1083455835189022791>")
   async def yes(self, interaction: discord.Interaction, button: discord.ui.Button): 
    if interaction.user == self.ctx.author: return await interaction.client.ext.warning(interaction, "you can't accept your own marriage".capitalize(), ephemeral=True)
    elif interaction.user != self.member: return await self.ctx.bot.ext.warning(interaction, "you are not the author of this embed".capitalize(), ephemeral=True)
    else:   
      await interaction.client.db.execute("INSERT INTO marry VALUES ($1, $2, $3)", self.ctx.author.id, self.member.id, datetime.datetime.now().timestamp())                   
      embe = discord.Embed(color=interaction.client.color, description=f"<a:milk_love:1208459088069922937> **{self.ctx.author}** succesfully married with **{self.member}**")
      await interaction.response.edit_message(content=None, embed=embe, view=None)
      self.status = True              

   @discord.ui.button(emoji="<:stop:1083455877450834041>")
   async def no(self, interaction: discord.Interaction, button: discord.ui.Button): 
     if interaction.user == self.ctx.author: return await self.ctx.bot.ext.warning(interaction, "you can't reject your own marriage".capitalize(), ephemeral=True)
     elif interaction.user != self.member: return await self.ctx.bot.ext.warning(interaction, "you are not the author of this embed".capitalize(), ephemeral=True)
     else:                         
        embe = discord.Embed(color=interaction.client.color, description=f"**{self.ctx.author}** i'm sorry, but **{self.member}** is probably not the right person for you")
        await interaction.response.edit_message(content=None, embed=embe, view=None)
        self.status = True 
   
   async def on_timeout(self):
     if self.status == False:
      embed = discord.Embed(color=0xd3d3d3, description=f"**{self.member}** didn't reply in time :(")  
      try: await self.message.edit(content=None, embed=embed, view=None)  
      except: pass 

class DiaryModal(discord.ui.Modal, title="Create a diary page"): 
  titl = discord.ui.TextInput(label="Your diary title", placeholder="Give your diary page a short name", style=discord.TextStyle.short)
  text = discord.ui.TextInput(label="Your diary text", placeholder="Share your feelings or thoughts here", max_length=2000, style=discord.TextStyle.long)
  
  async def on_submit(self, interaction: discord.Interaction): 
   now = datetime.datetime.now()
   date = f"{now.month}/{now.day}/{str(now.year)[2:]}"
   await interaction.client.db.execute("INSERT INTO diary VALUES ($1,$2,$3,$4)", interaction.user.id, self.text.value, self.titl.value, date) 
   embed = discord.Embed(color=interaction.client.color, description=f"> {interaction.client.yes} {interaction.user.mention}: Added a diary page for today")
   return await interaction.response.edit_message(embed=embed, view=None)
  
  async def on_error(self, interaction: discord.Interaction, error: Exception): 
   embed = discord.Embed(color=interaction.client.color, description=f"> {interaction.client.no} {interaction.user.mention}: Unable to create the diary")
   return await interaction.response.edit_message(embed=embed, view=None) 
  
  
class Joint: 
 
  def check_joint():
   async def predicate(ctx: commands.Context): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
    if not check: await ctx.bot.ext.error(ctx, f"This server **doesn't** have a **joint**. Use `{ctx.clean_prefix}joint toggle` to get one")    
    return check is not None    
   return commands.check(predicate)
  
  def joint_owner(): 
   async def predicate(ctx: commands.Context): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
    if check["holder"] != ctx.author.id: await ctx.warning( f"You don't have the **joint**. Steal it from <@{check['holder']}>")
    return check["holder"] == ctx.author.id
   return commands.check(predicate) 

class Pack: 

  scripts = scripts = ["This nigga ugly as shit you fat ass boy you been getting flamed by two donkeys when you walk to the store and one of them smacked you in the forehead fuckboy and then you go to come in with uh ???? and smacked you in the bootycheeks fuckboy you dirty as shit boy everytime you go to school nigga you get bullied by 10 white kids that say you gay behind the bus fuckboy suck my dick nigga unknown as shit nigga named nud you been getting hit by two frozen packs when you walk into the store fuckboy suck my dick unknown ass nigga named nud nigga you my son nigga hold on, ay creedo you can flame this nigga for me? Yeah im in this bitch fuck is you saying nigga my nigga.",
             "Whether you wipe that shit or eat that shit pussy ass nigga , I'll slap you with a massaacho ٴًٰٰdancing leprechaun in your bum-hole like HotWheels driving in your ass nigga and coming out like angry birds when I fucked your mom so hard that she be getting a dead line for bad communication in a iphone 64 produced by a buzz cut in India. nigga what you talkin about , nigga you sound like you boutta order Big macs for my whole family and got sidefucked by john cena in a karate tournament . Bitch ass nigga whenever you talk ,you sound like a crowd of chinese dhar man people debating about 'Is god real? ' Like shut yo bitch ass nigga you got a bible to read out loud like you gonna get whip in the ass when you ordered a ice cream from pornhub dumb ass nigga , remember when you clogged the kid's mouth in the class playing ' I dare you to shit in my mouth for one thousand V bucks' gay ass nigga , whenever you sleep you got yourself into a situation where white kids throwing gang signs in their deathbed you pussy ass nigga kiss heads Abc optimus prime tv looking ass nigga you lame ass shit that's why you get no pussy from valentines dumb ass nigga wanna be rich boy small boy faggot card magic school bus in your mum pussy ass nigga",
             " kno ass aint talkin boy you look like a discombobulated toe nail nigga whenever you take a bath your jerk off then the next you smell like ass nasty nigga fuck is you saying nigga you got smacked with a gold fish in the grocery store and smacked the gold fish with fish food nasty bitch boy you ugly as shit fuck is you saying FAT BOY ugly bitch my nigga i caught yo ass slap boxing yo granny with an apple fuck is you saying my nigga when you get horny you jerk off to donkeys fuck is you saying ugly bitch",
             "Aight bruh shut ur dumbass up before i get to the packing on ur ass u nasty no neck built ass happy meal looking ass bvoy shut ur big booty ass up i caught ur dumbass cosplaying as ronald mcdonald till u got body slammed by a chicken nugget u nasty as boy after that u fell into a coma when u wake up u thought u was from lego ninja go u started saying ninja gooo u started smacking people on the streets with racoons till ur fatass got hungry u started eating them u said yea u got the yummy yuh yummy yuh ma yummy yuh u nasty ass boy cum in a bum cum in a son nasty ass bitch u bout dirty as shit boy i caught ur fatass in ur backyard belly dancing with cockroaches till u started dong the dream speedrun anthem they started speedrunning trying to kill the enderdragon u said minecraft was the best game in 2022 u enchanted ur body parts with efficiency 5 u became the fastest person on earth u started going on a big mac rampage eating every big mac u see fat neck built ass bitch u became depressed cus u got rejected 19 times in a row u got a charger and charged it into ur heart thinking it will fix ur depression like shit boy u thought u was michael jordan u started slamming basketballs into ur grandmas pussy u dirty ass bitch",
             "shut yo ugly dumb ass up nigga thats why your grandma got caught throwing up gang signs because she thought it was sign language and got shot 19 times in the back ugly neck ass boy thats why your dad shoves cartons of milk up his ass infront of the chuck e cheese while screaming the lyrics to gummibar bozo ass nigga yo mom blackmails miley cirus while shoving turkey in her mouth like she is eating dick stupid ass nigga",
             "Ugly ass shit yo weak Hang your self with a noose fatass cow go run it through ur emo fruit ninja wrists my guy. You ugly tell your grandma mighty fine i might hit her from behind and make her whine bitch ass hush mode. Theres a stutter thats why u aint got no mother tell me why you got one foot longer then the other you dumbass mf mf retarded ass fag your 10 stfu im not a hoe you little ass slut. now dont be disrespectful whore.your mom violated your shit by nameing you (whatever their name is) and i did too. ill get down with you fagShut your lil stoopid ass talking abt my father left but ik ur not talking like ur father didnt get hit in his megamind forehead by a 40 guacamole rocket launcher by bro hold shit roman ranges finna slap u that why nobody likes u. ",
             "now im bout to get the packing on yo stuff boi u look like a zestful squirrel monkey black ah boi u look like you chew on diceratop ankles bitch ah boi yo momma built like an overweight camel fat ah momma i bet she chew on obnoxious tampons with her fat ah and i caught yo grandpa chewing on corkscrews dumb ah boi tell me why i caught yo ass chewing on coordinated tin can with yo fat ah boi u look like a rambunctious sea slime with yo stupid ah",
             "fucking autistic round head ass looking like a stickman, your profession is being a fucking donkey you fucking hipster, you look like a crackhead, when you turn to your side you dissapear like a magician you fucking scrawny little toe sucking cow shit mauling hunchback looking retard, i hope you get attacked by 67 rapid pitbulls while you walk home from school next week you fucking bitch ass camel, your sense of humor is worser than Drew Ackerman's, boring ass emo kid, your hairy is more greasy and tangly than a fucking street cat you rabbit ass cowboy looking motherfucker",
             "shut yo wiggly diggly spliggy fliggly diggity ass up my nigga you rented a u-haul truck just to drive to Jamaica and order a whopper from mcdonalds and then your life went to shit because you got ran over be a semi truck fucked three times in the ass hole by the tellitubies dumb ass boi you thought you could eat fucking gasoline and get high fat ass magic mushroom looking ass boi fuck up bro i shoved monster energy in your ass hole and you dark a whole bottle of laxatives' to get that shit out fat ass nigga",
             "boy you ugly as shit boy you fat bitch you are built like a transformers and your neck got dunked on by micheal jordan dumbass bitch your grandma started twerking on a fucking chair till your grandpa hit her off it fat ass boy you look like a racoon that started crawling out of a toilet you fat bitch",
             "Lick up sick up u mf monkey ass shi u horny nigga horse putin ur long dick between ur butts u fuckin dumb fuck boy ur two pairs of butts in ur head instead being ur brian in ur ass u fookin black monkey nigga ass shi u fuck boy ur mum get fucked inna hub from a group of black dick niggas go on the top n don stop n do a bunny hop go n fuck ur hoe nigga fake mandem pussyo blud",
             "shut yo stupid ass up you goofy ass nigga you used a fan to wipe ur ass meanwhile getting anally raped by 2 singing socks stop playing with me you look like you play basketball with a discombobulated doorknob that has aids you goofy ass bitch you used a tree to cut down an axe you dumbfuck you look like you have a bear with extra chromosome in ur backyard attacking 5 bees having oral sex with each other with baseball bats shut the fuck up you dirty as hell you thought a thesaurus was a fucking dinosaur you stupid ass nigga stop playing with me you started doing 360 backflips while having explosive diarrhea you dirty as hell boy you use a knife as a fucking sex toy dumbass bitch if you don't shut yo tangerine mr clean I agree I just cut down a tree I need this key you stupid ass bitch you thought deodorant was a ice cream bar you stupid ass bitch you bowl with a coconut you dumbass bitch",
             "Bro shut the fuck up you look like a dehydrated frog on cocaine boy a new shiny sex toy bro you suck 4 white cocks and got beat the shit out of boy you be getting thrashed on Fortnite Dying Light bitch ass lookin ass yo parets be disowning you just for your existence boy you look like the she said she was twelve crusty rusty dusty ass shelve boy what da hell satan kicked you outta hell for smelling like dayum Hersheys musty cheesy wheezy queezy pack o' chips bru you got stung by a scorpion and was admitted to a mental hospital cus yo toes look like an arrow I could shoot lasers out of PEW PEW PEW PEW PEW!"]