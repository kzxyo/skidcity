const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "guildicon",
  aliases: ['servericon', 'gicon', 'sicon', 'gico', 'sico'],
  description: "get the current guild's icon",
  usage: '{guildprefix}guildicon',
  run: async(client, message, args) => {

    let icon = message.guild.iconURL({ size: 2048, dynamic: true })

    if (icon) {
      icon = message.guild.iconURL({ size: 2048, dynamic: true })

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setAuthor({ name: `${message.guild.name}`, iconURL: `${message.guild.iconURL({ dynamic: true })}` })
      .setImage(icon)

      return message.channel.send({ embeds: [embed] }) 
    } else {
      return message.channel.send(`this server doesn't have a icon`)
    }
  }
}