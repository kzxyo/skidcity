const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')
const fetch = require("node-fetch");

module.exports = {
  name: "bitcoin",
  aliases: ['btc'],
  description: "get the current bitcoin price (usd default)",
  usage: '{guildprefix}bitcoin',
  run: async(client, message, args) => {

    const api_url = (`https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true`)
      
    const response = await fetch(api_url);
    const data = await response.json();
    const { bitcoin } = data

    const change = parseFloat(bitcoin.usd_24h_change).toFixed(2);

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setAuthor({ name: 'Bitcoin' })
    .setDescription(`**${bitcoin.usd} USD (${change}%)**`)
    .setFooter({ text: 'last updated' })
    .setTimestamp()

    return message.channel.send({ embeds: [embed] })
  }
}