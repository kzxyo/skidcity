const Command = require('../Command.js');

module.exports = class YesNoCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'yesno',
      aliases: ['yn'],
      usage: 'yesno [message]',
      description: 'reacts with thumbs up or thumbs down',
      type: client.types.FUN,
      subcommands: ['yesno']
    });
  }
  async run(message, args) {
    if (!args.length) {
      return this.help(message);
    }
    message.react("👍").then(message.react("👎"))
  }
};