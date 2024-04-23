const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'color',
        aliases: ['clr'],
        description: 'Get a color\'s hex code',
        syntax: 'color <color>',
        example: 'color red',
        parameters: 'color',
        module: 'utility',
    },
    run: async (session, message, args) => {
        if (!args[0]) {
            return displayCommandInfo(module.exports, session, message);
        }
        const apiUrl = `https://api.rival.rocks/color?query=${encodeURIComponent(args[0])}`;

        try {
            const response = await axios.get(apiUrl);
            if (response.data && response.data.hex) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(response.data.hex)
                        .setDescription(`> ${message.author}: That colors hex code is **${response.data.hex}**`)
                ]});
            } else {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: No color found with that name`),
                ]});
            }
        } catch (error) {
            console.error('Error fetching color information:', error);
            return message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.error)
                    .setDescription(`${session.mark} ${message.author}: An error occurred, please contact support`)
            ]});
        }
    }
};
