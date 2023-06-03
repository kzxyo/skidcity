const Command = require('../Command.js');

module.exports = class BoostSettings extends Command {
    constructor(client) {
        super(client, {
            name: 'boost',
            description: 'Boost settings for your server',
            usage: `boost [subcommand] [args]`,
            type: client.types.SERVER,
            clientPermissions: ['MANAGE_MESSAGES', 'MANAGE_CHANNELS'],
            userPermissions: ['MANAGE_MESSAGES', 'MANAGE_CHANNELS'],
        });
    }
    async run(message, args) { 
        if(!args.length) return this.help(message)
    }
}