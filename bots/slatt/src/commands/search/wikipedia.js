const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
var fetch = require('node-fetch');
const moment = require('moment')
module.exports = class wiki extends Command {
    constructor(client) {
        super(client, {
            name: 'wikipedia',
            aliases: ['w', 'wiki'],
            description: `Search wiki for a query`,
            type: client.types.SEARCH
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const query = args.join(' ')
        let res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(query)}`)
        res = await res.json()
        const arr = []
        if(!res || res.title === 'Not found.') return this.send_error(message, 1, `No results for **${args.join(' ')}** on wikipedia`)
        const content_urls = res.content_urls
        if (content_urls) {
            if (content_urls.desktop.page) {
                arr.push(content_urls.desktop.page)
            } if (content_urls.desktop.revisions) {
                arr.push(content_urls.desktop.revisions)
            } if (content_urls.desktop.edit) {
                arr.push(content_urls.desktop.edit)
            } if (content_urls.desktop.talk) {
                arr.push(content_urls.desktop.talk)
            }
        }
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
            .setTitle(`${res.title}`)
            .setDescription(res.description || 'UNKOWN_SEARCH_TERM')
            if(arr.length) embed.addField(`Pages`, arr.join('\n'))
            embed.setColor(this.hex)
            embed.setFooter(`Wikipedia - Page id ${res.pageid || 'UNKOWN_PAGE_ID'} - from ${moment(new Date(res.timestamp)).format('MM-DD-YYYY')}`, 'https://upload.wikimedia.org/wikipedia/commons/d/de/Wikipedia_Logo_1.0.png')
        message.channel.send({ embeds: [embed] })
    }
};