const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');

module.exports = class EvalCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'async',
            aliases: [`await`],
            usage: `async [code]`,
            description: 'Executes the provided code in **async**',
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }
    async run(message, args) {
        const Discord = require('discord.js')
        let client = message.client
        const input = args.join(' ');
        if (!input) return
        const embed = new MessageEmbed()
        try {
            let output = eval(`(async () => { ${input} })();`);
            if (typeof output !== 'string') output = require('util').inspect(output, {
                depth: 0
            });

            embed
                .setTitle(`Async`)
                .setDescription(`\`\`\`js\n${output.length > 1024 ? 'Too large to display.' : output}\`\`\``)
                .setColor('#66FF00');

        } catch (err) {
            embed
                .setTitle(`Async`)
                .setDescription(`\`\`\`js\n${err.length > 1024 ? 'Too large to display.' : err}\`\`\``)
                .setColor('#FF0000');
        }

        message.channel.send({ embeds: [embed] });


    }
}