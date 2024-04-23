const { MessageEmbed } = require('discord.js');

module.exports = {
    configuration : {
        commandName: 'vanityuses',
        aliases: ['uses'],
        description: 'Check how many uses your vanity has',
        syntax: 'vanityuses',
        example: 'vanityuses',
        module: 'information'
    },

    run: async (session, message, args) => {

        if (!message.guild.features.includes('VANITY_URL')) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: This server does not have a vanity`)
                ]
            });
        }

        const vanityURL = message.guild.vanityURLCode;
        if (!vanityURL) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: This server does not have a vanity`)
                ]
            });
        }

        const vanityInfo = await message.guild.fetchVanityData();
        return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setColor('#748cdc')
                    .setDescription(`:mag: ${message.author}: **https://discord.gg/${vanityURL}** has been used **${vanityInfo.uses.toLocaleString()}** times`)
            ]
        });

    }
}