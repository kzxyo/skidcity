const fs = require('fs');
const { MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'work',
        aliases: ['none'],
        description: 'Work to earn coins',
        module: 'fun',
        syntax: 'work',
        example: 'work'
    },
    run: async (session, message, args) => {
        const balancePath = '/root/rewrite/Database/Money/balance.json';

        const userId = message.author.id;
        const coinsEarned = Math.floor(Math.random() * (200 - 120 + 1) + 120);

        let balanceData = {};

        if (fs.existsSync(balancePath)) {
            const rawData = fs.readFileSync(balancePath);
            balanceData = JSON.parse(rawData);
        }

        if (!balanceData[userId]) {
            balanceData[userId] = 0;
        }

        balanceData[userId] += coinsEarned;

        fs.writeFileSync(balancePath, JSON.stringify(balanceData, null, 2));

        const embed = new MessageEmbed()
            .setColor('GREEN')
            .setDescription(`:money_with_wings: ${message.author}: You worked and earned ${coinsEarned} coins`);

        return message.channel.send({ embeds: [embed] });
    }
};
