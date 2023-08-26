const Command = require('../../Structures/Base/command.js')

module.exports = class Disconnect extends Command {
    constructor (bot) {
        super (bot, 'disconnect', {
            description : 'End the current session',
            aliases : [ 'dc', 'stop' ],
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

            await player.destroy()

            message.react('👋')
        } catch (error) {
            return message.error(error)
        }
    }
}