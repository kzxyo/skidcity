const Command = require('../Command.js');

module.exports = class Vanityrole extends Command {
    constructor(client) {
        super(client, {
            name: 'vanityrole',
            aliases: ['statusrole', 'vr', 'sr', 'vanity'],
            usage: 'vanityrole [subcommand] [args]',
            description: 'Settings to add roles to server members who apply your vanity in their status',
            userPermissions: ['MANAGE_GUILD', 'MANAGE_ROLES'],
            userPermissions: ['MANAGE_GUILD', 'MANAGE_ROLES'],
            type: client.types.SERVER,
        });
    }
    async run(message, args) {
        if(!args.length) return this.help(message)
    }
}