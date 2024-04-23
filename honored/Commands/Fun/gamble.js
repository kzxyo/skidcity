const fs = require('fs');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'gamble',
        aliases: ['none'],
        description: 'Gamble your coins for a chance to win or lose',
        syntax: 'gamble <amount>',
        example: 'gamble 100',
        module: 'fun',
        subcommands: ['> gamble all\n> gamble half']
    },
    run: async (session, message, args) => {
        const balancePath = '/root/rewrite/Database/Money/balance.json';

        const userId = message.author.id;
        let gambleAmount = 0;

        let balanceData = {};

        if (fs.existsSync(balancePath)) {
            const rawData = fs.readFileSync(balancePath);
            balanceData = JSON.parse(rawData);
        }

        if (!balanceData[userId]) {
            balanceData[userId] = 0;
        }

        if (balanceData[userId] <= 0) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: You don't have any coins to gamble`)
                ]
            });
        }

        if (args[0] === 'all') {
            gambleAmount = balanceData[userId];
        } else if (args[0] === 'half') {
            gambleAmount = Math.floor(balanceData[userId] / 2);
        } else {
            gambleAmount = parseInt(args[0]);

            if (isNaN(gambleAmount) || gambleAmount <= 0) {
                return displayCommandInfo(module.exports, session, message);
            }

            if (gambleAmount > balanceData[userId]) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: You don't have enough coins`)
                    ]
                });
            }
        }

        const winChance = Math.random() < 0.5;
        let resultMessage;

        if (winChance) {
            balanceData[userId] += gambleAmount;
            resultMessage = `You won ${gambleAmount} coins!`;
        } else {
            balanceData[userId] -= gambleAmount;
            resultMessage = `You lost ${gambleAmount} coins.`;
        }

        fs.writeFileSync(balancePath, JSON.stringify(balanceData, null, 2));

        const embed = new MessageEmbed()
            .setColor(winChance ? session.green : session.warn)
            .setDescription(`> ${message.author}: ${resultMessage}\nYour new balance: ${balanceData[userId]} coins`);

        return message.channel.send({ embeds: [embed] });
    }
};
