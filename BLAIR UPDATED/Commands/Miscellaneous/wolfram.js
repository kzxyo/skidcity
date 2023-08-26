const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const WolframAlpha = require('@dguttman/wolfram-alpha-api'), wolframAlphaApi = WolframAlpha(process.env.WOLFRAM_ALPHA_KEY)

module.exports = class Wolfram extends Command {
    constructor (bot) {
        super (bot, 'wolfram', {
            description : 'Search a query on Wolfram Alpha.',
            parameters : [ 'query' ],
            syntax : '(query)',
            example : 'Solve for x: 3x + 7 = 22',
            aliases : [ 'wolframalpha', 'wa', 'w' ],
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args) {
        try {
            if (!args[0]) {
                return bot.help(
                    message, this
                )
            }

            await wolframAlphaApi.getShort(args.join(' ')).then((results) => {
                message.reply({
                    content : results
                })
            }, () => {
                return message.reply({
                    content : 'No answer available.'
                })
            })
        } catch (error) {
            return bot.error(
                message, 'wolfram', error
            )
        }
    }
}