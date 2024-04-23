const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'generate',
        aliases: ['ai'],
        description: 'Generate an image based on a prompt',
        syntax: 'generate <prompt>',
        example: 'generate a cat in space',
        module: 'fun'
    },
    run: async (session, message, args) => {
        const prompt = args.join(' ');

        if (!prompt) {
            return displayCommandInfo(module.exports, session, message);
        }

        const loadingEmbed = await message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setColor(session.color)
                    .setDescription(`<a:w_loading:1229150546590695525> ${message.author}: Generating image`)
            ]
        });

        const apiUrl = `https://api.rival.rocks/image/generation?prompt=${encodeURIComponent(prompt)}&api-key=${session.rival}`;

        try {
            const response = await axios.get(apiUrl);
            const imageData = response.data;
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setImage(imageData.url);

            loadingEmbed.edit({ embeds: [embed] });
        } catch (error) {
            console.error('Error generating image:', error.message);
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: Couldn't generate an image based on that prompt`)
            ]});
        }
    }
};
