const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'roblox',
        aliases: ['rblx'],
        description: 'Get Roblox user information',
        syntax: 'roblox [username]',
        example: 'roblox builderman',
        permissions: 'N/A',
        parameters: 'username',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        const username = args[0];

        if (!username) {
            return displayCommandInfo(module.exports, session, message);
        }
        try {
            const response = await axios.get(`https://api.rival.rocks/roblox?username=${encodeURIComponent(username)}&api-key=${session.rival}`);
            const robloxData = response.data;

            const embed = new MessageEmbed()
                .setColor(session.color)
                .setTitle(`${robloxData.display_name} (${robloxData.username})`)
                .setURL(robloxData.url)
                .setDescription(`${robloxData.description || 'No bio available'}`)
                .addField('Friends', `${robloxData.statistics.friends}`, true)
                .addField('Followers', `${robloxData.statistics.followers}`, true)
                .addField('Following', `${robloxData.statistics.following}`, true)
                .addField('Badges', `${robloxData.badges.join(', ') || 'No badges'}`)
                .setImage(`${robloxData.avatar_url}`);

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log("Error:", error.message);
            const errorEmbed = new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${message.author}: API returned an errorr`);
            return message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
