const { MessageEmbed, Permissions } = require('discord.js');
const pagination = require('/root/rewrite/Utils/paginator.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const filepath = '/root/rewrite/Database/Moderation/warnings.json';
const fs = require('fs');

module.exports = {
    configuration: {
        commandName: 'warnings',
        aliases: [],
        description: 'View warnings of a server member.',
        syntax: 'warnings <user>',
        example: 'warnings @user',
        permissions: 'MANAGE_MESSAGES',
        parameters: 'user',
        module: 'moderation'
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_messages\``)
                        .setColor(session.warn)
                ]
            });
        }

        const targetUser = message.mentions.members.first();
        if (!targetUser) {
            return displayCommandInfo(module.exports, session, message);
        }

        let warnings = {};
        try {
            const data = fs.readFileSync(filepath, 'utf8');
            warnings = JSON.parse(data);
        } catch (error) {
            console.error('Error loading warnings from file:', error);
        }

        const userWarnings = warnings[message.guild.id]?.[targetUser.id];
        if (!userWarnings || userWarnings.length === 0) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${targetUser} has no warnings`)
                ]
            });
        }

        if (userWarnings.length === 1) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.color)
                        .setThumbnail(targetUser.user.displayAvatarURL({ dynamic: true }))
                        .setTitle(`Warnings for ${targetUser.user.username}`)
                        .setDescription(`> ${userWarnings}`)
                ]
            });
        }

        const pages = userWarnings.map((warning, index) => {
            return new MessageEmbed()
                .setColor(session.color)
                .setThumbnail(targetUser.user.displayAvatarURL({ dynamic: true }))
                .setTitle(`Warnings for ${targetUser.user.username}`)
                .setDescription(`> ${warning}`)
        });
        pagination(session, message, pages);
    }
};
