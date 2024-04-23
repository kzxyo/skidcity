const fs = require('fs');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'withdrawal',
        aliases: ['with', 'wd'],
        description: 'Withdraw money from your bank account to your balance.',
        syntax: 'withdrawal <amount>',
        example: 'withdrawal 1200',
        subcommands: ['> withdrawal all\n> withdrawal half'],
        module: 'fun'
    },
    run: async (session, message, args) => {
        const balancePath = '/root/rewrite/Database/Money/balance.json';
        const accountPath = '/root/rewrite/Database/Money/account.json';

        const userId = message.author.id;
        let withdrawalAmount = 0;

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
            withdrawalAmount = accountData[userId];
        } else if (args[0] === 'half') {
            withdrawalAmount = Math.floor(accountData[userId] / 2);
        } else {
            withdrawalAmount = parseInt(args[0]);

            if (isNaN(withdrawalAmount) || withdrawalAmount <= 0) {
                return displayCommandInfo(module.exports, session, message);
            }

            if (withdrawalAmount > accountData[userId]) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: You don't have enough coins`)
                
                ]});
            }
        }

        balanceData[userId] += withdrawalAmount;
        accountData[userId] -= withdrawalAmount;

        fs.writeFileSync(balancePath, JSON.stringify(balanceData, null, 2));
        fs.writeFileSync(accountPath, JSON.stringify(accountData, null, 2));

        const embed = new MessageEmbed()
            .setColor(session.green)
            .setDescription(`${session.grant} ${message.author}: Successfully withdrew ${withdrawalAmount} coins from your account`);

        return message.channel.send({ embeds: [embed] });
    }
};
