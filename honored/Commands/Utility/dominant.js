const { MessageEmbed } = require('discord.js');
const { getColor } = require('colorthief')
const axios = require('axios')
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'dominant',
        aliases: ['hex'],
        description: 'Get the dominant color of an image',
        syntax: 'dominant <attachment>',
        example: 'dominant color.png',
        parameters: 'attachment',
        module: 'utility'
    },
    run: async (session, message, args) => {
        const attachment = message.attachments.first();
        if (!attachment || !attachment.url) {
            return displayCommandInfo(module.exports, session, message);
        }
        try {
            const response = await axios.get(attachment.url, {
                responseType: 'arraybuffer'
            });
            const buffer = Buffer.from(response.data, 'binary');
            const color = await getColor(buffer);
            const hexColor = rgbToHex(color[0], color[1], color[2]);
            const embed = new MessageEmbed()
                .setColor(hexColor)
                .setDescription(`> ${message.author}: The dominant color of the image is **${hexColor}**`);

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            console.error('Error getting dominant color:', error);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: This does not support .webp files`)
                ]
            });
        }
    }
};

function rgbToHex(r, g, b) {
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}