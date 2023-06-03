const Discord = require('discord.js');
const { color } = require("../../config.json");

module.exports = {
  name: "about",
  aliases: ["bleed", "botinfo"],

  run: async (client, message, args) => {

    let days = Math.floor(client.uptime / 86400000);
    let hours = Math.floor(client.uptime / 3600000) % 24;
    let minutes = Math.floor(client.uptime / 60000) % 60;
    let seconds = Math.floor(client.uptime / 1000) % 60;

    let UptimeDays = days
    if (UptimeDays) {
      UptimeDays = `${days} days, `;
    } else {
      UptimeDays = ''
    }

    let UptimeHours = hours
    if (UptimeHours) {
      UptimeHours = `${hours} hours, `;
    } else {
      UptimeHours = ''
    }

    let UptimeMinutes = minutes
    if (UptimeMinutes) {
      UptimeMinutes = `${minutes} minutes, `;
    } else {
      UptimeMinutes = ''
    }

    let UptimeSeconds = seconds
    if (UptimeSeconds) {
      UptimeSeconds = `${seconds} seconds`;
    } else {
      UptimeSeconds = ''
    }

    const uniqueIDs = new Set();
    for (const guild of client.guilds.cache.values()) {
      for (const member of guild.members.cache.values()) {
        uniqueIDs.add(member.id);
      }
    }

    uniqueIDs.size

    const uniqueOnlineIDs = new Set();
    for (const guild of client.guilds.cache.values()) {
      for (const member of guild.members.cache.values()) {
        if (member.presence.status !== "offline") uniqueOnlineIDs.add(member.id);
      }
    }

    uniqueOnlineIDs.size

    const embed = new Discord.MessageEmbed()
      .setColor(color)
      .setAuthor(`${client.user.username}`, client.user.displayAvatarURL())
      .setDescription(`Bot statistics, developed by four#0001\n**Memory:** ${(process.memoryUsage().rss / 1024 / 1024).toFixed(2)}MB, **Commands:** ${client.commands.size}`)
      .addField('**Members**', `${client.guilds.cache.reduce((current, guild) => current + guild.memberCount, 0).toLocaleString()} total\n${uniqueIDs.size.toLocaleString()} unique\n${uniqueOnlineIDs.size.toLocaleString()} unique online`, true)
      .addField('**Channels**', `${client.channels.cache.size.toLocaleString()} total\n${client.channels.cache.filter(channel => channel.type == 'text').size.toLocaleString()} text\n${client.channels.cache.filter(channel => channel.type == 'voice').size.toLocaleString()} voice`, true)
      .addField('**Guilds**', `${client.guilds.cache.size.toLocaleString()} (public)`, true)
      .setFooter(`Uptime: ${UptimeDays}${UptimeHours}${UptimeMinutes}${UptimeSeconds}`)
      .setTimestamp()
    message.channel.send(embed)
  }
}