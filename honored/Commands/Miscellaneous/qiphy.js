const giphy = require('giphy')('4jpa0aSb0eF3ZQ0BUz4ngrGhuoYScG31');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'giphy',
        aliases: ['gif'],
        description: 'Search Giphy for a GIF.',
        syntax: 'giphy [query]',
        example: 'giphy cat',
        permissions: 'N/A',
        parameters: 'query',
        module: 'miscellaneous',
    },
    run: async (session, message, args) => {
        const query = args.join(' ');

        if (!query) {
            return displayCommandInfo(module.exports, session, message);  
        }

        try {
            giphy.search({ q: query }, (err, response) => {
                if (err) {
                    console.error('Error searching Giphy:', err);
                    return message.channel.send({ embeds: [
                        new MessageEmbed()
                            .setColor(session.error)
                            .setDescription(`${session.mark} ${message.author}: An error occurred while searching Giphy`)
                    ]});
                }

                if (!response || response.data.length === 0) {
                    return message.channel.send({ embeds: [
                        new MessageEmbed()
                            .setColor(session.error)
                            .setDescription(`${session.mark} ${message.author}: No results found`)
                    ]});
                }

                const gif = response.data[0];

                message.channel.send({ content: gif.url });
            });
        } catch (error) {
            session.log('Error:', error)
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.error)
                    .setDescription(`${session.mark} ${message.author}: The API returned an error`)
            ]});
        }
    },
};
