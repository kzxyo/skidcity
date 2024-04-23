const { MessageEmbed } = require("discord.js");
const moment = require('moment');
const pagination = require('/root/rewrite/Utils/paginator.js');

module.exports = {
    configuration: {
        commandName: 'boosters',
        aliases: ['boosters'],
        description: 'Shows the members who have boosted the server.',
        syntax: 'boosters',
        example: 'boosters',
        module: 'information',
    },
    run: async (session, message, args) => {
        const boosters = message.guild.members.cache.filter(member => member.premiumSince);
        if (boosters.size === 0) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: There are no boosters in this server`)
            ]});
        }

        if (boosters.size <= 10) {
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                .setTitle(`Boosters list`)
                .setDescription(boosters.map(member => `${member.user} (\`${member.user.id}\`)`).join('\n'));

            return message.channel.send({ embeds: [embed] });
        }

        const pages = [];
        for (let i = 0; i < boosters.size; i += 10) {
            const current = boosters.array().slice(i, i + 10);
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                .setTitle(`Boosters list`)
                .setDescription(current.map(member => `${member.user} (\`${member.user.id}\`)`).join('\n'));
            pages.push(embed);
        }

        pagination(session, message, pages, 1, '', `(${boosters.size} entries)`);
    }
};
