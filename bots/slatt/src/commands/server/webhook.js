const Command = require('../Command.js');
const { stripIndent } = require('common-tags')
module.exports = class Variables extends Command {
    constructor(client) {
        super(client, {
            name: "webhook",
            aliases: ['webh', 'whook'],
            description: `webhook stuffs`,
            usage: stripIndent`
            webhook [subcommand] [args]
            webhook [url] --embed <code> --content <content>
            `,
            type: client.types.SERVER,
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const embedbuilder = require('../../utils/embedbuilder/index.js')
        const fetch = require('node-fetch')
        const {
            MessageEmbed,
            WebhookClient
        } = require('discord.js');
        const url = args[0]
        if (!url.startsWith('https://discord.com/api/webhooks/')) return this.send_error(message, 1, `No valid **webhook URL** provided`)
        let res = await fetch(url)
        res = await res.json()
        if (message.guild.id !== res.guild_id) return this.send_error(message, 1, `no..`)

        const webhook = new WebhookClient({ url: url });
        const content = message.client.utils.flag(message.content, 'content')
        const embed_code = message.client.utils.flag(message.content, 'embed')
        let {
            msg,
            embed
        } = embedbuilder(message.client.utils.replace_all_variables(embed_code || '', message, message.member))
        embed = new MessageEmbed({
            type: embed.type,
            title: embed.title || null,
            description: embed.description || null,
            url: embed.url || null,
            color: embed.color || null,
            timestamp: embed.timestamp || null,
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
        webhook.send({
            content: message.client.utils.replace_all_variables(content, message, message.member),
            embeds: [embed]
        });

    }
}