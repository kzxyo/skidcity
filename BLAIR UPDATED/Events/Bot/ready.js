const Event = require('../../Structures/Base/event.js')

module.exports = class Ready extends Event {
    constructor (bot) {
        super (bot, 'ready', {
            once : true
        })
    }

    async execute (bot) {
        try {
            console.log(`Connected to Discord`)

            bot.Lavalink.init(bot.user.id)

            bot.on('raw', (packet) => bot.Lavalink.updateVoiceState(packet))
        } catch (error) {
            return console.error('Ready', error)
        }
    }
}