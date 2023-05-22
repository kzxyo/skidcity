const Command = require('../Command.js');

module.exports = class SupportServerCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'supportserver',
      aliases: ['support', 'ss'],
      subcommands: ['supportserver'],
      usage: 'supportserver',
      description: 'IT DOESNT EXIST ANYHMORE',
      type: client.types.INFO
    });
  }
  async run(message) {
      return message.channel.send('Doesnt. Exist')
  }
};
