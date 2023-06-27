# This source code is 100% original, any contents will be credited in revine's credits command. Created by fsb#1337 & report#0001

import discord, datetime, time, asyncio, random
from discord.ext import commands
from typing import Union
from discord.ui import View, Button
from classes import Emotes, Colors

start_time = time.time()

class mod(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

# --------------------------------------------------------------------------------------- Addrole Command

    @commands.command(aliases=['radd', 'arole', 'role'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_roles = True)
    async def addrole(self, ctx, member: discord.Member = None, role: discord.Role = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote}: Please mention a user.", color=Colors.warning)
            await ctx.send(embed=embed)
            return
        if role == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote}: Please mention a role.", color=Colors.warning)
            await ctx.send(embed=embed)
            return
        await member.add_roles(role)
        embed = discord.Embed(description=f"{Emotes.check_emote} Added: {role.mention} to {member.mention}.", colour=Colors.normal)
        await ctx.send(embed=embed, mention_author=False)
   
    @addrole.error
    async def addrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`Manage Roles`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False)
    
    @addrole.error
    async def addrole_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: I do not have permissions. [**`Manage Roles`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False)

# --------------------------------------------------------------------------------------- Removerole Command

    @commands.command(aliases=['remove', 'rrole'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_roles = True)
    async def removerole(self, ctx, member: discord.Member = None, role: discord.Role = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote}: Please mention a user.", color=Colors.warning)
            await ctx.send(embed=embed)
            return
        if role == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote}: Please mention a role.", color=Colors.warning)
            await ctx.send(embed=embed)
            return
        await member.remove_roles(role)
        embed = discord.Embed(description=f"Removed {role.mention} from {member.mention}", colour=Colors.normal)
        embed.set_footer(text="category: misc・revine ©️ 2023")
        await ctx.send(embed=embed, mention_author=False)
   
    @removerole.error
    async def removerole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`Manage Roles`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False)
            
    @removerole.error
    async def removerole_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: That role doesn't exist.", colour=Colors.warning)
            await ctx.send(embed=embed, mention_author=False)

# --------------------------------------------------------------------------------------- Ban Command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member:discord.Member = None, *, reason = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote}: Please mention a user.", color=Colors.warning)
            await ctx.send(embed=embed)
            return
        if reason == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote}: Please give a reason.", color=Colors.warning)
            await ctx.send(embed=embed)
            return
        await member.ban(reason = reason)
        embed = discord.Embed(description=f"banned {member.mention} **Reason: {reason}**", colour=Colors.normal)
        embed.set_footer(text="category: misc・revine ©️ 2023")
        await ctx.send(embed=embed, mention_author=False)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`Manage Roles`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False)

# --------------------------------------------------------------------------------------- Kick Command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member:discord.Member = None, *, reason = None):
        if member == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote}: Please mention a user.", color=Colors.warning)
            await ctx.send(embed=embed)
            return
        if reason == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote}: Please mention a role.", color=Colors.warning)
            await ctx.send(embed=embed)
            return
        await member.kick(reason = reason)
        embed = discord.Embed(description=f"Kicked {member.mention} **Reason: {reason}**", colour=Colors.normal)
        embed.set_footer(text="category: misc・revine ©️ 2023")
        await ctx.send(embed=embed, mention_author=False)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`Manage Roles`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False)

# --------------------------------------------------------------------------------------- Clear command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, number = None):
        if number == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} You haven't made a number input.", color=Colors.warning)
            await ctx.send(embed=embed)
            return
        number = int(number)
        await ctx.channel.purge(limit=number)
        clear = discord.Embed(description=f"{ctx.author.mention}: Cleared **{number}** Messages", color=Colors.normal)
        clear.set_footer(text="category: misc・revine ©️ 2023")
        await ctx.send(embed=clear)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`Manage Roles`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False)

# --------------------------------------------------------------------------------------- Lock command

    @commands.command(aliases=["lockdown"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
          embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Channel locked", color=Colors.normal)
          embed.set_footer(text="category: misc・revine ©️ 2023")
          await ctx.send(embed=embed)
          overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
          overwrite.send_messages = False
          await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)


    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`Manage Roles`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False)

# --------------------------------------------------------------------------------------- Unlock command

    @commands.command(aliases=["unlockdown"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
          embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Channel Unlocked", color=Colors.normal)
          embed.set_footer(text="category: misc・revine ©️ 2023")
          await ctx.send(embed=embed)
          overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
          overwrite.send_messages = True
          await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`Manage Roles`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False)

# --------------------------------------------------------------------------------------- Slowmode command

    @commands.command(aliases=["sl"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        if seconds == 0:
            await ctx.channel.edit(slowmode_delay = seconds)
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Slowmode set to default.", color=Colors.normal)
            await ctx.reply(embed=embed)
        else:
            await ctx.channel.edit(slowmode_delay = seconds)
            slow = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: slowmode set to **{seconds}**", color=Colors.normal)
            slow.set_footer(text="category: misc・revine ©️ 2023")
            await ctx.send(embed=slow)
        
    @slowmode.error
    async def slowmode_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**`Manage Roles`**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False)

    # --------------------------------------------------------------------------------------- Nuke command

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        if channel == None:
            n = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Mention a channel", color=Colors.warning)
            n.set_footer(text="category: misc・revine ©️ 2023")
            await ctx.send(embed=n)
            return
        if channel.id == 1075681602186788874:
            id = discord.Embed(description=(f"{Emotes.warning_emote} {ctx.author.mention}: You cannot nuke <#{channel.id}>"), color=Colors.warning)
            id.set_footer(text="category: misc・revine ©️ 2023")
            await ctx.send(embed=id)
            return
        channel = discord.utils.get(ctx.guild.channels, name = channel.name)
        if channel is not None:
            new_channel = await channel.clone(reason="Revine Logged: Nuked Channel")
            await channel.delete()
            nu = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: has nuked **{channel.name}**", color=Colors.warning)
            nu.set_footer(text="category: misc・revine ©️ 2023")
            await new_channel.send(embed=nu)
        
    @nuke.error
    async def nuke_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: You do not have permissions. [**` Manage Roles `**](https://discordapi.com/permissions.html#16)", colour=Colors.normal)
            await ctx.send(embed=embed, mention_author=False, delete_after=5)
            

async def setup(bot) -> None:
    await bot.add_cog(mod(bot))