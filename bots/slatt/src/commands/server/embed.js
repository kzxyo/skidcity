const embedbuilder = require('../../utils/embedbuilder/index.js')
const Command = require('../Command.js');
const moment = require('moment');
const { MessageEmbed } = require('discord.js');

module.exports = class EmbedCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'embed',
            usage: `embed $title • $color • $description • $image • $thumbnail • $footer • $field • $author • $url • $timestamp now • $message`,
            subcommands: [`embed`],
            clientPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'ADD_REACTIONS'],
            userPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'MANAGE_MESSAGES'],
            description: `example: embed $description {variable.variable} $author {variable.variable} $and {variable.image}`,
            type: client.types.SERVER,
        });

    }
    async run(message, args) {
        if (!args.length) {
            return this.help(message)
        }
        let {
            msg,
            embed
        } = embedbuilder(message.client.utils.replace_all_variables(args.join(' '), message, message.member))

        embed = new MessageEmbed({
            type: embed.type,
            title: embed.title || null,
            description: embed.description || null,
            url: embed.url || null,
            color: embed.color || null,
            timestamp: embed.url || null,
            fields: embed.fields,
            thumbnail: embed.thumbnail || null,
            image: embed.image || null,
            author: embed.author || null,
            footer: embed.footer,
        })
        let errors = []
        for (const param of Object.values(embed)) {
            if (param === null || param === []) {
                errors.push(param)
            }
        }
        if (errors.length === 10) {
            return this.send_error(message, 1, `Invalid embed paramaters.
If you are struggling with making embeds please visit **https://slatt.gitbook.io/slatt-help/variables/variables**
\`\`\`Please include at least one $paramater in your embed\`\`\``)
        }
        message.channel.send({ content: message.client.utils.replace_all_variables(args.join(' ').includes('$message') ? msg : null, message, message.member), embeds: [embed] }).then(msg => {
            this.db.set(`custom_embed_${message.guild.id}_${msg.id}`, {
                author: message.author.id
            })
        })

    }
}