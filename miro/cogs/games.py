import discord, aiohttp, random, json, time, asyncio, dateutil.parser
from discord.ext import commands
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
        if interaction.user.id != self.ctx.author.id:
            return await interaction.client.ext.send_warning(
                interaction, "This is not your game", ephemeral=True
            )
        botselection = random.choice(["rock", "paper, scissors"])

        def getwinner():
            if botselection == "rock" and selection == "scissors":
                return interaction.client.user.id
            elif botselection == "rock" and selection == "paper":
                return interaction.user.id
            elif botselection == "paper" and selection == "rock":
                return interaction.client.user.id
            elif botselection == "paper" and selection == "scissors":
                return interaction.user.id
            elif botselection == "scissors" and selection == "rock":
                return interaction.user.id
            elif botselection == "scissors" and selection == "paper":
                return interaction.client.user.id
            else:
                return "tie"

        if getwinner() == "tie":
            await interaction.response.edit_message(
                embed=discord.Embed(
                    color=interaction.client.color,
                    title="Tie!",
                    description=f"You both picked {self.get_emoji.get(selection)}",
                )
            )
        elif getwinner() == interaction.user.id:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    color=interaction.client.color,
                    title="You won!",
                    description=f"You picked {self.get_emoji.get(selection)} and the bot picked {self.get_emoji.get(botselection)}",
                )
            )
        else:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    color=interaction.client.color,
                    title="Bot won!",
                    description=f"You picked {self.get_emoji.get(selection)} and the bot picked {self.get_emoji.get(botselection)}",
                )
            )
        await self.disable_buttons()
        self.status = True

    @discord.ui.button(emoji="🪨")
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await self.action(interaction, "rock")

    @discord.ui.button(emoji="📰")
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await self.action(interaction, "paper")

    @discord.ui.button(emoji="✂️")
    async def scissors(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        return await self.action(interaction, "scissors")

    async def on_timeout(self):
        if self.status == False:
            await self.disable_buttons()


class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(
        self, x: int, y: int, player1: discord.Member, player2: discord.Member
    ):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
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
            if interaction.user != self.player1:
                return await interaction.response.send_message(
                    "you can't interact with this button", ephemeral=True
                )
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now **{self.player2.name}**'s turn"
        else:
            if interaction.user != self.player2:
                return await interaction.response.send_message(
                    "you can't interact with this button", ephemeral=True
                )
            self.style = discord.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now **{self.player1.name}'s** turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f"**{self.player1.name}** won!"
            elif winner == view.O:
                content = "**{}** won!".format(self.player2.name)
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
        for item in self.children:
            item.disabled = True
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
                data = str(byte, "utf-8")
                return data.splitlines()


class TypeRace:
    """TypeRace backend variables"""

    async def getanswer():
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://www.mit.edu/~ecprice/wordlist.100000") as r:
                byte = await r.read()
                data = str(byte, "utf-8")
                data = data.splitlines()
                mes = ""
                for _ in range(10):
                    mes = f"{mes}{random.choice(data)} "

                return mes

    def accurate(first: str, second: str):
        percentage = 0
        i = 0
        text1 = first.split()
        text2 = second.split()
        for t in text2:
            try:
                if t == text1[i]:
                    percentage += 10
                i += 1
            except:
                return percentage

        return percentage


class testcmds(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.hybrid_command(
        aliases=["rps"], description="play rock paper scissors with the bot", help="fun"
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def rockpaperscisssors(self, ctx: commands.Context):
        view = RockPaperScissors(ctx)
        embed = discord.Embed(
            color=self.bot.color,
            title="Rock Paper Scissors!",
            description="Click a button to play!",
        )
        view.message = await ctx.reply(embed=embed, view=view)

    @commands.hybrid_command(
        aliases=["howr"], description="retard rate an user", help="fun", usage="<member>"
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def howretarded(self, ctx, member: discord.Member = commands.Author):
        await ctx.reply(
            embed=discord.Embed(
                color=self.bot.color,
                title="how retarded",
                description=f"{member.mention} is {randrange(101)}% retarded <:jade_retarded:1114576204431888506>",
            )
        )

    @commands.hybrid_command(
       aliases=["howg"],description="gay rate an user", help="fun", usage="<member>"
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def howgay(self, ctx, member: discord.Member = commands.Author):
        await ctx.reply(
            embed=discord.Embed(
                color=self.bot.color,
                title="gay rate",
                description=f"{member.mention} is {randrange(101)}% gay 🏳️‍🌈",
            )
        )

    @commands.hybrid_command(
        aliases=["howc"],description="cool rate an user", help="fun", usage="<member>"
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def howcool(self, ctx, member: discord.Member = commands.Author):
        await ctx.reply(
            embed=discord.Embed(
                color=self.bot.color,
                title="cool rate",
                description=f"{member.mention} is {randrange(101)}% cool 😎",
            )
        )

    @commands.hybrid_command(
       aliases=["shiprate"], description="ship rate an user", help="fun", usage="[member]"
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def ship(self, ctx, member: discord.Member):
        return await ctx.reply(
            f"**{ctx.author.name}** 💞 **{member.name}** = **{randrange(101)}%**"
        )

    @commands.hybrid_command(
        aliases=["ttt"],
        description="play tictactoe with your friends",
        help="fun",
        usage="ttt [user]",
    )
    @commands.cooldown(1, 6, commands.BucketType.guild)
    async def tictactoe(self, ctx: commands.Context, *, member: discord.Member):
        if member is ctx.author:
            return await ctx.reply(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f"{self.bot.warning} {ctx.author.mention}: You can't play with yourself. It's ridiculous",
                )
            )
        if member.bot:
            return await ctx.reply("bots can't play")
        embed = discord.Embed(
            color=self.bot.color,
            description=f"**{ctx.author.name}** wants to play **tictactoe** with you. Do you accept?",
        )
        style = discord.ButtonStyle.gray
        yes = discord.ui.Button(emoji=self.bot.yes, style=style)
        no = discord.ui.Button(emoji=self.bot.no, style=style)

        async def yes_callback(interaction: discord.Interaction):
            if interaction.user != member:
                em = discord.Embed(
                    color=self.bot.color,
                    description=f"{self.bot.warning}: {interaction.user.mention} you are not the author of this embed",
                )
                return await interaction.response.send_message(embed=em, ephemeral=True)
            vi = TicTacToe(ctx.author, member)
            await interaction.message.delete()
            vi.message = await ctx.send(
                content=f"Tic Tac Toe: **{ctx.author.name}** goes first",
                embed=None,
                view=vi,
            )

        async def no_callback(interaction: discord.Interaction):
            if interaction.user != member:
                em = discord.Embed(
                    color=self.bot.color,
                    description=f"{self.bot.warning}: {interaction.user.mention} you are not the author of this embed",
                )
                return await interaction.response.send_message(embed=em, ephemeral=True)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f"I'm sorry but **{interaction.user.name}** doesn't want to play with you right now",
                ),
                view=None,
                content=ctx.author.mention,
            )

        yes.callback = yes_callback
        no.callback = no_callback
        view = discord.ui.View()
        view.add_item(yes)
        view.add_item(no)
        await ctx.send(embed=embed, view=view, content=member.mention)

    @commands.hybrid_command(description="play blacktea with your friends", help="fun", aliases=["blackt"])
    @commands.cooldown(1, 6, commands.BucketType.guild)
    async def blacktea(self, ctx: commands.Context):
        try:
            if BlackTea.MatchStart[ctx.guild.id] is True:
                return await ctx.reply(
                    "somebody in this server is already playing blacktea"
                )
        except KeyError:
            pass

        BlackTea.MatchStart[ctx.guild.id] = True
        embed = discord.Embed(
            color=self.bot.color,
            title="BlackTea Matchmaking",
            description=f"⏰ Waiting for players to join. To join react with 🍵.\nThe game will begin in **20 seconds**",
        )
        embed.add_field(
            name="goal",
            value="You have **10 seconds** to say a word containing the given group of **3 letters.**\nIf failed to do so, you will lose a life. Each player has **2 lifes**",
        )
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
            return await ctx.send(
                "😦 {}, not enough players joined to start blacktea".format(
                    ctx.author.mention
                ),
                allowed_mentions=discord.AllowedMentions(users=True),
            )

        while len(players) > 1:
            for player in players:
                strin = await BlackTea.get_string()
                await ctx.send(
                    f"⏰ <@{player}>, type a word containing **{strin.upper()}** in **10 seconds**",
                    allowed_mentions=discord.AllowedMentions(users=True),
                )

                def is_correct(msg):
                    return msg.author.id == player

                try:
                    message = await self.bot.wait_for(
                        "message", timeout=10, check=is_correct
                    )
                except asyncio.TimeoutError:
                    try:
                        BlackTea.lifes[player] = BlackTea.lifes[player] + 1
                        if BlackTea.lifes[player] == 3:
                            await ctx.send(
                                f" <@{player}>, you're eliminated ☠️",
                                allowed_mentions=discord.AllowedMentions(users=True),
                            )
                            BlackTea.lifes[player] = 0
                            players.remove(player)
                            leaderboard.append(player)
                            continue
                    except KeyError:
                        BlackTea.lifes[player] = 0
                    await ctx.send(
                        f"💥 <@{player}>, you didn't reply on time! **{2-BlackTea.lifes[player]}** lifes remaining",
                        allowed_mentions=discord.AllowedMentions(users=True),
                    )
                    continue
                i = 0
                for word in await BlackTea.get_words():
                    if (
                        strin.lower() in message.content.lower()
                        and message.content.lower() == word.lower()
                    ):
                        i += 1
                        pass
                if i == 0:
                    try:
                        BlackTea.lifes[player] = BlackTea.lifes[player] + 1
                        if BlackTea.lifes[player] == 3:
                            await ctx.send(
                                f" <@{player}>, you're eliminated ☠️",
                                allowed_mentions=discord.AllowedMentions(users=True),
                            )
                            BlackTea.lifes[player] = 0
                            players.remove(player)
                            leaderboard.append(player)
                            continue
                    except KeyError:
                        BlackTea.lifes[player] = 0
                    await ctx.send(
                        f"💥 <@{player}>, incorrect word! **{2-BlackTea.lifes[player]}** lifes remaining",
                        allowed_mentions=discord.AllowedMentions(users=True),
                    )
                else:
                    await message.add_reaction("✅")
                    i = 0

        leaderboard.append(players[0])
        le = 1
        auto = ""
        for leader in leaderboard[::-1]:
            auto += f"{'<:aadadad:1114578181580660866>' if le == 1 else f'`{le}`'} **{ctx.guild.get_member(leader) or leader}**\n"
            if le == 10:
                break
            le += 1
        e = discord.Embed(
            color=self.bot.color, title=f"leaderboard for blacktea", description=auto
        ).set_footer(
            text=f"top {'10' if len(leaderboard) > 9 else len(leaderboard)} players"
        )
        await ctx.send(embed=e)
        BlackTea.lifes[players[0]] = 0
        BlackTea.MatchStart[ctx.guild.id] = False

async def setup(bot) -> None:
    await bot.add_cog(testcmds(bot))
