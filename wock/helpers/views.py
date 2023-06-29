import asyncio
import contextlib

from datetime import timedelta

import discord

from discord.ext import commands
from discord.ui import Button, Select, View

from helpers import functions


class ConfirmView(View):
    def __init__(self, ctx: commands.Context):
        super().__init__()
        self.value = False
        self.ctx: commands.Context = ctx
        self.bot: commands.Bot = ctx.bot

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, _: discord.Button):
        """Approve the action"""

        self.value = True
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, _: discord.Button):
        """Decline the action"""

        self.value = False
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.warn(
                "You aren't the **author** of this embed",
            )
            return False


class UserInfoView(View):
    def __init__(self, ctx: commands.Context, member: discord.Member):
        super().__init__()
        self.ctx: commands.Context = ctx
        self.bot: commands.Bot = ctx.bot
        self.member: discord.Member = member

    @discord.ui.button(label="📝 Names", style=discord.ButtonStyle.gray)
    async def name_history(self, interaction: discord.Interaction, _: discord.Button):
        """View the user's name history"""

        await interaction.response.defer()
        self.children[0].disabled = True
        await interaction.message.edit(view=self, attachments=interaction.message.attachments)

        await self.ctx.invoke(self.bot.get_command("namehistory"), user=self.member)

    @discord.ui.button(label="🖼️ Avatars", style=discord.ButtonStyle.gray)
    async def avatar_history(self, interaction: discord.Interaction, _: discord.Button):
        """View the user's avatar history"""

        await interaction.response.defer()
        self.children[1].disabled = True
        await interaction.message.edit(view=self, attachments=interaction.message.attachments)

        avatars = await self.bot.db.fetch(
            "SELECT avatar, timestamp FROM metrics.avatars WHERE user_id = $1 ORDER BY timestamp DESC",
            self.member.id,
        )
        if not avatars:
            return await self.ctx.warn(
                "You don't have any **avatars** in the database"
                if self.member == self.ctx.author
                else f"**{self.member}** doesn't have any **avatars** in the database"
            )

        image = await functions.collage([row.get("avatar") for row in avatars[:35]])
        embeds = list(interaction.message.embeds)
        if len(embeds) == 1 and len(embeds[0].fields) == 3:
            embeds[0].set_image(url="attachment://collage.png")
        else:
            embed = discord.Embed()
            embed.set_image(url="attachment://collage.png")
            embeds.append(embed)

        with contextlib.suppress(discord.HTTPException):
            await interaction.message.edit(embeds=embeds, attachments=[image])

    @discord.ui.button(label="⏰ Activity", style=discord.ButtonStyle.gray)
    async def status_history(self, interaction: discord.Interaction, _: discord.Button):
        """View the user's status history"""

        await interaction.response.defer()
        self.children[2].disabled = True
        await interaction.message.edit(view=self, attachments=interaction.message.attachments)

        history = await self.bot.db.fetchrow(
            "SELECT offline, online, idle, dnd, last_status, timestamp FROM metrics.presences WHERE user_id = $1",
            self.member.id,
        )
        if not history:
            return await self.ctx.warn(
                "You don't have any **presence history** in the database"
                if self.member == self.ctx.author
                else f"**{self.member}** doesn't have any **presence history** in the database"
            )

        records = {}
        for status in ("online", "idle", "dnd", "offline", "last_status"):
            if status == "last_status":
                status = history.get("last_status")
                records[status] = int((discord.utils.utcnow() - history.get("timestamp")).total_seconds())
            else:
                records[status] = history.get(status)

        tracking_since = 0
        for record in records.values():
            tracking_since += record
        tracking_since = discord.utils.utcnow() - timedelta(seconds=tracking_since)

        image = await functions.chart(values=records)
        embeds = list(interaction.message.embeds)
        if len(embeds) == 1 and len(embeds[0].fields) == 3:
            embeds[0].set_image(url="attachment://chart.png")
        else:
            embed = discord.Embed()
            embed.set_image(url="attachment://chart.png")
            embeds.append(embed)

        await interaction.message.edit(embeds=embeds, attachments=[image])

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(
                view=None,
            )

        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.warn(
                "You aren't the **author** of this embed",
            )
            return False


class Reminder(View):
    def __init__(self, jump_url: str):
        super().__init__()
        self.jump_url = jump_url
        self.add_item(
            Button(
                label="Original Message",
                url=self.jump_url,
                style=discord.ButtonStyle.link,
            )
        )


class RemoveDuplicates(View):
    def __init__(self, ctx: commands.Context, duplicates: dict[str, list[discord.Emoji]]):
        super().__init__()
        self.ctx: commands.Context = ctx
        self.bot: commands.Bot = ctx.bot
        self.duplicates: dict[str, list[discord.Emoji]] = duplicates
        self.add_item(RemoveDuplicatesDropdown(ctx, duplicates))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.warn(
                "You aren't the **author** of this embed",
                followup=False,
            )
            return False

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(
                view=None,
            )

        self.stop()

    async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(
                view=None,
            )

        self.stop()

    async def start(self):
        embed = discord.Embed(
            title="Duplicate Emojis",
        )

        for hash, emojis in self.duplicates.items():
            embed.add_field(
                name=f"**{hash}**",
                value=">>> " + "\n".join(f"{emoji} [`:{emoji.name}:`]({emoji.url})" for emoji in emojis),
                inline=True,
            )

        self.message = await self.ctx.send(
            embed=embed,
            view=self,
        )


