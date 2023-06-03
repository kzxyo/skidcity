const Subcommand = require('../../Subcommand.js');
const Discord = require('discord.js')

module.exports = class emoji_add extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'starboard',
            name: 'threshold',
            aliases: ['num', 'number'],
            type: client.types.SERVER,
            usage: 'emoji threshold [number]',
            description: 'Set a threshold for starboard messages',
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const number = args[0]
        if(isNaN(args[0])) return this.send_error(message, 1, `You must provided a number`)
        const num = parseInt(number)
        if(num === 0 || num > 15) return this.send_error(message, 1, `Provide a number 1-15`)
        this.db.set(`starboard_threshold_${message.guild.id}`, num)
        return this.send_success(message, `Updated starboard required emoji count to **${num}**`)
    }
}