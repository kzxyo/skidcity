const Command = require('../../Structures/Base/Command.js')

module.exports = class AFK extends Command {
    constructor (Client) {
        super (Client, 'afk', {
            Aliases : [ 'away' ]
        })
    }
    
    async Invoke (Client, Message, Arguments) {
        const Status = Arguments.join(' ') || 'AFK'
        
        Client.AFK.set(Message.author.id, [Status, Message.createdTimestamp])

        new Client.Response(
            Message, `You've been set as **Away** with the status: ${Status}`
        )
    }
}