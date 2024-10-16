const { MessageEmbed } = require('discord.js')
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "uptime",
  description: 'gets how long pluto has been running',
  usage: '{guildprefix}uptime',
  run: async(client, message, args) => {

    let totalseconds = (client.uptime / 1000);
    let days = Math.floor(totalseconds / 86400);
    totalseconds %= 86400;
    let hours = Math.floor(totalseconds / 3600);
    totalseconds %= 3600;
    let minutes = Math.floor(totalseconds / 60);
    let seconds = Math.floor(totalseconds % 60);

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setDescription(`pluto has been running for **${days}d ${hours}h ${minutes}m ${seconds}s**`)

    message.channel.send({ embeds: [embed] })
  }
}