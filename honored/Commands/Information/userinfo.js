const { MessageEmbed } = require("discord.js");
const moment = require("moment");

module.exports = {
    configuration: {
        commandName: 'userinfo',
        description: 'Get information about a user',
        aliases: ['ui'],
        syntax: 'userinfo <@user>',
        example: 'userinfo @x6l',
        permissions: 'N/A',
        parameters: 'member',
        module: 'information'
    },
    run: async (session, message, args) => {

        const mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
        const member = mentionedMember || message.member;
        const created = moment(member.user.createdAt).format('MMMM Do YYYY, h:mm:ss a');
        const joined = moment(member.joinedAt).format('MMMM Do YYYY, h:mm:ss a');

        const embed = new MessageEmbed()
            .setAuthor(member.user.username, member.user.displayAvatarURL({ dynamic: true }))
            .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
            .addField('Dates', `Created: ${created}\nJoined: ${joined}`);

        const topRole = member.roles.highest;
        embed.setColor(topRole ? topRole.hexColor : session.color);

        const roles = member.roles.cache
            .filter(role => role.name !== '@everyone')
            .sort((a, b) => b.position - a.position)
            .map(role => role.toString()); 
        embed.addField('Roles', roles.length > 0 ? roles.join(' ') : 'No roles');

        message.channel.send({ embeds: [embed] });
    }
};
