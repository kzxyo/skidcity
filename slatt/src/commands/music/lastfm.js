const Command = require('../Command.js');
module.exports = class LastfmCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'lastfm',
            aliases: ['lf', 'lfm'],
            description: `Last.fm commands to provide info directly from the site, to discord through slatt`,
            usage: `lastfm [subcommand] [args]`,
            type: client.types.LASTFM,
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const is_subcommand = message.client.subcommands.get(`lastfm ${args[0]}`) || message.client.subcommand_aliases.get(`lastfm ${args[0]}`)
        if (!is_subcommand) {
        return this.send_info(message, `Invalid Last.fm command usage. Use \`${message.prefix}help lastfm\``)
        }
    }
}