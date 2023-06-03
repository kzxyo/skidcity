const Command = require('../Command.js');

module.exports = class log extends Command {
    constructor(client) {
        super(client, {
            name: 'log',
            usage: `log [channel] or "none"`,
            description: `Update your servers slatt-log`,
            type: client.types.SERVER,
            userPermissions: ['ADMINISTRATOR'],
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const check = this.db.get(`slatt_log_${message.guild.id}`)

        if (args[0].toLowerCase() === 'none' && check !== null) {
            this.db.delete(`slatt_log_${message.guild.id}`)
            return this.send_success(message, `Your previous log channel was deleted`)
        } else if (args[0].toLowerCase() === 'none' && check === null) {
            return this.send_error(message, 1, `There was no **previous log channel** found to remove`)
        }
        const channel = this.functions.get_channel(message, args.join(' '))
        if (!channel) return this.send_error(message, 0, 'Please provide a channel or provide a valid channel ID');
        this.db.set(`slatt_log_${message.guild.id}`, channel.id)
        return this.send_success(message, `Log channel for this server has been updated to ${channel}`)
    }
};
