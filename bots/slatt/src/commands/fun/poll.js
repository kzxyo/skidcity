const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
module.exports = class PollCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'poll',
            subcommands: ['poll should we delete this server'],
            description: `create a quick poll that no one cares about`,
            type: client.types.FUN,
            usage: `poll`,
        });

    }

    async run(message, args, ) {
        let content = args.join(" ")
        if (!args.length) {
            return this.help(message);
        }
        const embed = new MessageEmbed()
            .setAuthor(message.member.displayName,  message.author.displayAvatarURL({ dynamic: true }))
            .setDescription(`*${content}*`)
            .setColor(this.hex)
            .setFooter(`poll created by ${message.author.tag}`)
        message.channel.send({ embeds: [embed] }).then(embedMessage => {
            embedMessage.react("👍").then(embedMessage.react("👎"))
        })
    }
}