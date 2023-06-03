const Subcommand = require('../../Subcommand.js');
const embedbuilder = require('../../../utils/embedbuilder/index.js')
module.exports = class Message extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'welcome',
            name: 'check',
            aliases: ['see'],
            type: client.types.SERVER,
            usage: 'welcome check',
            description: 'View your welcome message',
        });
    }
    async run(message, args) {
        const { MessageEmbed } = require('discord.js')
        const Message = await message.client.db.welcome_message.findOne({ where: { guildID: message.guild.id } })
        const Embed = await message.client.db.welcome_embed.findOne({ where: { guildID: message.guild.id } })
        if (!Message && !Embed) return this.send_error(message, 1, `There isnt any **welcome settings** for this server yet`)
        if (Embed) {
            let {
                msg,
                embed
            } = embedbuilder(message.client.utils.replace_all_variables(Embed.code, message, message.member))
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
            message.channel.send({
                content: message.client.utils.replace_all_variables(msg, message, message.member),
                embeds: [embed]
            })
        } else if (Message) {
            message.channel.send(message.client.utils.replace_all_variables(Message.message, message, message.member))
        }
    }
}