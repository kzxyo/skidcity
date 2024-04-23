const { MessageEmbed } = require("discord.js");
const moment = require('moment');
const pagination = require('/root/rewrite/Utils/paginator.js');

module.exports = {
    configuration: {
        commandName: 'youngest',
        aliases: ['youth'],
        description: 'Shows the youngest members in the server.',
        syntax: 'youngest',
        example: 'youngest',
        module: 'information',
    },
    run: async (session, message, args) => {
        const youngestMembers = message.guild.members.cache.sort((a, b) => b.user.createdAt - a.user.createdAt).first(5);
        const pages = youngestMembers.map(member => {
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setTitle(`Youngest member: ${member.user.username}`)
                .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
                .setDescription(`**Created:** ${moment(member.user.createdAt).format('ll')} (<t:${Math.floor(member.user.createdAt.getTime() / 1000)}:R>)\n**Joined:** ${moment(member.joinedAt).format('ll')} (<t:${Math.floor(member.joinedAt.getTime() / 1000)}:R>)`);
            return embed;
        });

        pagination(session, message, pages);
    }
};
