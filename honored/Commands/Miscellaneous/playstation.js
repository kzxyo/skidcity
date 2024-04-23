const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration : {
        commandName: 'playstation',
        aliases: ['psn'],
        syntax: 'playstation [username]',
        example: 'playstation rust',
        permissions: 'N/A',
        parameters: 'username',
        description: 'Search for a playstation profile',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        if (!args.length) {
            return displayCommandInfo(module.exports, session, message);
        }

        const username = args[0];

        try {
            const url = `https://psnprofiles.com/${username}`;
            const response = await axios.get(url);
            const ogTitle = response.data.match(/<meta property="og:title" content="(.*?)" \/>/)[1];
            const ogDescription = response.data.match(/<meta property="og:description" content="(.*?)" \/>/)[1];
            const ogImage = response.data.match(/<meta property="og:image" content="(.*?)" \/>/)[1];
            const ogUrl = response.data.match(/<meta property="og:url" content="(.*?)" \/>/)[1];

            const embed = new MessageEmbed()
                .setTitle(`${username}`)
                .setDescription(ogDescription)
                .setImage(ogImage)
                .setURL(ogUrl)
                .setFooter('Playstation', 'https://lains.win/playstation.png')
                .setColor(session.color);

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error);
            message.channel.send({ embeds: [
                new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: API returned an error`)
            ]});
        }
    },
};
