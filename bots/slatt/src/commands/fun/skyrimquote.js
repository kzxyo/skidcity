const Command = require('../Command.js');
const line = require('../../utils/json/skyrimquote.json');

module.exports = class SkyrimCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'skyrimquote',
            subcommands: ['skyrimquote'],
            aliases: ['guard', 'skyrimguard', 'guardline', 'quote'],
            type: client.types.FUN,
            description: 'Get a random guard quote from skyrim',
        });
    }

    async run(message) {
        return this.send_info(message, line[Math.round(Math.random() * (line.length - 1))]);
    }
}