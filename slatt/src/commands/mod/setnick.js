const Command = require('../Command.js');
const Discord = require('discord.js');

module.exports = class SetnickCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'setnick',
            aliases: ['nick', 'nickname'],
            description: 'changes the nickname of a user',
            type: client.types.MOD,
            clientPermissions: ['MANAGE_NICKNAMES'],
            userPermissions: ['MANAGE_NICKNAMES'],
            subcommands: [`setnick @conspiracy cutie`],
            usage: `setnick <user> <nickName>`
        });

    }

    async run(message, args) {
        if (!args.length) {
            return this.help(message)
        }
        const member = this.functions.get_member(message, args[0])
        if (!member) {
            return this.invalidUser(message)
        }
        if (member.roles.highest.comparePositionTo(message.guild.me.roles.highest) >= 0) return this.send_error(message, 1, `I cant change **${member.user.username}**'s nickname`)
        if (!args[1]) {
            member.setNickname('')
            return this.send_success(message, `Reset **${member.user.tag}**'s nickname`)
        }
        let nick = args.slice(1).join(' ');
        if(nick.length > 32) return this.send_error(message, 1, `Cant update a nickname longer than **32** characters`)
        message.client.utils.send_log_message(message, member, this.name, `**{user.tag}** nickname updated to **${nick}**`)
        member.setNickname(nick)
        return this.send_success(message, `Changed Nickname of **${member.user.tag}** to **${nick}**`)
    }
}