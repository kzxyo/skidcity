const Command = require('../Command.js');

module.exports = class SetMuteRoleCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'muterole',
      usage: `muterole <role>`,
      subcommands: ['muterole'],
      description: 'Set a muterole in your server',
      type: client.types.SERVER,
      userPermissions: ['MANAGE_GUILD'],
    });
  }
  async run(message, args) {
    if (!args.length) return this.help(message)
    const muteRoleId = await message.client.db.mute_role.findOne({ where: { guildID: message.guild.id } })
    const role = this.functions.get_role(message, args.join(' '))
    if (!role) return this.invalidArgs(message, `The role you provided was invalid`)
    if (muteRoleId === null) {
      await message.client.db.mute_role.create({
        guildID: message.guild.id,
        role: role.id
      })
    } else {
      await message.client.db.mute_role.update({ role: role.id }, {
        where: { guildID: message.guild.id }
      })
    }
    this.send_success(message, `The muterole has been set to ${role}`)
    message.client.utils.send_log_message(message, message.member, this.name, `**{user.tag}** Updated mute role to ${role}`)

  }
};
