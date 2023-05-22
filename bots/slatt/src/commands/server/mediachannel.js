const Command = require('../Command.js');

module.exports = class MediaChannel extends Command {
    constructor(client) {
        super(client, {
            name: 'mediachannel',
            aliases: ['mediac', 'medc'],
            type: client.types.SERVER,
            usage: `mediachannel [subcommand] [args]`,
            clientPermissions: ['MANAGE_CHANNELS', 'MANAGE_MESSAGES'],
            userPermissions: ['MANAGE_CHANNELS', 'MANAGE_MESSAGES'],
            description: `Set a media channel to restrict channel content to pictures/videos`,
        });
    }

    async run(message, args) {
        if (!args.length) return this.help(message)
    }
}
