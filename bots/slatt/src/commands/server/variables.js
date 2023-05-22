const {
    MessageEmbed
} = require('discord.js');
const Command = require('../Command.js');
const ReactionMenu = require('../ReactionMenu.js');
const moment = require('moment');

module.exports = class Variables extends Command {
    constructor(client) {
        super(client, {
            name: "variables",
            aliases: ['vari', 'var'],
            description: `variables used for customcommands, lastfm nowplaying embeds, welcome messages, etc..`,
            usage: 'variables',
            type: client.types.SERVER,
            subcommands: ['variables'],
        });
    }
    async run(message) {
      return this.send_info(message, `Click [here](https://slatt.gitbook.io/slatt-help/variables/variables) to view a list of **input variables**`)
    }
}