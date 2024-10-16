const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')
const fetch = require('node-fetch');

module.exports = {
  name: "randomcat",
  aliases: ['cat', 'catten', 'catto'],
  description: `displays a random cat image`,
  usage: '{guildprefix}randomcat',
  run: async(client, message, args) => {

    const res = await fetch('http://shibe.online/api/cats');
    const img = (await res.json())[0];

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setImage(img)

    return message.channel.send({ embeds: [embed] })
  }
}