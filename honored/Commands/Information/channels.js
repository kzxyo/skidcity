const { MessageEmbed } = require("discord.js");
const moment = require('moment');
const pagination = require('/root/rewrite/Utils/paginator.js');

module.exports = {
    configuration: {
        commandName: 'channels',
        aliases: ['channel'],
        description: 'Shows all channels in the server',
        syntax: 'channels',
        example: 'channels',
        module: 'information',
    },

    run: async (session, message, args) => {
        const channels = message.guild.channels.cache
            .filter(channel => channel.type !== 'GUILD_CATEGORY')
            .sort((a, b) => b.position - a.position)
            .map(channel => channel);

        if (channels.length === 0) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: There are no channels in this server`)
            ]});
        }

        if (channels.length <= 10) {
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setTitle(`Channels in ${message.guild.name}`)
                .setDescription(channels.map(channel => `<#${channel.id}>`).join('\n'));

            return message.channel.send({ embeds: [embed] });
        }

        const pages = [];
        for (let i = 0; i < channels.length; i += 10) {
            const current = channels.slice(i, i + 10);
            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                .setTitle(`Channel list`)
                .setDescription(current.map(channel => `<#${channel.id}> (\`${channel.id}\`)`).join('\n'));
            pages.push(embed);
        }

        pagination(session, message, pages, 1, '', `(${channels.length} entries excluding categories)`);
    }
};
