const {
    MessageEmbed
} = require('discord.js');
const Command = require('../Command.js');
const ReactionMenu = require('../ReactionMenu.js');

module.exports = class InRoleCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'inrole',
            aliases: ['members'],
            type: client.types.INFO,
            description: `check members in a role`,
            usage: `inrole [role]`,
            subcommands: ['inrole'],
        });
    }
    async run(message, args) {
        if (!args.length) {
            return this.help(message)
        }
        let memberRole =  this.functions.get_role(message, args.join(' '))
        if (!memberRole) {
            return this.send_error(message, 1, `You must provide a role`)
        }
        
        let num = 1
        const role = memberRole
        if (memberRole.members.size === 0) {
            return this.send_error(message, 1, `There is no one in **${role.name}**`)
        }
        let list = role.members.map(u => `\`${num++}\` ${u.user.tag}`)
        if (!list.length) {
            return this.send_error(message, 1, `There is no one in **${role.name}**`)
        }
        const embed = new MessageEmbed()
            .setTitle(`members for ${role.name}`)
            .setFooter(`${list.length} members`, message.author.displayAvatarURL({
                dynamic: true
            }))
            .setDescription(list.join('\n'))
            .setAuthor(role.name, message.guild.iconURL({dynamic:true}))
            .setTimestamp()
            .setColor(this.hex);
        if (list.length <= 10) {
            return message.channel.send({ embeds: [embed] })
        } else {
            return new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
}