const Command = require('../Command.js');

module.exports = class MembersCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'membercount',
      aliases: ['memberstatus', 'memberc', 'mc'],
      usage: 'membercount',
      subcommands: ['members'],
      description: 'Displays how many server members are online, busy, AFK, and offline.',
      type: client.types.INFO
    });
  }
  async run(message) {
    const members = message.guild.members.cache.filter(x => (Date.now() - x.joinedTimestamp) < 86400000).sort((a, b) => parseInt(b.joinedTimestamp) - parseInt(a.joinedTimestamp))
    return this.send_info(message, `There are currently **${message.guild.memberCount}** members, and **+${members.size}** new members today`)
  }
};