const Command = require('../Command.js');

module.exports = class UnmuteCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'unmute',
      type: client.types.MOD,
      usage: `unmute [member]`,
      description: 'unmute a member in your server',
      clientPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'MANAGE_ROLES'],
      userPermissions: ['MANAGE_ROLES'],
      subcommands: ['unmute']
    });
  }
  async run(message, args) {
    const muteRoleId = await message.client.db.mute_role.findOne({ where: { guildID: message.guild.id } })
    let muteRole;
    if (muteRoleId) muteRole = message.guild.roles.cache.get(muteRoleId.role);
    else return this.send_error(message, 1, 'There is currently no mute role set on this server');
    if (!args.length) {
      return this.help(message)
    }
    const member = this.functions.get_member(message, args[0])
    if (!member) {
      return this.invalidUser(message)
    }
    if (member.roles.highest.position >= message.member.roles.highest.position)
      return this.send_error(message, 0, 'You cannot unmute someone with an equal or higher role');

    let reason = args.slice(2).join(' ');
    if (!reason) reason = 'no reason provided';
    if (reason.length > 1024) reason = reason.slice(0, 1021) + '...';

    if (!member.roles.cache.has(muteRole.id))
      return this.send_error(message, 0, 'Provided member is not muted');
    clearTimeout(member.timeout);
    try {
      member.roles.remove(muteRole)
      await message.client.db.muted.destroy({
        where: {
          userID: member.id
        }
      })
      message.client.utils.send_punishment({
        message: message,
        action: 'unmuted',
        reason: reason,
        member: member,
      })
      const amount = (await message.client.db.history.findAll({ where: { guildID: message.guild.id, userID: member.id } })).length + 1
      await message.client.db.history.create({
        guildID: message.guild.id,
        userID: member.id,
        action: 'unmuted',
        reason: reason,
        author: message.author.id,
        date: `${Date.now()}`,
        num: amount,
      })
      message.client.utils.send_log_message(message, member, this.name, `**{user.tag}** was unmuted`)
      return this.send_success(message, `${member} has been unmuted`)
    } catch (err) {
      message.client.logger.error(err.stack);
      return this.send_error(message, 1, 'Please check the role hierarchy', err.message);
    }
  }
}