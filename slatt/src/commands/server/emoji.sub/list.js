const Subcommand = require('../../Subcommand.js');
const Discord = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js');

module.exports = class emoji_add extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'emoji',
            name: 'list',
            aliases: ['ls'],
            type: client.types.SERVER,
            usage: 'emoji list',
            description: 'View a list of your servers emotes',
        });
    }
    async run(message, args) {
        if (!message.guild.emojis.cache.size) {
            return this.send_error(message, 1, `There are no emojis in this server`)
        }
        const emojis = message.guild.emojis.cache
        let list = emojis.map(e => `${e} - **${e.name}**`)
        const embed = new Discord.MessageEmbed()
            .setThumbnail(message.guild.iconURL({
                dynamic: true
            }))
            .setDescription(list.join('\n'))
            .setTitle(`Emoji List`)
            .setAuthor(message.author.tag, message.author.avatarURL({dynamic:true}))
            .setColor(this.hex)
            .setFooter(`${message.guild.emojis.cache.size} emojis`)
        if (list.length <= 10) {
            message.channel.send({ embeds: [embed] });
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
}
}