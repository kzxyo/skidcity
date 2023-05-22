const Subcommand = require('../../Subcommand.js');

module.exports = class Boostchannel extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'boost',
            name: 'channel',
            type: client.types.SERVER,
            usage: 'boost channel [channel] or "none"',
            description: 'Update your servers boost channel',
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        if (args[0].toLowerCase() === 'none') {
            const channel = await message.client.db.boost_channel.findOne({ where: { guildID: message.guild.id } })
            if (channel === null) {
                return this.send_error(message, 1, `There is no **boost message channel** for this server`)
            } else {
                await message.client.db.boost_channel.destroy({ where: { guildID: message.guild.id } })
                return this.send_success(message, `The **boost message channel** has been removed`)
            }
        } else {
            const find_channel = await message.client.db.boost_channel.findOne({ where: { guildID: message.guild.id } })
            const channel = this.functions.get_channel(message, args.join(' '))
            if (!channel) {
                return this.invalidArgs(message, `I could not find channel **${args.join(' ')}**`)
            } else {
                if (find_channel === null) {
                    await message.client.db.boost_channel.create({
                        guildID: message.guild.id,
                        channel: channel.id
                    })
                } else {
                    await message.client.db.boost_channel.update({channel: channel.id},{ where: { guildID: message.guild.id }})
                }
                return this.send_success(message, `The **boost message channel** has been set to ${channel}`)
            }
        }
    }
}