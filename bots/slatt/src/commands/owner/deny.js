const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');

module.exports = class Deny extends Command {
    constructor(client) {
        super(client, {
            name: 'deny',
            usage: `deny <id>`,
            aliases: ["disapprove"],
            type: client.types.OWNER,
            ownerOnly: true,

        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const user = message.client.users.cache.get(args[0])
        if (!user) return this.invalidArgs(message, `Invalid user`)
        try {
            user.send(`<:redx:827632831999246346> Your latest suggestion for slatt has been **denied**. ${args[1] ? `Heres some more info: **${args.slice(1).join(' ')}**` : ""}`)
            this.send_info(message, `Denied suggestion from **${user.tag}**`)
        } catch (error) {
            return this.send_error(message, 1, `Could not dm **${user.tag}**`)
        }
    }
}