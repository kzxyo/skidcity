const { MessageEmbed } = require('discord.js');
const axios = require('axios');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'steam',
        aliases: ['steamgame'],
        description: 'Search Steam for a game',
        syntax: 'steam <game>',
        example: 'steam CSGO',
        permissions: 'N/A',
        parameters: 'game',
        module: 'miscellaneous'
    },

    run: async (session, message, args) => {
        const query = args.join(" ");

        if (!args.length) {
            return displayCommandInfo(module.exports, session, message);
        }

        try {
            const search = await axios.get('https://store.steampowered.com/api/storesearch', {
                params: {
                    cc: 'us',
                    l: 'en',
                    term: query
                }
            });

            if (!search.data.items.length) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: No results found for **${query}**`)
                ]});
            }

            const { id, tiny_image } = search.data.items[0];

            const { data } = await axios.get('https://store.steampowered.com/api/appdetails', {
                params: { appids: id }
            });

            const { data: appData } = data[id.toString()];
            const current = appData.price_overview ? `$${appData.price_overview.final / 100}` : 'Free';
            const original = appData.price_overview ? `$${appData.price_overview.initial / 100}` : 'Free';
            const price = current === original ? current : `~~${original}~~ ${current}`;
            const platforms = [];
            if (appData.platforms) {
                if (appData.platforms.windows) platforms.push('Windows');
                if (appData.platforms.mac) platforms.push('Mac');
                if (appData.platforms.linux) platforms.push('Linux');
            }

            const embed = new MessageEmbed()
                .setColor(session.color)
                .setAuthor('Steam', 'https://i.imgur.com/xxr2UBZ.png', 'http://store.steampowered.com/')
                .setTitle(`__**${appData.name}**__`)
                .setURL(`http://store.steampowered.com/app/${appData.steam_appid}`)
                .setImage(tiny_image)
                .addField('Price', ` ${price}`, true)
                .addField('Recommendations', ` ${appData.recommendations ? appData.recommendations.total : '???'}`, true)
                .addField('Platforms', ` ${platforms.join(', ') || 'None'}`, true)
                .addField('Release Date', ` ${appData.release_date ? appData.release_date.date : '???'}`, true)
                .addField('Developers', ` ${appData.developers ? appData.developers.join(', ') || '???' : '???'}`, true)
                .addField('Publishers', ` ${appData.publishers ? appData.publishers.join(', ') || '???' : '???'}`, true)
                .setFooter('Steam', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/1200px-Steam_icon_logo.svg.png');

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error.message);
            message.channel.send('Error fetching data from Steam API. Please try again later.');
        }
    }
};
