const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: `hackban`,
  aliases: ['hban'],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`ban_members\`` } });
    if (!message.guild.me.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`ban_members\`` } });

    const hackbanEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: hackban')
      .setDescription('Ban user from guild even if they arent in the server')
      .addField('**Aliases**', 'hban', true)
      .addField('**Parameters**', 'member, reason', true)
      .addField('**Information**', `${warn} Ban Members\n:notepad_spiral: Make sure to use a User ID (not name#tag...etc)`, true)
      .addField('**Usage**', '\`\`\`Syntax: hackban (user id) <reason>\nExample: hackban 262429076763967488 Raider\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(hackbanEmbed)

    const target = args[0];
    if (target.id == message.author.id) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot ban **yourself**` } })
    if (message.member.roles.highest.comparePositionTo(target.roles.highest) >= 0) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot ban someone that is **higher** than **yours**` } })
    if (isNaN(target)) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: You must to **specify** a valid user ID` } });

    const reason = args.splice(1, args.length).join(' ');

    message.guild.members.ban(target, { reason: reason.length < 1 ? 'No Reason Supplied' : reason });

    return message.channel.send('👍');
  }
}