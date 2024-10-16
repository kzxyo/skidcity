const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "membercount",
  aliases: ['mc', 'mcount', 'mbrcnt', 'mbrcount'],
  description: "get the server total/human/bot member count",
  usage: '{guildprefix}membercount',
  run: async(client, message, args) => {

    const usercount = message.guild.memberCount

    const botcount = message.guild.members.cache.filter(m => m.user.bot).size

    const humans = usercount - botcount

    if (message.guild.iconURL({ dynamic: true })) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setAuthor({ name: `${message.guild.name}`, iconURL: `${message.guild.iconURL({ dynamic: true })}` })
      .setDescription(`**${usercount}** (**${humans}** humans & **${botcount}** bots)`)

      return message.channel.send({ embeds: [embed] })

    } else {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setAuthor({ name: `${message.guild.name}` })
      .setDescription(`**${usercount}** (**${humans}** humans & **${botcount}** bots)`)

      return message.channel.send({ embeds: [embed] })      
    }
  }
}