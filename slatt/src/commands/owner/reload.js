const Command = require('../Command.js');
const {
    join,
    resolve
} = require('path');

module.exports = class Reload extends Command {
    constructor(client) {
        super(client, {
            name: 'reload',
            aliases: ['rl'],
            usage: `reload [command]`,
            subcommands: ['reload'],
            type: client.types.OWNER,
            ownerOnly: true,
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const client = message.client
        if (args[0].toLowerCase() === 'all') {
            message.client.unloadCommands('./src/commands')
            message.client.loadCommands('./src/commands')
            return this.send_success(message, `Reloaded: **${message.client.commands.size}** commands`)
        }
        if (args[0].toLowerCase() === 'event' || args[0].toLowerCase() === '--event' || args[0].toLowerCase() === 'e') {
            const event = args[1]
            client.removeAllListeners(event)
            delete require.cache[require.resolve(`../../events/${event}.js`)]
            const new_pull = require(`../../events/${event}.js`)
            client.on(event, new_pull.bind(null, this.client))
            return this.send_success(message, `Reloaded event **${event}**`)
        }
        const command = client.commands.get(args[0].toLowerCase()) || client.aliases.get(args[0].toLowerCase())
        if (!command) return this.send_error(message, 1, `Invalid subcommand/command provided`)
        const subcommand = client.subcommands.get(command.name + ' ' + args[1]) || client.subcommand_aliases.get(command.name + ' ' + args[1])
        if (!subcommand && !command) return this.send_error(message, 1, `Invalid subcommand/command provided`)
        if (subcommand) {
            delete require.cache[require.resolve(`../${command.type === 'lastfm' ? 'music' : command.type}/${command.name}.sub/${subcommand.name}.js`)]
            if (subcommand.aliases) {
                subcommand.aliases.forEach(alias => {
                    client.subcommand_aliases.delete(command.name + ' ' + alias)
                });
            }
            client.subcommands.delete(command.name + ' ' + subcommand.name)
            const pull = require(`../${subcommand.type === 'lastfm' ? 'music' : command.type}/${command.name}.sub/${subcommand.name}.js`)
            const class_update = new pull(this.client)
            client.subcommands.set(command.name + ' ' + subcommand.name, class_update);
            if (subcommand.aliases) {
                subcommand.aliases.forEach(alias => {
                    client.subcommand_aliases.set(command.name + ' ' + alias, class_update)
                });
            }
            return this.send_info(message, `Subcommand **${subcommand.base + ' ' + subcommand.name}** reloaded for type **${command.type}** on base command **${subcommand.base}**`)
        }
        if (!command) return this.send_info(message, `There was no command/alise found with the name **${args[0]}**`)
        delete require.cache[require.resolve(`../${command.type === 'lastfm' ? 'music' : command.type}/${command.name}.js`)]
        if (command.aliases) {
            command.aliases.forEach(alias => {
                client.aliases.delete(alias)
            });
        }
        client.commands.delete(command.name)
        const pull = require(`../${command.type === 'lastfm' ? 'music' : command.type}/${command.name}.js`)
        const class_update = new pull(this.client)
        client.commands.set(command.name, class_update);
        if (command.aliases) {
            command.aliases.forEach(alias => {
                client.aliases.set(alias, class_update)
            });
        }
        return this.send_info(message, `Command **${command.name}** reloaded for type **${command.type}**`)
    }
}