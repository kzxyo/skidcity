const Command = require('../Command.js');


module.exports = class SetPrefixCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'setprefix',
      aliases: ['prefix'],
      description: 'Set a new server prefix',
      type: client.types.SERVER,
      userPermissions: ['MANAGE_GUILD'],
      subcommands: ['setprefix']
    });
  }
  async run(message, args) {
    const oldPrefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
    const prefix = args[0];
    if (!prefix) {
      return this.help(message);
    } else if (prefix.length > 10)
      return this.send_error(message, 0, 'prefix too long, make sure its under 10 characters');
    await message.client.db.prefix.update({ prefix: prefix }, { where: { guildID: message.guild.id } })
    this.send_success(message, `prefix updated from \`${oldPrefix.prefix}\` to \`${prefix}\``)
    message.client.utils.send_log_message(message, message.member, this.name, `**{user.tag}** Updated prefix from \`${oldPrefix.prefix}\` to \`${prefix}\``)

  }
};