const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')

module.exports = class Check extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'starboard',
            name: 'check',
            aliases: ['show'],
            type: client.types.SERVER,
            usage: 'starboard view',
            description: 'View your starboard settings',
        });
    }
    async run(message, args) {
        const starboardChannelId = await message.client.db.starboard.findOne({ where: { guildID: message.guild.id } })
        const emoji = await message.client.db.starboard_emoji.findOne({ where: { guildID: message.guild.id } })
        let displayemoji
        if (emoji !== null && emoji.emoji_id !== null) {
            displayemoji = `<:${emoji.emoji}:${emoji.emoji_id}>`
        } else {
            displayemoji = `${emoji.emoji}`
        }
        let count
        const threshold = this.db.get(`starboard_threshold_${message.guild.id}`)
        if (threshold) {
            count = parseInt(threshold)
        } else {
            count = 1
        }
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynamic: true
            }))
            .addField(`**Channel**`, `${starboardChannelId !== null ? message.guild.channels.cache.get(starboardChannelId.channel) : 'None'}`, true)
            .addField(`**Emoji**`, `${displayemoji}`, true )
            .addField(`**Threshold**`, `${count}`, true)
            .setTitle(`Starboard settings`)
            .setThumbnail(message.guild.iconURL({
                dynamic: true
            }))
            .setFooter(`channel ID: ${starboardChannelId !== null ? message.guild.channels.cache.get(starboardChannelId.channel).id : 'None'}`)
            .setColor(this.hex)
        message.channel.send({ embeds: [embed] })
    }
}