class RemoveDuplicatesDropdown(Select):  # Select which emojis to keep using a dropdown
    def __init__(self, ctx: commands.Context, duplicates: dict[str, list[discord.Emoji]]):
        super().__init__(
            placeholder="Select which emojis to keep..",
            min_values=1,
            max_values=len(duplicates),
        )
        self.ctx: commands.Context = ctx
        self.bot: commands.Bot = ctx.bot
        self.duplicates: dict[str, list[discord.Emoji]] = duplicates
        for hash in duplicates:
            for emoji in duplicates[hash]:
                self.add_option(
                    label=emoji.name,
                    value=emoji.id,
                    emoji=emoji,
                )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Get the selected emojis
        duplicates = [emoji for hash in self.duplicates for emoji in self.duplicates[hash]]
        selected = [emoji for option in interaction.data["values"] if (emoji := self.bot.get_emoji(int(option)))]
        if not selected:
            return await interaction.warn(
                "You didn't **select** any emojis",
            )
        elif len(selected) == len(duplicates):
            return await interaction.warn(
                f"You can't **delete** all the emojis",
            )

        with contextlib.suppress(discord.HTTPException):
            await self.view.message.delete()

        await self.ctx.prompt(f"Are you sure you want to delete {functions.plural(len(duplicates) - len(selected), bold=True):duplicate emoji}?")
        await self.ctx.load(f"Deleting {functions.plural(len(duplicates) - len(selected), bold=True):duplicate emoji}.. This may take a while!")

        deleted, failed = 0, 0
        for emoji in duplicates:
            if emoji not in selected:
                try:
                    await emoji.delete(reason=f"Duplicate emoji ({hash}) - {self.ctx.author}")
                except discord.HTTPException:
                    failed += 1
                else:
                    deleted += 1

                await asyncio.sleep(1)

        await self.ctx.approve(f"Deleted {functions.plural(deleted, bold=True):duplicate emoji}" + (f" (`{failed}` failed)" if failed else ""))


class TicTacToeButton(Button):
    def __init__(self, label: str, style: discord.ButtonStyle, row: int, custom_id: str):
        super().__init__(label=label, style=style, row=row, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        await self.view.callback(interaction, self)


class TicTacToe(View):
    def __init__(self, ctx: commands.Context, member: discord.Member):
        super().__init__(timeout=60.0)
        self.ctx: commands.Context = ctx
        self.bot: commands.Bot = ctx.bot
        self.message: discord.Message = None
        self.member: discord.Member = member
        self.turn: discord.Member = ctx.author
        self.winner: discord.Member = None
        for i in range(9):
            self.add_item(
                TicTacToeButton(
                    label="\u200b",
                    style=discord.ButtonStyle.gray,
                    row=i // 3,
                    custom_id=f"board:{i}",
                )
            )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.turn.id:
            return True
        else:
            await interaction.warn(
                f"It's {self.turn.mention}'s turn!",
                followup=False,
            )
            return False

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(
                content=f"**{self.ctx.author.name}** vs **{self.member.name}**\n\nThe game has ended due to inactivity",
                view=self,
            )

        self.stop()

    async def on_error(self, error: Exception, item: Button, interaction: discord.Interaction):
        await self.ctx.warn(
            f"An error occurred while processing your action: {item}",
            followup=False,
        )
        self.stop()

    async def callback(self, interaction: discord.Interaction, button: TicTacToeButton):
        await interaction.response.defer()

        button.label = "X" if self.turn == self.ctx.author else "O"
        button.disabled = True
        button.style = discord.ButtonStyle.red if self.turn == self.ctx.author else discord.ButtonStyle.green
        if winner := await self.check_win(interaction):
            await interaction.message.edit(
                content=f"**{self.ctx.author.name}** vs **{self.member.name}**\n\n{winner}",
                view=self,
            )
            self.stop()
            return

        self.turn = self.member if self.turn == self.ctx.author else self.ctx.author
        await interaction.message.edit(
            content=(
                f"**{self.ctx.author.name}** vs **{self.member.name}**\n\n{'❌' if self.turn == self.ctx.author else '⭕'} It's {self.turn.mention}'s"
                " turn"
            ),
            view=self,
        )

    async def check_win(self, interaction: discord.Interaction):
        board = [button.label for button in self.children]
        if board[0] == board[1] == board[2] != "\u200b":
            self.winner = self.ctx.author if board[0] == "X" else self.member
        elif board[3] == board[4] == board[5] != "\u200b":
            self.winner = self.ctx.author if board[3] == "X" else self.member
        elif board[6] == board[7] == board[8] != "\u200b":
            self.winner = self.ctx.author if board[6] == "X" else self.member
        elif board[0] == board[3] == board[6] != "\u200b":
            self.winner = self.ctx.author if board[0] == "X" else self.member
        elif board[1] == board[4] == board[7] != "\u200b":
            self.winner = self.ctx.author if board[1] == "X" else self.member
        elif board[2] == board[5] == board[8] != "\u200b":
            self.winner = self.ctx.author if board[2] == "X" else self.member
        elif board[0] == board[4] == board[8] != "\u200b":
            self.winner = self.ctx.author if board[0] == "X" else self.member
        elif board[2] == board[4] == board[6] != "\u200b":
            self.winner = self.ctx.author if board[2] == "X" else self.member
        elif "\u200b" not in board:
            self.winner = "tie"

        if self.winner:
            for child in self.children:
                child.disabled = True
            return f"🏆 {self.winner.mention} won!" if self.winner != "tie" else "It's a **tie**!"
        return False

    async def start(self):
        """Start the TicTacToe game"""

        self.message = await self.ctx.channel.send(
            content=f"**{self.ctx.author.name}** vs **{self.member.name}**\n\n❌ It's {self.turn.mention}'s turn",
            view=self,
        )
