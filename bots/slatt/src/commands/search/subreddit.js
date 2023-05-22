const Command = require('../Command.js');
const fetch = require('node-fetch');
const { MessageEmbed } = require('discord.js');
const moment = require('moment')
module.exports = class subreddit extends Command {
    constructor(client) {
        super(client, {
            name: 'subreddit',
            usage: 'subreddit [subreddit]',
            aliases: ['subr', 'sreddit'],
            description: 'View information on a given subreddit',
            type: client.types.SEARCH,
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const subredditName = args.join(' ')
        let subreddit = await fetch(`https://www.reddit.com/r/${subredditName}/about.json`)
        subreddit = await subreddit.json()
        subreddit = subreddit.data
        if (!subreddit) return this.api_error(message, `Reddit`)
        if (!subreddit) return this.api_error(message, `Reddit`)
        const embed = new MessageEmbed()
            .setTitle(subreddit.title)
            .setDescription(subreddit.public_description)
            .setURL(`https://www.reddit.com/r/${subredditName}/`)
            .setThumbnail(subreddit.icon_img)
            .setImage(subreddit.banner_img)
            .addField("Subscribers", subreddit.subscribers.toLocaleString(), true)
            .addField("Users Active", subreddit.accounts_active.toLocaleString(), true)
            .addField("Created", moment(new Date(subreddit.created_utc * 1000)).format('MMM DD YYYY'), true)
            .setColor('#FF3F18')
            .setFooter('Reddit', 'https://external-preview.redd.it/iDdntscPf-nfWKqzHRGFmhVxZm4hZgaKe5oyFws-yzA.png?auto=webp&s=38648ef0dc2c3fce76d5e1d8639234d8da0152b2')
        return message.channel.send({ embeds: [embed] });
    }
}
