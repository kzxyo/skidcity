const fs = require('fs');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'donate',
        aliases: ['give'],
        description: 'Donate money to another member',
        syntax: 'donate <user> (amount)',
        example: 'donate @x6l 1000',
        parameters: 'member, amount',
        module: 'fun'
    },

    run: async (session, message, args) => {
        const balancePath = '/root/rewrite/Database/Money/balance.json';
        const userId = message.author.id;
        let amount = 0;
        let targetId;
        let balanceData = {};

        if (fs.existsSync(balancePath)) {
            const rawData = fs.readFileSync(balancePath);
            balanceData = JSON.parse(rawData);
        }

        if (!balanceData[userId]) {
            balanceData[userId] = 0;
        }

        if (message.mentions.users.size > 0) {
            targetId = message.mentions.users.first().id;
        } else {
            return displayCommandInfo(module.exports, session, message);
        }

        if (!balanceData[targetId]) {
            balanceData[targetId] = 0;
        }

        if (args[1] === 'all') {
            amount = balanceData[userId];
        } else if (args[1] === 'half') {
            amount = Math.floor(balanceData[userId] / 2);
        } else {
            amount = parseInt(args[1]);

            if (isNaN(amount) || amount <= 0) {
                return displayCommandInfo(module.exports, session, message);
            }

            if (amount > balanceData[userId]) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: You don't have enough coins`)

                    ]
                });
            }
        }

        balanceData[userId] -= amount;
        balanceData[targetId] += amount;

        fs.writeFileSync(balancePath, JSON.stringify(balanceData, null, 4));

        message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setColor('GREEN')
                    .setDescription(`💸 ${message.author}: You donated ${amount} coins to <@${targetId}>`)
            ]
        });

    }

}