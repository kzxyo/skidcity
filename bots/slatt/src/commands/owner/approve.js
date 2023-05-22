const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');

module.exports = class Approve extends Command {
    constructor(client) {
        super(client, {
            name: 'approve',
            usage: `approve <id>`,
            aliases: ["accept"],
            type: client.types.OWNER,
            ownerOnly: true,

        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const user = message.client.users.cache.get(args[0])
        if (!user) return this.invalidArgs(message, `Invalid user`)
        try {
            user.send(`<:success:827634903067394089> Your latest suggestion for slatt has been **approved**. ${args[1] ? `Heres some more info: **${args.slice(1).join(' ')}**` : ""}`)
            this.send_info(message, `Approved suggestion from  **${user.tag}**`)
        } catch (error) {
            return this.send_error(message, 1, `Could not dm **${user.tag}**`)
        }
    }
}