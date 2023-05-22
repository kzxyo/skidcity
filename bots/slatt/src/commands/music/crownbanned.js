const Command = require('../Command.js');
const ReactionMenu = require('../ReactionMenu.js');
const Discord = require('discord.js')
module.exports = class Crownbanned extends Command {
    constructor(client) {
        super(client, {
            name: 'crownbanned',
            aliases: ['cbanned'],
            type: client.types.LASTFM,
            usage: 'crownbanned',
            description: 'Displays a list of every crownbanned member',
            userPermissions: ['MANAGE_GUILD', 'MANAGE_MESSAGES'],
            subcommands: ['crownbanned']
        });
    }
    async run(message, args) {
        const {
            bans,
        } = require('../../utils/db.js')
        const banned = await bans.findAll({
            where: {
                guildID: message.guild.id,
            }
        })
        if(!banned.length) {
            return this.send_info(message, `There are **no** crownbanned members here`)
        }
        let num = 0
        let list = banned.map(b => `${++num} \`${b.userID}\` (${message.guild.members.cache.get(b.userID).user.tag})`)
        const embed = new Discord.MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynamic: true
            }))
            .setThumbnail(message.guild.iconURL({dynamic:true}))
            .setColor(this.hex)
        if (list.length <= 10) {
            const range = (list.length == 1) ? '[1]' : `[1 - ${list.length}]`;
            message.channel.send(embed.setTitle(`${message.guild.name}'s crownbanned members ${range}`).setDescription(list.join('\n')));
        } else {
            return new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
}