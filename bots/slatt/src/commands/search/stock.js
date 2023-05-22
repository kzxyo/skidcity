const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const Discord = require('discord.js')

module.exports = class GuildBannerCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'stock',
            usage: `stock <query>`,
            aliases: ["stocks", "st"],
            description: `Search a stock by query (NOT DONE)`,
            type: client.types.SEARCH,
        });
    }
    async run(message, args) {
        return
        if (!args.length) return this.help(message)
    }
}