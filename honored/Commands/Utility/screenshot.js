const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const { MessageAttachment, MessageEmbed } = require('discord.js');
const axios = require('axios');

module.exports = {
    configuration: {
        commandName: 'screenshot',
        aliases: ['ss'],
        description: 'Takes a screenshot of a website',
        syntax: 'screenshot [url]',
        example: 'screenshot honored.rip',
        parameters: 'url',
        module: 'utility'
    },
    run: async (session, message, args) => {
        try {
            const url = args[0];
            if (!url) {
                return displayCommandInfo(module.exports, session, message);
            }

            const loadingEmbed = await message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.color)
                    .setDescription(`> ${message.author} Taking a screenshot of **${url}**`)
            ]});

            const apiUrl = `https://api.rival.rocks/screenshot?url=${encodeURIComponent(url)}&safe=true&full_page=false&wait=0&response_type=file&api-key=${session.rival}`;
            const response = await axios.get(apiUrl, { responseType: 'arraybuffer' });
            const screenshotAttachment = new MessageAttachment(response.data, 'screenshot.png');

            const embed = new MessageEmbed()
                .setTitle('Screenshot')
                .setDescription(`Screenshot of **${url}**`)
                .setImage('attachment://screenshot.png')
                .setColor(session.color);

            await message.channel.send({ embeds: [embed], files: [screenshotAttachment] });

            await loadingEmbed.delete();
        } catch (error) {
            console.error('Error taking screenshot:', error);
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: Couldn't take a screenshot of that page ( probably nsfw or doesnt exist )`)
            ]});
        }
    }
};
