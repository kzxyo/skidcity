const Subcommand = require('../../Subcommand.js');

module.exports = class Channel extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'vanityrole',
            name: 'channel',
            type: client.types.SERVER,
            usage: 'vanityrole channel [channel] or "none"',
            description: 'Update your servers vanityrole message channel',
        });
    }
    async run(message, args) {
        if(!args.length) return this.help(message)
        const vr_channel = await message.client.db.vanity_channel.findOne({ where: { guildID: message.guild.id } })
        let channel = await this.functions.get_channel(message, args.join(' '))
        if (args[0] === 'none') {
            if (vr_channel) {
                await message.client.db.vanity_channel.destroy({ where: { guildID: message.guild.id } })
                return this.send_success(message, `Vanityrole message channel has been removed`)
            } else {
                return this.send_error(message, 1, `I could not find a vanityrole message channel to remove`)
            }
        }
        if (vr_channel === null) {
            await message.client.db.vanity_channel.create({
                guildID: message.guild.id,
                channel: channel.id
            })
        } else {
            await message.client.db.vanity_channel.update({channel: channel.id }, {
                where: { guildID: message.guild.id }
            })
        }
        return this.send_success(message, `Vanityrole message channel has been set to **${channel}**`)
    }
}