const { MessageEmbed } = require("discord.js");
const pagination = require('/root/rewrite/Utils/paginator.js');

module.exports = {
    configuration: {
        commandName: 'bots',
        aliases: ['bots'],
        description: 'Shows the bots in the server.',
        syntax: 'bots',
        example: 'bots',
        module: 'information',
    },
    run: async (session, message, args) => {
        const bots = message.guild.members.cache.filter(member => member.user.bot);
        if (bots.size === 0) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: There are no bots in this server`)
            ]});
        }

        if (bots.size <= 10) {
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                .setTitle(`Bots list`)
                .setDescription(bots.map(member => `${member.user} (\`${member.user.id}\`)`).join('\n'));

            return message.channel.send({ embeds: [embed] });
        }

        const pages = [];
        for (let i = 0; i < bots.size; i += 10) {
            const current = bots.array().slice(i, i + 10);
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                .setTitle(`Bots list`)
                .setDescription(current.map(member => `${member.user} (\`${member.user.id}\`)`).join('\n'));
            pages.push(embed);
        }

        pagination(session, message, pages, 1, '', `(${bots.size} entries)`);
    }
};