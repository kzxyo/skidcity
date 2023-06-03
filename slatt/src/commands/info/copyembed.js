const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');


module.exports = class copyembed extends Command {
    constructor(client) {
        super(client, {
            name: 'copyembed',
            aliases: ['ce', 'embedcopy', 'copy', 'stealembed'],
            usage: 'copyembed [message id]',
            description: 'Copy a messages embed paramaters',
            type: client.types.INFO
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const id = args[0]
        try {
            const msg = await message.channel.messages.fetch(id)
            if (!msg.embeds.length) return this.send_info(message, `message \`${msg.id}\` does not contain any embeds`)
            const code = message.client.utils.convert_embed_to_string(msg.embeds[0])
            const embed = new MessageEmbed()
            .setTitle(`Embed copied`)
            .setAuthor(message.author.tag, message.author.avatarURL({dynamic:true}))
            .setDescription(`\`\`\`${code.join('\n')}\`\`\``)
            .setFooter(`${code.length} total embed paramaters`)
            .setColor(this.hex)
            return message.channel.send({ embeds: [embed] })
        } catch (error) {
            console.log(error)
            return this.send_error(message, 1, `Invalid message id provided: \`${id}\``)
        }
    }
};