const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')
const axios = require('axios');

module.exports = {
  name: "randomdog",
  aliases: ['dog', 'doggo'],
  description: `sends a random dog picture`,
  usage: '{guildprefix}randomdog',
  run: async(client, message, args) => {

    const url = "https://some-random-api.ml/img/dog";

    let image, response;

    response = await axios.get(url);
    image = response.data;

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setImage(image.link)

    return message.channel.send({ embeds: [embed] })
  }
}