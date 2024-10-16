const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "avatar",
  aliases: ['av', 'ab', 'ac', 'ah', 'pfp', 'avi', 'ico', 'icon'],
  description: 'get any discord user profile picture',
  usage: '{guildprefix}avatar\n{guildprefix}avatar [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0])

    const author = message.member

    if (user) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setAuthor({ name: `${user.user.tag}`, iconURL: `${user.user.displayAvatarURL({ dynamic: true })} `})
      .setImage(user.user.displayAvatarURL({size: 1024, dynamic: true}))

      return message.channel.send({ embeds: [embed] })
      
    } else {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setAuthor({ name: `${author.user.tag}`, iconURL: `${author.displayAvatarURL({ dynamic: true })} `})
      .setImage(author.displayAvatarURL({size: 1024, dynamic: true}))

      return message.channel.send({ embeds: [embed] })  
    }
  }
}