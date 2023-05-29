
import sys, os, discord
from discord.ext import commands
from typing import Union

class GoodRole(commands.Converter):
  async def convert(self, ctx: commands.Context, argument): 
    try: role = await commands.RoleConverter().convert(ctx, argument)
    except commands.BadArgument: role = discord.utils.get(ctx.guild.roles, name=argument) 
    if role is None: 
      role = ctx.find_role(argument)
      if role is None: raise commands.BadArgument(f"No role called **{argument}** found") 
    if role.position >= ctx.guild.me.top_role.position: raise commands.BadArgument("This role cannot be managed by the bot") 
    if ctx.author.id == ctx.guild.owner_id: return role 
    if role.position >= ctx.author.top_role.position: raise commands.BadArgument(f"You cannot manage this role")
    return role

class NoStaff(commands.Converter): 
  async def convert(self, ctx: commands.Context, argument): 
    try: member = await commands.MemberConverter().convert(ctx, argument)
    except commands.BadArgument: member = discord.utils.get(ctx.guild.members, name=argument)
    if member is None: raise commands.BadArgument(f"No member called **{argument}** found")  
    if member.id == ctx.guild.me.id: raise commands.BadArgument("leave me alone <:mmangry:1081633006923546684>") 
    if member.top_role.position >= ctx.guild.me.top_role.position: raise commands.BadArgument(f"The bot cannot execute the command on **{member}**") 
    if ctx.author.id == ctx.guild.owner_id: return member
    if member.top_role.position >= ctx.author.top_role.position or member.id == ctx.guild.owner_id: raise commands.BadArgument(f"You cannot use this command on **{member}**") 
    return member

