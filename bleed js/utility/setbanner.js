const Discord = require('discord.js')
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')
const { color } = require('../../config.json')
const { deny } = require('../../emojis.json')

module.exports = {
  name: "setbanner",

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });
    if (!message.guild.me.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_guild\`` } });
    if (!message.guild.features.includes("BANNER")) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: This command requires: Guild \`Level 2\``}})
    let banner

    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: setbanner')
      .setDescription('Set a new guild banner')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'url', true)
      .addField('**Information**', `${warn} Manage Guild`, true)
      .addField('**Usage**', '\`\`\`Syntax: setbanner (url)\nExample: setbanner media.discordapp.com/attachments/871...png\`\`\`')
      .setFooter(`Module: servers`)
      .setTimestamp()
      .setColor(color)
    if (!banner) return message.channel.send(embed)

    if (message.attachments.first()) {
      banner = message.attachments.first().url
      message.guild.setBanner(banner).then(() => {
        message.channel.send({ embed: { color: "a3eb7b", description: `${approve} ${message.author}: Successfully set the guild banner to [**this image**](${banner})` } })
      })
    } else {
      banner = args[0]
      if (!banner) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You must provide a **url or attachment** to set as the guild banner` } })
      message.guild.setBanner(banner).then(() => {
        message.channel.send({ embed: { color: "a3eb7b", description: `${approve} ${message.author}: Successfully set the guild banner to [**this image**](${banner})` } })
      })
    }
  }
}