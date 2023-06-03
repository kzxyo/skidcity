const Subcommand = require('../../Subcommand.js');

module.exports = class Remove extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'mediachannel',
            name: 'remove',
            aliases: ['delete'],
            type: client.types.SERVER,
            usage: 'mediachannel remove [channel]',
            description: 'Remove a previously set mediachannel',
        });
    }
    async run(message, args) {
        const channel = this.functions.get_channel(message, args.join(' '))
        const check = await message.client.db.media_channel.findOne({ where: { guildID: message.guild.id, channelID: channel.id } })
        if (!channel) {
            return this.invalidArgs(message, `I could not find a channel with the name **${args.join(' ')}**`)
        } else {
            if (check === null) {
                return this.send_error(message, 1, `There is no current **media channel settings** applied to ${channel}`)
            } else {
                await message.client.db.media_channel.destroy({ where: { guildID: message.guild.id, channelID: channel.id } })
                return this.send_success(message, `Media channel settings removed from ${channel}`)
            }
        }
    }
}