const Command = require('../../Structures/Base/command.js')

module.exports = class Move extends Command {
    constructor (bot) {
        super (bot, 'move', {
            description : 'Change the position of a song in the queue',
            parameters : [ 'from', 'to' ],
            syntax : '(from) (to)',
            example : '7 1',
            aliases : [ 'mv', 'reorder' ],
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

            const from = args[0], to = args[1]

            const queue = player.queue

            const adjustedFrom = from - 1
            const adjustedTo = to - 1

            if (adjustedFrom < 0 || adjustedFrom >= queue.size || adjustedTo < 0 || adjustedTo >= queue.size) {
                return
            }

            const tracks = Array.from(queue.values()), [ track ] = tracks.splice(adjustedFrom, 1)

            tracks.splice(adjustedTo, 0, track)

            queue.clear()

            player.queue.add(tracks)

            message.react('✅')

            message.approve(`Moved track at index **#${from}** to **#${to}**`)
        } catch (error) {
            return message.error(error)
        }
    }
}