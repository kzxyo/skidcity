const { MessageEmbed } = require('discord.js');
const axios = require('axios');
const qs = require('qs');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'itunes',
        aliases: ['itu'],
        description: 'Search iTunes for a song',
        syntax: 'itunes [query]',
        example: 'itunes patchmade',
        module: 'music'
    },

    run: async (session, message, args) => {
        try {
            if (!args[0]) {
                return displayCommandInfo(module.exports, session, message);
            }

            const query = qs.stringify({
                term: args.join(' '),
                entity: 'song'
            });

            const response = await axios.get(`https://itunes.apple.com/search?${query}`);

            if (!response.data.results.length) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: No results found for **${args.join(' ')}**`)
                ]});
            }

            message.channel.send(response.data.results[0].trackViewUrl);
        } catch (error) {
            console.error('Error while executing itunes command:', error);
            message.reply('An error occurred while searching on iTunes.');
        }
    }
};
