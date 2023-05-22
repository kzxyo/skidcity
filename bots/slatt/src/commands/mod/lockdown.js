const Command = require('../Command.js');
const Discord = require('discord.js');

module.exports = class LockdownCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'lockdown',
            aliases: ['lock'],
            usage: `lockdown`,
            description: 'locks down a channel',
            type: client.types.MOD,
            clientPermissions: ['MANAGE_CHANNELS'],
            userPermissions: ['MANAGE_CHANNELS'],
            subcommands: ['lockdown']
        });

    }

    async run(message, args) {
        let channel = await this.functions.get_channel(message, args.join(' '))
        await channel.permissionOverwrites.create(message.guild.id, {
            SEND_MESSAGES: false,
        })
        message.client.utils.send_log_message(message, message.member, this.name, `${channel} locked down`)
        return this.send_success(message, `i have set a lockdown for ${channel}`)
    };
}