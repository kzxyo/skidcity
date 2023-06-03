const { Message } = require('discord.js')
const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: 'unmute',

  /**
   * @param {Message} message
   */

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\``}});
    if (!message.guild.me.hasPermission("MANAGE_ROLES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_roles\``}});

    const unmuteEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: unmute')
      .setDescription('Unmutes the mentioned member in all channels')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'member', true)
      .addField('**Information**', `${warn} Manage Messages`, true)
      .addField('**Usage**', '\`\`\`Syntax: unmute <member>\nExample: unmute four#0001\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(unmuteEmbed)

    let user = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.member;

    const Member = message.mentions.members.first() || message.guild.members.cache.get(args[0])

    if (!Member) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: I was unable to find a member with that name` } })

    const role = message.guild.roles.cache.find(r => r.name.toLowerCase() === 'muted');

    await Member.roles.remove(role)

    message.channel.send({ embed: { color: "RED", description: `${message.author}: **${user.user.tag}** is now unmuted` } })
  }
}