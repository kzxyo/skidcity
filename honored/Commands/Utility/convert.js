const axios = require('axios');
const ffmpeg = require('fluent-ffmpeg');
const fs = require('fs');
const path = require('path');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'convert',
        aliases: ['mp3'],
        description: 'Convert a video to an MP3',
        syntax: 'convert [file]',
        example: 'convert yeat.mov',
        permissions: 'N/A',
        parameters: 'file',
        module: 'utility',
    },
    run: async (session, message, args) => {
        if (!message.attachments.first()) {
            return displayCommandInfo(module.exports, session, message);
        }

        const attachment = message.attachments.first();
        const fileName = attachment.name;
        const fileExtension = path.extname(fileName);

        if (!['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm'].includes(fileExtension)) {
            return displayCommandInfo(module.exports, session, message);    
        }

        const inputFilePath = path.join(__dirname, fileName);
        const outputFileName = 'lain.mp3';
        const outputFilePath = path.join(__dirname, outputFileName);

        try {
            const response = await axios.get(attachment.url, { responseType: 'stream' });
            const writer = fs.createWriteStream(inputFilePath);
            response.data.pipe(writer);

            await new Promise((resolve, reject) => {
                writer.on('finish', resolve);
                writer.on('error', reject);
            });
            ffmpeg(inputFilePath)
                .outputOptions('-vn')
                .output(outputFilePath)
                .on('end', () => {
                    message.channel.send({
                        files: [{
                            attachment: outputFilePath,
                            name: outputFileName
                        }]
                    }).then(() => {
                        fs.unlinkSync(inputFilePath);
                        fs.unlinkSync(outputFilePath);
                    }).catch(error => {
                        console.error('Error sending MP3:', error);
                        message.channel.send({ embeds: [
                            new MessageEmbed()
                                .setColor(session.warn)
                                .setDescription(`${session.mark} ${message.author}: An error occurred while converting the MP3`)
                        ]});
                    });
                })
                .on('error', (error) => {
                    console.error('Error converting video to MP3:', error);
                    message.channel.send({ embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: An error occurred while converting the MP3`)
                    ]});
                })
                .run();
        } catch (error) {
            console.error('Error downloading video:', error);
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: An error occurred while converting the MP3`)
            ]});
        }
    }
};
