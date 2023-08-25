import discord
from discord.ext import commands
from typing import List


class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        global player1
        global player2

        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            if interaction.user != player1:
                embed = discord.Embed(
                    color=self.bot.yellow,
                    description=f"{interaction.user.mention} it is not your turn yet",
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                self.style = discord.ButtonStyle.danger
                self.label = "X"
                self.disabled = True
                view.board[self.y][self.x] = view.X
                view.current_player = view.O
                content = f"{player2.mention}"

        else:
            if interaction.user != player2:
                embed = discord.Embed(
                    color=self.bot.yellow,
                    description=f"{interaction.user.mention} it is not your turn yet",
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                self.style = discord.ButtonStyle.success
                self.label = "O"
                self.disabled = True
                view.board[self.y][self.x] = view.O
                view.current_player = view.X
                content = f"{player1.mention}"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f"{player1.mention} is the winner!"
            elif winner == view.O:
                content = f"{player2.mention} is the winner!"
            else:
                content = "its a tie"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

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


class tictactoe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ttt"], help="play tictactoe with a friend")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def tictactoe(self, ctx, member: discord.Member = None):
        if member == None:
            return await ctx.reply("please mention a user")
        if member == ctx.author:
            return await ctx.reply("please mention a user")

        await ctx.reply(f"{member.mention}", view=TicTacToe())

        global player1
        global player2

        player1 = member
        player2 = ctx.author


async def setup(bot) -> None:
    await bot.add_cog(tictactoe(bot))
