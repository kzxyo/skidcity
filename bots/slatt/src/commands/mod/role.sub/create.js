const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const ReactionMenu = require('../../ReactionMenu.js')

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'role',
            name: 'create',
            type: client.types.MOD,
            usage: 'role create [role] $c [color]',
            description: 'Create a role in your server with a optional color',
        });
    }
    async run(message, args) {
        let role = args[0]
        if (!role) return this.invalidArgs(message, `Provide a role name to set your newly created role to`)
        const role_paramater = this.functions.paramater('c', args.join(' '))
        const newRole = await message.guild.roles.create({
            name: `${role_paramater[0]}`,
            color: `${role_paramater[1]}`,

        })
        message.client.utils.send_log_message(message, message.member, `${this.base} ${this.name}`, `New role created: ${newRole} with the color **${args.join(' ').split('$c')[1] || 'Default'}**`)
        return this.send_success(message, `I have created ${newRole} with the color **${args.join(' ').split('$c')[1] || 'Default'}**`)
    }
}