const Command = require('../Command.js');

module.exports = class AfkCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'afk',
            type: client.types.FUN,
            description: `sets your AFK status with optional content`,
            subcommands: ['afk brb'],
            usage: 'afk [content]'
        });
    }
    async run(message, args) {
        let content = args.join(' ') || 'AFK'
        if (content.length >= 300) {
            return this.send_error(message, 1, `Your AFK content cannot be longer than **300** characters`)
        }
        let cont = content.replace(/\s+/g, ' ')
        await message.client.db.afk.create({guildID: message.guild.id, userID: message.author.id, content: cont,time: Date.now()})
        this.send_success(message, `You have been set to afk: **${cont}**`)
    }
}