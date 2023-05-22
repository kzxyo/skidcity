const Command = require('../Command.js');

module.exports = class PingCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'ping',
      usage: 'ping',
      subcommands: ['ping'],
      description: 'provides my current latency',
      type: client.types.INFO
    });
  }
  async run(message) {
    return this.send_info(message, `Websocket ping: **${message.client.ws.ping}ms**`)
  }
};