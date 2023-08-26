const Command = require('../../Structures/Base/command.js')

const { fetch } = require('undici')

module.exports = class SoundCloud extends Command {
    constructor (bot) {
        super (bot, 'soundcloud', {
            description : 'Search for a song on SoundCloud',
            parameters : [ 'query' ],
            syntax : '(query)',
            example : '1017 alyx',
            aliases : [ 'sc' ],
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
            
            const results = await fetch(`https://api-v2.soundcloud.com/search/tracks?q=${args.join(' ')}`, {
                method : 'GET',
                headers : {
                    'Authorization': `OAuth ${process.env.SOUNDCLOUD_API_KEY}`
                }
            }).then((response) => response.json()).catch((error) => {
                return bot.warn(
                    message, `Bad response (\`${error.response.status}\`) from the **API**`
                )
            })

            if (!results.collection.length) {
                return bot.warn(
                    message, `No results found for **${args.join(' ')}**`
                )
            }

            message.reply(`${results.collection[0].permalink_url}`)

            if (!args[0]) {
                return bot.help(
                    message, this
                )
            }
        } catch (error) {
            return bot.error(
                message, 'soundcloud', error
            )
        }
    }
}