const { MessageEmbed } = require("discord.js");
const moment = require('moment');
const pagination = require('/root/rewrite/Utils/paginator.js');

module.exports = {
    configuration: {
        commandName: 'roles',
        aliases: ['role'],
        description: 'Shows all roles in the server',
        syntax: 'roles',
        example: 'roles',
        module: 'information',
    },

    run: async (session, message, args) => {
        const roles = message.guild.roles.cache
            .filter(role => role.name !== '@everyone')
            .sort((a, b) => b.position - a.position)
            .map(role => role);

        if (roles.length === 0) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: There are no roles in this server`)
            ]});
        }

        if (roles.length <= 10) {
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setTitle(`Roles in ${message.guild.name}`)
                .setDescription(roles.map(role => `<@&${role.id}>`).join('\n'));

            return message.channel.send({ embeds: [embed] });
        }

        const pages = [];
        for (let i = 0; i < roles.length; i += 10) {
            const current = roles.slice(i, i + 10);
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                .setTitle(`Role list`)
                .setDescription(current.map(role => `<@&${role.id}> (\`${role.id}\`)`).join('\n'));
            pages.push(embed);
        }

        pagination(session, message, pages, 1, '', `(${roles.length} entries excluding @everyone)`);
    }
};
