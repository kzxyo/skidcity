import discord, random, datetime
from discord.ext import commands

def create_account():
  async def predicate(ctx: commands.Context):
    check = await ctx.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
    if check is None:
      await ctx.bot.db.execute("INSERT INTO economy VALUES ($1,$2,$3,$4,$5,$6)", ctx.author.id, 0, 0, datetime.datetime.now().timestamp(), datetime.datetime.now().timestamp(), datetime.datetime.now().timestamp())
    return True
  return commands.check(predicate)

def daily_taken():
  async def predicate(ctx: commands.Context):
    check = await ctx.bot.db.fetchrow("SELECT daily FROM economy WHERE user_id = $1", ctx.author.id)
    if check[0] > datetime.datetime.now().timestamp(): 
      await ctx.send_warning(f"You **already** claimed your daily credits\nTry again in <t:{check[0]}:R>")
      return False
    return True
  return commands.check(predicate)

def dice_cd():
  async def predicate(ctx: commands.Context):
    check = await ctx.bot.db.fetchrow("SELECT dice FROM economy WHERE user_id = $1", ctx.author.id)
    if check[0] > datetime.datetime.now().timestamp():
      await ctx.send_warning(f"Please wait **25 seconds** before you use dice again")
      return False
    return True
  return commands.check(predicate)

def rob_cd():
  async def predicate(ctx: commands.Context):
    check = await ctx.bot.db.fetchrow("SELECT rob FROM economy WHERE user_id = $1", ctx.author.id)
    if check[0] > datetime.datetime.now().timestamp():
      await ctx.send_warning(f"You can rob again in <t:{check[0]}:R>")
      return False
    return True
  return commands.check(predicate)

class Transfer(discord.ui.View):
  def __init__(self, ctx: commands.Context, member: discord.Member, amount):
   super().__init__()
   self.member = member
   self.amount = round(amount, 2)
   self.ctx = ctx
   self.status = False
  
  @discord.ui.button(label="yes", style=discord.ButtonStyle.green)
  async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True)
    check = await interaction.client.db.fetchrow("SELECT cash FROM economy WHERE user_id = $1", interaction.user.id)
    check2 = await interaction.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", self.member.id)
    lol = round(check[0], 2)
    await interaction.client.db.execute("UPDATE economy SET cash = $1 WHERE user_id = $2", lol-self.amount, interaction.user.id)
    await interaction.client.db.execute("UPDATE economy SET cash = $1 WHERE user_id = $2", check2['cash']+self.amount, self.member.id)
    self.status = True
    await interaction.response.edit_message(view=None, embed=discord.Embed(color=interaction.client.color, description=f"{interaction.client.yes} {interaction.user.mention}: transfered **{self.amount}** to {self.member}"))
  
  @discord.ui.button(label="no", style=discord.ButtonStyle.danger)
  async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "You are not the author of this embed", ephemeral=True)
    await interaction.response.edit_message(view=None, embed=discord.Embed(color=interaction.client.color, description="aborting action..."))
    self.status = True
  
  async def on_timeout(self) -> None:
       if self.status == False: 
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self) 

