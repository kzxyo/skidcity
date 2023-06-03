const Subcommand = require('../../Subcommand.js');

module.exports = class Channel extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'starboard',
            name: 'channel',
            type: client.types.SERVER,
            usage: 'starboard channel [channel] or "none"',
            description: 'Update your starboard channel',
        });
    }
    async run(message, args) {
        const starboardChannelId = await message.client.db.starboard.findOne({ where: { guildID: message.guild.id } })
        if (!args[0]) return this.invalidArgs(message, `Provide a channel, or "none"`)
        if (args[0].toLowerCase() === 'none') {
            if (!starboardChannelId) return this.send_error(message, 1, `There is no starboard channel set`)
            await message.client.db.starboard.destroy({ where: { guildID: message.guild.id } })
            return this.send_success(message, `The starboard channel has been deleted`)
        }
        const channel = await this.functions.get_channel(message, args.join(' '))
        if(!channel) return this.invalidArgs(message, `The channel you provided was invalid`)
        if (starboardChannelId === null) {
            await message.client.db.starboard.create({
                guildID: message.guild.id,
                channel: channel.id
            })
        } else {
            await message.client.db.starboard.update({channel: channel.id }, {
                where: { guildID: message.guild.id }
            })
        }
        return this.send_success(message, `Starboard channel updated to ${channel}`)
    }
}