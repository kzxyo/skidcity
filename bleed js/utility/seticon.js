const Discord = require('discord.js')
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')
const { color } = require('../../config.json')

module.exports = {
  name: "seticon",

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
    if (!message.guild.me.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_guild\`` } });
    let icon = args[0]
    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: seticon')
      .setDescription('Set a new guild icon')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'url', true)
      .addField('**Information**', `${warn} Manage Guild`, true)
      .addField('**Usage**', '\`\`\`Syntax: seticon (url)\nExample: seticon media.discordapp.com/attachments/871...png\`\`\`')
      .setFooter(`Module: servers`)
      .setTimestamp()
      .setColor(color)
    if (!icon) return message.channel.send(embed)

    if (message.attachments.first()) {
      icon = message.attachments.first().url
      message.guild.setIcon(icon).then(() => {
        message.channel.send({ embed: { color: "a3eb7b", description: `${approve} ${message.author}: Successfully set the guild icon to [**this image**](${icon})` } })
      })
    } else {
      if (!icon) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You must provide a **url or attachment** to set as the guild icon` } })
      message.guild.setIcon(icon).then(() => {
        message.channel.send({ embed: { color: "a3eb7b", description: `${approve} ${message.author}: Successfully set the guild icon to [**this image**](${icon})` } })
      })
    }
  }
}