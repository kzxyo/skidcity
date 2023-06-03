const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const embedbuilder = require('../../utils/embedbuilder/index.js')

module.exports = class editembed extends Command {
    constructor(client) {
        super(client, {
            name: 'editembed',
            aliases: ['edite', 'embededit', 'edit'],
            usage: 'editembed [message id] [code]',
            description: 'Edit an embeds code',
            clientPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'ADD_REACTIONS'],
            userPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'MANAGE_MESSAGES'],
            type: client.types.SERVER
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const id = args[0]
        try {
            const msgg = await message.channel.messages.fetch(id)
            if (msgg.author.id !== message.client.user.id) return this.send_error(message, 1, `**[Message](${msgg.url})** is not one of my embeds`)
            if (!msgg.embeds.length) return this.send_info(message, `**[Message](${msgg.url})** does not contain any embeds`)
            if (!this.db.get(`custom_embed_${message.guild.id}_${msgg.id}`)) {
                return this.send_error(message, 1, `**[Message](${msgg.url})** is not a custom made embed`)
            }
            let {
                msg,
                embed,
                errors
            } = embedbuilder(message.client.utils.replace_all_variables(args.slice(1).join(' '), message, message.member))
            embed = new MessageEmbed({
                type: 'rich',
                title: embed.title || null,
                description: embed.description || null,
                url: embed.url || null,
                color: embed.color || null,
                timestamp: embed.url || null,
                fields: embed.fields,
                thumbnail: embed.thumbnail || null,
                image: embed.image || null,
                author: embed.author || null,
                footer: embed.footer || null,
            })
            if (errors.length > 0) {
                return this.send_error(message, 1, 'error has occured, for help try using \`help embed\`')
            }
            msgg.edit({content: args.slice(1).join(' ').includes('$message') ? msg : null, embeds: [embed]})
            this.db.set(`custom_embed_${message.guild.id}_${msgg.id}`, {author: message.author.id})
            return this.send_success(message, `Edited **[message](${msgg.url})** with new embed code`)
        } catch (error) {
            console.log(error)
            return this.send_error(message, 1, `Invalid message id provided: \`${id}\``)
        }
    }
};