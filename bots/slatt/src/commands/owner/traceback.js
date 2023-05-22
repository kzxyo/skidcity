const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');

module.exports = class TraceBack extends Command {
    constructor(client) {
        super(client, {
            name: 'traceback',
            aliases: [`traceb`, 'tb', 'error'],
            usage: `traceback`,
            description: 'Traces back the last command error',
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }
    async run(message, args) {
        let tr = this.db.get(`TraceBack`)
        const embed = new MessageEmbed()
            .setAuthor(tr.author.tag, tr.author.avatarURL)
            .setDescription(`${tr.content}\n\`\`\`js
${tr.error.split('at')[0]}\`\`\``)
            .setTitle(`Error: ${tr.command}`)
            .setColor(this.hex)
        message.channel.send({ embeds: [embed] })
    }
}