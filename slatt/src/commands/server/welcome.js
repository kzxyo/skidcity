const Command = require('../Command.js');

module.exports = class SetWelcomeMessageCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'welcome',
      aliases: ['welc', 'wlc'],
      description: `Welcome messages, use the 'variables' command for a list of keywords`,
      usage: 'welcome [subcommand] [args]',
      type: client.types.SERVER,
      userPermissions: ['MANAGE_GUILD', 'MANAGE_MESSAGES'],
    });
  }
  async run(message, args) {
    if (!args.length) return this.help(message)
  }
}