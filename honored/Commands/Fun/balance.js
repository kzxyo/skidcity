const fs = require('fs');
const { MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'balance',
        aliases: ['bal'],
        description: 'Check the balance of your bank account',
        syntax: 'balance',
        example: 'balance',
        module: 'fun'
    },
    run: async (session, message, args) => {
        const balancePath = '/root/rewrite/Database/Money/balance.json';
        const accountPath = '/root/rewrite/Database/Money/account.json';

        const userId = message.author.id;
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

        const embed = new MessageEmbed()
            .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true }))
            .setColor(session.color)
            .setTitle(`${message.author.username}'s Balance`)
            .addField('Balance', `${balanceData[userId]} coins`, true)
            .addField('Bank', `${accountData[userId]} coins`, true);

        return message.channel.send({ embeds: [embed] });
    }
};
