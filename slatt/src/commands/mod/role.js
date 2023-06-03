const {
    MessageEmbed
} = require('discord.js');
const Command = require('../Command.js');
module.exports = class Role extends Command {
    constructor(client) {
        super(client, {
            name: 'role',
            type: client.types.MOD,
            description: `Manage roles in your server easier`,
            usage: `role [subcommand] [args]`,
            clientPermissions: ['MANAGE_ROLES'],
            userPermissions: ['MANAGE_ROLES'],
        });
    }
    async run(message, args) {
        if (!args.length) {
            return this.help(message)
        }
        const is_subcommand = message.client.subcommands.get(`role ${args[0]}`) || message.client.subcommand_aliases.get(`role ${args[0]}`)
        if (!is_subcommand) {
            const rMember = this.functions.get_member(message, args[0])
            if (!rMember) {
                return this.invalidUser(message)
            }
            if (!args[1]) return this.send_error(message, 0, `provide a role to add to **${rMember.user.tag}**`)
            let role = this.functions.get_role(message, args.slice(1).join(' '))
            if (!role) return this.invalidArgs(message, `There was no role found with the name **${args.slice(1).join(' ')}**`)
            if (role.managed) {
                return this.invalidArgs(message, `I am unable to add **${role.name}** to **${rMember.user.tag}** as the role is managed by another bot`)
            }
            if (message.member.roles.highest.position <= rMember.roles.highest.position && rMember !== message.member) return this.send_error(message, 0, `the member **${rMember.user.tag}** is too high on the hierarchy for you to manage`);
            if (role.rawPosition >= message.member.roles.highest.position) return this.send_error(message, 0, `the role **${role.name}** is too high on the hierarchy for you to manage`);
            if (role.rawPosition >= message.guild.me.roles.highest.position) return this.send_error(message, 0, `the role **${role.name}** is too high on the hierarchy for me to manage`);
            if (rMember.roles.cache.has(role.id)) {
                await rMember.roles.remove(role.id).catch(e => {
                    return this.send_error(message, 1, `There was an error removing ${role} fom **${rMember.user.tag}**`)
                })
                this.send_success(message, `The role ${role} has been removed from **${rMember.user.tag}**`)
                return message.client.utils.send_log_message(message, rMember, this.name, `Role removed from **{user.tag}**`)
            } else {
                await rMember.roles.add(role.id).catch(e => {
                    return this.send_error(message, 1, `There was an error adding ${role} to **${rMember.user.tag}**`)
                })
                this.send_success(message, `The role ${role} has been added to **${rMember.user.tag}**`)
                return message.client.utils.send_log_message(message, rMember, this.name, `Role added to **{user.tag}**`)
            }
        }
    }
}