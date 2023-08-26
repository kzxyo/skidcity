const Command = require('../../Structures/Base/command.js')

const { fetch } = require('undici'), qs = require('qs')

module.exports = class iTunes extends Command {
    constructor (bot) {
        super (bot, 'itunes', {
            description : 'Search for a song on iTunes',
            parameters : [ 'query' ],
            syntax : '(query)',
            example : '9SM',
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args, prefix) {
        try {
            if (!args[0]) {
                return bot.help(
                    message, this, prefix
                )
            }

            const query = qs.stringify({
                term : args.join(' '),
                entity : 'song'
            })

            const results = await fetch(`https://itunes.apple.com/search?${query}`, {
                method : 'GET'
            }).then((response) => response.json()).catch((error) => {
                return bot.warn(
                    message, `Bad response (\`${error.response.status}\`) from the **API**`
                )
            })

            if (!results.results.length) {
                return bot.warn(
                    message, `No results found for **${args.join(' ')}**`
                )
            }

            message.reply(`${results.results[0].trackViewUrl}`)
        } catch (error) {
            return bot.error(
                message, 'itunes', error
            )
        }
    }
}