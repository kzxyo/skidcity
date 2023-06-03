const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const moment = require('moment');
const ReactionMenu = require('../ReactionMenu.js')

module.exports = class avatars extends Command {
    constructor(client) {
        super(client, {
            name: 'names',
            aliases: ['usernames', 'pastnames', 'previousnames', 'unames'],
            usage: 'names [member]',
            description: 'Fetch a members previous logged names',
            type: client.types.INFO
        });
    }
    async run(message, args) {
        let member = this.functions.get_member_or_self(message, args.join(' '))
        if (!member) {
            if (isNaN(args[0])) {
                return this.invalidUser(message)
            }
            member = await message.client.users.fetch(args[0])
        }
        member = await message.client.users.fetch(member.id)
        const names = this.db.get(`names_${member.id}`)
        if (names === null || !names.length) return this.send_error(message, 1, `No logged names for **${member.username + '#' + member.discriminator}**`)
        let num = 1
        const list = names.map(x => `\`${num++}\` ${x.name} **(${moment(x.date).format('MM-DD-YYYY')})**`)
        const embed = new MessageEmbed()
            .setAuthor(member.username + '#' + member.discriminator)
            .setColor(this.hex)
            .setDescription(list.join('\n'))
            .setTitle(`Logged names for **${member.username}**`)
            .setFooter(`${list.length} total logged names`)
        if (list.length <= 10) {
            message.channel.send({ embeds: [embed] });
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
};