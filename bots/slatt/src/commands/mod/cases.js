const { MessageEmbed } = require('discord.js');
const Command = require('../Command.js');
const ReactionMenu = require('../ReactionMenu.js');

module.exports = class Cases extends Command {
    constructor(client) {
        super(client, {
            name: 'cases',
            aliases: ['history', 'modhistory', 'punishments', 'past', 'case'],
            usage: 'cases [user]',
            description: 'View history on a user in your server',
            type: client.types.MOD,
            userPermissions: ['MANAGE_MESSAGES'],
        });
    }
    async run(message, args) {
        if (!args.length) {
            return this.help(message)
        }
        const member = await this.functions.get_member(message, args.join(' '))
        if(!member) return this.invalidUser(message)
        const cases = await message.client.db.history.findAll({ where: { userID: member.id, guildID: message.guild.id} })
        const list = cases.map(x => `\`${x.num}\` **${message.client.utils.capitalize(x.action)}**: ${x.reason}`)
        if(list.length === 0) return this.send_error(message, 1, `No cases found for ${member}`)
        const embed = new MessageEmbed()
        .setColor(this.hex)
        .setAuthor(message.author.tag, message.author.avatarURL({dynamic:true}))
        .setDescription(`${list.join('\n')}`)
        .setTitle(`Cases from **${member.user.tag}**`)
        .setFooter(`${list.length} total logged punishments`)
        if(list.length <= 10) {
            message.channel.send({embeds: [embed]})
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
}