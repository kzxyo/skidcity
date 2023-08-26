const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const { WiktionaryParser } = require('parse-wiktionary')

module.exports = class Dictionary extends Command {
    constructor (bot) {
        super (bot, 'dictionary', {
            description : 'Show the definition of a word',
            parameters : [ 'word' ],
            syntax : '(word)',
            example : 'brah',
            aliases : [ 'definition', 'define' ],
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args) {
        try {
const parser = new WiktionaryParser();
const englishResults = await parser.parse(args[0]);
console.log(englishResults[0].definitions)
        } catch (error) {
            return bot.error(
                message, 'dictionary', error
            )
        }
    } 
}