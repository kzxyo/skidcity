const Command = require('../../Structures/Base/command.js')

module.exports = class Dominant extends Command {
    constructor (bot) {
        super (bot, 'dominant', {
            description : 'Get the dominant color of an image',
            parameters : [ 'image' ],
            syntax : '(image)',
            example : '.../attachments/...',
            aliases : [ 'extract' ],
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args) {
        try {
            const attachment = await bot.converters.attachment(
                message, args.join(' '), {
                    types : [
                        'attachment', 'message', 'reference', 'member'
                    ],
                    finder : true
                }
            )

            if (!attachment) return message.reply('bra there aint no attachment')

            const color = await bot.converters.color(
                '', {
                    dominant : attachment.url
                }
            )

            if (!color) return message.reply('How is there no color??')

            bot.neutral(
                message, `The dominant color is **${color}**`, {
                    color : color
                }
            )
        } catch (error) {
            return bot.error(
                message, 'dominant', error
            )
        }
    }
}