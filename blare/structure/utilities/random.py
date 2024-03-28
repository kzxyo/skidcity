from discord import Message

def dump(message: Message):
    return {
        "guild": {
            "id": message.guild.id,
            "name": message.guild.name,
            "chunked": message.guild.chunked,
            "member_count": message.guild.member_count,
        },
        "channel": {
            "id": message.channel.id,
            "name": message.channel.name,
            "position": message.channel.position,
            "category_id": message.channel.category_id
        },
        "author": {
            "name": message.author.name,
            "id": message.author.id,
            "discriminator": message.author.discriminator,
            "bot": message.author.bot,
            "nick": message.author.nick,
            "avatar": message.author.avatar.url if message.author.avatar else None,
        },
        "attachments": [
            attachment.url
            for attachment in (
                message.attachments + list(
                    (embed.thumbnail or embed.image) 
                    for embed in message.embeds 
                    if embed.type == "image"
                )
            )
        ],
        "stickers": [
            sticker.url 
            for sticker in message.stickers
        ],
        "embeds": [
            embed.to_dict() 
            for embed in message.embeds[:8] 
            if not embed.type == "image" 
            and not embed.type == "video"
        ],
        "content": message.content,
        "timestamp": message.created_at.timestamp(),
        "id": message.id,
    }
