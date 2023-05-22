const Discord = require('discord.js')
const {
    parse
} = require("twemoji-parser");
const Command = require('../Command.js');

module.exports = class EnlargeCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'enlarge',
            aliases: ['e'],
            subcommands: ['enlarge'],
            description: 'enlarge a emoji, and sends it as a link',
            usage: 'enlarge <emoji>',
            type: client.types.FUN
        });
    }

    async run(message, args) {
        const emoji = args[0];
        if (!args.length) {
            return this.help(message);
        }
        let custom = Discord.Util.parseEmoji(emoji);
        if (custom.id) {
            message.channel.send(`https://cdn.discordapp.com/emojis/${custom.id}.${custom.animated ? "gif" : "png"}`);
        } else {
            let parsed = parse(emoji, {
                assetType: "png"
            });
            if (!parsed[0]) return this.send_error(message, 0, "Invalid emoji");

            message.channel.send(parsed[0].url);
        }
    }
}