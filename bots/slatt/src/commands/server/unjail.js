const Command = require('../Command.js');
const db = require("quick.db")

module.exports = class DeafenCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'unjail',
            type: client.types.SERVER,
            clientPermissions: ['MANAGE_MESSAGES'],
            userPermissions: ['MANAGE_MESSAGES'],
            subcommands: ['unjail [member] '],
            usage: `unjail [member] [reason]`
        });

    }

    async run(message, args) {
        let dbjailrole = await message.client.db.jail_role.findOne({ where: { guildID: message.guild.id } })
        var jailrole = message.guild.roles.cache.get(dbjailrole) || await message.guild.roles.cache.find(r => r.name === "Jailed")
        if (!jailrole) {
            return this.send_error(message, 1, `there is no jail role set yet`)
        }
        if (!args.length) {
            return this.help(message);
        }
        if (!args.length) {
            return this.help(message)
        }
        const member = this.functions.get_member(message, args[0])
        if (!member) {
            return this.invalidUser(message)
        }
        let reason = args.slice(1).join(' ');
        if (!reason) reason = 'no reason provided';
        if (reason.length > 1024) reason = reason.slice(0, 1021) + '...';
        if (member.roles.cache.has(jailrole.id)) {
            await member.roles.remove(jailrole.id)
            message.client.utils.send_punishment({
                message: message,
                action: 'unjailed',
                reason: reason,
                member: member,
            })
            const amount = (await message.client.db.history.findAll({ where: { guildID: message.guild.id, userID: member.id } })).length + 1
            await message.client.db.history.create({
                guildID: message.guild.id,
                userID: member.id,
                action: 'unjailed',
                reason: reason,
                author: message.author.id,
                date: `${Date.now()}`,
                num: amount,
            })
            await message.client.db.jailed.destroy({ where: { userID: member.id } })
            this.send_success(message, `**${member.user.tag}** has been unjailed`)
            message.client.utils.send_log_message(message, member, this.name, `**{user.tag}** has been unjailed`)
        } else {
            return this.send_error(message, 0, "the user you provided is not jailed")

        }
    }
}