const Discord = require("discord.js")
const config = require("../../config.json")
const db = require("quick.db")
const { color } = require("../../config.json");

module.exports = {
  name: "editsnipe",
  aliases: ["es", "esnipe"],

  run: async (client, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

    let prefix = await db.fetch(`prefix_${message.guild.id}`)
    if (prefix == null) {
      prefix = config.DEFAULT_PREFIX
    }

    const msg = client.messageUpdate.get(message.channel.id)
    if (!msg) return message.channel.send({ embed: { color: "#6495ED", description: `:mag_right: ${message.author}:  No **recently edited messages** were found in this channel` } })
    if (message.author.bot) return;
    const embed = new Discord.MessageEmbed()
      .setAuthor(msg.author, message.guild.members.cache.find(u => u.user.tag == msg.author).user.displayAvatarURL({ format: "png", dynamic: true }))
      .setDescription(msg.content)
      .setColor(mentionedMember.displayHexColor || color)
      .setFooter(`Sniped message by: ${message.author.tag}`)
      .setTimestamp()
    if (msg.image) embed.setImage(msg.image)

    message.channel.send(embed)


  }
}