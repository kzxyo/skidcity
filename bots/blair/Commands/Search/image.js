const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

const Google = require('googlethis')

module.exports = class Image extends Command {
    constructor (Client) {
        super (Client, 'image', {
            Aliases : [ 'im', 'img' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        if (!Arguments[0]) {
            return new Client.Help(
                Message, {
                    About : 'Search for images through Google search engine.',
                    Syntax : 'image (Search)'
                }
            )
        }

        try {
            Message.channel.sendTyping()

            const Images = await Google.image(Arguments.join(' '), { 
                safe : true 
            })

            const Embeds = []
            for (const Image of Images) {
                Embeds.push(new EmbedBuilder({
                    title : `${Image.origin.website.name} (${Image.origin.website.domain})`,
                    description : `[${Image.origin.title}](${Image.origin.website.url})`
                }).setImage(Image.url).setColor(Client.Color))
            }

            if (Embeds.length > 1) { 
                const Paginator = new Client.Paginator(Message)
                
                Paginator.SetEmbeds(Embeds)
                
                await Paginator.Send()
            } else { 
                return Message.channel.send({ 
                    embeds: [
                        Embeds[0]
                    ] 
                }) 
            }
        } catch (Error) {
            return new Client.Response(
                Message, `Couldn't find any **Image Search** results for that.`
            )
        }
    }
}