const Command = require('../../Structures/Base/command.js')

module.exports = class Skip extends Command {
    constructor (bot) {
        super (bot, 'skip', {
            description : 'Skip to the next song in the queue',
            aliases : [ 'sk', 'next' ],
            module : 'Music'
        })
    }

    async execute (bot, message, args) {
        try {
            if (!message.member.voice.channel) {
                return message.warn(`You aren't connected to a **voice channel**`)
            }

            const player = bot.Lavalink.get(message.guild.id)

            if (!player) {
                return message.warn(`There isn't a **player** currently active`)
            }

            if (message.member.voice.channel.id !== message.guild.members.me.voice.channel.id) {
                return message.warn(`You're in a different **voice channel** than me`)
            }

            if (player.queue.size === 0) {
                return message.warn(`The queue is **empty**; there aren't any songs`)
            }

            await player.stop()

            message.react('⏭️')
        } catch (error) {
            return message.error(error)
        }
    }
}