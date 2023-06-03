const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const ReactionMenu = require('../ReactionMenu.js');

module.exports = class Top extends Command {
    constructor(client) {
        super(client, {
            name: 'topinvites',
            aliases: ['topinv', 'invites'],
            usage: 'topinvites, topinvites [user]',
            subcommands: ['invites'],
            description: 'shows overall top invites for your server',
            type: client.types.FUN
        });
    }
    async run(message, args) {
        if (args[0]) {
            const member = this.functions.get_member(message, args.join(' '))
            if (!member) {
                return this.invalidUser(message)
            } else {
                const invites = message.guild.invites.cache
                console.log(invites)
                const invite_count = invites.filter(inv => inv.inviter.id === member.id)
                if(!Array(invite_count).length) return this.send_info(message, `**${member.user.username}** has no invites`)
                const count = []
                invite_count.forEach(c => { 
                    count.push(c.uses)
                })
                return this.send_info(message, `**${member.user.username}** has created **${Array(invite_count).length}**  with \`${count || '0'}\` successful uses`)
            }
        }
        const invites =  message.guild.invites.cache
        let num = 0
        const topTen = invites.filter((inv) => inv.uses > 0).sort((a, b) => b.uses - a.uses)
        let list = topTen.map((inv) => `> \`${num++}.\` **${inv.inviter.username}** has **${inv.uses.toLocaleString()}** uses for \`${inv.code}\``)
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynamic: true
            }))
            .setTitle(`${message.guild.name}'s Top Invites`)
            .setThumbnail(message.guild.iconURL({
                dynamic: true
            }))
            .setFooter(`Showing all time invites`)
            .setColor(this.hex)
        if (list.length <= 10) {
            message.channel.send({embeds: [embed]});
        } else {
            return new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
};