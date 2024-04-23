const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const pagination = require("/root/rewrite/Utils/paginator.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'google',
        aliases: ['g'],
        description: 'Search Google and display the top results',
        syntax: 'google <query>',
        example: 'google cats',
        permissions: 'N/A',
        parameters: 'query',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        const query = args.join(' ');

        if (!query) {
            return displayCommandInfo(module.exports, session, message);
        }

        const apiUrl = `https://api.rival.rocks/google/search?query=${encodeURIComponent(query)}&safe=false&limit=10&api-key=${session.rival}`;

        try {
            const response = await axios.get(apiUrl);
            const searchResults = response.data.slice(0, 10);
            const embeds = searchResults.map(result => (
                new MessageEmbed()
                    .setColor(session.color)
                    .setTitle(result.title)
                    .setDescription(`Website: [**${result.website}**](${result.url})`)
            ));

            pagination(session, message, embeds, 10, '', `(10 entries)`);
        } catch (error) {
            console.error('Error fetching Google search results:', error.message);
            message.channel.send('An error occurred while fetching Google search results.');
        }
    }
};
