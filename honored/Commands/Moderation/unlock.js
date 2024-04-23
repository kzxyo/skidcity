const { Permissions, MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'unlock',
        description: 'Unlocks the channel for everyone',
        aliases: ['ulock'],
        syntax: 'unlock',
        example: 'unlock',
        permissions: ['manage_channels'],
        parameters: 'N/A',
        module: 'moderation'
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're missing the \`manage_channels\` permission.`)
                        .setColor(session.warn)
                ]
            });
        }

        message.channel.permissionOverwrites.edit(message.guild.roles.everyone, {
            SEND_MESSAGES: null
        }).then(() => {
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`:unlock: ${message.author}: This channel has been unlocked`)
                        .setColor('#fcac34')
                ]
            });
        }).catch(error => {
            console.error(error);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Failed to unlock the channel`)
                        .setColor(session.warn)
                ]
            });
        });
    }
};
