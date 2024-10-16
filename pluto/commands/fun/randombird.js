const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')
const fetch = require('node-fetch');

module.exports = {
  name: "randombird",
  aliases: ['bird', 'birb', 'randombirb'],
  description: `displays a random bird image`,
  usage: '{guildprefix}randombird',
  run: async(client, message, args) => {

    const res = await fetch('http://shibe.online/api/birds');
    const img = (await res.json())[0];

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setImage(img)

    return message.channel.send({ embeds: [embed] })
  }
}