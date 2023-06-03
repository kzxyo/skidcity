const Discord = require('discord.js')
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: "unlock",
  aliases: ["unlockdown"],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`ban_members\`` } });
    if (!message.guild.me.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`ban_members\`` } });

    const channel = message.mentions.channels.first() || message.channel;

    const lockEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: unlock')
      .setDescription('Unlock a channel')
      .addField('**Aliases**', 'unlockdown', true)
      .addField('**Parameters**', 'channel, reason', true)
      .addField('**Information**', `${warn} Ban Members`, true)
      .addField('**Usage**', '\`\`\`Syntax: unlock <channel>\nExample: unlock #general\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(lockEmbed)

    if (channel.permissionsFor(message.guild.id).has('SEND_MESSAGES') === true) {
      const unlockchannelError2 = new Discord.MessageEmbed()
        .setDescription(`${warn} ${message.author}: ${channel} is not locked!`)
        .setColor('#efa23a');

      return message.channel.send(unlockchannelError2);
    }

    channel.updateOverwrite(message.guild.id, { SEND_MESSAGES: true });

    const embed = new Discord.MessageEmbed()
      .setDescription(`:unlock: ${message.author}: ${channel} unlocked - check permissions if previously hidden`)
      .setColor('#efa23a');

    message.channel.send(embed);
  }

};