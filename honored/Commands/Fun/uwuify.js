const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'uwuify',
        aliases: ['uwu'],
        description: 'Uwuify a string of text',
        syntax: 'uwuify [text]',
        example: 'uwuify i love you',
        parameters: 'text',
        module: 'fun'
    },
    run: async (session, message, args) => {
        try {
            const text = args.join(' ');

            if (!text) {
                return displayCommandInfo(module.exports, session, message);
            }

            const response = await axios.get(`https://nekos.life/api/v2/owoify?text=${encodeURIComponent(text)}`);

            const uwuText = response.data.owo;

            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.color)
                        .setDescription('> ' + uwuText)
                ]
            });
        } catch (error) {
            console.error('Error uwuifying text:', error);
            message.channel.send('An error occurred while uwuifying text.');
        }
    }
};
