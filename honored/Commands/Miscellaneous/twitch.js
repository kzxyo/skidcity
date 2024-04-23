const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'twitch',
        aliases: ['ttv'],
        description: 'Get Twitch user information',
        syntax: 'twitch [username]',
        example: 'twitch 7993',
        permissions: 'N/A',
        parameters: 'username',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        const username = args[0];

        if (!username) {
            return displayCommandInfo(module.exports, session, message);
        }

        const apiUrl = `https://api.rival.rocks/twitch?username=${encodeURIComponent(username)}&api-key=${session.rival}`;

        try {
            const response = await axios.get(apiUrl);
            const twitchData = response.data;

            const embed = new MessageEmbed()
                .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true }))
                .setColor(session.color)
                .setTitle(`${twitchData.display_name} (@${twitchData.username})`)
                .setURL(`https://www.twitch.tv/${twitchData.username}`)
                .setDescription(`${twitchData.description || 'No description available'}`)
                .addField('Followers', `${twitchData.followers}`)
                .setFooter(`Joined ${new Date(twitchData.created_at * 1000).toLocaleString()}`)
                .setThumbnail(`${twitchData.avatar}`);

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
