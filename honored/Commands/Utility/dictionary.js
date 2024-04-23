const { MessageEmbed } = require('discord.js');
const { WiktionaryParser } = require('parse-wiktionary');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'dictionary',
        aliases: ['definition', 'define'],
        description: 'Show the definition of a word',
        syntax: 'dictionary [word]',
        example: 'dictionary cool',
        permissions: 'N/A',
        parameters: 'word',
        module: 'utility'
    },
    run: async (session, message, args) => {
        try {
            if (!args[0]) {
                return displayCommandInfo(module.exports, session, message);
            }

            const parser = new WiktionaryParser();
            const englishResults = await parser.parse(args[0]);
            const definitions = englishResults[0].definitions;

            const formattedDefinitions = definitions.map(def => `${def.text}`).join('\n');

            const embed = new MessageEmbed()
                .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true }))
                .setColor(session.color)
                .setTitle(`Word: ${args[0]}`)
                .setDescription(formattedDefinitions)

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            console.error(error);
            message.channel.send(`An error occurred: ${error.message}`);
        }
    }
};
