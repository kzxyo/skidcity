const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')

module.exports = class RoleColor extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'role',
            name: 'color',
            type: client.types.MOD,
            usage: 'role color [role] [color]',
            description: 'Edit a specific roles color',
        });
    }
    async run(message, args) {
        let roleColor = this.functions.get_role(message, args[0])
        if (!roleColor) {
            return this.invalidArgs(message, `There was no role found with the name **${args[0]}**`)
        }
        let newColor = args[1]
        if (!newColor || newColor.length > 7) {
            return this.invalidArgs(message, `Provide a hexcode, for example: **#304583**`)
        }
        roleColor.edit({
            color: newColor
        })
        message.client.utils.send_log_message(message, message.member, `${this.base} ${this.name}`, `${roleColor} role color updated to ${newColor}`)
        return this.send_success(message, `${roleColor}'s color has been changed to **${newColor}**`)
    }
}