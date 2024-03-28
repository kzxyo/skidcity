
from puke import Puke
from puke.managers import Context

from discord import  Member
from discord.ext.commands import Cog, command, has_permissions


class Moderation(Cog):
    def __init__(self, bot):
        self.bot: Puke = bot

    @command(
        name="ban",
        aliases=[
            'deport', 
            'banish'
        ]
    )
    @has_permissions(ban_members=True)
    async def ban(
        self: "Moderation",
        ctx: Context,
        user: Member,
        *,
        reason: str = "No reason provided"
    ):
        """
        Ban a member
        """

        await ctx.guild.ban(
            user,
            reason=f"{ctx.author} - {reason}"
        )
        return await ctx.approve(f"**{user}** has been banned | {reason}")

    @command(
        name="kick",
        aliases=[
            "boot"
        ]
    )
    @has_permissions(kick_members=True)
    async def kick(
        self: "Moderation",
        ctx: Context,
        user: Member,
        *,
        reason: str = "No reason provided"
    ):
        """
        Kick a member
        """

        await ctx.guild.kick(
            user,
            reason=f"{ctx.author} - {reason}"
        )
        return await ctx.approve(f"**{user}** has been kicked | {reason}")
    

    @command(
        name="unban",
        aliases=[
            'forgive', 
            'pardon'
        ]
    )
    @has_permissions(ban_members=True)
    async def unban(
        self: "Moderation",
        ctx: Context,
        user: Member
    ):
        """
        Unban a member
        """
        try:
            await ctx.guild.unban(
            user,
        )
            return await ctx.approve(f"**{user}** has been unbanned")
        except:
            await ctx.warn(f"{ctx.author.mention}: {user} is not banned from the server")
    
    @command(
        name="purge",
        aliases=[
            'clear',
            'c'
        ]
    )
    @has_permissions(manage_messages=True)
    async def purge(
        self: "Moderation",
        ctx: Context,
        amount: int = 15
    ):
        """
        Clear messages
        """
        
        await ctx.channel.purge(
            limit=amount+1
        )
    
async def setup(bot):
    await bot.add_cog(Moderation(bot))