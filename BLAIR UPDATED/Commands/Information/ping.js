const Command = require('../../Structures/Base/command.js')

module.exports = class Ping extends Command {
    constructor (bot) {
        super (bot, 'ping', {
            description : 'Show websocket latency',
            aliases : [ 'latency' ],
            module : 'Information'
        })
    }

    async execute (bot, message, args) {
        try {
            const msg = await message.channel.send(`gateway: **${bot.ws.ping}ms**`)
            
            const random = Math.floor(Math.random() * [1, 2, 3, 4, 5, 6, 7, 8, 9].length)
            const difference = (msg.editedAt || msg.createdAt) - (message.editedAt || message.createdAt)
            
            await msg.edit(`gateway: **${bot.ws.ping}ms** (edit: ${difference}.${random})`)
        } catch (error) {
            return bot.error(
                message, 'ping', error
            )
        }
    }
}