class Whitelist: 
  async def whitelist_things(ctx: commands.Context, module: str, target: Union[discord.Member, discord.User, discord.TextChannel]): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    if check: return await ctx.send_warning( f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is **already** whitelisted for **{module}**")
    await ctx.bot.db.execute("INSERT INTO whitelist VALUES ($1,$2,$3,$4)", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    return await ctx.send_success(f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is now whitelisted for **{module}**")

  async def unwhitelist_things(ctx: commands.Context, module: str, target: Union[discord.Member, discord.TextChannel]): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    if not check: return await ctx.send_warning( f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is **not** whitelisted from **{module}**")
    await ctx.bot.db.execute("DELETE FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    return await ctx.send_success(f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is now unwhitelisted from **{module}**")

  async def whitelisted_things(ctx: commands.Context, module: str, target: str): 
   i=0
   k=1
   l=0
   mes = ""
   number = []
   messages = []  
   results = await ctx.bot.db.fetch("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND mode = $3", ctx.guild.id, module, target)
   if len(results) == 0: return await ctx.send_warning( f"No whitelisted **{target}s** found for **{module}**")  
   for result in results:
    id = result['object_id'] 
    if target == "channel": mes = f"{mes}`{k}` {f'{ctx.guild.get_channel(id).mention} ({id})' if ctx.guild.get_channel(result['object_id']) is not None else result['object_id']}\n"
    else: mes = f"{mes} `{k}` {await ctx.bot.fetch_user(id)} ({id})\n"
    k+=1
    l+=1
    if l == 10:
     messages.append(mes)
     number.append(discord.Embed(color=ctx.bot.color, title=f"whitelisted {target}s ({len(results)})", description=messages[i]))
     i+=1
     mes = ""
     l=0
    
   messages.append(mes)  
   number.append(discord.Embed(color=ctx.bot.color, title=f"whitelisted {target}s ({len(results)})", description=messages[i]))
   await ctx.paginator(number)

class InvokeClass:
 
 async def invoke_send(ctx: commands.Context, member: Union[discord.User, discord.Member], reason: str): 
  res = await ctx.bot.db.fetchrow("SELECT embed FROM invoke WHERE guild_id = $1 AND command = $2", ctx.guild.id, ctx.command.name)
  if res: 
     code = res['embed']
     try: 
      x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(member, InvokeClass.invoke_replacement(member, code.replace("{reason}", reason))))
      await ctx.reply(content=x[0], embed=x[1], view=x[2])
     except: await ctx.reply(EmbedBuilder.embed_replacement(member, InvokeClass.invoke_replacement(member, code.replace("{reason}", reason)))) 
     return True 
  return False   
 
 def invoke_replacement(member: Union[discord.Member, discord.User], params: str=None):
  if params is None: return None
  if '{member}' in params: params=params.replace("{member}", str(member))
  if '{member.id}' in params: params=params.replace('{member.id}', str(member.id))
  if '{member.name}' in params: params=params.replace('{member.name}', member.name)
  if '{member.mention}' in params: params=params.replace('{member.mention}', member.mention)
  if '{member.discriminator}' in params: params=params.replace('{member.discriminator}', member.discriminator)
  if '{member.avatar}' in params: params=params.replace('{member.avatar}', member.display_avatar.url)
  return params

 async def invoke_cmds(ctx: commands.Context, member: Union[discord.Member, discord.User], embed: str) -> discord.Message:
  res = await ctx.bot.db.fetchrow("SELECT embed FROM invoke WHERE guild_id = $1 AND command = $2", ctx.guild.id, ctx.command.name)
  if res:
   code = res['embed']    
   if embed == "none": 
    await ctx.bot.db.execute("DELETE FROM invoke WHERE guild_id = $1 AND command = $2", ctx.guild.id, ctx.command.name)
    return await ctx.send_success( f"Deleted the **{ctx.command.name}** custom response")
   elif embed == "view": 
    em = discord.Embed(color=ctx.bot.color, title=f"invoke {ctx.command.name} message", description=f"```{code}```")
    return await ctx.reply(embed=em)
   elif embed == code: return await ctx.send_warning( f"This embed is already **configured** as the {ctx.command.name} custom response")
   else:
      await ctx.bot.db.execute("UPDATE invoke SET embed = $1 WHERE guild_id = $2 AND command = $3", embed, ctx.guild.id, ctx.command.name)
      return await ctx.send_success( f"Updated your custom **{ctx.command.name}** message to {'the embed' if '--embed' in embed else ''}\n```{embed}```")
  else: 
   await ctx.bot.db.execute("INSERT INTO invoke VALUES ($1,$2,$3)", ctx.guild.id, ctx.command.name, embed)
   return await ctx.send_success( f"Added your custom **{ctx.command.name}** message to {'the embed' if '--embed' in embed else ''}\n```{embed}```")

class EmbedBuilder:
 def ordinal(self, num: int) -> str:
   """Convert from number to ordinal (10 - 10th)""" 
   numb = str(num) 
   if numb.startswith("0"): numb = numb.strip('0')
   if numb in ["11", "12", "13"]: return numb + "th"
   if numb.endswith("1"): return numb + "st"
   elif numb.endswith("2"):  return numb + "nd"
   elif numb.endswith("3"): return numb + "rd"
   else: return numb + "th"    

 def get_parts(params):
    params=params.replace('{embed}', '')
    return [p[1:][:-1] for p in params.split('$v')]

 def embed_replacement(user: discord.Member, params: str=None):
    if params is None: return None
    if '{user}' in params:
        params=params.replace('{user}', str(user.name) + "#" + str(user.discriminator))
    if '{user.mention}' in params:
        params=params.replace('{user.mention}', user.mention)
    if '{user.name}' in params:
        params=params.replace('{user.name}', user.name)
    if '{user.avatar}' in params:
        params=params.replace('{user.avatar}', str(user.display_avatar.url))
    if '{user.joined_at}' in params:
        params=params.replace('{user.joined_at}', discord.utils.format_dt(user.joined_at, style='R'))
    if '{user.created_at}' in params:
        params=params.replace('{user.created_at}', discord.utils.format_dt(user.created_at, style='R'))
    if '{user.discriminator}' in params:
        params=params.replace('{user.discriminator}', user.discriminator)
    if '{guild.name}' in params:
        params=params.replace('{guild.name}', user.guild.name)
    if '{guild.count}' in params:
        params=params.replace('{guild.count}', str(user.guild.member_count))
    if '{guild.count.format}' in params:
        params=params.replace('{guild.count.format}', EmbedBuilder.ordinal(len(user.guild.members)))
    if '{guild.id}' in params:
        params=params.replace('{guild.id}', user.guild.id)
    if '{guild.created_at}' in params:
        params=params.replace('{guild.created_at}', discord.utils.format_dt(user.guild.created_at, style='R'))
    if '{guild.boost_count}' in params:
        params=params.replace('{guild.boost_count}', str(user.guild.premium_subscription_count))
    if '{guild.booster_count}' in params:
        params=params.replace('{guild.booster_count}', str(len(user.guild.premium_subscribers)))
    if '{guild.boost_count.format}' in params:
        params=params.replace('{guild.boost_count.format}', EmbedBuilder.ordinal(user.guild.premium_subscription_count))
    if '{guild.booster_count.format}' in params:
        params=params.replace('{guild.booster_count.format}', EmbedBuilder.ordinal(len(user.guild.premium_subscribers)))
    if '{guild.boost_tier}' in params:
        params=params.replace('{guild.boost_tier}', str(user.guild.premium_tier))
    if '{guild.vanity}' in params: 
        params=params.replace('{guild.vanity}', "/" + user.guild.vanity_url_code or "none")         
    if '{invisible}' in params: 
        params=params.replace('{invisible}', '2f3136') 
    if '{botcolor}' in params: 
        params=params.replace('{botcolor}', '6d827d')       
    if '{guild.icon}' in params:
      if user.guild.icon:
        params=params.replace('{guild.icon}', user.guild.icon.url)
      else: 
        params=params.replace('{guild.icon}', "https://none.none")        

    return params

 async def to_object(params):

    x={}
    fields=[]
    content=None
    view=discord.ui.View()

    for part in EmbedBuilder.get_parts(params):
        
        if part.startswith('content:'):
            content=part[len('content:'):]

        if part.startswith('title:'):
            x['title']=part[len('title:'):]
        
        if part.startswith('description:'):
            x['description']=part[len('description:'):]

        if part.startswith('color:'):
            try:
                x['color']=int(part[len('color:'):].replace("#", ""), 16)
            except:
                x['color']=0x2f3136

        if part.startswith('image:'):
            x['image']={'url': part[len('image:'):]}

        if part.startswith('thumbnail:'):
            x['thumbnail']={'url': part[len('thumbnail:'):]}
        
        if part.startswith('author:'):
            z=part[len('author:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            try:
                url=z[2] if z[2] else None
            except:
                url=None

            x['author']={'name': name}
            if icon_url:
                x['author']['icon_url']=icon_url
            if url:
                x['author']['url']=url

        if part.startswith('field:'):
            z=part[len('field:'):].split(' && ')
            try:
                name=z[0] if z[0] else None
            except:
                name=None
            try:
                value=z[1] if z[1] else None
            except:
                value=None
            try:
                inline=z[2] if z[2] else True
            except:
                inline=True

            if isinstance(inline, str):
                if inline == 'true':
                    inline=True

                elif inline == 'false':
                    inline=False

            fields.append({'name': name, 'value': value, 'inline': inline})

        if part.startswith('footer:'):
            z=part[len('footer:'):].split(' && ')
            try:
                text=z[0] if z[0] else None
            except:
                text=None
            try:
                icon_url=z[1] if z[1] else None
            except:
                icon_url=None
            x['footer']={'text': text}
            if icon_url:
                x['footer']['icon_url']=icon_url
                
        if part.startswith('button:'):
            z=part[len('button:'):].split(' && ')
            disabled=True
            style=discord.ButtonStyle.gray
            emoji=None 
            label=None 
            url=None
            for m in z:
             if "label:" in m: label=m.replace("label:", "")
             if "url:" in m: 
                url=m.replace("url:", "").strip()
                disabled=False
             if "emoji:" in m: emoji=m.replace("emoji:", "").strip()
             if "disabled" in m: disabled=True     
             if "style:" in m: 
               if m.replace("style:", "").strip() == "red": style=discord.ButtonStyle.red 
               elif m.replace("style:", "").strip() == "green": style=discord.ButtonStyle.green 
               elif m.replace("style:", "").strip() == "gray": style=discord.ButtonStyle.gray 
               elif m.replace("style:", "").strip() == "blue": style=discord.ButtonStyle.blurple   

            view.add_item(discord.ui.Button(style=style, label=label, emoji=emoji, url=url, disabled=disabled))
            
    if not x: embed=None
    else:
        x['fields']=fields
        embed=discord.Embed.from_dict(x)
    return content, embed, view 

class EmbedScript(commands.Converter): 
  async def convert(self, ctx: commands.Context, argument: str):
   x = await EmbedBuilder.to_object(EmbedBuilder.embed_replacement(ctx.author, argument))
   if x[0] or x[1]: return {"content": x[0], "embed": x[1], "view": x[2]} 
   return {"content": EmbedBuilder.embed_replacement(ctx.author, argument)}

class GoToModal(discord.ui.Modal, title="change the page"):
  page = discord.ui.TextInput(label="page", placeholder="change the page", max_length=3)

  async def on_submit(self, interaction: discord.Interaction) -> None:
   if int(self.page.value) > len(self.embeds): return await interaction.client.ext.send_warning(interaction, f"You can only select a page **between** 1 and {len(self.embeds)}", ephemeral=True) 
   await interaction.response.edit_message(embed=self.embeds[int(self.page.value)-1]) 
  
  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: 
    await interaction.client.ext.send_warning(interaction, "Unable to change the page", ephemeral=True)

class PaginatorView(discord.ui.View): 
    def __init__(self, ctx: commands.Context, embeds: list): 
      super().__init__()  
      self.embeds = embeds
      self.ctx = ctx
      self.i = 0

    @discord.ui.button(emoji="<:left:1018156480991612999>", style=discord.ButtonStyle.blurple)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")          
      if self.i == 0: 
        await interaction.response.edit_message(embed=self.embeds[-1])
        self.i = len(self.embeds)-1
        return
      self.i = self.i-1
      return await interaction.response.edit_message(embed=self.embeds[self.i])

    @discord.ui.button(emoji="<:right:1018156484170883154>", style=discord.ButtonStyle.blurple)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")     
      if self.i == len(self.embeds)-1: 
        await interaction.response.edit_message(embed=self.embeds[0])
        self.i = 0
        return 
      self.i = self.i + 1  
      return await interaction.response.edit_message(embed=self.embeds[self.i])   
 
    @discord.ui.button(emoji="<:filter:1039235211789078628>")
    async def goto(self, interaction: discord.Interaction, button: discord.ui.Button): 
     if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")     
     modal = GoToModal()
     modal.embeds = self.embeds
     await interaction.response.send_modal(modal)
     await modal.wait()
     try:
      self.i = int(modal.page.value)-1
     except: pass 
    
    @discord.ui.button(emoji="<:stop:1018156487232720907>", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed")     
      await interaction.message.delete()

    async def on_timeout(self) -> None: 
        mes = await self.message.channel.fetch_message(self.message.id)
        if mes is None: return
        if len(mes.components) == 0: return
        for item in self.children:
            item.disabled = True

        try: await self.message.edit(view=self)   
        except: pass

class Pack: 

  scripts = ["This nigga ugly as shit you fat ass boy you been getting flamed by two donkeys when you walk to the store and one of them smacked you in the forehead fuckboy and then you go to come in with uh ???? and smacked you in the bootycheeks fuckboy you dirty as shit boy everytime you go to school nigga you get bullied by 10 white kids that say you gay behind the bus fuckboy suck my dick nigga unknown as shit nigga named nud you been getting hit by two frozen packs when you walk into the store fuckboy suck my dick unknown ass nigga named nud nigga you my son nigga hold on, ay creedo you can flame this nigga for me? Yeah im in this bitch fuck is you saying nigga my nigga.",
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

class StartUp:

 async def startup(bot):
    await bot.wait_until_ready()
    await bot.tree.sync()
    print('Sucessfully synced applications commands')

 async def loadcogs(self): 
  for file in os.listdir("./events"): 
   if file.endswith(".py"):
    try:
     await self.load_extension(f"events.{file[:-3]}")
     print(f"Loaded plugin {file[:-3]}".lower())
    except Exception as e: print("failed to load %s %s".lower(), file[:-3], e)
  for fil in os.listdir("./cogs"):
   if fil.endswith(".py"):
    try:
     await self.load_extension(f"cogs.{fil[:-3]}")
     print(f"Loaded plugin {fil[:-3]}".lower())
    except Exception as e: print("failed to load %s %s".lower(), fil[:-3], e)

 async def identify(self):
    payload = {
        'op': self.IDENTIFY,
        'd': {
            'token': self.token,
            'properties': {
                '$os': sys.platform,
                '$browser': 'Discord iOS',
                '$device': 'Discord iOS',
                '$referrer': '',
                '$referring_domain': ''
            },
            'compress': True,
            'large_threshold': 250,
            'v': 3
        }
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload['d']['presence'] = {
            'status': state._status,
            'game': state._activity,
            'since': 0,
            'afk': False
        }

    if state._intents is not None:
        payload['d']['intents'] = state._intents.value

    await self.call_hooks('before_identify', self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)

async def create_db(self: commands.AutoShardedBot): 
  await self.db.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id BIGINT, prefix TEXT)")  
  await self.db.execute("CREATE TABLE IF NOT EXISTS selfprefix (user_id BIGINT, prefix TEXT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS nodata (user_id BIGINT, state TEXT)")       
  await self.db.execute("CREATE TABLE IF NOT EXISTS snipe (guild_id BIGINT, channel_id BIGINT, author TEXT, content TEXT, attachment TEXT, avatar TEXT, time TIMESTAMPTZ)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS afk (guild_id BIGINT, user_id BIGINT, reason TEXT, time INTEGER);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS voicemaster (guild_id BIGINT, channel_id BIGINT, interface BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS vcs (user_id BIGINT, voice BIGINT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS fake_permissions (guild_id BIGINT, role_id BIGINT, permissions TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS confess (guild_id BIGINT, channel_id BIGINT, confession INTEGER);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS authorize (guild_id BIGINT, buyer BIGINT, tags TEXT, transfers INTEGER, boosted TEXT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS marry (author BIGINT, soulmate BIGINT, time INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS mediaonly (guild_id BIGINT, channel_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS tickets (guild_id BIGINT, message TEXT, channel_id BIGINT, category BIGINT, color INTEGER, logs BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS opened_tickets (guild_id BIGINT, channel_id BIGINT, user_id BIGINT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS ticket_topics (guild_id BIGINT, name TEXT, description TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS pingonjoin (channel_id BIGINT, guild_id BIGINT);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS autorole (role_id BIGINT, guild_id BIGINT);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS levels (guild_id BIGINT, author_id BIGINT, exp INTEGER, level INTEGER, total_xp INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS levelsetup (guild_id BIGINT, channel_id BIGINT, destination TEXT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS levelroles (guild_id BIGINT, level INTEGER, role_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS oldusernames (username TEXT, discriminator TEXT, time INTEGER, user_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS donor (user_id BIGINT, time INTEGER);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS restore (guild_id BIGINT, user_id BIGINT, roles TEXT);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS lastfm (user_id BIGINT, username TEXT);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS lastfmcc (user_id BIGINT, command TEXT);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS lfmode (user_id BIGINT, mode TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS lfcrowns (user_id BIGINT, artist TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS lfreactions (user_id BIGINT, reactions TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS starboardmes (guild_id BIGINT, channel_starboard_id BIGINT, channel_message_id BIGINT, message_starboard_id BIGINT, message_id BIGINT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS starboard (guild_id BIGINT, channel_id BIGINT, count INTEGER, emoji_id BIGINT, emoji_text TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS seen (guild_id BIGINT, user_id BIGINT, time INTEGER);")
  await self.db.execute("CREATE TABLE IF NOT EXISTS booster_module (guild_id BIGINT, base BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS booster_roles (guild_id BIGINT, user_id BIGINT, role_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS hardban (guild_id BIGINT, banned BIGINT, author BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS forcenick (guild_id BIGINT, user_id BIGINT, nickname TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS uwulock (guild_id BIGINT, user_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS autopfp (guild_id BIGINT, channel_id BIGINT, genre TEXT, type TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS antiinvite (guild_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS whitelist (guild_id BIGINT, module TEXT, object_id BIGINT, mode TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS invoke (guild_id BIGINT, command TEXT, embed TEXT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS chatfilter (guild_id BIGINT, word TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS autoreact (guild_id BIGINT, trigger TEXT, emojis TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS autoresponder (guild_id BIGINT, trigger TEXT, response TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS welcome (guild_id BIGINT, channel_id BIGINT, mes TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS leave (guild_id BIGINT, channel_id BIGINT, mes TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS boost (guild_id BIGINT, channel_id BIGINT, mes TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS antiraid (guild_id BIGINT, command TEXT, punishment TEXT, seconds INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS disablecommand (guild_id BIGINT, command TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS reactionrole (guild_id BIGINT, message_id BIGINT, channel_id BIGINT, role_id BIGINT, emoji_id BIGINT, emoji_text TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS editsnipe (guild_id BIGINT, channel_id BIGINT, author_name TEXT, author_avatar TEXT, before_content TEXT, after_content TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS reactionsnipe (guild_id BIGINT, channel_id BIGINT, author_name TEXT, author_avatar TEXT, emoji_name TEXT, emoji_url TEXT, message_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS mod (guild_id BIGINT, channel_id BIGINT, jail_id BIGINT, role_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS cases (guild_id BIGINT, count INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS warns (guild_id BIGINT, user_id BIGINT, author_id BIGINT, time TEXT, reason TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS jail (guild_id BIGINT, user_id BIGINT, roles TEXT)")
  await self.db.execute('CREATE TABLE IF NOT EXISTS cmderror (code TEXT, error TEXT)')
  await self.db.execute('CREATE TABLE IF NOT EXISTS joint (guild_id BIGINT, hits INTEGER, holder BIGINT)')
  await self.db.execute("CREATE TABLE IF NOT EXISTS counters (guild_id BIGINT, channel_type TEXT, channel_id BIGINT, channel_name TEXT, module TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS bumps (guild_id BIGINT, bool TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS boosterslost (guild_id BIGINT, user_id BIGINT, time INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS dm (guild_id BIGINT, command TEXT, embed TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS discrim (guild_id BIGINT, role_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS joindm (guild_id BIGINT, message TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS birthday (user_id BIGINT, bday TIMESTAMPTZ, said TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS antispam (guild_id BIGINT, seconds INTEGER, count INTEGER, punishment TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS timezone (user_id BIGINT, zone TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS webhook (guild_id BIGINT, channel_id BIGINT, code TEXT, url TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS naughtycorner (guild_id BIGINT, channel_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS naughtycorner_members (guild_id BIGINT, user_id BIGINT)") 
  await self.db.execute("CREATE TABLE IF NOT EXISTS confess_members (guild_id BIGINT, user_id BIGINT, confession INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS confess_mute (guild_id BIGINT, user_id BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS autotags (guild_id BIGINT, url TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS antinuke_toggle (guild_id BIGINT, logs BIGINT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS antinuke (guild_id BIGINT, module TEXT, punishment TEXT, threshold INTEGER)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS giveaway (guild_id BIGINT, channel_id BIGINT, message_id BIGINT, winners INTEGER, members TEXT, finish TIMESTAMPTZ, host BIGINT, title TEXT)")
  await self.db.execute("CREATE TABLE IF NOT EXISTS gw_ended (channel_id BIGINT, message_id BIGINT, members TEXT)")
  await self.db.execute('CREATE TABLE IF NOT EXISTS diary (user_id BIGINT, text TEXT, title TEXT, date TEXT)')