const { MessageEmbed, Permissions } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'removeicon',
        aiases: ['delicon'],
        description: 'Remove the icon from the server',
        syntax: 'removeicon',
        example: 'removeicon',
        permissions: 'manage_guild',
        module: 'moderation',
    },

    run: async (session, message, args) => {
        if (!message.member.permissions.has('MANAGE_GUILD')) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_guild\``)
                        .setColor(session.warn)
                ]
            });
        }

        if (!message.guild.icon) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: This server does not have an icon`)
                ]
            });
        }

        try {
            await message.guild.setIcon(null);
            const embed = new MessageEmbed()
                .setColor(session.green)
                .setDescription(`${session.grant} ${message.author}: The server icon has been removed`);
            message.channel.send({ embeds: [embed] });
        } catch (error) {
            console.error('Error while removing server icon:', error);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: An error occurred, please contact support`)
                ]
            });
        }

    }
}