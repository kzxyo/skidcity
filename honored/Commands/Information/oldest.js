const { MessageEmbed } = require("discord.js");
const moment = require('moment');
const pagination = require('/root/rewrite/Utils/paginator.js');

module.exports = {
    configuration: {
        commandName: 'oldest',
        aliases: ['ancient'],
        description: 'Shows the oldest members in the server.',
        syntax: 'oldest',
        example: 'oldest',
        module: 'information',
    },
    run: async (session, message, args) => {
        const oldestMembers = [];
        message.guild.members.cache.forEach(member => {
            if (member.user.createdAt) {
                oldestMembers.push(member);
            }
        });

        oldestMembers.sort((a, b) => a.user.createdAt - b.user.createdAt);
        const topOldestMembers = oldestMembers.slice(0, 5);
        const pages = topOldestMembers.map(member => {
            return new MessageEmbed()
                .setColor(session.color)
                .setTitle(`Oldest member: ${member.user.username}`)
                .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
                .setDescription(`**Created:** ${moment(member.user.createdAt).format('ll')} (<t:${Math.floor(member.user.createdAt.getTime() / 1000)}:R>)\n**Joined:** ${moment(member.joinedAt).format('ll')} (<t:${Math.floor(member.joinedAt.getTime() / 1000)}:R>)`);
        });

        // Paginate the top 5 oldest members
        pagination(session, message, pages);
    }
};
