const Command = require('../../Structures/Base/command.js')

const axios = require('axios')

module.exports = class Shazam extends Command {
    constructor (bot) {
        super (bot, 'shazam', {
        })
    }

    async execute (bot, message, args) {
        const URL = message.attachments.first().url || args[0]

        if (!URL) {
            return message.help()
        }

        const data = await axios.post(
            'https://dev.blair.win/shazam/recognize/?authorization=nick:3b0eac835f14e29003e82d0c1973f0bc', {
                url: URL
            }
        );

        if (data.status !== 200) {
            return message.channel.send(`didn't work lowkey`)
        }

        const a = data.data

        message.channel.send(`Found **${a.track.title}** by **${a.artist.name}**`)
    }
}