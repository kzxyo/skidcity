const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'vanitycheck',
        description: 'Check if a vanity URL is available',
        aliases: ['vanity'],
        syntax: 'vanitycheck <vanity>',
        example: 'vanitycheck discord',
        permissions: 'N/A',
        parameters: 'vanity',
        module: 'utility'
    },

    run: async (session, message, args) => {
        if (!args[0]) {
            return displayCommandInfo(module.exports, session, message);
        }

        const vanity = args[0];
        const vanityURL = `${vanity}`;

        message.guild.fetchVanityData().then(data => {
            if (data.code === vanity) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: The vanity \`${vanityURL}\` is **already taken**`)
                            .setColor(session.warn)
                    ]
                });
            } else {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.grant} ${message.author}: The vanity \`${vanityURL}\` is **available** ( or termed )`)
                            .setColor(session.green)
                    ]
                });
            }
        }).catch(error => {
            console.error(error);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: `)
                        .setColor(session.warn)
                ]
            });
        });


    }
}