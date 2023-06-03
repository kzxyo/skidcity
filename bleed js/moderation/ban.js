const Discord = require('discord.js');
const db = require('quick.db')
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')
const { deny } = require('../../emojis.json')

module.exports = {
  name: "ban",

  run: async (client, message, args) => {
    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };

    if (!message.member.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`ban_members\`` } });
    if (!message.guild.me.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`ban_members\`` } });

    let reason = args.slice(1).join(" ");
    const mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);

    if (!reason) reason = 'No Reason Supplied';
    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: ban')
      .setDescription('Bans the mentioned user from the guild')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'member, reason', true)
      .addField('**Information**', `${warn} Ban Members`, true)
      .addField('**Usage**', '\`\`\`Syntax: ban (member) <reason>\nExample: ban four#0001 Threatening members\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(embed)
    if (mentionedMember.id == message.author.id) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot ban **yourself**` } })
    if (message.member.roles.highest.comparePositionTo(mentionedMember.roles.highest) >= 0) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot ban someone that is **higher** than **yours**` } })
    if (!mentionedMember) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: **Invalid User**. Do \`${prefix}ban\` to see the variables` } })
    if (!mentionedMember.bannable) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Cannot ban due to **hierarchy**` } })
    if (message.member.roles.highest.comparePositionTo(mentionedMember.roles.highest) >= 0) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot ban someone that is **higher** than **yours**` } })


    const banEmbed = new Discord.MessageEmbed()
      .setTitle('**Banned**')
      .addField(`**You have been banned in**`, `${message.guild.name}`, true)
      .addField(`**Moderator**`, `${message.author.tag}`, true)
      .addField(`**Reason**`, `${reason}`, true)
      .setColor("#e74c3c")
      .setThumbnail(message.author.avatarURL({ dynamic: true, size: 2048 }))
      .setTimestamp()
      .setFooter('If you would like to dispute this punishment, contact a staff member.');

    await mentionedMember.send(banEmbed).catch(err => console.log(err));
    await mentionedMember.ban({
      days: 7,
      reason: reason
    }).catch(err => console.log(err)).then(() => message.channel.send('👍'))
  }
}