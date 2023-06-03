const Subcommand = require('../../Subcommand.js');

module.exports = class vanityroleMessage extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'vanityrole',
            name: 'message',
            aliases: ['msg'],
            type: client.types.SERVER,
            usage: 'vanityrole message [message] or "none"',
            description: 'Update your vanityrole message',
        });
    }
    async run(message, args) {
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        if (!args.length) return this.help(message)
        const msg = await message.client.db.vanity_message.findOne({ where: { guildID: message.guild.id } })
        if (args[0].toLowerCase() === 'none') {
            if (msg === null) {
                return this.send_error(message, 1, `There is no **vanityrole message** for this server`)
            } else {
                await message.client.db.vanity_message.destroy({ where: { guildID: message.guild.id } })
                return this.send_success(message, `The **vanityrole message** has been removed`)
            }
        } else {
            const content = args.join(' ')
            if (msg === null) {
                await message.client.db.vanity_message.create({
                    guildID: message.guild.id,
                    message: content
                })
            } else {
                await message.client.db.vanity_message.update({ message: content }, {
                    where: { guildID: message.guild.id }
                })
            }
            return this.send_success(message, `The **vanityrole message** has been updated, use \`${prefix.prefix}vanityrole check\``)
        }
    }
}