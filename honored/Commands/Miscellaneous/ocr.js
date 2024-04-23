const { MessageEmbed } = require('discord.js');
const axios = require('axios');
const formdata = require('form-data');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'ocr',
        aliases: ['read'],
        description: 'Extract text from an image',
        syntax: 'ocr [attachment]',
        example: 'ocr meow.png',
        permissions: 'N/A',
        parameters: 'attachment',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        let imageURL;

        if (message.attachments.size === 1) {
            imageURL = message.attachments.first().url;
        } else if (args.length === 1 && (args[0].startsWith('http://') || args[0].startsWith('https://'))) {
            imageURL = args[0];
        } else {
            return displayCommandInfo(module.exports, session, message);
        }
        const data = new formdata();
        data.append('url', imageURL);
        data.append('language', 'eng');
        data.append('scale', 'true');
        data.append('OCREngine', '2');

        try {
            const response = await axios.post('https://api.ocr.space/parse/image', data, {
                headers: {
                    apikey: 'K84848884588957',
                    ...data.getHeaders()
                },
                maxContentLength: Infinity,
                maxBodyLength: Infinity
            });
            const text = response.data?.ParsedResults?.[0]?.ParsedText;

            if (text !== undefined) {
                const results = new MessageEmbed()
                    .setAuthor(message.author.username, message.author.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                    .setColor(session.color)
                    .setDescription(`\`\`\`${text}\`\`\``);

                message.channel.send({ embeds: [results] });
            } else {
                const error = new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: Couldn't extract text from that image`);

                message.channel.send({ embeds: [error] });
            }
        } catch (error) {
            console.error(error);

            const errorEmbed = new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${message.author}: Couldn't extract text from that image`);

            message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
