const Command = require('../Command.js');
const rgx = /^(?:<@!?)?(\d+)>?$/;

module.exports = class LeaveGuildCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'leaveguild',
      usage: 'leaveguild <server ID>',
      description: 'Forces Kami to leave the specified server.',
      type: client.types.OWNER,
      ownerOnly: true,
      subcommands: ['leaveguild 709992782252474429']
    });
  }
  async run(message, args) {
    const guildId = args[0];
    if (!rgx.test(guildId))
      return this.send_error(message, 0, 'Please provide a valid server ID');
    const guild = message.client.guilds.cache.get(guildId);
    if (!guild) return this.send_error(message, 0, 'Unable to find server, please check the provided ID');
    await guild.leave();
    return this.send_success(message, `I have left **${guild.name}**`)
  } 
};
