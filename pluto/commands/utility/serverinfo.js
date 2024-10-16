const { MessageEmbed } = require('discord.js')
const { embedcolor } = require('./../../config.json')
const moment = require('moment')

module.exports = {
  name: "serverinfo",
  aliases: ['guildinfo', 'ginfo', 'sinfo', 'si'],
  description: "gets details about a guild",
  usage: '{guildprefix}serverinfo',
  run: async(client, message, args) => {

    const owner = await message.guild.fetchOwner()

    const membercount = message.guild.memberCount

    const botcount = message.guild.members.cache.filter(m => m.user.bot).size

    const channelscount = message.guild.channels.cache

    function checkDays(date) {
      let now = new Date();
      let diff = now.getTime() - date.getTime();
      let days = Math.floor(diff / 86400000);
      return days + (days == 1 ? " day" : " days") + " ago";
    };

    const verificationlevels = {
      NONE: 'NONE',
      LOW: 'LOW',
      MEDIUM: 'MEDIUM',
      HIGH: 'HIGH',
      VERY_HIGH: 'HIGHEST'
    };

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setTitle(message.guild.name)
    .setDescription(`id: \`${message.guild.id}\`\nserver age: \`${checkDays(message.channel.guild.createdAt)}\``)
    .addFields( 
    { name: 'owner', value: `${owner}`, inline: true },
    { name: 'boost', value: `level ${message.guild.premiumTier >= 1 ? `${message.guild.premiumTier}` : `0`}\n${message.guild.premiumSubscriptionCount >= 1 ? `${message.guild.premiumSubscriptionCount}` : `0`} boosts`, inline: true },
    { name: 'members', value: `${membercount} members total\n${membercount - botcount} humans & ${botcount} bots`, inline: true },
    { name: 'channels', value: `${channelscount.filter(channel => channel.type === 'GUILD_TEXT').size} text channels\n${channelscount.filter(channel => channel.type === 'GUILD_VOICE').size} voice channels`, inline: true },
    { name: 'other', value: `${message.guild.roles.cache.size} roles\n${message.guild.emojis.cache.size} emojis`, inline: true },
    { name: 'information', value: `region: \`deprecated\`\nverification level: \`${verificationlevels[message.guild.verificationLevel]}\``, inline: true },
    )
    .setThumbnail(message.guild.iconURL({ dynamic: true }))
    .setFooter({ text: `server created • ${moment(message.guild.createdAt).format("MM/DD/YYYY")}` })
  
    message.channel.send({ embeds: [embed] })
  }
}