const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "guildbanner",
  aliases: ['serverbanner', 'gbanner', 'sbanner'],
  description: "get the current guild banner",
  usage: '{guildprefix}guildbanner',
  run: async(client, message, args) => {

    let banner = message.guild.bannerURL({ format: 'gif', size: 2048 })

    if (banner) {

      banner = message.guild.bannerURL({ format: 'gif', size: 2048 })

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setAuthor({ name: `${message.guild.name}`, iconURL: `${message.guild.iconURL({ dynamic: true })}` })
      .setImage(banner)

      return message.channel.send({ embeds: [embed] }) 
    } else {
      return message.channel.send(`this server doesn't have a banner`)
    }
  }
}