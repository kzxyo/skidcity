const Discord = require('discord.js');
const Command = require('../Command.js');

module.exports = class GuildBannerCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'disconnect',
            aliases: ['dc'],
            usage: `disconnect <member>`,
            description: `disconnect a user from voice chat`,
            subcommands: [`disconnect @conspiracy`],
            type: client.types.MOD,
            clientPermissions: ['MOVE_MEMBERS'],
            userPermissions: ['MOVE_MEMBERS'],
        });
    }
    async run(message, args) {
        if (!args.length) {
            return this.help(message)
        }
        const member = this.functions.get_member(message, args.join(' '))
        if (!member) {
            return this.invalidUser(message)
        }
        let {
            channel
        } = member.voice;

        if (!channel) return this.send_error(message, 0, 'provided user isnt in a voice channel');

        message.client.utils.send_log_message(message, member, this.name, `**{user.tag}** was disconnected from ${channel}`)
        member.voice.disconnect();
        return this.send_success(message, `${member} was successfully kicked from ${channel}`)

    }
}