const Command = require('../Command.js');

module.exports = class EvalCommand extends Command {
  constructor(client) {
      super(client, {
          name: "try",
      });

  }
  async run(message, args) {
   message.channel.send(obh)
  }
}