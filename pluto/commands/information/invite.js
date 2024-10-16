const { MessageEmbed } = require('discord.js')
const { embedcolor, invite, support } = require('./../../config.json')

module.exports = {
  name: "invite",
  aliases: ['inv'],
  description: `gets bot invite`,
  usage: '{guildprefix}invite',
  run: async(client, message, args) => {

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setAuthor({ name: 'pluto is free..'})
    .setDescription(`contact **packrunnerkankan** if you have any questions, or join the [support server](${support}) for more info..\n> if pluto was accidentally removed, invite it [here](${invite})`)

    message.channel.send({ embeds: [embed] })
  }
}