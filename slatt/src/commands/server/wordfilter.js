const Command = require('../Command.js');


module.exports = class Wordfilter extends Command {
    constructor(client) {
        super(client, {
            name: 'wordfilter',
            aliases: ['filter', 'wordban', 'chatfilter', 'wf'],
            type: client.types.SERVER,
            description: 'Ban words from being said in your server',
            clientPermissions: ['MANAGE_MESSAGES', 'BAN_MEMBERS', 'KICK_MEMBERS', 'MANAGE_ROLES'],
            userPermissions:  ['MANAGE_MESSAGES', 'BAN_MEMBERS', 'KICK_MEMBERS', 'MANAGE_ROLES'],
            usage: `wordfilter [subcommand] [args]`
        });
    }
    async run(message, args) {
        if(!args.length) return this.help(message)

    }
}