const Command = require('../Command.js');

module.exports = class CommandCountCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'commandcount',
            aliases: ['cmdcount', 'cmdc'],
            usage: 'commandcount',
            type: client.types.INFO,
            description: 'current count of commands',
            subcommands: ['commandcount']
        });
    }
    async run(message) {
        return this.send_info(message, `**${parseInt(message.client.commands.size)+parseInt(message.client.subcommands.size)}** total commands, **${message.client.aliases.size}** aliases, and **${message.client.subcommands.size}** subcommands`)
    }
};