const { Permissions, MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'lockdown',
        description: 'Locks the channel from everyone',
        aliases: ['lock'],
        syntax: 'lock',
        example: 'lock',
        permissions: 'manage_channels',
        parameters: 'N/A',
        module: 'moderation',
        devOnly: true
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
            SEND_MESSAGES: false
        }).then(() => {
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`🔒 ${message.author}: This channel has been locked`)
                        .setColor('#fcac34')
                ]
            });
        }).catch(error => {
            console.error(error);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: Failed to lock the channel`)
                        .setColor(session.warn)
                ]
            });
        });
    }
};
