const { MessageEmbed } = require('discord.js');
const fs = require('fs');
const path = require('path');
const archiver = require('archiver');
const axios = require('axios');

module.exports = {
    configuration: {
        commandName: 'emojizip',
        aliases: ['zip'],
        description: 'Download all emojis and send in zip',
        syntax: 'emojizip',
        example: 'emojizip',
        permissions: 'manage_emojis',
        parameters: 'N/A',
        module: 'utility'
    },
    run: async (session, message, args) => {

        if (!message.member.permissions.has('MANAGE_EMOJIS')) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** the \`MANAGE_EMOJIS\` permission`)
                        .setColor(session.warn)
                ]
            });
        }

        const emojis = message.guild.emojis.cache.map(emoji => {
            if (emoji.url) {
                return { url: emoji.url, name: emoji.name }; // Custom emoji
            } else {
                return { url: emoji.identifier, name: emoji.name }; // Standard Discord emoji
            }
        });
        const zip = archiver('zip', { zlib: { level: 9 } });
        const outputFilePath = path.join(__dirname, '..', '..', 'emojis.zip');
        const output = fs.createWriteStream(outputFilePath);

        zip.pipe(output);

        try {
            for (const emoji of emojis) {
                const filename = emoji.name + path.extname(emoji.url);
                const response = await axios.get(emoji.url, { responseType: 'arraybuffer' });
                zip.append(response.data, { name: filename });
            }

            zip.finalize();

            output.on('close', () => {
                message.channel.send({
                    files: [{
                        attachment: outputFilePath,
                        name: 'emojis.zip'
                    }]
                }).then(() => {
                    fs.unlink(outputFilePath, (err) => {
                        if (err) {
                            console.error('Error deleting zip file:', err);
                        }
                    });
                });
            });

            output.on('error', (err) => {
                console.error('Output stream error:', err);
            });
        } catch (error) {
            console.error('Error fetching emojis:', error);
        }
    }
};
