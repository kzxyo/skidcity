const Subcommand = require('../../Subcommand.js');
const db = require('quick.db')
const ReactionMenu = require('../../ReactionMenu.js');
const { MessageEmbed } = require('discord.js');

module.exports = class Add extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'wordfilter',
            name: 'list',
            aliases: ['ls', 'all'],
            type: client.types.SERVER,
            usage: 'wordfilter list',
            description: 'View a list of every word filtered',
        });
    }
    async run(message, args) {
        const check = db.get(`word_filter_${message.guild.id}`)
        if(!check || !check.length) {
           return this.send_error(message, 1, `There arent any **word filters** set up yet`)
        } 
        let num = 1
        const filters = db.get(`word_filter_${message.guild.id}_punish`)
        const list = filters.map(x => `\`${num++}\` **${x.split('--')[0]}** (${x.split('--')[1]})`)
        const embed = new MessageEmbed()
        .setTitle(`Filtered words`)
        .setAuthor(message.author.tag, message.author.avatarURL({dynamic:true}))
        .setDescription(list.join('\n'))
        .setFooter(`${list.length} total filtered words`)
        .setColor(this.hex)
        if(list.length <= 10) {
            message.channel.send({ embeds: [embed] })
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
}