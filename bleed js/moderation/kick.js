const Discord = require('discord.js');
const db = require('quick.db')
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')
const { deny } = require('../../emojis.json')

module.exports = {
  name: "kick",

  run: async (client, message, args) => {
    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };

    if (!message.member.hasPermission("KICK_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`kick_members\`` } });
    if (!message.guild.me.hasPermission("KICK_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`kick_members\`` } });
    const mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    let reason = args.slice(1).join(" ");
    if (!reason) reason = "No Reason Supplied"
    const kickEmbed = new Discord.MessageEmbed()
      .setTitle('**Kicked**')
      .addField(`**You have been kicked from**`, `${message.guild.name}`, true)
      .addField(`**Moderator**`, `${message.author.tag}`, true)
      .addField(`**Reason**`, `${reason}`, true)
      .setColor("#e74c3c")
      .setThumbnail(message.author.avatarURL({ dynamic: true, size: 2048 }))
      .setTimestamp()
      .setFooter('If you would like to dispute this punishment, contact a staff member.');

    //,kick @user [reason]
    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: kick')
      .setDescription('Kicks the mentioned user from the guild')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'member, reason', true)
      .addField('**Information**', `${warn} Kick Members`, true)
      .addField('**Usage**', '\`\`\`Syntax: kick (member) <reason>\nExample: kick four#0001 You need a break\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(embed)
    if (mentionedMember.id == message.author.id) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot kick **yourself**` } })
    if (message.member.roles.highest.comparePositionTo(mentionedMember.roles.highest) <= 0) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot kick someone that is **higher** than **yours**` } })
    if (!mentionedMember) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: **Invalid User**. Do \`${prefix}kick\` to see the variables` } });
    if (!mentionedMember.kickable) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Cannot kick due to **hierarchy**` } })
    if (message.member.roles.highest.comparePositionTo(mentionedMember.roles.highest) >= 0) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot kick someone that is **higher** than **yours**` } })
    try {
      await mentionedMember.send(kickEmbed);
    } catch (err) {
      return message.channel.send('Cannot dm that member');
    }

    try {
      await mentionedMember.kick(reason)
      return message.channel.send('👍')
    } catch (err) {
      console.log(err);
    }

  }
}