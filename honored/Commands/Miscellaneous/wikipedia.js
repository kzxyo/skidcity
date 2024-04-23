const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const moment = require('moment');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'wikipedia',
        aliases: ['wiki'],
        description: 'Search wiki for a query',
        syntax: 'wikipedia [query]',
        example: 'wikipedia Earth',
        parameters: 'query',
        permissions: 'N/A',
        module: 'miscellaneous'
    },
    run: async (session, message, args, prefix) => {
        if (!args.length) {
            return displayCommandInfo(module.exports, session, message, prefix);
        }

        const query = args.join(' ');
        let res;

        try {
            res = await axios.get(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(query)}`);
        } catch (error) {
            console.error(error);
            const errorEmbed = new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: The API returned a bad response`);
            return message.channel.send({ embeds: [errorEmbed] });
        }

        if (!res || res.data.title === 'Not found.') {
            const noResultEmbed = new MessageEmbed()
                .setColor(session.warn)
                .setDescription(`${session.mark} ${message.author}: No results for **${query}** on **Wikipedia**`);
            return message.channel.send({ embeds: [noResultEmbed] });
        }

        const arr = [];
        const content_urls = res.data.content_urls;

        if (content_urls) {
            if (content_urls.desktop.page) arr.push(content_urls.desktop.page);
            if (content_urls.desktop.revisions) arr.push(content_urls.desktop.revisions);
            if (content_urls.desktop.edit) arr.push(content_urls.desktop.edit);
            if (content_urls.desktop.talk) arr.push(content_urls.desktop.talk);
        }

        const embed = new MessageEmbed()
            .setAuthor(message.author.username, message.author.avatarURL({ dynamic: true }))
            .setTitle(res.data.title)
            .setDescription(res.data.description || 'UNKNOWN_SEARCH_TERM');

        if (arr.length) embed.addField('Pages', arr.join('\n'));

        embed.setColor(session.color);
        embed.setFooter(`Wikipedia - Page id ${res.data.pageid || 'UNKNOWN_PAGE_ID'} - from ${moment(new Date(res.data.timestamp)).format('MM-DD-YYYY')}`, 'https://upload.wikimedia.org/wikipedia/commons/d/de/Wikipedia_Logo_1.0.png');

        message.channel.send({ embeds: [embed] });
    }
};
