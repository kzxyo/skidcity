const fs = require('fs');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'deposit',
        aliases: ['dep'],
        description: 'Deposit money from your balance to your bank account.',
        syntax: 'deposit <amount>',
        example: 'deposit 1200',
        subcommands: ['> deposit all\n> deposit half'],
        module: 'fun'
    },
    run: async (session, message, args) => {
        const balancePath = '/root/rewrite/Database/Money/balance.json';
        const accountPath = '/root/rewrite/Database/Money/account.json';

        const userId = message.author.id;
        let depositAmount = 0;

        let balanceData = {};
        let accountData = {};

        if (fs.existsSync(balancePath)) {
            const rawData = fs.readFileSync(balancePath);
            balanceData = JSON.parse(rawData);
        }

        if (fs.existsSync(accountPath)) {
            const rawData = fs.readFileSync(accountPath);
            accountData = JSON.parse(rawData);
        }

        if (!balanceData[userId]) {
            balanceData[userId] = 0;
        }

        if (!accountData[userId]) {
            accountData[userId] = 0;
        }

        if (args[0] === 'all') {
            depositAmount = balanceData[userId];
        } else if (args[0] === 'half') {
            depositAmount = Math.floor(balanceData[userId] / 2);
        } else {
            depositAmount = parseInt(args[0]);

            if (isNaN(depositAmount) || depositAmount <= 0) {
                return displayCommandInfo(module.exports, session, message);
            }

            if (depositAmount > balanceData[userId]) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: You don't have enough coins to deposit that amount.`)
                
                ]});
            }
        }

        balanceData[userId] -= depositAmount;
        accountData[userId] += depositAmount;

        fs.writeFileSync(balancePath, JSON.stringify(balanceData, null, 2));
        fs.writeFileSync(accountPath, JSON.stringify(accountData, null, 2));

        const embed = new MessageEmbed()
            .setColor(session.green)
            .setDescription(`${session.grant} ${message.author}: Successfully deposited ${depositAmount} coins to your account.\nYour new balance: ${balanceData[userId]} coins\nYour account balance: ${accountData[userId]} coins`);

        return message.channel.send({ embeds: [embed] });
    }
};
