from structure import Blare
from structure.managers import Context

from discord import Message, Member
from discord.ext.commands import Cog, command, group, has_permissions

class Moderation(Cog):
    def __init__(self, bot: Blare):
        self.bot: Blare = bot

    @group(
        name="purge",
        aliases=[
            "c",
            "clear"
        ],
        invoke_without_command=True
    )
    @has_permissions(manage_messages=True)
    async def purge(
        self: "Moderation", 
        ctx: Context,
        amount: int = 15
    ) -> Message:
        """
        Clear a certain amount of messages
        """
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name
        )
        return await ctx.send(f"👍", delete_after=3)

    @purge.command(
        name="user",
        aliases=['member']
    )
    @has_permissions(manage_messages=True)
    async def purge_user(
        self: "Moderation",
        ctx: Context,
        member: Member,
        amount: int = 15
    ) -> Message:
        """
        Clear messages from a specific user
        """

        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.author == member
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="bot",
        aliases=['bots']
    )
    @has_permissions(manage_messages=True)
    async def purge_bot(
        self: "Moderation",
        ctx: Context,
        amount: int = 15
    ) -> Message:
        """
        Clear messages from bots
        """

        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.author.bot
        )

        return await ctx.send("👍", delete_after=3)

    
    @purge.command(
        name="links",
        aliases=['embeds']
    )
    @has_permissions(manage_messages=True)
    async def purge_embeds(
        self: "Moderation",
        ctx: Context,
        amount: int = 15
    ) -> Message:
        """
        Clear messages containing links or embeds
        """
        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.embeds or 'http://' in m.content or 'https://' in m.content
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="attachments",
        aliases=[
            'files',
            'images'
        ]
    )
    @has_permissions(manage_messages=True)
    async def purge_attachments(
        self: "Moderation",
        ctx: Context,
        amount: int = 15
    ) -> Message:
        """
        Clear messages containing attachments
        """
        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.attachments
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="humans",
        aliases=['members']
    )
    @has_permissions(manage_messages=True)
    async def purge_humans(
        self: "Moderation",
        ctx: Context,
        amount: int = 15
    ) -> Message:
        """
        Clear messages from humans
        """
        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: not m.author.bot
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="invites",
        aliases=[
            'inv',
            'invite'
        ]
    )
    @has_permissions(manage_messages=True)
    async def purge_invites(
        self: "Moderation",
        ctx: Context,
        amount: int = 15
    ) -> Message:
        """
        Clear messages containing invites
        """
        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: '.gg/' in m.content or '/invite/' in m.content
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="reactions",
        aliases=[
            'reacts',
            'emoji'
        ]
    )
    @has_permissions(manage_messages=True)
    async def purge_reactions(
        self: "Moderation",
        ctx: Context,
        amount: int = 15
    ) -> Message:
        """
        Clear messages containing reactions
        """
        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.emojis
        )

        return await ctx.send("ok", delete_after=3)
    
    @purge.command(
        name="stickers",
        aliases=['sticker']
    )
    @has_permissions(manage_messages=True)
    async def purge_stickers(
        self: "Moderation",
        ctx: Context,
        amount: int = 15
    ) -> Message:
        """
        Clear messages containing stickers
        """
        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.stickers
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="mentions",
        aliases=['mention']
    )
    @has_permissions(manage_messages=True)
    async def purge_mentions(
        self: "Moderation",
        ctx: Context,
        amount: int = 15
    ) -> Message:
        """
        Clear messages containing mentions
        """
        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.mentions
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="after",
        aliases=['since']
    )
    @has_permissions(manage_messages=True)
    async def purge_after(
        self: "Moderation",
        ctx: Context,
        message: Message
    ) -> Message:
        """
        Clear messages after a specific message
        """

        if message.channel != ctx.channel:
            return await ctx.send("The message must be in this channel!")
        
        await ctx.channel.purge(
            limit=300,
            after=message,
            before=ctx.message,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.mentions
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="between",
        aliases=['range']
    )
    @has_permissions(manage_messages=True)
    async def purge_between(
        self: "Moderation",
        ctx: Context,
        start: Message,
        end: Message
    ) -> Message:
        """
        Clear messages between two specific messages
        """

        if start.channel != ctx.channel or end.channel != ctx.channel:
            return await ctx.send("The messages must be in this channel!")
        
        await ctx.channel.purge(
            limit=300,
            after=start,
            before=end,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.mentions
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="startswith",
        aliases=['start']
    )
    @has_permissions(manage_messages=True)
    async def purge_startswith(
        self: "Moderation",
        ctx: Context,
        string: str,
        amount: int = 15
    ) -> Message:
        """
        Clear messages starting with a specific string
        """

        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.content and m.content.lower().startswith(string.lower())
        )

        return await ctx.send("👍", delete_after=3)
    
    @purge.command(
        name="endswith",
        aliases=['end']
    )
    @has_permissions(manage_messages=True)
    async def purge_endswith(
        self: "Moderation",
        ctx: Context,
        string: str,
        amount: int = 15
    ) -> Message:
        """
        Clear messages ending with a specific string
        """

        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.content and m.content.lower().endswith(string.lower())
        )

        return await ctx.send("👍", delete_after=3)
    

    @purge.command(
        name="contains",
        aliases=['contain']
    )
    @has_permissions(manage_messages=True)
    async def purge_contains(
        self: "Moderation",
        ctx: Context,
        string: str,
        amount: int = 15
    ) -> Message:
        """
        Clear messages containing a specific string
        """

        if amount > 1000:
            return await ctx.alert("You can only delete 1000 messages at a time!")
        
        await ctx.channel.purge(
            limit=amount,
            bulk=True,
            reason=ctx.author.name,
            check=lambda m: m.content and string.lower() in m.content.lower()
        )

        return await ctx.send("👍", delete_after=3)
    
    @command(
        name="ban",
        aliases=['banish']
    )
    @has_permissions(ban_members=True)
    async def ban(
        self: "Moderation",
        ctx: Context,
        member: Member,
        *,
        reason: str = "N/A"
    ):
        """
        Ban a member from your guild
        """

        await ctx.guild.ban(
            member,
            reason=ctx.author.name + f" - {reason}"
        )
        
        return await ctx.send("👍", delete_after=3)
    
async def setup(bot: Blare) -> None:
    await bot.add_cog(Moderation(bot))
