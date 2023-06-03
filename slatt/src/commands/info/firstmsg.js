const Command = require('../Command.js');

module.exports = class FirstMsgCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'firstmsg',
            aliases: ['firstmessage'],
            usage: 'firstmsg',
            description: 'shows firstmessage ever sent in the channel',
            subcommands: ['firstmsg'],
            type: client.types.INFO,
        });
    }
    async run(message) {
        const messages = await message.channel.messages.fetch({
            after: 1,
            limit: 1
        });
        const fMessage = messages.first();
        return this.send_info(message, `**${fMessage.content}** · [jump](${fMessage.url})`)
    };

}