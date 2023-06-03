const Command = require('../../Structures/Base/Command.js')

module.exports = class CreateEmbed extends Command {
    constructor (Client) {
        super (Client, 'createembed', {
            Aliases : [ 'ce' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        if (!Arguments[0]) {
            return new Client.Help(
                Message, {
                    About : 'Create an embed.'
                }
            )
        }

        try {
            const Content = new Client.Variables(Arguments.join(' '))

            const Code = await Content.Replace({ 
                User : Message.author, 
                Member : Message.member, 
                Guild : Message.guild
            })

            const Embed = new Client.EmbedParser(Code)

            Message.channel.send(Embed).catch((Error) => {
                console.log(Error.message)
                return new Client.Response(
                    Message, `Error\n\`\`\`${Error.message}\`\`\``
                )
            })
        } catch (Error) {
            return new Client.Error(
                Message, 'createembed', Error
            )
        }
    }
}