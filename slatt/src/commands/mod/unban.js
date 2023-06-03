const Command = require('../Command.js');
const {
  MessageEmbed
} = require('discord.js');

module.exports = class UnbanCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'unban',
      usage: 'unban [user] [reason]',
      description: 'Unbans a member from your server',
      type: client.types.MOD,
      clientPermissions: ['SEND_MESSAGES', 'EMBED_LINKS', 'BAN_MEMBERS'],
      userPermissions: ['BAN_MEMBERS'],
      subcommands: ['unban']
    });
  }
  async run(message, args) {
    if (!args.length) {
      return this.help(message)
    }
    const banned = await message.guild.bans.fetch()
    const user = banned.find(u => u.user.username.toLowerCase().includes(args.join(' ').toLowerCase()) || u.user.username + '#' + u.user.discriminator === args.join(' ') || u.user.id === args[0])
    if (!user) {
      return this.invalidArgs(message, `There was no match for **${args.join(' ')}** on the ban list`)
    }
    await message.guild.members.unban(user.user.id)
    let invite = message.guild.channels.cache.find(ch => ch.type == "GUILD_TEXT" && ch.permissionsFor(ch.guild.me).has("CREATE_INSTANT_INVITE"));
    if (!invite) invite = 'cannot create invite'
    else invite = await invite.createInvite({
      temporary: false,
      maxAge: 0
    })
    if (message.client.users.cache.get(user.user.id)) {
      const member = message.client.users.cache.get(user.user.id)
      message.client.utils.send_punishment({
        message: message,
        action: 'unbanned',
        reason: 'no reason provided',
        member: member,
        info: `${invite.url}`
      })
      const amount = (await message.client.db.history.findAll({ where: { guildID: message.guild.id, userID: member.id } })).length + 1
      await message.client.db.history.create({
        guildID: message.guild.id,
        userID: member.id,
        action: 'unbanned',
        reason:  'no reason provided',
        author: message.author.id,
        date: `${Date.now()}`,
        num: amount,
      })
    }
    message.client.utils.send_log_message(message, user, this.name, `**{user.tag}** has been unbanned`)
    this.send_success(message, `**${user.user.tag}** was successfully unbanned `)
  }
};