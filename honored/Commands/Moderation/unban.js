const { Permissions, MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'unban',
        description: 'Unban a user by ID or username',
        syntax: 'unban [userID]',
        example: 'unban 11..241..126',
        permissions: 'ban_members',
        aliases: ['pardon', 'forgive'],
        module: 'moderation'
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) {
            const errorEmbed = new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: You're **missing** the \`ban_members\` permission`);
            return message.channel.send({ embeds: [errorEmbed] });
        }

        if (!message.guild.me.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) {
            const errorEmbed = new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: I'm **missing** the \`ban_members\` permission`);
            return message.channel.send({ embeds: [errorEmbed] });
        }

        const userArg = args[0];
        const userId = /^\d+$/.test(userArg) ? userArg : null;
        const bannedUser = userId
            ? await message.guild.bans.fetch(userId).catch(() => null)
            : message.guild.bans.cache.find(ban => ban.user.username.toLowerCase() === userArg.toLowerCase());

        if (!bannedUser) {
            return displayCommandInfo(module.exports, session, message);
        }

        message.guild.members.unban(bannedUser.user)
            .then(unbannedUser => {
                const successEmbed = new MessageEmbed()
                    .setColor(session.green)
                    .setDescription(`${session.grant} ${message.author}: **${unbannedUser.username}** has been unbanned`);
                message.channel.send({ embeds: [successEmbed] });
            })
            .catch(error => {
                console.error('Error while unbanning user:', error);
                const errorEmbed = new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: Unable to unban that user`);
                message.channel.send({ embeds: [errorEmbed] });
            });
    }
};
