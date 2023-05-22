const Command = require('../Command.js');


module.exports = class PurgeCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'servername',
            aliases: ['guildname', 'setname'],
            type: client.types.MOD,
            description: 'Set a new server name',
            clientPermissions: ['MANAGE_GUILD'],
            userPermissions: ['MANAGE_GUILD'],
            usage: `servername <name>`
        });
    }
    async run(message, args) {
        let guild = message.guild;
        if (!args.length) {
            return this.help(message);
        }

        let newName = args.join(' ');
        let oldName = message.guild.name;
        guild.setName(newName)
            .then(updated => {
                message.client.utils.send_log_message(message, message.member, this.name, `**{user.tag}** Updated the server name from **${oldName}** to **${updated.name}**`)
                return this.send_success(message, `Successfully changed the name from **${oldName}** to **${updated.name}**`)
            })
            .catch(err => {
                this.send_error(message, 1, `an error occured while updating this server`)
            })

    }
}