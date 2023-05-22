const Command = require('../Command.js');

module.exports = class BanCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'ban',
      aliases: ['hackban', 'banuser'],
      usage: 'ban [user] [reason]',
      description: 'Bans a member from your server, or a user outside of it',
      type: client.types.MOD,
      clientPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'BAN_MEMBERS'],
      userPermissions: ['BAN_MEMBERS'],
      subcommands: ['ban']
    });
  }
  async run(message, args) {
    if (!args.length) {
      return this.help(message)
    }
    const member = this.functions.get_member(message, args[0])
    if (!member) {
      if (isNaN(args[0])) {
        return this.invalidUser(message)
      }
      message.client.users.fetch(args[0]).then(async u => {
        const banned = await message.guild.bans.fetch()
        const check = banned.find(u => u.user.id === args[0])
        if (check) return this.send_error(message, 1, `**${u.username + '#' + u.discriminator}** is already banned.`)
        message.guild.members.ban(u.id)
        message.client.utils.send_log_message(message, message.member, this.name, `**${u.username + '#' + u.discriminator}** has been banned (hackban)`)
        this.send_success(message, `**${u.username + '#' + u.discriminator}** has been successfully banned`)
      })
      return
    }
    if (member === message.member)
      return this.send_error(message, 0, 'You cannot ban yourself')
    if (member.roles.highest.position >= message.member.roles.highest.position)
      return this.send_error(message, 0, 'You cannot ban someone with an equal or higher role');
    if (!member.bannable)
      return this.send_error(message, 0, `**${member.user.tag}** is not bannable`);
    let reason = args.slice(1).join(' ');
    if (!reason) reason = 'no reason provided';
    if (reason.length > 1024) reason = reason.slice(0, 1021) + '...';
    message.client.utils.send_punishment({
      message: message,
      action: 'banned',
      reason: reason,
      member: member
    })
    member.ban({ reason: reason })
    this.send_success(message, `**${member.user.tag}** has been successfully banned ${reason !== 'no reason provided' ? `with reason: **${reason}**` : ''}`)
    message.client.utils.send_log_message(message, member, this.name, `**{user.tag}** has been banned`)
    const amount = (await message.client.db.history.findAll({ where: { guildID: message.guild.id, userID: member.id } })).length + 1
    await message.client.db.history.create({
      guildID: message.guild.id,
      userID: member.id,
      action: 'banned',
      reason: reason,
      author: message.author.id,
      date: `${Date.now()}`,
      num: amount,
    })
  }
}