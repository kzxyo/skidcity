const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: "createembed",
  aliases: ["ce", "embed"],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\`` } });

    const ceEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: createembed')
      .setDescription('Create your own embed\n**Documentation found [h̶e̶r̶e̶](https://google.com/)**')
      .addField('**Aliases**', 'ce, embed', true)
      .addField('**Parameters**', 'arg', true)
      .addField('**Information**', `${warn} Manage Messages`, true)
      .addField('**Usage**', '\`\`\`Syntax: createembed <embed code>\nExample: createembed {"title": "hi"}\`\`\`')
      .setFooter(`Module: misc`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(ceEmbed)
    try {
      const json = JSON.parse(args.join(' '))
      const { text = '' } = json

      if ({}.hasOwnProperty.call(json, "thumbnail")) {
        json.thumbnail = { url: json.thumbnail };
      }
      if ({}.hasOwnProperty.call(json, "image")) {
        json.image = { url: json.image };
      }

      message.channel.send(text, {
        embed: json
      })
    } catch (e) {
      message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: ${e.message}` } });
    }
  }
}