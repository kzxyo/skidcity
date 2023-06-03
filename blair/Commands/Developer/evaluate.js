const Command = require('../../Structures/Base/Command.js')

module.exports = class Evaluate extends Command {
    constructor (Client) {
        super (Client, 'evaluate', {
            Aliases : [ 'eval' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        if (Message.author.id !== '944099356678717500') return

        const Script = Arguments.join(' ').replace('```', '')

        try {
            var Evaluated
            try {
                Evaluated = await eval(Script)
            } catch (Error) {
                console.log(Error)
                return Message.react('‼️')
            }

            if (typeof Evaluated !== 'string') Evaluated = require('util').inspect(Evaluated)

            Script.length > 30 ? Message.react('▶️') : null 

            Message.react('✅')

            console.log(Evaluated)
        } catch (Error) {
            return new Client.Error(
                Message, 'evaluate', Error
            )
        }
    }
}