const { MessageEmbed } = require("discord.js");
const marriageFilePath = '/root/rewrite/Database/Users/marriage.json';
const fs = require('fs');

module.exports = {
    configuration: {
        commandName: 'marriage',
        aliases: ['married'],
        description: 'See who a user is married to',
        syntax: 'marriage <member>',
        example: 'marriage @x6l',
        module: 'fun',
    },
    run: async (session, message, args) => {
        const marriageData = loadMarriageData();
        let targetId;

        if (message.mentions.users.size > 0) {
            targetId = message.mentions.users.first().id;
        } else {
            targetId = message.author.id;
        }

        if (targetId in marriageData) {
            const spouseId = marriageData[targetId];
            const spouse = message.guild.members.cache.get(spouseId);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.color)
                        .setDescription(`💒 ${message.author}: You're married to ${spouse}`)
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

function loadMarriageData() {
    try {
        const data = fs.readFileSync(marriageFilePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('Error loading marriage data:', error);
        return {};
    }
}