const Discord = require('discord.js');
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')
const { deny } = require('../../emojis.json')

module.exports = {
  name: "unpin",
  category: "utility",

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\``}});
    if (!message.guild.me.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`manage_messages\``}});

    const pinID = args.join(" ");

    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: unpin')
      .setDescription('Unpin any recent message by ID')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'message', true)
      .addField('**Information**', `${warn} Manage Messages`, true)
      .addField('**Usage**', '\`\`\`Syntax: unpin (messageid)\`\`\`')
      .setFooter(`Module: servers`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(embed)

    message.channel.messages.fetch(pinID).then(d => {
      d.unpin().catch(err => {
        message.channel.send({ embed: { color: "#e74c3c", description: `${deny} ${message.author}: An error has occurred! Failed to unpin message` } })
        console.log(err)
      })
      message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: **Unpinned** Message - \`${pinID}\`` } })
    }).catch(() => {
      message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: \`${pinID}\` is not a valid message id` } })
    })
  }
}