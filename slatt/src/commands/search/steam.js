const Command = require('../Command.js');
const { MessageEmbed } = require('discord.js');
const request = require('node-superfetch');

module.exports = class SteamCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'steam',
            usage: 'steam [game]',
            description: 'Finds a game from steam',
            type: client.types.SEARCH,
            subcommands: ['steam']
        });
    }

    async run(message, args) {
        const query = args.join(" ");

        if (!args.length) {
            return this.help(message)
        }
        const search = await request
            .get('https://store.steampowered.com/api/storesearch')
            .query({
                cc: 'us',
                l: 'en',
                term: query
            });

        if (!search.body.items.length) return this.send_error(message, 1, `No search results found for **${query}**`);

        const { id, tiny_image } = search.body.items[0];

        const { body } = await request
            .get('https://store.steampowered.com/api/appdetails')
            .query({ appids: id });

        const { data } = body[id.toString()];
        const current = data.price_overview ? `$${data.price_overview.final / 100}` : 'Free';
        const original = data.price_overview ? `$${data.price_overview.initial / 100}` : 'Free';
        const price = current === original ? current : `~~${original}~~ ${current}`;
        const platforms = [];
        if (data.platforms) {
            if (data.platforms.windows) platforms.push('Windows');
            if (data.platforms.mac) platforms.push('Mac');
            if (data.platforms.linux) platforms.push('Linux');
        }

        const embed = new MessageEmbed()
            .setColor(this.hex)
            .setAuthor('Steam', 'https://i.imgur.com/xxr2UBZ.png', 'http://store.steampowered.com/')
            .setTitle(`__**${data.name}**__`)
            .setURL(`http://store.steampowered.com/app/${data.steam_appid}`)
            .setImage(tiny_image)
            .addField('Price', ` ${price}`, true)
            .addField('Recommendations', ` ${data.recommendations ? data.recommendations.total : '???'}`, true)
            .addField('Platforms', ` ${platforms.join(', ') || 'None'}`, true)
            .addField('Release Date', ` ${data.release_date ? data.release_date.date : '???'}`, true)
            .addField('Developers', ` ${data.developers ? data.developers.join(', ') || '???' : '???'}`, true)
            .addField('Publishers', ` ${data.publishers ? data.publishers.join(', ') || '???' : '???'}`, true)
            .setFooter(`Steam`, 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/1200px-Steam_icon_logo.svg.png')

        message.channel.send({ embeds: [embed] });
    
}
};
