const { MessageEmbed, Permissions } = require("discord.js");

module.exports = {
    configuration: {
        commandName: "removejail",
        description: "Remove the jail from the server",
        syntax: 'removejail',
        example: 'removejail',
        permissions: 'manage_roles',
        parameters: 'user',
        module: "moderation"
    },

    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_roles\``)
                        .setColor(session.warn)
                ]
            });
        }

        const jailRole = message.guild.roles.cache.find(role => role.name === 'jailed');
        if (!jailRole) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: The jail role has not been set`)
                ]
            });
        }

        const jailChannel = message.guild.channels.cache.find(channel => channel.name === 'jail');
        if (!jailChannel) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: The jail channel has not been set`)
                ]
            });
        }

        try {
            await jailRole.delete();
            await jailChannel.delete();
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.green)
                        .setDescription(`${session.grant} ${message.author}: Jail role and channel have been successfully removed`)
                ]
            });
        } catch (error) {
            console.error('Error removing jail role and channel:', error);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.error)
                        .setDescription(`${session.mark} ${message.author}: An error occurred while removing the jail role and channel`)
                ]
            });
        }
    }
};
