const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')

module.exports = class List extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'mediachannel',
            name: 'list',
            type: client.types.SERVER,
            usage: 'mediachannel list',
            description: 'View a list of your mediachannel channels',
        });
    }
    async run(message, args) {
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        const check = await message.client.db.media_channel.findAll({ where: { guildID: message.guild.id } })
        if (!check.length) {
            return this.send_error(message, 1, `There was no media channel settings found for this server, start by using \`${prefix.prefix}mediachannel add\``)
        } else {
            let num = 1
            const list = check.map(c => `\`${num++}\` ${message.guild.channels.cache.get(c.channel)}`)
            if (!list.length) {
                return this.send_error(message, 1, `There was no media channel settings found for this server, start by using \`${prefix.prefix}mediachannel add\``)
            }
            const embed = new MessageEmbed()
                .setTitle(`Media channels`)
                .setColor(this.hex)
                .setFooter(`${list.length} media channels`)
                .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
                .setDescription(list.join('\n'))
            if (list.length < 10) {
                message.channel.send({ embeds: [embed] })
            } else {
                return new ReactionMenu(message.client, message.channel, message.member, embed, list);
            }
        }
    }
}