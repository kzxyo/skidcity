const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'cashapp',
        aliases: ['ca'],
        description: 'View a CashApp profile',
        syntax: 'cashapp [username]',
        example: 'cashapp entxxs',
        permissions: 'N/A',
        parameters: 'username',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        if (args.length === 0) {
            return displayCommandInfo(module.exports, session, message);
        }

        const username = args[0];

        try {
            const response = await axios.get(`https://cash.app/${username}`);
            const profileRegex = /var profile = (.*?);<\/script>/s;
            const match = response.data.match(profileRegex);
            if (!match || match.length < 2) {
                throw new Error('Profile information not found in the response.');
            }

            const profileJsonStr = match[1];
            const profileJson = JSON.parse(profileJsonStr);
            const { display_name, avatar } = profileJson;

            const embed = new MessageEmbed()
                .setTitle(`${display_name} ($${username})`)
                .setURL(`https://cash.app/${username}`)
                .setImage(avatar.image_url)
                .setColor('#04cc54')

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error.message);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: API returned an errorr`)
                ]
            });
        }
    },
};
