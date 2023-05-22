const Command = require('../../Structures/Base/Command.js')

const { EmbedBuilder } = require('discord.js')

module.exports = class CopyEmbed extends Command {
    constructor (Client) {
        super (Client, 'copyembed', {
            Aliases : [ 'embedcode' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        try {
            var MessageID = Arguments[0], ChannelID = Message.channel.id, URL = `https://discord.com/channels/${Message.guild.id}/${Message.channel.id}/${Arguments[0]}`

            if (isNaN(Arguments[0])) {
                const IDs = []
                
                if (!Arguments[0].startsWith('https://discord.com/channels/') && !Arguments[0].startsWith('https://canary.discord.com/channels/')) {
                    return new Client.Response(
                        Message, `Invalid **Message Link** was provided in your arguments. Try again.`
                    )
                }

                for (const ID of String(Arguments[0]).replace('https:', '').replace('discord.com', '').replace('canary.discord.com', '').replace('channels', '').split('/')) { 
                    if (ID.length > 0) IDs.push(ID) 
                }
                
                if (isNaN(IDs[0]) || isNaN(IDs[1]) || isNaN(IDs[2]) || IDs[0] && IDs[1] && !IDs[2] || IDs[0] && !IDs[1] && !IDs[2]) {
                    return new Client.Response(
                        Message, `Invalid format for **Message Link**.`
                    )
                }

                MessageID = IDs[2], ChannelID = IDs[1], URL = Arguments[0]
            }
            
            const Channel = Message.guild.channels.cache.get(ChannelID)

            if (!Channel) { 
                return new Client.Response(
                    Message, `Couldn't find a **Channel** with that ID.`
                )
            }

            try { 
                await Channel.messages.fetch(MessageID) 
            } catch (Error) {
                return new Client.Response(
                    Message, `Couldn't find a **Message** with that ID.`
                )
            }
            
            const MessageX = await Channel.messages.fetch(MessageID)

            if (!MessageX.embeds || !MessageX.embeds.length) { 
                return new Client.Response(
                    Message, `Message [${MessageX.id}](${URL}) does not contain any embeds.`
                )
            }

            const EmbedCode = Syntax(MessageX.Content, MessageX.embeds[0])

            return new Client.Response(
                Message, `Copied [${MessageX.id}](${URL})'s embed code.\`\`\`${EmbedCode}\`\`\``
            )
        } catch (Error) {
            return new Client.Error(
                Message, 'copyembed', Error
            )
        }
    }
}

function Syntax (Content, Embed) {
    console.log(Embed)
    const EmbedCode = []

    if (Content) EmbedCode.push(`}$v{message: ${Content}`)

    if (Embed.author) {
        if (Embed.author.name) {
            EmbedCode.push(`}$v{author: ${Embed.author.name}`)
        }
        if (Embed.author.iconURL) {
            EmbedCode.push(` && ${Embed.author.iconURL}`)
        }
        if (Embed.author.url) {
            EmbedCode.push(` && ${Embed.author.url}`)
        }
    }

    if (Embed.title) EmbedCode.push(`}$v{title: ${Embed.title}`)

    if (Embed.url) EmbedCode.push(`}$v{url: ${Embed.url}`)

    if (Embed.description) EmbedCode.push(`}$v{description: ${Embed.description}`)

    if (Embed.fields) {
        for (const Field of Embed.fields) {
            EmbedCode.push(`}$v{field: ${Field.name} && ${Field.value}${Field.inline === true ? ' inline' : ''}`)
        }
    }

    if (Embed.footer) {
        if (Embed.footer.text) {
            EmbedCode.push(`}$v{footer: ${Embed.footer.text}`)
        }
        if (Embed.footer.iconURL) {
            EmbedCode.push(` && ${Embed.footer.iconURL}`)
        }
    }

    if (Embed.image) {
        EmbedCode.push(`}$v{image: ${Embed.image.url}`)
    }

    if (Embed.thumbnail) {
        EmbedCode.push(`}$v{thumbnail: ${Embed.thumbnail.url}`)
    }

    if (Embed.timestamp) EmbedCode.push(`}$v{timestamp`)

    if (Embed.color) EmbedCode.push(`}$v{color: ${Embed.hexColor}`)
    
    return '{embed}$v' + EmbedCode[0].replace('}$v', '') + EmbedCode.slice(1).join('') + '}'
}