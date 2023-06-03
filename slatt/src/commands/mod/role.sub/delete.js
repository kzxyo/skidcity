const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'role',
            name: 'delete',
            type: client.types.MOD,
            usage: 'role delete [role]',
            description: 'Delete a role in your server',
        });
    }
    async run(message, args) {
        if (!args[0]) {
            return this.invalidArgs(message, `Provide a role to delete`)
        }
        let role = this.functions.get_role(message, args.join(' '))
        if(!role) return this.invalidArgs(message, `There was no role found with the name **${args.join(' ')}**`)
        let role_mention = role
        message.client.utils.send_log_message(message, message.member, `${this.base} ${this.name}`, `${role} was deleted`)
        await role.delete()
        return this.send_success(message, `I have deleted the role **${role_mention}**`)
    }
}