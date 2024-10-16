const { MessageEmbed } = require('discord.js')
const { embedcolor, token } = require('./../../config.json')
const axios = require("axios")

module.exports = {
  name: "userbanner",
  aliases: ['ubanner', 'banner'],
  description: "get any discord user profile banner",
  usage: '{guildprefix}userbanner\{guildprefix}nuserbanner [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0])

    const author = message.member

    if (user) {

      axios.get(`https://discord.com/api/users/${user.id}`, {
        headers: {
          Authorization: `Bot ${token}`
        },
      })
      .then((res) => {
      
        const { banner } = res.data;

        if (banner) {
          
          const extension = banner.startsWith("a_") ? ".gif" : ".png";
          const url = `https://cdn.discordapp.com/banners/${user.id}/${banner}${extension}?size=2048`;

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setAuthor(`${user.user.tag}`, user.displayAvatarURL({ dynamic: true }))
          .setImage(url)

          return message.channel.send({ embeds: [embed] })
      
        } else {
      
          return message.channel.send(`this user doesn't have a banner`)
        }
      })

    } else {

      axios.get(`https://discord.com/api/users/${author.id}`, {
        headers: {
          Authorization: `Bot ${token}`
        },
      })
      .then((res) => {
        
        const { banner } = res.data;

        if (banner) {
          
          const extension = banner.startsWith("a_") ? ".gif" : ".png";
          const url = `https://cdn.discordapp.com/banners/${author.id}/${banner}${extension}?size=2048`;

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setAuthor({ name: `${message.author.tag}`, iconURL: `${message.author.displayAvatarURL({ dynamic: true })}` })
          .setImage(url)

          return message.channel.send({ embeds: [embed] })
        } else {
          return message.channel.send(`you don't have a banner`)
        }
      })
    }
  }
}