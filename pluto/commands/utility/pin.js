const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "pin",
  description: 'pin a message',
  usage: '{guildprefix}pin [id]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires \`manage messages\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires me to have \`manage messages\` permission`)

    const pin = args[0]

    if (!pin) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}pin`)
      .setDescription('pin a message')
      .addFields(
      { name: '**usage**', value: `${guildprefix}pin [id]`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    message.channel.messages.fetch(pin).then(d => {
      d.pin().catch(() => { 
        return message.channel.send(`an error occured`)
      })
    }).catch(() => { 
      return message.channel.send(`that is not a valid message id`)
    })
  }
}