const { MessageEmbed } = require("discord.js");
const marriageFilePath = '/root/rewrite/Database/Users/marriage.json';
const fs = require('fs');

module.exports = {
    configuration: {
        commandName: 'divorce',
        aliases: ['dvc'],
        description: 'Divorce your partner',
        syntax: 'divorce',
        example: 'divorce',
        module: 'fun',
    },
    run: async (session, message, args) => {
        const marriageData = loadMarriageData();
        const authorId = message.author.id;

        if (authorId in marriageData) {
            const spouseId = marriageData[authorId];
            delete marriageData[authorId];
            delete marriageData[spouseId];
            saveMarriageData(marriageData);

            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor('#dc2c44')
                        .setDescription(`💔 ${message.author}: You've divorced your partner`)
                ]
            });
        }

        message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: You're not married to anyone`)
            ]
        });
    }
};

function saveMarriageData(data) {
    fs.writeFileSync(marriageFilePath, JSON.stringify(data, null, 4));
}

function loadMarriageData() {
    try {
        const data = fs.readFileSync(marriageFilePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('Error loading marriage data:', error);
        return {};
    }
}
