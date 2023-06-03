const Command = require('../Command.js');

module.exports = class WhitelistGuild extends Command {
    constructor(client) {
        super(client, {
            name: 'wl',
            description: "whitelist a guild",
            aliases: ["gwl", "guilwl"],
            usage: "whitelist <id>",
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }

    async run(message, args) {
        this.db.set(`WhitelistedGuild_${args[0]}`, true)
        message.channel.send(':thumbsup:')
    }
}