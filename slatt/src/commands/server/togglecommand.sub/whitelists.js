const Subcommand = require('../../Subcommand.js');
const ReactionMenu = require('../../ReactionMenu.js');
const { MessageEmbed } = require('discord.js');
module.exports = class Check extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'togglecommand',
            name: 'whitelists',
            aliases: ['whitelisted', 'ignoring'],
            type: client.types.SERVER,
            usage: 'togglecommand whitelists',
            description: 'View a list of every member whitelisted for a command',
        });
    }
    async run(message, args) {
        const cmds = await message.client.db.command_whitelists.findAll({where: {guildID: message.guild.id}})
        let num = 0
        const list = cmds.map(x => `\`${++num}\` ${message.client.users.cache.get(x.userID) ? message.client.users.cache.get(x.userID).tag : `UNKOWN_USER_${x.userID}`}: **${x.cmd}**`)
        const embed = new MessageEmbed()
        .setTitle(`Whitelists`)
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