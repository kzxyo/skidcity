const { MessageEmbed } = require('discord.js')
const { embedcolor } = require('./../../config.json')
const moment = require('moment')

module.exports = {
  name: "joined",
  description: "get time that a user joined",
  usage: '{guildprefix}joined\n{guildprefix}joined [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.member;

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setAuthor({ name: `${user.user.tag}`, iconURL: `${user.user.displayAvatarURL({ size: 512, dynamic: true })}` })
    .setDescription(`join date: ${moment(user.joinedAt).format("MM/DD/YYYY, h:mm A")}`)

    message.channel.send({ embeds: [embed] })
  }
}