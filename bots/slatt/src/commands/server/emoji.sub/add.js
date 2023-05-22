const Subcommand = require('../../Subcommand.js');
const Discord = require('discord.js')

module.exports = class emoji_add extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'emoji',
            name: 'add',
            aliases: ['create'],
            type: client.types.SERVER,
            usage: 'emoji add [emote | url] [name]',
            description: 'add an emote to your server',
        });
    }
    async run(message, args) {
        if (!args.length && !message.attachments.first()) return this.help(message)
        let emote
        let link
        if (args.length && !args[0].startsWith("http") && !message.attachments.first() && Discord.Util.parseEmoji(args[0])) {
            emote = Discord.Util.parseEmoji(args[0])
            link = `https://cdn.discordapp.com/emojis/${emote.id}.${emote.animated ? "gif" : "png"}`
        } else if (args.length && args[0].startsWith("https://cdn.discordapp.com/")) {
            link = args[0]
        } else if (message.attachments.first()) {
            link = message.attachments.first().url
        } else {
            return this.send_error(message, 1, `You didnt provide a **cdn.discordapp.com** link`)
        }
        const name = args[1]
        if (!name && !emote && !message.attachments.first()) return this.send_error(message, 1, `Provide an emoji name`)
        message.guild.emojis.create(
            `${link}`, `${name || `${emote ? emote.name : 'new_emoji'}`}`
        )
        this.send_success(message, `new emoji created with name: **${name || `${emote ? emote.name : 'new_emoji'}`}** - [click to view](${link})`)
        message.client.utils.send_log_message(message, message.member, this.base + ' ' + this.name, `**{user.tag}** Added a new emoji`)
    }
}