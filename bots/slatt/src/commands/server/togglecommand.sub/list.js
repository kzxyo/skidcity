const Subcommand = require('../../Subcommand.js');
const ReactionMenu = require('../../ReactionMenu.js');
const { MessageEmbed } = require('discord.js');
module.exports = class Check extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'togglecommand',
            name: 'list',
            aliases: ['ls', 'view'],
            type: client.types.SERVER,
            usage: 'togglecommand list',
            description: 'View your disabled commands',
        });
    }
    async run(message, args) {
        const cmds = await message.client.db.toggled_commands.findAll({where: {guildID: message.guild.id}})
        let num = 0
        const list = cmds.map(x => `\`${++num}\` **${x.cmd}**`)
        const embed = new MessageEmbed()
        .setTitle(`Disabled commands`)
        .setAuthor(message.author.tag, message.author.avatarURL({dynamic:true}))
        .setDescription(list.join('\n'))
        .setFooter(`${list.length} total`)
        .setColor(this.hex)
        if(list.length <= 10) {
            message.channel.send({ embeds: [embed] })
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
}