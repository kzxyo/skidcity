const { MessageEmbed } = require("discord.js");
const { embedcolor } = require('./../../config.json')

module.exports = {
  name: "editsnipe",
  aliases: ['es'],
  description: `sends latest edited message`,
  usage: '{guildprefix}editsnipe',
  run: async(client, message, args) => {

    const msg = client.editsnipes.get(message.channel.id);

    if (!msg) return message.channel.send(`there's nothing to snipe in this channel`)
  
    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setAuthor({ name: `${msg.author}`, iconURL: `${message.guild.members.cache.find(u => u.user.tag == msg.author).user.displayAvatarURL({ format: "png", dynamic: true })}` })
    .setDescription(msg.content)
    .setFooter({ text: `${message.author.tag}` })
    .setTimestamp()

    if (msg.image) embed.setImage(msg.image)

    message.channel.send({ embeds: [embed] })
  }
}