const Command = require('../Command.js');

module.exports = class KickCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'kick',
      type: client.types.MOD,
      usage: `kick <member>`,
      description: `kicks a naughty user from your server`,
      clientPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'KICK_MEMBERS'],
      userPermissions: ['KICK_MEMBERS'],
      subcommands: ['kick @conspiracy']
    });
  }
  async run(message, args) {
    if (!args.length) {
      return this.help(message)
    }
    const member = this.functions.get_member(message, args[0])
    if (!member) {
      return this.invalidUser(message)
    }
    if (member === message.member)
      return message.channel.send(`FFUJCK YOU`)
    if (member.roles.highest.position >= message.member.roles.highest.position)
      return this.send_error(message, 0, 'You cant kick someone with a role higher or equal to yours');
    if (!member.kickable)
      return this.send_error(message, 0, `**${member.user.tag}** is not kickable`);

    let reason = args.slice(1).join(' ');
    if (!reason) reason = 'no reason provided';
    if (reason.length > 1024) reason = reason.slice(0, 1021) + '...';
    member.kick(reason);
    this.send_success(message, `${member} was successfully kicked ${reason !== 'no reason provided' ? `with reason: **${reason}**` : ''}`)
    message.client.utils.send_log_message(message, member, this.name, `**{user.tag}** has been kicked`)
    message.client.utils.send_punishment({
      message: message,
      action: 'kick',
      reason: reason,
      member: member
    })
    const amount = (await message.client.db.history.findAll({ where: { guildID: message.guild.id, userID: member.id } })).length + 1
    await message.client.db.history.create({
      guildID: message.guild.id,
      userID: member.id,
      action: 'kicked',
      reason: reason,
      author: message.author.id,
      date: `${Date.now()}`,
      num: amount,
    })
  }
}