class Economy(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.cash = "💵"
        self.card = "💳"
        self.color = 0x2ECC71
    
    async def economy_send(self, ctx: commands.Context, message: str) -> discord.Message:
      return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.cash} {ctx.author.mention}: {message}"))
    
    @commands.command(description="transfer cash to a member", help="economy", usage="[amount] [member]")
    @create_account()
    async def give(self, ctx: commands.Context, amount: str, *, member: discord.Member):
      if member.id == ctx.author.id: return await ctx.send_warning("You cannot transfer to yourself")
      check = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", member.id)
      check2 = await self.bot.db.fetchrow("SELECT cash FROM economy WHERE user_id = $1", ctx.author.id)
      if not check: return await ctx.send_warning(f"**{member}** doesn't have an economy account")
      if amount.lower() == "all":
        amount = round(check2[0], 2)
      else:
        try:
            amount = float(amount)
        except: return await ctx.send_warning("This is not a valid number")
      if str(amount)[::-1].find(".") > 2: return await ctx.send_warning("The number can only have **2 decimals**")
      if amount < 0: return await ctx.send_warning("You cannot transfer less than **0**")
      if check[0] < amount: return await ctx.send_warning("You dont have enough **cash** to transfer")
      embed = discord.Embed(color=self.bot.color, description=f"{ctx.author.mention}: Are you sure you want to transfer **{amount}** to **{member.mention}**")
      view = Transfer(ctx, member, amount)
      view.message = await ctx.send(embed=embed, view=view)
    
    @commands.command(description="get your daily credits", help="economy")
    @daily_taken()
    @create_account()
    async def daily(self, ctx: commands.Context):
      check = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
      newbal = round(random.uniform(300, 600), 2)
      nextdaily = int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp())
      await self.bot.db.execute("UPDATE economy SET cash = $1, daily = $2 WHERE user_id = $3", round(check['cash']+newbal, 2), nextdaily, ctx.author.id)
      return await self.economy_send(ctx, f"You just got **{round(newbal, 2)}** {self.cash}\nCome back again **tomorrow**")
    
    @commands.command(description="rob someone's money", help="economy", usage="[member]")
    @rob_cd()
    @create_account()
    async def rob(self, ctx: commands.Context, member: discord.Member):
      if member.id == ctx.author.id: return await ctx.send_warning("You cannot rob yourself")
      check = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", member.id)
      if not check: return await ctx.send_warning(f"**{member}** doesn't have an economy account")
      elif not check['cash']: return await ctx.send(f"**{member}** is too poor to rob")
      check2 = await self.bot.db.fetchrow("SELECT cash FROM economy WHERE user_id = $1", ctx.author.id)
      amount = round(random.randint(400, 800), 2)
      await self.bot.db.execute("UPDATE economy SET cash = $1 WHERE user_id = $2", round(check['cash']-amount, 2), member.id)
      await self.bot.db.execute("UPDATE economy SET cash = $1, rob = $2 WHERE user_id = $3", round(check2[0]+amount, 2), int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()), ctx.author.id)
      await self.economy_send(ctx, f"Robbed **{amount}** {self.cash} from **{member}**")
      await member.send(f"Oh noo! **{ctx.author.name}** robbed **{amount}** {self.cash} from you. To prevent this in the future, store your cash in the bank")
    
    @commands.command(description="deposit money to the bank", help="economy", usage="[amount]")
    @create_account()
    async def deposit(self, ctx: commands.Context, *, amount: str):
      check = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
      if amount.lower() == "all":
        amount = round(check['cash'], 2)
      else:
        try:
            amount = float(amount)
        except: return await ctx.send_warning("This is not a valid number")
      if str(amount)[::-1].find(".") > 2: return await ctx.send_warning("The number can only have **2 decimals**")
      if check['cash'] < amount: return await ctx.send_warning("You dont have enough **cash** to deposit")
      if check['cash'] == 0: return await ctx.send_warning("You dont have any cash")
      await self.bot.db.execute("UPDATE economy SET cash = $1, bank = $2 WHERE user_id = $3", round(check['cash']-amount, 2), round(check['bank']+amount, 2), ctx.author.id)
      return await self.economy_send(ctx, f"Deposited **{amount}** {self.card}")
    
    @commands.command(description="play dice by putting a bet", help="economy", usage="[amount]")
    @dice_cd()
    @create_account()
    async def dice(self, ctx: commands.Context, *, amount: str):
      check = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
      if amount.lower() == "all":
        amount = round(check['cash'], 2)
      else:
        try:
            amount = float(amount)
        except: return await ctx.send_warning("This is not a valid number")
      if str(amount)[::-1].find(".") > 2: return await ctx.send_warning("The number can have only **2 decimals**")
      if check['cash'] < amount: return await ctx.send_warning("You dont have enough **money** to bet")
      if amount < 20: return await ctx.send_warning(f"You cannot bet below **20** {self.cash}")
      my_dice = random.randint(1, 6) + random.randint(1, 6)
      bot_dice = random.randint(1, 6) + random.randint(1, 6)
      if my_dice > bot_dice:
        await ctx.send(f"You won **{amount}**")
        await self.bot.db.execute("UPDATE economy SET cash = $1, dice = $2 WHERE user_id = $3", round(check['cash']+amount, 2), int((datetime.datetime.now() + datetime.timedelta(seconds=25)).timestamp()), ctx.author.id)
      elif bot_dice > my_dice:
        await ctx.send(f"You lost **{amount}**")
        await self.bot.db.execute("UPDATE economy SET cash = $1, dice = $2 WHERE user_id = $3", round(check['cash']-amount, 2), int((datetime.datetime.now() + datetime.timedelta(seconds=25)).timestamp()), ctx.author.id)
      else:
        await ctx.send("It's a tie!")
        await self.bot.db.execute("UPDATE economy SET dice = $1 WHERE user_id = $2", int((datetime.datetime.now() + datetime.timedelta(seconds=25)).timestamp()), ctx.author.id)
    
    @commands.command(description="check you or someone's economy balance", help="economy", usage="<member>", aliases=["bal"])
    @create_account()
    async def balance(self, ctx: commands.Context, *, member: discord.Member=None):
      if not member: member = ctx.author
      check = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", member.id)
      if not check: return await ctx.send_warning(f"**{member}** doesnt have an economy account")
      await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"**{member.name}'s** balance").add_field(name="💵 Cash", value=float(check['cash'])).add_field(name="💳 Bank", value=float(check['bank'])).set_author(name=member.global_name if member.global_name else member.name, icon_url=member.display_avatar.url))
    
    @commands.command(description="withdraw money from the bank", help="economy", usage="[amount]")
    @create_account()
    async def withdraw(self, ctx: commands.Context, *, amount: str):
      check = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
      if amount.lower() == "all":
        amount = round(check['bank'], 2)
      else:
        try:
            amount = float(amount)
        except: return await ctx.send_warning("This is not a valid number")
      if str(amount)[::-1].find(".") > 2: return await ctx.send_warning("The number can only have **2 decimals**")
      if check['bank'] < amount: return await ctx.send_warning("You dont have enough **money** to withdraw")
      if check['bank'] == 0: return await ctx.send_warning(f"You dont have any money in the bank")
      await self.bot.db.execute("UPDATE economy SET cash = $1, bank = $2 WHERE user_id = $3", round(check['cash']+amount, 2), round(check['bank']-amount, 2), ctx.author.id)
      return await self.economy_send(ctx, f"Withdrawed **{amount}** {self.card}")
    
async def setup(bot):
    await bot.add_cog(Economy(bot))