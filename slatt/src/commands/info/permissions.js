const Command = require('../Command.js');
const {
  MessageEmbed
} = require('discord.js');
const permissions = require('../../utils/json/permissions.json');
const ReactionMenu = require('../ReactionMenu.js');

module.exports = class PermissionsCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'permissions',
      aliases: ['perms'],
      usage: 'permissions [user mention/ID]',
      description: `Display a members guild permissions`,
      type: client.types.INFO,
      subcommands: ['permissions @conspiracy']
    });
  }
  async run(message, args) {
    const member = this.functions.get_member_or_self(message, args.join(' '))
    if (!member) return this.invalidUser(message)
    const memberPermissions = member.permissions.toArray();
    const finalPermissions = [];
    for (const permission in permissions) {
      if (memberPermissions.includes(permission)) finalPermissions.push(`${permissions[permission]}`);
    }
    let num = 1
    const list = finalPermissions.map(x => `\`${num++}\` : **${x}**`)
    const embed = new MessageEmbed()
      .setAuthor(message.author.tag, message.author.avatarURL({
        dynamic: true
      }))
      .setColor(this.hex)
      .setTitle(`${member.displayName}'s permissions`)
      .setFooter(`${list.length} permissions`)
      .setDescription(list.join('\n'))
    if (list.length <= 10) {
      message.channel.send({ embeds: [embed] })
    } else {
      new ReactionMenu(message.client, message.channel, message.member, embed, list);
    }
  }
}