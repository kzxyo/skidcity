const Discord = require('discord.js');
const db = require('quick.db')
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: "lockdown",
  aliases: ["lock"],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`ban_members\`` } });
    if (!message.guild.me.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`ban_members\`` } });

    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };

    const lockEmbed = new Discord.MessageEmbed()
    .setAuthor(message.author.username, message.author.avatarURL({
      dynamic: true
    }))
    .setTitle('Command: lockdown')
    .setDescription('Lockdown a channel')
    .addField('**Aliases**', 'lock', true)
    .addField('**Parameters**', 'channel, reason', true)
    .addField('**Information**', `${warn} Ban Members`, true)
    .addField('**Usage**', '\`\`\`Syntax: lockdown <channel>\nExample: lockdown #general\`\`\`')
    .setFooter(`Module: moderation`)
    .setTimestamp()
    .setColor(color)
      if (!args[0]) return message.channel.send(lockEmbed)

    let channel = message.mentions.channels.first();

    if (channel) {
      reason = args.join(' ').slice(22) || 'Not Specified';
    } else {
      channel = message.channel;
    }

    if (channel.permissionsFor(message.guild.id).has('SEND_MESSAGES') === false) {
      const lockchannelError2 = new Discord.MessageEmbed()
        .setDescription(`${warn} ${message.author}: ${channel} is already locked!`)
        .setColor('#efa23a');

      return message.channel.send(lockchannelError2);
    }

    channel.updateOverwrite(message.guild.id, { SEND_MESSAGES: false });

    const embed = new Discord.MessageEmbed()
      .setDescription(`:lock: ${message.author}: ${channel} locked. Use \`${prefix}unlock\` to remove this lockdown`)
      .setColor('#efa23a');

    message.channel.send(embed);
  }

};