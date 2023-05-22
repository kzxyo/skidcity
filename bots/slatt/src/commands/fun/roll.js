const Command = require('../Command.js');

module.exports = class RollCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'roll',
      aliases: ['dice', 'r'],
      usage: 'roll <dice sides>',
      description: 'Rolls a dice with the specified number of sides. Will default to 6 sides if no number is given.',
      type: client.types.FUN,
      subcommands: ['roll 20']
    });
  }
  async run(message, args) {
    let limit = args[0];
    if (!limit) limit = 6;
    if(limit > 6) return this.send_info(message, `Provide a number 1-6`)
    const n = Math.floor(Math.random() * limit + 1);
    if (!n || limit <= 0) return this.invalidArgs(message, 'Please provide a valid number of dice sides');
    return this.send_info(message, `You rolled a **${n}**!`)
  }
};
