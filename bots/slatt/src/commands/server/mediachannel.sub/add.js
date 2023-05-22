const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const db = require('quick.db')
module.exports = class Add extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'mediachannel',
            name: 'add',
            aliases: ['create'],
            type: client.types.SERVER,
            usage: 'mediachannel add [channel]',
            description: 'Add a mediachannel settings for a channel',
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const channel = this.functions.get_channel(message, args.join(' '))
        const check = await message.client.db.media_channel.findOne({ where: { guildID: message.guild.id, channelID: channel.id } })
        if (!channel) {
            return this.invalidArgs(message, `I could not find a channel with the name **${args.join(' ')}**`)
        } else {
            if (check === null) {
                message.client.db.media_channel.create({
                    guildID: message.guild.id,
                    channelID: channel.id,
                    channel: channel.id
            })
            return this.send_success(message, `A new **media channel** was set to ${channel}`)
        } else {
            return this.send_error(message, 1, `There is already **media channel settings** applied to ${channel}`)
        }
    }
}
}