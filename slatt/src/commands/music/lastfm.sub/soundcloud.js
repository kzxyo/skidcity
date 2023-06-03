const Subcommand = require('../../Subcommand.js');

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'soundcloud',
            aliases: ['sc'],
            type: client.types.LASTFM,
            usage: 'lastfm soundcloud [track]',
            description: 'Search for a soundcloud track',
        });
    }
    async run(message, args) {
        message.client.commands.get('soundcloud').run(message, args)
    }
}