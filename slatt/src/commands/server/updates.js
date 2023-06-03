const Command = require('../Command.js');

module.exports = class Updates extends Command {
    constructor(client) {
        super(client, {
            name: 'updates',
            usage: `updates [channel] or "none"`,
            aliases: ['updateschannel'],
            description: 'Set a channel to be notified about new bot features',
            type: client.types.SERVER,
            userPermissions: ['MANAGE_GUILD'],
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const check = await message.client.db.updates.findOne({ where: { guildID: message.guild.id } })
        if (args[0].toLowerCase() === 'none' && check !== null) {
            const channel = await message.client.db.updates.findOne({ where: { guildID: message.guild.id } })
            if (channel === null) {
                return this.send_error(message, 1, `There is no **updates channel** for this server`)
            } else {
                await message.client.db.updates.destroy({ where: { guildID: message.guild.id } })
                return this.send_success(message, `The **updates channel** has been removed`)
            }
        }
        const find_channel = await message.client.db.updates.findOne({ where: { guildID: message.guild.id } })
            const channel = this.functions.get_channel(message, args.join(' '))
            if (!channel) {
                return this.invalidArgs(message, `I could not find channel **${args.join(' ')}**`)
            } else {
                if (find_channel === null) {
                    await message.client.db.updates.create({
                        guildID: message.guild.id,
                        channelID: channel.id
                    })
                } else {
                    await message.client.db.updates.update({channelID: channel.id},{ where: { guildID: message.guild.id }})
                }
                return this.send_success(message, `The **updates channel** has been set to ${channel}`)
            }
    }
};
