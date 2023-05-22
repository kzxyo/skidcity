const Command = require('../Command.js');

module.exports = class SetStarboardChannelCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'starboard',
      aliases: ['star'],
      usage: 'starboard [subcommand] [args]',
      description: `Update starboard settings for your server`,
      type: client.types.SERVER,
      userPermissions: ['MANAGE_GUILD', "MANAGE_EMOJIS"],
    });
  }
  async run(message, args) {
    if (!args.length) return this.help(message)
  }
};