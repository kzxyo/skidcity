const Command = require('../Command.js');


module.exports = class Togglecommand extends Command {
    constructor(client) {
        super(client, {
            name: 'togglecommand',
            aliases: ['togglecmd', 'toggle', 'disable', 'disablecommand'],
            description: 'Disable commands in your server',
            usage: `togglecommand <command name>`,
            type: client.types.SERVER,
            userPermissions: ['ADMINISTRATOR'],
        });
    }
    async run(message, args) {
        const client = message.client
        if (!args.length) return this.help(message)
        let subcommand
        let command = client.commands.get(args[0]) || client.aliases.get(args[0])
        if (command) subcommand = client.subcommands.get(`${command.name} ${args[1]}`) || client.subcommand_aliases.get(`${command.name} ${args[1]}`)
        if (subcommand) {
            const check = await client.db.toggled_commands.findOne({ where: { guildID: message.guild.id, cmd: `${command.name} ${subcommand.name}` } })
            if (check) {
                await client.db.toggled_commands.destroy({ where: { guildID: message.guild.id, cmd: `${command.name} ${subcommand.name}` } })
                return this.send_success(message, `Enabled subcommand **${command.name} ${subcommand.name}**`)
            } else {
                await client.db.toggled_commands.create({ guildID: message.guild.id, cmd: `${command.name} ${subcommand.name}` })
                return this.send_success(message, `Disabled subcommand **${command.name} ${subcommand.name}**`)
            }
        } else if (command) {
            const check = await client.db.toggled_commands.findOne({ where: { guildID: message.guild.id, cmd: command.name } })
            if (check) {
                await client.db.toggled_commands.destroy({ where: { guildID: message.guild.id, cmd: command.name } })
                return this.send_success(message, `Enabled command **${command.name}**`)
            } else {
                await client.db.toggled_commands.create({ guildID: message.guild.id, cmd: command.name })
                return this.send_success(message, `Disabled command **${command.name}**`)
            }
        } else {
            return this.send_error(message, 1, `Invalid **command or subcommand**. Use \`${message.prefix}help\` for a list`)
        }

    }
};