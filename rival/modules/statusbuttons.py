import discord
from discord import Status

statuses={
	0: Status.online,
	1: Status.idle,
	2: Status.dnd,
	3: Status.offline
}
async def confirm(self:discord.ext.commands.Cog, ctx:discord.ext.commands.Context, msg:discord.Message, *, timeout:int=180):
	"""Waits for confirmation via reaction from the user before continuing
	Parameters
	----------
	self : discord.ext.commands.Cog
		Cog the command is invoked in
	ctx : discord.ext.commands.Context
		Command invocation context
	msg : discord.Message
		The message to prompt for confirmation on
	timeout = timeout : int, optional
		How long to wait before timing out (seconds), by default 20
	Returns
	-------
	output : bool or None
		True if user confirms action, False if user does not confirm action, None if confirmation times out
	"""
	view = Confirm(invoker=ctx.author, timeout=timeout)
	await msg.edit(view=view)
	# Wait for the View to stop listening for input...
	await view.wait()
	return view.value

class Confirm(discord.ui.View):
	def __init__(self, invoker:"discord.User|discord.Member", *, timeout:float=180):
		if timeout is not None:
			super().__init__(timeout=timeout)
		else:
			super().__init__()
		self.value = None
		self.invoker = invoker
		self.authorized_user = invoker
	
	
	@discord.ui.button(label='Online', style=discord.ButtonStyle.green)
	async def online(self, interaction:discord.Interaction, button:discord.ui.Button):
		await self.confirmation(interaction, 0)


	@discord.ui.button(label='Idle', style=discord.ButtonStyle.blurple)
	async def idle(self, interaction:discord.Interaction, button:discord.ui.Button):
		await self.confirmation(interaction, 1)

	@discord.ui.button(label='DnD', style=discord.ButtonStyle.red)
	async def dnd(self, interaction:discord.Interaction, button:discord.ui.Button):
		await self.confirmation(interaction, 2)

	@discord.ui.button(label='Offline', style=discord.ButtonStyle.gray)
	async def offline(self, interaction:discord.Interaction, button:discord.ui.Button):
		await self.confirmation(interaction, 3)

	async def confirmation(self, interaction:discord.Interaction, confirm:int):
		if not interaction.user.id == self.invoker.id:
			await interaction.response.send_message(embed=discord.Embed(description=f"{self.bot.warn} {interaction.user.mention}: **You cannot interact with this**", color=int("faa61a", 16)), ephemeral=True)
			return
		elif confirm:
			await interaction.response.defer()
		else:
		   await interaction.response.defer()
		self.value = confirm
		self.stop()