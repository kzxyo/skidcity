const pagination = require('/root/rewrite/Utils/paginator.js');
const { MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'recentmembers',
        aliases: ['recent'],
        description: 'Shows the most recent members that joined the server.',
        syntax: 'recentmembers',
        example: 'recentmembers',
        module: 'information',
    },
    run: async (session, message, args) => {
        const recentMembers = message.guild.members.cache.sort((a, b) => b.joinedAt - a.joinedAt).first(5);
        const pages = recentMembers.map(member => {
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setTitle(`Recent member: ${member.user.username}`)
                .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
                .setDescription(`**Created:** ${member.user.createdAt.toDateString()} (<t:${Math.floor(member.user.createdAt.getTime() / 1000)}:R>)\n**Joined:** ${member.joinedAt.toDateString()} (<t:${Math.floor(member.joinedAt.getTime() / 1000)}:R>)`);
            return embed;
        });

        pagination(session, message, pages, 1, '', `(1 entry)`);
    }
};