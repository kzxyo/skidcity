const Command = require('../Command.js');
const Discord = require('discord.js')
module.exports = class FMCommand extends Command {
    constructor(client) {
        super(client, {
            name: "cleanup",
            type: client.types.MOD,
            aliases: ['clean'],
            description: `cleansup commands from me, not other bots.`,
            clientPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'MANAGE_MESSAGES'],
            userPermissions: ['MANAGE_MESSAGES'],
            subcommands: [`cleanup`]
        });
    }

    async run(message) {
        this.send_info(message, `Cleaning up messages sent by me`)
        const msgs = await message.channel.messages.fetch({ limit: 90 });
        let msg_array = msgs
          .filter(
            m =>
              m.author.id === this.client.user.id
          );
          message.client.utils.send_log_message(message, message.member, this.name, `Cleaned up messages by me in ${message.channel}`)
          message.channel.bulkDelete(msg_array);
    }

}

