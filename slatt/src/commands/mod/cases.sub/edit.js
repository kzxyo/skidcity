const Subcommand = require('../../Subcommand.js');

module.exports = class RoleColor extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'cases',
            name: 'edit',
            aliases: ['update'],
            type: client.types.MOD,
            userPermissions: ['MANAGE_MESSAGES'],
            usage: 'cases edit [member] [case num] [new reason]',
            description: 'Update a case on a member',
        });
    }
    async run(message, args) {
        if (!args.length) {
            return this.help(message)
        }
        const member = await this.functions.get_member(message, args[0])
        if (!member) return this.invalidUser(message)
        if (isNaN(args[1])) return this.send_error(message, 1, `Provide a case number`)
        const num = parseInt(args[1])
        const check = await message.client.db.history.findOne({ where: { guildID: message.guild.id, userID: member.id, num: num, } })
        if (check === null) {
            return this.send_error(message, 1, `Case **#${num}** not found for ${member}`)
        } else {
            let reason = args.slice(2).join(' ');
            if (!reason) reason = 'no reason provided';
            if (reason.length > 1024) reason = reason.slice(0, 1021) + '...';
            await message.client.db.history.update({ reason: `${reason} *(edited)*` }, { where: { guildID: message.guild.id, userID: member.id, num: num, } })
            return this.send_success(message,  `Case **#${num}** updated ${member}`)
        }
    }
}