const Subcommand = require('../../Subcommand.js');
const Discord = require('discord.js')

module.exports = class emoji_add extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'emoji',
            name: 'remove',
            aliases: ['delete'],
            type: client.types.SERVER,
            usage: 'emoji delete [emote]',
            description: 'Remove an emote fromy your server',
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        if (message.guild.emojis.cache.size === 0) {
            return this.send_error(message, 1, `There arent any emojis to delete in this server`)
        }
        let EmojiRegex = args[0].match(/(?<=<?a?:?\w{2,32}:)\d{17,19}(?=>?)/gi)
        if (!EmojiRegex === null) return this.invalidArgs(message, `The emoji you provided was invalid`)
        EmojiRegex = EmojiRegex[0]
        let emoji = message.guild.emojis.cache.get(EmojiRegex)
        if (!emoji) {
            return this.invalidArgs(message, `The emoji you provided was invalid`)
        }
        if (!emoji.name || !emoji.id) {
            return this.invalidArgs(message, `The emoji you provided was not from this server or invalid`)
        }
        await emoji.delete()
        this.send_success(message, `Deleted emoji: **${emoji.name}**`)
        message.client.utils.send_log_message(message, message.member, this.base + ' ' + this.name, `**{user.tag}** Deleted an emoji`)
    }
}