const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'role',
            name: 'rename',
            type: client.types.MOD,
            usage: 'role rename [role]',
            description: 'Edit a specific roles name',
        });
    }
    async run(message, args) {
        if(!args.length) return this.help(message)
        let roleName = this.functions.get_role(message, args[0])
            if (!roleName) {
                return this.invalidArgs(message, `There was no role found with the name **${args[0]}**`)
            }
            let newName = args.slice(1).join(' ')
            if (!newName) {
                return this.send_error(message, 1, `provide a name to set your role to`)
            }
            roleName.edit({
                name: newName
            })
            message.client.utils.send_log_message(message, message.member, `${this.base} ${this.name}`, `\`${roleName.name}'s\` name has been changed to **${newName}**`)
            return this.send_success(message, `\`${roleName.name}'s\` name has been changed to **${newName}**`)
    }
}