const { MessageEmbed, Permissions } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'striproles',
        aliases: ['strip'],
        description: 'Strip all of a users roles',
        syntax: 'strip <member>',
        example: 'strip @x6l',
        permissions: 'manage_roles',
        parameters: 'member',
        module: 'moderation'
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
        const user = message.mentions.members.first();

        if (!user) {
            return displayCommandInfo(module.exports, session, message);
        }

        if (user.guild.id !== message.guild.id) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You can only strip roles from users in your own server`)
                        .setColor(session.warn)
                ]
            });
        }

        // check if the mentioned user has a higher, or same role as the message.author
        if (user.roles.highest.position >= message.member.roles.highest.position) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You can't strip roles from someone with a higher or equal roles as you`)
                        .setColor(session.warn)
                ]
            });
        }

        try {
            await user.roles.set([]);
            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.green)
                        .setDescription(`${session.grant} ${message.author}: I have removed all of ${user}'s roles`)
                ]
            });
        } catch (error) {
            console.error('Error executing strip roles:', error);
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: An error occurred, please contact support`)
                    .setColor(session.warn)
            ]});
        }
    }
}
       