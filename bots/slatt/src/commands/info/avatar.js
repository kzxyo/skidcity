const Command = require('../Command.js');
const {
  MessageEmbed,
  MessageButton
} = require('discord.js');

module.exports = class AvatarCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'avatar',
      aliases: ['pfp', 'av', 'ava'],
      usage: 'avatar [user mention/ID]',
      description: 'Display a users avatar',
      type: client.types.INFO,
      subcommands: ['avatar @conspiracy']
    });
  }
  async run(message, args) {
    const member = this.functions.get_member_or_self(message, args.join(' '))
    if (!member) {
      if (isNaN(args[0])) {
        return this.invalidUser(message)
      }
      message.client.users.fetch(args[0]).then(u => {
        const embed = new MessageEmbed()
          .setAuthor(u.username + '#' + u.discriminator, `https://cdn.discordapp.com/avatars/${u.id}/${u.avatar}.webp`)
          .setImage(`https://cdn.discordapp.com/avatars/${u.id}/${u.avatar}.${u.avatar.startsWith('a_') ? 'gif' : 'png'}?size=512`)
          .setColor(this.hex)
        return message.channel.send({ embeds: [embed] })
      })
    } else {
      const embed = new MessageEmbed()
        .setImage(member.user.displayAvatarURL({ dynamic: true, size: 512 }))
        .setAuthor(member.user.tag, member.user.displayAvatarURL({ dynamic: true }))
        .setColor(this.hex)
      message.channel.send({ embeds: [embed] })
    }
  }

}