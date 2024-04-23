const marriageFilePath = '/root/rewrite/Database/Users/marriage.json';
const { MessageActionRow, MessageButton, MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const fs = require('fs');

module.exports = {
    configuration: {
        commandName: 'marry',
        aliases: ['mrryto'],
        description: 'Marry a server member.',
        syntax: 'marry <member>',
        example: 'marry @x6l',
        module: 'fun',
    },
    run: async (session, message, args) => {
        const mention = message.mentions.members.first();
        
        if (!mention || mention.user.bot || mention.id === message.author.id) {
            return displayCommandInfo(module.exports, session, message);    
        }

        const marriageData = loadMarriageData();

        if (message.author.id in marriageData) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: you're already married.. (cheater)`)
                ]
            });
        }

        if (mention.id in marriageData) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: ${mention} is already married`)
                ]
            });
        }

        const embed = new MessageEmbed()
            .setColor(session.color)
            .setDescription(`> 💒 ${mention}, ${message.author} has proposed to marry you! Do you accept?`);

        const row = new MessageActionRow()
            .addComponents(
                new MessageButton()
                    .setCustomId('accept')
                    .setLabel('Accept')
                    .setStyle('SECONDARY'),
                new MessageButton()
                    .setCustomId('reject')
                    .setLabel('Reject')
                    .setStyle('SECONDARY'),
            );

        const proposalMessage = await message.channel.send({ embeds: [embed], components: [row] });

        const filter = i => ['accept', 'reject'].includes(i.customId) && i.user.id === mention.id;
        const collector = proposalMessage.createMessageComponentCollector({ filter, time: 15000 });

        collector.on('collect', async interaction => {
            row.components.forEach(component => component.setDisabled(true));
            await proposalMessage.edit({ components: [row] });

            if (interaction.customId === 'accept') {
                marriageData[mention.id] = message.author.id;
                marriageData[message.author.id] = mention.id;
                saveMarriageData(marriageData);

                message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.color)
                        .setDescription(`> 💒 ${message.author}: ${mention} has accepted the marriage proposal 💍`)
                ]});
            } else {
                message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`> 💔 ${message.author}: ${mention} has rejected the marriage proposal ( ROFL )`)
                ]});
            }
        });

        collector.on('end', async () => {
            row.components.forEach(component => component.setDisabled(true));
            await proposalMessage.edit({ components: [row] });
        });
    }
};

function loadMarriageData() {
    if (!fs.existsSync(marriageFilePath)) {
        fs.writeFileSync(marriageFilePath, '{}');
    }

    const rawData = fs.readFileSync(marriageFilePath);
    return JSON.parse(rawData);
}

function saveMarriageData(data) {
    fs.writeFileSync(marriageFilePath, JSON.stringify(data, null, 2));
}
