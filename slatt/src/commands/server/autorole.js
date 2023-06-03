const Command = require('../Command.js');

module.exports = class SetAutoRoleCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'autorole',
      usage: `autorole [role] or "none"`,
      description: `set a role to be added to new members`,
      type: client.types.SERVER,
      userPermissions: ['MANAGE_GUILD'],
      subcommands: ['autorole']
    });
  }
  async run(message, args) {
    const check = await message.client.db.autorole.findOne({ where: { guildID: message.guild.id } })
    if (!args.length) return this.help(message)
    if (args[0].toLowerCase() === 'none' && check !== null) {
      await message.client.db.autorole.destroy({ where: { guildID: message.guild.id } })
      return this.send_success(message, `Your previous autorole was deleted`)
    } else if (args[0].toLowerCase() === 'none' && check === null) {
      return this.send_error(message, 1, `There was no **previous autorole** found to remove`)
    }
    const autoRole = this.functions.get_role(message, args.join(' '))
    if (!autoRole) return this.send_error(message, 0, 'Please provide a role or provide a valid role ID');
    if (check === null) {
      await message.client.db.autorole.create({
        guildID: message.guild.id,
        role: autoRole.id
      })
    } else {
      await message.client.db.autorole.update({ role: autoRole.id }, { where: { guildID: message.guild.id } })
    }
    message.client.utils.send_log_message(message, message.member, this.name, `**{user.tag}** Updated autorole to ${autoRole}`)
    return this.send_success(message, `Autorole for this server has been updated to ${autoRole}`)
  }
};
