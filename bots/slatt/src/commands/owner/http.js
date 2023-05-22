const Command = require('../Command.js');
const { MessageEmbed } = require('discord.js');
const {
    STATUS_CODES
} = require("http");

module.exports = class ReloadOwnerCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'http',
            description: "HTTP Status codes",
            aliases: ["httpcat", "cathttp"],
            usage: "httpstatus <status>",
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }

    async run(msg, [status]) {
        if (status !== "599" && !STATUS_CODES[status]) return this.send_error(msg, 1, `**${status}** is an invalid HTTP error code`)
        const embed = new MessageEmbed()
            .setColor(this.hex)
            .setDescription(status === "599" ? "Network Connect Timeout Error" : STATUS_CODES[status])
            .setAuthor(msg.author.tag, msg.author.displayAvatarURL({
                size: 64
            }))
        msg.channel.send(embed);
    }
}