const Subcommand = require('../../Subcommand.js');

module.exports = class Boostmessage extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'boost',
            name: 'message',
            aliases: ['msg'],
            type: client.types.SERVER,
            usage: 'boost message [message] or "none"',
            description: 'Update your servers boost message',
        });
    }
    async run(message, args) {
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        if (!args.length) return this.help(message)
        const msg = await message.client.db.boost_message.findOne({ where: { guildID: message.guild.id } })
        if (args[0].toLowerCase() === 'none') {
            if (msg === null) {
                return this.send_error(message, 1, `There is no **boost message** for this server`)
            } else {
                await message.client.db.boost_message.destroy({ where: { guildID: message.guild.id } })
                return this.send_success(message, `The **boost message** has been removed`)
            }
        } else {
            const content = args.join(' ')
            if (msg === null) {
                await message.client.db.boost_message.create({guildID: message.guild.id, message: content })
            } else {
                await message.client.db.boost_message.update({ message: content }, { where: { guildID: message.guild.id } })
            }
            return this.send_success(message, `The **boost message** has been updated, use \`${prefix.prefix}boost config\``)
        }
    }
}