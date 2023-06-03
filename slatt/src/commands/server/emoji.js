const Command = require('../Command.js');
const Discord = require('discord.js')
const getColors = require('get-image-colors')
var rgb2hex = require('rgb2hex');

module.exports = class emoji extends Command {
    constructor(client) {
        super(client, {
            name: 'emoji',
            aliases: ['em', 'emote'],
            description: 'View an emoji',
            usage: `emoji [subcommand] [args]`,
            type: client.types.SERVER,
            clientPermissions: ['MANAGE_EMOJIS'],
            userPermissions: ['MANAGE_EMOJIS'],
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const emoji = Discord.Util.parseEmoji(args[0])
        if (Discord.Util.parseEmoji(args[0])) {
            getColors(`https://cdn.discordapp.com/emojis/${emoji.id}.${emoji.animated ? "gif" : "png"}`).then(colors => {
                let rgb = `${colors[0]._rgb[0]}, ${colors[0]._rgb[1]}, ${colors[0]._rgb[2]}`
                let color = rgb2hex(`rgb(${rgb})`)
                const embed = new Discord.MessageEmbed()
                    .setAuthor(`Emoji: ${emoji.name}`, `https://cdn.discordapp.com/emojis/${emoji.id}.${emoji.animated ? "gif" : "png"}`)
                    .addField(`**Id**`, `\`${emoji.id}\``)
                    .addField(`**Animated**`, `\`${emoji.animated ? 'Yes' : 'No'}\``)
                    .setColor(color.hex)
                    .setFooter(`Color: ${color.hex}`)
                    .setThumbnail(`https://cdn.discordapp.com/emojis/${emoji.id}.${emoji.animated ? "gif" : "png"}`)
                return message.channel.send({ embeds: [embed] })

            })
        } else {
            return this.send_error(message, 1, `Invalid emoji content`)
        }
    }
}