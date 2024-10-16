const { MessageEmbed } = require('discord.js')
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "presence",
  description: "gets user presence",
  usage: '{guildprefix}presence\n{guildprefix}presence [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.member;

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setTitle(`${user.user.username}'s presence`)
    .setDescription(`${user.presence.activities[0] ? user.presence.activities[0].state : `this user is currently offline..`}`)

    message.channel.send({ embeds: [embed] })
  }
}