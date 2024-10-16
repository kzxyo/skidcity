const { MessageEmbed } = require('discord.js')
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "version",
  description: 'gets bot version',
  usage: '{guildprefix}version',
  run: async(client, message, args) => {
  
    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setDescription('pluto — **v13.8.0**')

    message.channel.send({ embeds: [embed] })
  }
}