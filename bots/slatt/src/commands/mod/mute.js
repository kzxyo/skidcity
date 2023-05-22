const Command = require('../Command.js');
const ms = require('ms');
const db = require("quick.db")

module.exports = class MuteCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'mute',
      type: client.types.MOD,
      usage: `mute <member> <time>`,
      description: 'silence an annoying member',
      clientPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'MANAGE_ROLES'],
      userPermissions: ['MANAGE_ROLES'],
    });
  }
  async run(message, args) {
    if (!args.length) {
      return this.help(message)
    }
    const muteRoleId = await message.client.db.mute_role.findOne({ where: { guildID: message.guild.id } })
    let muteRole;
    if (muteRoleId !== null) muteRole = message.guild.roles.cache.get(muteRoleId.role);
    else return this.send_error(message, 1, `No mute role setup for this server, create it by using \`${message.prefix}muterole\``);
    const member = this.functions.get_member(message, args[0])
    if (!member) {
      return this.invalidUser(message)
    }
    if (member === message.member)
      return this.send_error(message, 0, 'You cannot mute yourself');
    if (member === message.guild.me) return this.send_error(message, 0, 'You cannot mute me');
    if (member.roles.highest.position >= message.member.roles.highest.position)
      return this.send_error(message, 0, 'You cannot mute someone with an equal or higher role');
    let ms_time
    if (args[1]) ms_time = args[1]
    if (!args[1]) ms_time = '1h'
    let time = ms(ms_time)
    if (!time || time > 1209600000)
      return this.send_error(message, 0, 'Please enter a length of time of 14 days or less (1s/m/h/d)');

    let reason = args.slice(2).join(' ');
    if (!reason) reason = 'no reason provided';
    if (reason.length > 1024) reason = reason.slice(0, 1021) + '...';

    if (member.roles.cache.has(muteRoleId))
      return this.send_error(message, 0, 'Provided member is already muted');
    try {
      await member.roles.add(muteRole)
      await message.client.db.muted.create({
        userID: member.id
      })
      if (!message.author.bot) {
        message.client.utils.send_punishment({
          message: message,
          action: 'muted',
          reason: reason,
          member: member,
          info: `muted for **${ms(time, { long: true })}**`
        })
        const amount = (await message.client.db.history.findAll({where: {guildID: message.guild.id, userID: member.id}})).length+1
        await message.client.db.history.create({
          guildID: message.guild.id,
          userID: member.id,
          action: 'muted',
          reason: reason,
          author: message.author.id,
          date: `${Date.now()}`,
          num: amount,
        })
        message.client.utils.send_log_message(message, member, this.name, `**{user.tag}** muted for **${ms(time, { long: true })}**`)
        this.send_success(message, `**${member.user.tag}** has now been muted for **${ms(time, { long: true })}**`)
      }
    } catch (err) {
      message.client.logger.error(err.stack);
      return this.send_error(message, 1, 'Please check the role hierarchy', err.message);
    }
    member.timeout = setTimeout(async () => {
      try {
        await member.roles.remove(muteRole);
        await message.client.db.muted.destroy({ where: { userID: member.id } })
        message.client.utils.send_punishment({
          message: message,
          action: 'unmuted (manually)',
          reason: reason,
          member: member,
          info: `unmuted after being muted for **${ms(time, { long: true })}**`
        })
        message.client.utils.send_log_message(message, member, this.name, `**{user.tag}** Manually unmuted after **${ms(time, { long: true })}**`)
        return this.send_success(message, `**${member.user.tag}** has been unmuted manually, they were muted for **${ms(time, { long: true })}**`)
      } catch (err) {
        message.client.logger.error(err.stack);
        return this.send_error(message, 1, 'Please check the role hierarchy', err.message);
      }
    }, time);
  }
}