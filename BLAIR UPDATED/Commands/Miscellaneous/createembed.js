const Command = require('../../Structures/Base/command.js')

module.exports = class CreateEmbed extends Command {
    constructor (bot) {
        super (bot, 'createembed', {
            description : 'Send an embed',
            permissions : [ 'ManageMessages' ],
            parameters : [ 'embed script' ],
            syntax : '(embed script)',
            example : '{embed: $title: YO!!!11}',
            aliases : [ 'embed', 'ce' ],
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args) {
        try {
            if (!args[0]) {
                return bot.warn(
                    message, `Missing **content** to parse`
                )
            }

            const code = await bot.variables.convert(
                args.join(' '), {
                    user : message.author,
                    member : message.member,
                    guild : message.guild,
                    channel : message.channel,
                    message : message,
                    if : true
                }
            )

            const script = new bot.MessageParser(bot, code)

            message.channel.send(script).catch((error) => {
                return bot.warn(
                    message, `Invalid **script**\`\`\`${error.message}\`\`\``,
                )
            })
        } catch (error) {
            return bot.error(
                message, 'createembed', error
            )
        }
    }
}