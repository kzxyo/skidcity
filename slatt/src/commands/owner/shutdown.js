const Discord = require('discord.js');
const Command = require('../Command.js');
const { MessageEmbed } = require('discord.js');


module.exports = class ServersCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'shutdown',
            subcommands: [`shutdown`],
            aliases: ["exot"],
            usage: `shutdown`,
            description: 'shut the bot down',
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }

    run(message) {
        const embed = new MessageEmbed()
            .setTitle("shutdown")
            .setDescription("`shutdown` is only for the developer")
            .setColor(message.guild.me.displayHexColor);
        if (message.author.id !== '540071388069756931') return message.channel.send({ embeds: [embed] });

        message.channel.send(`Shutting down in ${Math.round(message.client.ws.ping)}ms`).then(() => {
            process.exit(1);
        })
    }
}