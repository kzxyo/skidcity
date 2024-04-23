const pagination = require('/root/rewrite/Utils/paginator.js');
const { MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'firstmembers',
        aliases: ['recent'],
        description: 'Shows the first members to join the server',
        syntax: 'recentmembers',
        example: 'recentmembers',
        module: 'information',
    },
    run: async (session, message, args) => {
        const firstMembers = message.guild.members.cache.sort((a, b) => a.joinedAt - b.joinedAt).first(5);
        const pages = firstMembers.map(member => {
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setTitle(`First member: ${member.user.username}`)
                .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
                .setDescription(`**Created:** ${member.user.createdAt.toDateString()} (<t:${Math.floor(member.user.createdAt.getTime() / 1000)}:R>)\n**Joined:** ${member.joinedAt.toDateString()} (<t:${Math.floor(member.joinedAt.getTime() / 1000)}:R>)`);
            return embed;
        });

        pagination(session, message, pages, 1, '', `(1 entry)`);
    }
};