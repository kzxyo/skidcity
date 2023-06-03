const Discord = require('discord.js')
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')
const { color } = require('../../config.json')
const { deny } = require('../../emojis.json')

module.exports = {
  name: "setsplash",

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
    if (!message.guild.me.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_guild\`` } });
    if (!message.guild.features.includes("SPLASH")) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: This command requires: Guild \`Level 1\``}})
    let splash

    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: setsplash')
      .setDescription('Set a new guild splash')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'url', true)
      .addField('**Information**', `${warn} Manage Guild`, true)
      .addField('**Usage**', '\`\`\`Syntax: setsplash (url)\nExample: setsplash media.discordapp.com/attachments/871...png\`\`\`')
      .setFooter(`Module: servers`)
      .setTimestamp()
      .setColor(color)
    if (!splash) return message.channel.send(embed)

    if (message.attachments.first()) {
      splash = message.attachments.first().url
      message.guild.setSplash(splash).then(() => {
        message.channel.send({ embed: { color: "a3eb7b", description: `${approve} ${message.author}: Successfully set the guild splash to [**this image**](${splash})` } })
      })
    } else {
      splash = args[0]
      if (!splash) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You must provide a **url or attachment** to set as the guild splash` } })
      message.guild.setSplash(splash).then(() => {
        message.channel.send({ embed: { color: "a3eb7b", description: `${approve} ${message.author}: Successfully set the guild splash to [**this image**](${splash})` } })
      })
    }
  }
}