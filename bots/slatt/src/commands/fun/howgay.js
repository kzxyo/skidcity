const Command = require('../Command.js')

module.exports = class HowGayCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'howgay',
            aliases: ['gay', 'sus'],
            usage: 'howgay [user]',
            subcommands: ['howgay'],
            description: 'how gay are you?',
            type: client.types.FUN
        });
    }
    async run(message, args) {
        let howgay = ['99%', '100%', '80%', '88%', '94%', '95%']
        const member = this.functions.get_member_or_self(message, args.join(' '))
        if (!member) {
            return this.invalidUser(message)
        }
        if (!args.length) {
            return this.send_info(message, `You are **${howgay[Math.round(Math.random() * (howgay.length - 1))]}** gay`)
        }
        return this.send_info(message, `The user ${member} is **${howgay[Math.round(Math.random() * (howgay.length - 1))]}** gay`)
    }
};