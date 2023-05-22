const Command = require('../Command.js');
const ms = require('ms');
const parseMilliseconds = require("parse-ms");
const { MessageEmbed } = require('discord.js');
const ReactionMenu = require('../ReactionMenu.js');
module.exports = class Recentlyjoined extends Command {
    constructor(client) {
        super(client, {
            name: 'recentlyjoined',
            aliases: ['recents', 'recent', 'new', 'joined'] ,
            usage: 'recentlyjoined [time]',
            description: 'Display a list of recently joined members',
            type: client.types.INFO,
        });
    }
    async run(message, args) {
        let time = args[0]
        if (args[0].toLowerCase() === 'today') {
            time = 86400000
            const members = message.guild.members.cache.filter(x => (Date.now() - x.joinedTimestamp) < time).sort((a, b) => parseInt(b.joinedTimestamp) - parseInt(a.joinedTimestamp))
            let num = 0
            let list = members.map(x => `\`${++num}\` **${x.user.tag}**`)
            const input = parseMilliseconds(time)
            let arr = []
            if (input.days) arr.push(`${input.days} ${input.days !== 1 ? `days` : 'day'}`)
            if (input.hours) arr.push(`${input.hours} ${input.hours !== 1 ? `hours` : 'hour'}`)
            if (input.minutes) arr.push(`${input.minutes} ${input.minutes !== 1 ? `minutes` : 'minute'}`)
            if (input.seconds) arr.push(`${input.seconds} ${input.seconds !== 1 ? `seconds` : 'second'}`)
            if (!list.length) return this.send_info(message, `There arent any members who joined during today`)
            const embed = new MessageEmbed()
                .setTitle(`Members joined today`)
                .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
                .setDescription(list.join('\n'))
                .setColor(this.hex)
                .setFooter(`${list.length} total members`)
            if (list.length <= 10) {
                message.channel.send({ embeds: [embed] })
            } else {
                new ReactionMenu(message.client, message.channel, message.member, embed, list);
            }
            return
        }
        if (!time) time = '10m'
        time = time.toLowerCase()
        if (['s', 'h', 'm', 'd'].some(x => time.includes(x)) === false) return this.send_error(message, 1, `Your time isnt formatted properly. Heres an example: **10m** = **10 minutes**, **5s** = **5 seconds**`)
        time = ms(time)
        if (time === undefined) return this.send_error(message, 1, `Your time isnt formatted properly. Heres an example: **10m** = **10 minutes**, **5s** = **5 seconds**`)
        const members = message.guild.members.cache.filter(x => (Date.now() - x.joinedTimestamp) < time).sort((a, b) => parseInt(b.joinedTimestamp) - parseInt(a.joinedTimestamp))
        let num = 0
        let list = members.map(x => `\`${++num}\` **${x.user.tag}** Joined \`${convert(x)}\``)
        function convert(x) {
            let arr = []
            const time = parseMilliseconds(Date.now() - x.joinedTimestamp)
            if (time.days) arr.push(`${time.days} ${time.days !== 1 ? `days` : 'day'}`)
            if (time.hours) arr.push(`${time.hours} ${time.hours !== 1 ? `hours` : 'hour'}`)
            if (time.minutes) arr.push(`${time.minutes} ${time.minutes !== 1 ? `minutes` : 'minute'}`)
            if (time.seconds) arr.push(`${time.seconds} ${time.seconds !== 1 ? `seconds` : 'second'}`)
            const ago = arr.join(', ') + ' ago'
            return ago
        }
        const input = parseMilliseconds(time)
        let arr = []
        if (input.days) arr.push(`${input.days} ${input.days !== 1 ? `days` : 'day'}`)
        if (input.hours) arr.push(`${input.hours} ${input.hours !== 1 ? `hours` : 'hour'}`)
        if (input.minutes) arr.push(`${input.minutes} ${input.minutes !== 1 ? `minutes` : 'minute'}`)
        if (input.seconds) arr.push(`${input.seconds} ${input.seconds !== 1 ? `seconds` : 'second'}`)
        const ago = arr.join(', ') + ' ago'
        if (!list.length) return this.send_info(message, `There arent any members who joined before **${ago}**`)
        const embed = new MessageEmbed()
            .setTitle(`Recently joined: ${ago}`)
            .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
            .setDescription(list.join('\n'))
            .setColor(this.hex)
            .setFooter(`${list.length} recently joined members`)
        if (list.length <= 10) {
            message.channel.send({ embeds: [embed] })
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    };

}